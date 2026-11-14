"""Collaudo Fase 5.2: etichette e ripartizione su più categorie (dati di esempio)."""
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
async def open_new(pg):
    await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT", accept_downloads=True); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            await open_new(pg)
            await pg.get_by_label("Importo (€)").fill("100")
            await pg.get_by_label("Descrizione").fill("Ipermercato")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
            await pg.get_by_role("button", name="Dividi tra più categorie").click()
            check(f"{label}: prima riga con categoria e totale", await pg.get_by_label("Importo categoria 1", exact=True).input_value() == "100,00")
            await pg.get_by_label("Importo categoria 1", exact=True).fill("30")
            await pg.get_by_label("Categoria 2", exact=True).select_option(label="Casa")
            check(f"{label}: la riga vuota prende il resto", await pg.get_by_text("prende il resto: 70,00 €").count() == 1)
            await pg.get_by_role("button", name="+ Aggiungi etichette").click()
            tag = pg.get_by_label("Etichette")
            await tag.fill("Vacanze estate"); await tag.press("Enter")
            await tag.fill("#regali"); await tag.press("Enter")
            check(f"{label}: etichette come chip", await pg.locator(".tag").count() == 2)
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            t = (await store(pg, "transactions"))[0]
            cats = {c["id"]: c["name"] for c in await store(pg, "categories")}
            check(f"{label}: ripartizione salvata", [(cats[s["categoryId"]], s["amount"]) for s in t["splits"]] == [("Spesa alimentare", 3000), ("Casa", 7000)], json.dumps(t.get("splits")))
            check(f"{label}: categoria principale = la parte più grande", cats[t["categoryId"]] == "Casa")
            check(f"{label}: etichette salvate", t["tags"] == ["Vacanze estate", "regali"], json.dumps(t["tags"]))
            row = await pg.locator(".list li").first.inner_text()
            check(f"{label}: riga con categorie ed etichette", "Spesa alimentare + Casa" in row and "#Vacanze estate" in row, row.replace("\n", " "))
            # analisi
            await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(500)
            bars = await pg.locator(".card").filter(has_text="Uscite per categoria").inner_text()
            check(f"{label}: analisi divide gli importi", "70,00" in bars and "30,00" in bars, bars.replace("\n", " ")[:200])
            tags_card = pg.locator(".card").filter(has=pg.get_by_role("heading", name="Etichette"))
            check(f"{label}: scheda etichette", "#Vacanze estate" in await tags_card.inner_text() and "100,00" in await tags_card.inner_text())
            await tags_card.get_by_role("button", name=re.compile("Vacanze estate")).click(); await pg.wait_for_timeout(400)
            check(f"{label}: dall'etichetta alla ricerca", pg.url.endswith("#/cerca") and await pg.get_by_text("1 movimento", exact=True).count() == 1)
            async with pg.expect_download() as d:
                await pg.get_by_role("button", name="Esporta per Excel (CSV)").click()
            csv = open(await (await d.value).path(), encoding="utf-8-sig").read()
            check(f"{label}: CSV una riga per categoria", "Ipermercato (parte 1 di 2);-30,00" in csv and "Ipermercato (parte 2 di 2);-70,00" in csv and "Vacanze estate, regali" in csv)
            # modifica: torna a una sola categoria
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            await pg.locator(".list li").first.click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: in modifica la ripartizione è caricata", await pg.get_by_label("Importo categoria 2", exact=True).input_value() == "70,00")
            await pg.get_by_role("button", name="Una sola categoria").click()
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            t = (await store(pg, "transactions"))[0]
            check(f"{label}: ripartizione tolta", t["splits"] == [] and cats[t["categoryId"]] == "Spesa alimentare")
            # errori
            await open_new(pg)
            await pg.get_by_label("Importo (€)").fill("50")
            await pg.get_by_role("button", name="Dividi tra più categorie").click()
            await pg.get_by_label("Categoria 1", exact=True).select_option(label="Svago")
            await pg.get_by_label("Importo categoria 1", exact=True).fill("20")
            await pg.get_by_label("Categoria 2", exact=True).select_option(label="Regali")
            await pg.get_by_label("Importo categoria 2", exact=True).fill("20")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
            err = await pg.locator("dialog [role=alert], dialog .error").all_text_contents()
            check(f"{label}: somma sbagliata segnalata", any("uguale al totale" in e for e in err), str(err))
            await pg.get_by_label("Importo categoria 2", exact=True).fill("")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            check(f"{label}: resto calcolato al salvataggio", len(await store(pg, "transactions")) == 2)
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
