"""Collaudo v0.25: icona delle categorie (scelta nel modulo, salvataggio, elenco e scelta della categoria)."""
import asyncio, re, json
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
# primo tracciato di ogni icona Lucide e numero di icone delle categorie, letti dal file generato
ICONS_TS = open("src/lib/icons.ts", encoding="utf-8").read()
N_CATEGORY_ICONS = len(re.findall(r"^  [a-z0-9]+: '", ICONS_TS.split("CATEGORY_ICONS = {")[1].split("}")[0], re.M))
FIRST = {}
for m in re.finditer(r"^  '([a-z0-9-]+)': (\[.*\]),$", ICONS_TS, re.M):
    nodes = json.loads(m.group(2)); FIRST[m.group(1)] = json.dumps(nodes[0][1], sort_keys=True)
async def store(pg, name):
    return await pg.evaluate("""(name) => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction(name).objectStore(name).getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null)) } } })""", name)
async def cat(pg, name):
    return next(c for c in await store(pg, "categories") if c["name"] == name and c["kind"] == "uscita")
async def drawn(loc):
    """Primo elemento disegnato nell'icona (per riconoscere quale icona è), oppure il testo (iniziale)."""
    return await loc.evaluate("""(el) => { const s = el.querySelector('svg > *'); if (!s) return 'TXT:' + el.textContent.trim();
      const o = {}; for (const a of s.attributes) o[a.name] = a.value; return JSON.stringify(o, Object.keys(o).sort()) }""")
def is_icon(d, lucide):
    return json.loads(d) == json.loads(FIRST[lucide]) if not d.startswith("TXT:") else False
def row(pg, name):
    return pg.locator("button.list-row", has=pg.get_by_text(name, exact=True))
async def open_cat(pg, name):
    await row(pg, name).first.click(); await pg.wait_for_selector("dialog[open]")
async def save(pg):
    await pg.locator("dialog").get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"], "color_scheme": "light"}), ("PC scuro", {"viewport": {"width": 1366, "height": 800}, "color_scheme": "dark"})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            # un conto, perché il modulo del movimento si apre solo se ce n'è uno
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav", state="attached"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.locator("dialog input[type=date]").fill("2026-11-01")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/categorie"); await pg.wait_for_selector("button.list-row"); await pg.wait_for_timeout(300)
            check(f"{label}: categoria iniziale con l'icona predefinita", is_icon(await drawn(row(pg, "Svago").first.locator(".cat-icon")), "popcorn"))
            await open_cat(pg, "Svago")
            field = pg.locator("dialog fieldset", has=pg.locator("legend", has_text="Icona"))
            toggle = field.locator("button[aria-expanded]")
            check(f"{label}: anteprima con il nome dell'icona", "Popcorn" in await field.locator(".what").inner_text() and await toggle.get_attribute("aria-expanded") == "false")
            await toggle.click()
            radios = field.get_by_role("radio")
            check(f"{label}: griglia aperta con tutte le icone e 'Nessuna'", await toggle.get_attribute("aria-expanded") == "true" and await radios.count() == N_CATEGORY_ICONS + 1, str(await radios.count()))
            check(f"{label}: icona attuale selezionata", await field.get_by_role("radio", name="Popcorn").get_attribute("aria-checked") == "true")
            box = await field.get_by_role("radio", name="Ciak").bounding_box()
            check(f"{label}: pulsanti dell'icona grandi almeno 44px", box["width"] >= 44 and box["height"] >= 44, str(box))
            await field.get_by_role("radio", name="Ciak").click()
            check(f"{label}: scelta aggiornata nell'anteprima", "Ciak" in await field.locator(".what").inner_text() and is_icon(await drawn(field.locator(".current .cat-icon")), "clapperboard"))
            await save(pg)
            check(f"{label}: icona salvata come chiave", (await cat(pg, "Svago")).get("icon") == "cinema")
            check(f"{label}: elenco con la nuova icona", is_icon(await drawn(row(pg, "Svago").first.locator(".cat-icon")), "clapperboard"))
            # nessuna icona -> iniziale
            await open_cat(pg, "Svago"); await field.locator("button[aria-expanded]").click()
            await field.get_by_role("radio", name="Nessuna icona (iniziale)").click(); await save(pg)
            check(f"{label}: 'Nessuna' salva null e mostra l'iniziale", (await cat(pg, "Svago")).get("icon", "assente") is None and await drawn(row(pg, "Svago").first.locator(".cat-icon")) == "TXT:S")
            # modifica senza toccare l'icona: quella predefinita non si scrive nei dati
            await open_cat(pg, "Regali"); await pg.get_by_role("radio", name="Colore 5").click(); await save(pg)
            c = await cat(pg, "Regali")
            check(f"{label}: senza cambiare icona il campo resta assente", c["color"] == "s5" and "icon" not in c, json.dumps(c))
            # nuova categoria con icona
            await pg.get_by_role("button", name=re.compile("Categoria")).first.click(); await pg.wait_for_selector("dialog[open]")
            await pg.locator("dialog").get_by_label("Nome").fill("Palestra")
            check(f"{label}: nuova categoria parte senza icona", "iniziale" in await field.locator(".what").inner_text() and await field.locator("button[aria-expanded]").inner_text() == "Scegli")
            await field.locator("button[aria-expanded]").click(); await field.get_by_role("radio", name="Manubrio").click(); await save(pg)
            check(f"{label}: nuova categoria salvata con l'icona", (await cat(pg, "Palestra")).get("icon") == "sport")
            # scelta della categoria in un nuovo movimento
            await pg.goto(BASE + "/#/movimenti/nuovo"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(300)
            opt = pg.locator(".cat-list .cat", has=pg.get_by_text("Palestra", exact=True))
            check(f"{label}: icona anche nella scelta della categoria", is_icon(await drawn(opt.locator(".cat-icon")), "dumbbell"))
            await pg.reload(); await pg.goto(BASE + "/#/categorie"); await pg.wait_for_timeout(500)
            check(f"{label}: icone conservate dopo il riavvio", is_icon(await drawn(row(pg, "Palestra").first.locator(".cat-icon")), "dumbbell") and await drawn(row(pg, "Svago").first.locator(".cat-icon")) == "TXT:S")
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
