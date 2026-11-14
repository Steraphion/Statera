"""Collaudo v0.29: logo e icone dell'app (bilancia a tratto) — manifest, favicon, scorciatoie, logo nell'app.

Controlla che ogni icona dichiarata esista con la dimensione giusta e lo scopo giusto (any, maskable, monochrome),
le parti trasparenti e piene (maskable piena fino agli angoli, monochrome trasparente fuori dal simbolo), la favicon
ICO con 16/32/48, che tutto sia nella cache per l'uso senza rete e il logo nella barra laterale in chiaro e in scuro.
Uso: `npm run build && npx vite preview --port 4173` e poi `python3 qa/icona.py`.
"""
import asyncio, json, struct
from playwright.async_api import async_playwright

BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

def png_size(b):
    return struct.unpack(">II", b[16:24]) if b[:8] == b"\x89PNG\r\n\x1a\n" else None

# Legge i pixel di un'immagine nella pagina: angolo in alto a sinistra e centro (RGBA)
PIXELS = """async (src) => { const img = new Image(); img.src = src; await img.decode();
  const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d'); g.drawImage(img, 0, 0);
  const at = (x, y) => [...g.getImageData(x, y, 1, 1).data];
  return { corner: at(1, 1), centre: at(c.width >> 1, Math.round(c.height * 0.45)), w: c.width, h: c.height } }"""
INDACO = [83, 90, 166]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(viewport={"width": 1366, "height": 800}, locale="it-IT", color_scheme="light")
        pg = await ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_selector("nav", state="attached"); await pg.wait_for_timeout(300)

        m = json.loads(await (await pg.request.get(BASE + "/manifest.webmanifest")).text())
        icons = m.get("icons", [])
        by = {(i.get("purpose", "any"), i["sizes"]): i["src"] for i in icons}
        for need in [("any", "192x192"), ("any", "512x512"), ("maskable", "192x192"), ("maskable", "512x512"), ("monochrome", "512x512"), ("any", "16x16"), ("any", "32x32"), ("any", "48x48")]:
            check(f"manifest: icona {need[0]} {need[1]}", need in by, json.dumps(icons)[:300])
        for i in icons:
            r = await pg.request.get(BASE + "/" + i["src"]); body = await r.body()
            w, h = (int(x) for x in i["sizes"].split("x"))
            check(f"manifest: {i['src']} raggiungibile e di {w}×{h}", r.status == 200 and png_size(body) == (w, h), f"{r.status} {png_size(body)}")
        check("manifest: sfondo d'avvio e barra di sistema", m.get("background_color", "").upper() == "#F4F5FB" and m.get("theme_color", "").upper() == "#F4F5FB", json.dumps([m.get("background_color"), m.get("theme_color")]))

        px = await pg.evaluate(PIXELS, BASE + "/" + by[("any", "512x512")])
        check("icona any: angoli trasparenti, riquadro indaco", px["corner"][3] == 0 and px["centre"][:3] in (INDACO, [255, 255, 255]), json.dumps(px))
        px = await pg.evaluate(PIXELS, BASE + "/" + by[("maskable", "512x512")])
        check("icona maskable: piena fino agli angoli", px["corner"] == INDACO + [255], json.dumps(px))
        px = await pg.evaluate(PIXELS, BASE + "/" + by[("monochrome", "512x512")])
        check("icona monochrome: trasparente fuori dal simbolo, simbolo opaco", px["corner"][3] == 0 and px["centre"][3] == 255, json.dumps(px))

        sc = m.get("shortcuts", [])
        check("manifest: tre scorciatoie con icona", len(sc) == 3 and all(s.get("icons") for s in sc))
        for s in sc:
            r = await pg.request.get(BASE + "/" + s["icons"][0]["src"])
            check(f"scorciatoia {s['short_name']}: icona di 96×96", r.status == 200 and png_size(await r.body()) == (96, 96))

        links = await pg.evaluate("() => [...document.querySelectorAll('link[rel=icon], link[rel=apple-touch-icon]')].map(l => [l.rel, l.getAttribute('href'), l.type, l.getAttribute('sizes')])")
        check("pagina: favicon ICO, SVG e icona Apple", [l[1] for l in links] == ["./favicon.ico", "./favicon.svg", "./icons/apple-touch-icon.png"], json.dumps(links))
        ico = await (await pg.request.get(BASE + "/favicon.ico")).body()
        n = struct.unpack("<HHH", ico[:6])
        sizes = sorted(ico[6 + 16 * i] for i in range(n[2])) if n[:2] == (0, 1) else []
        check("favicon.ico: 16, 32 e 48 px", sizes == [16, 32, 48], json.dumps(sizes))
        svg = await (await pg.request.get(BASE + "/favicon.svg")).text()
        check("favicon.svg: riquadro indaco, nessuna risorsa esterna", "#535AA6" in svg and "http" not in svg.replace("http://www.w3.org/2000/svg", ""))
        apple = await (await pg.request.get(BASE + "/icons/apple-touch-icon.png")).body()
        check("icona Apple: 180×180", png_size(apple) == (180, 180))

        sw = await (await pg.request.get(BASE + "/sw.js")).text()
        missing = [f for f in ["favicon.ico", "favicon.svg", "icons/maskable-512.png", "icons/monochrome-512.png", "icons/shortcut-uscita.png"] if f not in sw]
        check("senza rete: icone nella cache dell'app", not missing, ", ".join(missing))

        # Logo nella barra laterale (PC), chiaro e scuro
        brand = pg.locator("nav .brand svg")
        check("logo: nella barra laterale col riquadro e il simbolo", await brand.count() == 1 and await brand.locator("rect.tile").count() == 1 and await brand.locator("g.glyph > *").count() >= 5)
        fill = await brand.locator("rect.tile").evaluate("e => getComputedStyle(e).fill")
        check("logo: riquadro indaco in tema chiaro", fill == "rgb(83, 90, 166)", fill)
        await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(300)
        await pg.get_by_role("radiogroup", name="Tema").get_by_role("radio", name="Scuro").click(); await pg.wait_for_timeout(200)
        fill = await brand.locator("rect.tile").evaluate("e => getComputedStyle(e).fill")
        glyph = await brand.locator("g.glyph").evaluate("e => getComputedStyle(e).color")
        check("logo: riquadro lilla e simbolo scuro in tema scuro", fill == "rgb(169, 179, 238)" and glyph == "rgb(14, 15, 22)", f"{fill} {glyph}")
        await pg.get_by_role("radiogroup", name="Tema").get_by_role("radio", name="Automatico").click()
        check("nessun errore in console", not errs, "; ".join(errs[:3]))
        await ctx.close()

        # Telefono: il logo non deve comparire nella barra in basso
        ctx = await b.new_context(**p.devices["Pixel 7"], locale="it-IT"); pg = await ctx.new_page()
        await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_selector("nav", state="attached"); await pg.wait_for_timeout(300)
        check("telefono: logo nascosto nella barra in basso", not await pg.locator("nav .brand").is_visible())
        await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
