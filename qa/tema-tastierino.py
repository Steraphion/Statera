"""Collaudo v0.26: scelta del tema (Automatico/Chiaro/Scuro) e tastierino degli importi su telefono."""
import asyncio, re, json
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
async def store(pg, name):
    return await pg.evaluate("""(name) => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction(name).objectStore(name).getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null)) } } })""", name)
async def state(pg):
    return await pg.evaluate("""() => ({ theme: document.documentElement.dataset.theme,
      bg: getComputedStyle(document.body).backgroundColor, meta: [...document.querySelectorAll('meta[name=theme-color]')].map(m => m.content),
      saved: localStorage.getItem('statera.tema') })""")
async def pick_theme(pg, name):
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(300)
    await pg.get_by_role("radiogroup", name="Tema").get_by_role("radio", name=name).click(); await pg.wait_for_timeout(200)
LIGHT_BG, DARK_BG = "rgb(244, 245, 251)", "rgb(14, 15, 22)"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts, phone in [("Android scuro", {**p.devices["Pixel 7"], "color_scheme": "dark"}, True), ("PC chiaro", {"viewport": {"width": 1366, "height": 800}, "color_scheme": "light"}, False)]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_selector("nav", state="attached"); await pg.wait_for_timeout(300)
            st = await state(pg)
            sys_theme = "dark" if phone else "light"
            check(f"{label}: all'inizio segue il sistema", st["theme"] == sys_theme and st["bg"] == (DARK_BG if phone else LIGHT_BG) and st["saved"] is None, json.dumps(st))
            other, other_name = ("light", "Chiaro") if phone else ("dark", "Scuro")
            await pick_theme(pg, other_name)
            st = await state(pg)
            check(f"{label}: scelta '{other_name}' applicata subito", st["theme"] == other and st["bg"] == (LIGHT_BG if phone else DARK_BG) and st["saved"] == other, json.dumps(st))
            check(f"{label}: colore della barra di sistema aggiornato", all(m.lower() == ("#f4f5fb" if phone else "#0e0f16") for m in st["meta"]), json.dumps(st["meta"]))
            await pg.reload(); await pg.wait_for_timeout(300)
            first = await pg.evaluate("() => document.documentElement.dataset.theme")
            check(f"{label}: la scelta resta dopo il riavvio", first == other)
            await pick_theme(pg, "Automatico")
            st = await state(pg)
            check(f"{label}: 'Automatico' torna al sistema", st["theme"] == sys_theme and st["saved"] is None, json.dumps(st))
            # conto di esempio
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.locator("dialog input[type=date]").fill("2026-11-01")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti/nuovo"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
            amt = pg.get_by_label("Importo (€)"); kp = pg.locator("dialog .keypad")
            if phone:
                check(f"{label}: tastierino aperto sull'importo, senza tastiera del telefono", await kp.count() == 1 and await amt.get_attribute("inputmode") == "none" and await amt.evaluate("e => e === document.activeElement"))
                async def key(n): await kp.get_by_role("button", name=n, exact=True).click()
                for k in ["1", "2", "Virgola", "5", "Più", "3"]: await key(k)
                check(f"{label}: i tasti scrivono nel campo", await amt.input_value() == "12,5+3", await amt.input_value())
                check(f"{label}: anteprima del calcolo", await pg.get_by_text("= 15,50 €").count() == 1)
                await key("Calcola")
                check(f"{label}: '=' sostituisce il calcolo col risultato", await amt.input_value() == "15,50", await amt.input_value())
                await key("Cancella"); await key("Cancella")
                check(f"{label}: cancella l'ultima cifra", await amt.input_value() == "15,", await amt.input_value())
                check(f"{label}: il cursore resta nel campo mentre si usa il tastierino", await amt.evaluate("e => e === document.activeElement"))
                save = pg.locator("dialog").get_by_role("button", name="Salva", exact=True)
                box, vh = await save.bounding_box(), pg.viewport_size["height"]
                kb = await kp.bounding_box()
                check(f"{label}: Salva resta visibile sotto il tastierino", box["y"] + box["height"] <= vh and box["y"] >= kb["y"] + kb["height"] - 1, f"{box} {kb}")
                keys = await kp.get_by_role("button").all()
                sizes = [await k.bounding_box() for k in keys]
                check(f"{label}: tasti grandi almeno 44px", all(s["height"] >= 44 and s["width"] >= 44 for s in sizes if s))
                await key("Fatto")
                check(f"{label}: 'Fatto' chiude il tastierino", await kp.count() == 0 and not await amt.evaluate("e => e === document.activeElement"))
                await amt.click(); await pg.wait_for_timeout(100)
                check(f"{label}: toccando il campo il tastierino torna", await kp.count() == 1)
                cat = pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare"))
                await cat.tap(); await pg.wait_for_timeout(500)
                check(f"{label}: con il tastierino aperto il tocco su una categoria non va perso", await cat.get_attribute("aria-checked") == "true" and await kp.count() == 0)
                await amt.tap(); await pg.wait_for_timeout(150)
                await pg.get_by_label("Descrizione").click(); await pg.wait_for_timeout(100)
                check(f"{label}: su un campo di testo si chiude", await kp.count() == 0)
                await pg.get_by_label("Descrizione").fill("Pane")
                check(f"{label}: niente pulsante + accanto al campo (è nel tastierino)", await pg.get_by_role("button", name="Aggiungi un importo (somma)").count() == 0)
            else:
                check(f"{label}: su PC niente tastierino, tastiera normale", await kp.count() == 0 and await amt.get_attribute("inputmode") == "decimal" and await pg.get_by_role("button", name="Aggiungi un importo (somma)").count() == 1)
                await amt.fill("15,"); await pg.get_by_label("Descrizione").fill("Pane")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
            await pg.locator("dialog").get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            t = await store(pg, "transactions")
            check(f"{label}: movimento salvato con l'importo scritto", len(t) == 1 and t[0]["parts"][0]["amount"] == 1500, json.dumps([x["parts"] for x in t]))
            if phone:
                # numero di buoni: solo cifre
                await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
                await pg.get_by_role("button", name="Conto").first.click()
                await pg.get_by_label("Nome").fill("Buoni"); await pg.get_by_label("Tipo").select_option("buoni_pasto"); await pg.wait_for_timeout(200)
                await pg.get_by_label("Buoni disponibili").click(); await pg.wait_for_timeout(100)
                kp2 = pg.locator("dialog .keypad")
                check(f"{label}: per i buoni il tastierino ha solo cifre", await kp2.count() == 1 and not await kp2.get_by_role("button", name="Virgola").is_visible() and not await kp2.get_by_role("button", name="Più").is_visible())
                await pg.get_by_role("button", name="Chiudi").first.click(); await pg.wait_for_timeout(200)
                # Cerca: il tastierino compare in fondo alla pagina
                await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(300)
                await pg.get_by_role("button", name=re.compile("^Filtri")).click(); await pg.wait_for_timeout(200)
                await pg.get_by_label("Importo da (€)").click(); await pg.wait_for_timeout(150)
                fk = pg.locator(".keypad.floating")
                check(f"{label}: in Cerca il tastierino sta in fondo alla pagina", await fk.count() == 1)
                await fk.get_by_role("button", name="5", exact=True).click(); await fk.get_by_role("button", name="0", exact=True).click()
                check(f"{label}: e scrive nel filtro", await pg.get_by_label("Importo da (€)").input_value() == "50")
                await fk.get_by_role("button", name="Fatto").click()
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
