"""Collaudo Fase 5.4: importazione da CSV (file di esempio generati qui)."""
import asyncio, re, json, tempfile, os
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
tmp = tempfile.mkdtemp()
BANK = os.path.join(tmp, "estratto-conto.csv")
open(BANK, "w", encoding="utf-8").write("Data operazione;Descrizione;Importo\n03/11/2026;PAGAMENTO POS SUPERMERCATO;-45,20\n04/11/2026;BONIFICO RICEVUTO;300,00\n05/11/2026;RIGA ROTTA;xx\n")
OWN = os.path.join(tmp, "statera.csv")
open(OWN, "w", encoding="utf-8-sig").write("Data;Tipo;Categoria;Sottocategoria;Descrizione;Importo;Conto o carta;Verso;Buoni;Note;Etichette\r\n06/11/2026;Uscita;Casa;Bollette;Luce;-60,50;Conto;;;nota di prova;Casa nuova\r\n07/11/2026;Trasferimento;;;Prelievo;50,00;Conto;Contanti;;;\r\n")
def sel(pg, label):
    return pg.locator("dialog label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(label)}$"))).locator("select")
async def store(pg, name):
    return await pg.evaluate("""(name) => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction(name).objectStore(name).getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null)) } } })""", name)
async def open_import(pg, path):
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name="Importa da CSV").click(); await pg.wait_for_selector("dialog[open]")
    await pg.locator("dialog input[type=file]").set_input_files(path); await pg.wait_for_timeout(400)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.locator("dialog input[type=date]").fill("2026-11-01")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            # estratto conto della banca
            await open_import(pg, BANK)
            check(f"{label}: colonne riconosciute", await sel(pg, "Data *").input_value() == "0" and await sel(pg, "Importo *").input_value() == "2" and await sel(pg, "Descrizione").input_value() == "1")
            summ = await pg.locator(".summary").inner_text()
            check(f"{label}: riepilogo dell'anteprima", "2 da importare" in summ and "1 con problemi" in summ and "Altro" in summ, summ)
            check(f"{label}: anteprima con il problema della riga", await pg.get_by_text("Riga 4: Importo non valido").count() == 1)
            await pg.get_by_role("button", name="Importa 2 movimenti").click(); await pg.wait_for_timeout(600)
            t = await store(pg, "transactions")
            check(f"{label}: importati con il tipo dal segno", sorted((x["type"], x["parts"][0]["amount"]) for x in t) == [("entrata", 30000), ("uscita", 4520)], json.dumps([(x["type"], x["parts"][0]["amount"]) for x in t]))
            check(f"{label}: avviso di conferma", "2 movimenti importati" in await pg.locator(".toast").inner_text())
            await open_import(pg, BANK)
            summ = await pg.locator(".summary").inner_text()
            check(f"{label}: reimportando, i movimenti già presenti si saltano", "0 da importare" in summ and "2 già presenti" in summ and await pg.get_by_role("button", name="Importa 0 movimenti").is_disabled(), summ)
            await pg.get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(300)
            # file esportato da Statera
            await open_import(pg, OWN)
            check(f"{label}: formato di Statera riconosciuto", await sel(pg, "Sottocategoria").input_value() == "3" and await sel(pg, "Etichette").input_value() == "10")
            check(f"{label}: trasferimento escluso", await pg.get_by_text("Trasferimento: non si importa").count() == 1)
            await pg.get_by_role("button", name="Importa 1 movimento").click(); await pg.wait_for_timeout(600)
            t = await store(pg, "transactions")
            cats = {c["id"]: c["name"] for c in await store(pg, "categories")}
            luce = [x for x in t if x["description"] == "Luce"]
            check(f"{label}: categoria, nota ed etichetta riprese", len(luce) == 1 and cats[luce[0]["categoryId"]] == "Bollette" and luce[0]["notes"] == "nota di prova" and luce[0]["tags"] == ["Casa nuova"], json.dumps(luce))
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
