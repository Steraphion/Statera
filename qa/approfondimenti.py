"""Collaudo Fase 5.1: riepilogo del mese, ritmo e stima, confronti, patrimonio (orologio fisso, dati di esempio)."""
import asyncio, re, os, datetime
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
SAMPLE = open(os.path.join(os.path.dirname(__file__), "anno-di-esempio.js")).read()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 5, 10, 0))
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("2000")
            await pg.locator("dialog input[type=date]").fill("2025-11-30")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.evaluate(SAMPLE)
            await pg.goto(BASE + "/#/movimenti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
            recap = pg.locator("section.recap")
            check(f"{label}: riepilogo di ottobre nei primi giorni del mese", await recap.count() == 1 and "Ottobre in breve" in await recap.inner_text())
            txt = await recap.inner_text()
            check(f"{label}: riepilogo con confronto e categoria principale", "rispetto a settembre" in txt and "Casa" in txt, txt.replace("\n", " | "))
            await recap.get_by_role("button", name="Vedi l'analisi").click(); await pg.wait_for_timeout(600)
            check(f"{label}: apre l'analisi di ottobre", pg.url.endswith("#/analisi") and await pg.get_by_role("heading", name="Ottobre 2026").count() == 1)
            pace = pg.locator(".pace")
            check(f"{label}: mese passato: media al giorno, senza stima", await pace.count() == 1 and "al giorno" in await pace.inner_text() and "stima" not in await pace.inner_text())
            await pg.get_by_role("button", name="Oggi").click(); await pg.wait_for_timeout(400)
            check(f"{label}: mese in corso: stima di fine mese", "a questo ritmo" in await pace.inner_text() and "(stima)" in await pace.inner_text())
            ch = pg.locator(".changes .change")
            check(f"{label}: confronto con la media", await ch.count() >= 1, str(await ch.count()))
            first = await ch.first.inner_text() if await ch.count() else ""
            check(f"{label}: confronto con direzione scritta (non solo colore)", ("più" in first or "meno" in first or "nuova" in first) and "media di" in first, first.replace("\n", " "))
            worth = pg.locator("h2", has_text="Patrimonio")
            check(f"{label}: grafico del patrimonio", await worth.count() == 1 and await pg.locator("svg[aria-label^='Patrimonio']").count() == 1)
            card = pg.locator(".card", has=worth)
            await card.get_by_role("button", name="Tabella").click(); await pg.wait_for_timeout(200)
            rows = await card.locator("tbody tr").count()
            check(f"{label}: tabella del patrimonio (12 mesi)", rows == 12, str(rows))
            check(f"{label}: primo mese della tabella è novembre", "novembre 2026" in (await card.locator("tbody tr").first.inner_text()).lower())
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
            check(f"{label}: riepilogo non più mostrato", await recap.count() == 0)
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        # dopo il 7 del mese il riepilogo non compare
        ctx = await b.new_context(locale="it-IT"); pg = await ctx.new_page()
        await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 12, 10, 0))
        await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(300)
        await pg.get_by_role("button", name="Conto").first.click()
        await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("2000")
        await pg.locator("dialog input[type=date]").fill("2025-11-30")
        await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
        await pg.evaluate(SAMPLE)
        await pg.goto(BASE + "/#/movimenti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
        check("dopo il 7 del mese niente riepilogo", await pg.locator("section.recap").count() == 0)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
