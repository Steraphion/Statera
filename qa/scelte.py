"""Collaudo v0.33: su telefono elenchi a tendina e date si scelgono in un pannello dell'app (non quello di
Android); il campo vero riceve il valore. Su PC restano i campi del sistema. Uso come collaudo.py."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
SHOTS = sys.argv[1] if len(sys.argv) > 1 else None
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
# il dito che tocca: si registra se la fine del tocco è stata annullata (= Android non apre il suo pannello)
SPY = """() => { window.__tocchi = []; document.addEventListener('touchend', e => {
  if (e.target.matches && e.target.matches('select, input[type=date]')) window.__tocchi.push(e.defaultPrevented) }) }"""
def sheet(pg, title):
    return pg.locator("dialog[open]", has=pg.locator("h2", has_text=re.compile("^" + re.escape(title) + "$")))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for scheme in ("light", "dark"):
            label = f"Telefono {'chiaro' if scheme == 'light' else 'scuro'}"
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**p.devices["Pixel 7"], color_scheme=scheme, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav", state="attached"); await pg.wait_for_timeout(400)
            await pg.evaluate(SPY)
            await pg.get_by_role("button", name="Conto").first.tap(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Nome").fill("Conto di prova")
            # --- elenco a tendina
            tipo = pg.get_by_label("Tipo")
            before = await tipo.input_value()
            await tipo.tap(); await pg.wait_for_timeout(500)
            ps = sheet(pg, "Tipo")
            check(f"{label}: toccando 'Tipo' si apre il pannello dell'app", await ps.count() == 1)
            check(f"{label}: il pannello di Android non si apre (tocco annullato)", await pg.evaluate("() => window.__tocchi.at(-1)") is True)
            radios = ps.get_by_role("radio")
            names = [await r.inner_text() for r in await radios.all()]
            check(f"{label}: tutte le voci, quella attuale segnata", names == ["Contanti", "Conto corrente", "Buoni pasto", "Altro"] and await ps.get_by_role("radio", name="Conto corrente").get_attribute("aria-checked") == "true", json.dumps(names))
            boxes = [await r.bounding_box() for r in await radios.all()]
            check(f"{label}: voci alte almeno 44 px", all(x["height"] >= 44 for x in boxes))
            if SHOTS: await pg.screenshot(path=f"{SHOTS}/scelta-elenco-{scheme}.png")
            await ps.get_by_role("radio", name="Buoni pasto").tap(); await pg.wait_for_timeout(500)
            check(f"{label}: la scelta arriva al campo e il modulo si aggiorna", await tipo.input_value() == "buoni_pasto" and await pg.get_by_label("Buoni disponibili").count() == 1 and await ps.count() == 0, before)
            # Esc / Chiudi: nessun cambiamento
            await tipo.tap(); await pg.wait_for_timeout(400)
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
            check(f"{label}: Esc chiude senza cambiare", await sheet(pg, "Tipo").count() == 0 and await tipo.input_value() == "buoni_pasto" and await pg.locator("dialog[open]").count() == 1)
            await tipo.tap(); await pg.wait_for_timeout(400)
            await sheet(pg, "Tipo").get_by_role("radio", name="Conto corrente").tap(); await pg.wait_for_timeout(500)
            # --- data
            data = pg.locator("dialog[open] input[type=date]").first
            await data.fill("2026-11-15")
            await data.tap(); await pg.wait_for_timeout(500)
            ds = pg.locator("dialog[open]").last
            title = await ds.locator("h2").inner_text()
            check(f"{label}: toccando la data si apre il calendario dell'app", await ds.get_by_role("group", name="novembre 2026").count() == 1, title)
            check(f"{label}: niente calendario di Android", await pg.evaluate("() => window.__tocchi.at(-1)") is True)
            check(f"{label}: giorno attuale evidenziato", await ds.get_by_role("button", name="domenica 15 novembre 2026").get_attribute("aria-pressed") == "true")
            if SHOTS: await pg.screenshot(path=f"{SHOTS}/scelta-data-{scheme}.png")
            await ds.get_by_role("button", name="Mese precedente").tap(); await pg.wait_for_timeout(200)
            check(f"{label}: mese precedente", await ds.get_by_role("group", name="ottobre 2026").count() == 1)
            # mesi e anni
            await ds.get_by_role("button", name="ottobre 2026", exact=True).tap(); await pg.wait_for_timeout(200)
            await ds.get_by_role("button", name="Anno precedente").tap(); await pg.wait_for_timeout(200)
            if SHOTS: await pg.screenshot(path=f"{SHOTS}/scelta-mesi-{scheme}.png")
            await ds.get_by_role("button", name="marzo 2025").tap(); await pg.wait_for_timeout(200)
            await ds.get_by_role("button", name="lunedì 3 marzo 2025").tap(); await pg.wait_for_timeout(500)
            check(f"{label}: scelta di un giorno lontano tramite mesi e anni", await data.input_value() == "2025-03-03" and await pg.locator("dialog[open]").count() == 1)
            await data.tap(); await pg.wait_for_timeout(400)
            ds = pg.locator("dialog[open]").last
            await ds.get_by_role("button", name="Oggi").tap(); await pg.wait_for_timeout(400)
            today = await pg.evaluate("() => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') }")
            check(f"{label}: 'Oggi'", await data.input_value() == today)
            await pg.get_by_role("button", name="Salva").tap(); await pg.wait_for_timeout(600)
            # --- modulo del movimento: 'Con' e il + che resta escluso dal rinnovo Google
            await pg.goto(BASE + "/#/movimenti/nuovo"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
            con = pg.locator("dialog[open] label.field", has=pg.locator("span", has_text=re.compile("^Con$"))).locator("select")
            await con.tap(); await pg.wait_for_timeout(400)
            cs = pg.locator("dialog[open]").last
            check(f"{label}: 'Con' nel pannello dell'app sopra il modulo", await pg.locator("dialog[open]").count() == 2 and await cs.get_by_role("radio").count() >= 1)
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
            # --- Cerca: data facoltativa, 'Cancella'
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
            await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(400)
            fb = pg.get_by_role("button", name=re.compile("^Filtri"))
            if await fb.count(): await fb.tap(); await pg.wait_for_timeout(300)
            dal = pg.locator("input[type=date]").first
            await dal.tap(); await pg.wait_for_timeout(400)
            ds = pg.locator("dialog[open]").last
            await ds.get_by_role("button", name=re.compile(r"^\w+ 1 ")).first.tap(); await pg.wait_for_timeout(400)
            got = await dal.input_value()
            check(f"{label}: in Cerca il calendario funziona anche fuori dai pannelli", got.endswith("-01"), got)
            await dal.tap(); await pg.wait_for_timeout(400)
            await pg.locator("dialog[open]").last.get_by_role("button", name="Cancella").tap(); await pg.wait_for_timeout(400)
            check(f"{label}: 'Cancella' svuota una data facoltativa", await dal.input_value() == "")
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        # --- PC: campi del sistema, nessun pannello
        print("\n===== PC =====")
        ctx = await b.new_context(viewport={"width": 1366, "height": 800}, locale="it-IT"); pg = await ctx.new_page()
        await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(500)
        await pg.get_by_role("button", name="Conto").first.click(); await pg.wait_for_selector("dialog[open]")
        tipo = pg.get_by_label("Tipo")
        await tipo.click(); await pg.wait_for_timeout(300)
        check("PC: niente pannello dell'app, resta l'elenco del sistema", await pg.locator("dialog[open]").count() == 1 and await tipo.get_attribute("data-picker") is None)
        await ctx.close(); await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
