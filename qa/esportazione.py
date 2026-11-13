"""Collaudo esportazione CSV per Excel (dati di esempio)."""
import asyncio, re, datetime
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
TODAY = datetime.date.today()
async def new_movement(pg, kind, amount, cat, desc):
    await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
    if kind == "entrata": await pg.get_by_role("radio", name="Entrata").click()
    await pg.get_by_label("Importo (€)").fill(amount)
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile(f"^{cat}")).first.click()
    await pg.get_by_label("Descrizione").fill(desc)
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
async def read_download(pg, click):
    async with pg.expect_download() as d:
        await click()
    dl = await d.value
    data = open(await dl.path(), "rb").read()
    return dl.suggested_filename, data
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT", accept_downloads=True); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto di prova"); await pg.get_by_label("Saldo iniziale (€)").fill("500")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            await new_movement(pg, "uscita", "1234,5", "Spesa", 'Caffè; "pausa"')
            await new_movement(pg, "uscita", "12", "Bollette", "=1+1")
            await new_movement(pg, "entrata", "1500", "Stipendio", "Stipendio")
            # Cerca
            await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(300)
            await pg.get_by_label("Cerca").fill("caff"); await pg.wait_for_timeout(300)
            name, data = await read_download(pg, lambda: pg.get_by_role("button", name="Esporta per Excel (CSV)").click())
            text = data.decode("utf-8")
            check(f"{label}: Cerca — nome file", name == "statera-movimenti.csv", name)
            check(f"{label}: Cerca — BOM UTF-8", data.startswith(b"\xef\xbb\xbf"))
            lines = text.lstrip("﻿").split("\r\n")
            check(f"{label}: Cerca — intestazione con ;", lines[0].startswith("Data;Tipo;Categoria;Sottocategoria;Descrizione;Importo"), lines[0])
            check(f"{label}: Cerca — solo i risultati", len([l for l in lines[1:] if l]) == 1, str(lines))
            check(f"{label}: Cerca — accenti, virgolette e importo", 'Caffè; ""pausa""";-1234,50;Conto di prova' in text, lines[1] if len(lines) > 1 else "")
            check(f"{label}: Cerca — data italiana", lines[1].startswith(TODAY.strftime("%d/%m/%Y")), lines[1])
            # Analisi
            await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(500)
            name, data = await read_download(pg, lambda: pg.get_by_role("button", name=re.compile("^Esporta i movimenti del periodo")).click())
            text = data.decode("utf-8-sig")
            first = TODAY.replace(day=1).isoformat()
            check(f"{label}: Analisi — nome file con il periodo", name.startswith(f"statera-movimenti-{first}_"), name)
            rows = [l for l in text.split("\r\n")[1:] if l]
            check(f"{label}: Analisi — tutti i movimenti del mese", len(rows) == 3, str(rows))
            check(f"{label}: Analisi — formula neutralizzata", ";'=1+1;" in text)
            check(f"{label}: Analisi — entrata positiva", ";1500,00;" in text)
            await pg.get_by_role("radio", name="Anno").click(); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Periodo precedente").click(); await pg.wait_for_timeout(300)
            check(f"{label}: Analisi — periodo vuoto, pulsante disattivato",
                  await pg.get_by_role("button", name=re.compile("^Esporta i movimenti del periodo")).is_disabled())
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
