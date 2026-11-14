"""Collaudo Fase 4.1: inserimento rapido (dati di esempio)."""
import asyncio, re, json
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
async def alive(pg):
    return await pg.evaluate("""() => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction('transactions').objectStore('transactions').getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null).map(t => ({d: t.description, a: t.parts.map(p => p.amount), c: t.categoryId, card: t.parts.map(p => p.cardId), type: t.type}))) } } })""")
def sel(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(label)}$"))).locator("select")
async def open_new(pg):
    await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Carta").first.click()
            await pg.get_by_label("Nome").fill("Bancomat"); await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            # 1) calcolo nell'importo + pulsante +
            await open_new(pg)
            amt = pg.get_by_label("Importo (€)")
            await amt.fill("12,50")
            # su telefono il + è nel tastierino dell'app, su PC accanto al campo
            plus = pg.get_by_role("button", name="Aggiungi un importo (somma)")
            await (plus if await plus.count() else pg.locator(".keypad").get_by_role("button", name="Più")).click()
            check(f"{label}: il + aggiunge l'operatore e lascia il cursore nel campo", await amt.input_value() == "12,50+" and await amt.evaluate("e => e === document.activeElement"))
            await amt.press_sequentially("3,20")
            check(f"{label}: anteprima del risultato", await pg.get_by_text("= 15,70 €").count() == 1)
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
            check(f"{label}: il calcolo resta visibile fino al salvataggio", await pg.get_by_text("= 15,70 €").count() == 1)
            await sel(pg, "Con").select_option(label="Bancomat (Conto)")
            await pg.get_by_label("Descrizione").fill("Conad")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
            a = await alive(pg)
            check(f"{label}: salvato il risultato del calcolo", a and a[0]["a"] == [1570], json.dumps(a))
            # 2) suggerimenti: nuovo movimento, si parte dalla descrizione
            await open_new(pg)
            await pg.get_by_label("Descrizione").fill("co")
            sug = pg.locator("#desc-suggestions button")
            check(f"{label}: compare il suggerimento", await sug.count() == 1 and "Conad" in await sug.first.inner_text())
            detail = await sug.first.inner_text()
            check(f"{label}: il suggerimento mostra categoria, carta e importo", "Spesa alimentare" in detail and "Bancomat" in detail and "15,70" in detail, detail)
            await sug.first.click()
            check(f"{label}: descrizione completata", await pg.get_by_label("Descrizione").input_value() == "Conad")
            check(f"{label}: importo dell'ultima volta", await pg.get_by_label("Importo (€)").input_value() == "15,70")
            check(f"{label}: fonte dell'ultima volta", "Bancomat" in await sel(pg, "Con").evaluate("e => e.options[e.selectedIndex].text"))
            check(f"{label}: categoria dell'ultima volta", await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).is_checked())
            check(f"{label}: lista chiusa dopo la scelta", await sug.count() == 0)
            await pg.get_by_label("Importo (€)").fill("20")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
            a = await alive(pg)
            check(f"{label}: secondo movimento con carta e categoria", len(a) == 2 and all(x["card"][0] for x in a) and all(x["c"] == a[0]["c"] for x in a), json.dumps(a))
            # importo già scritto: il suggerimento non lo sovrascrive
            await open_new(pg)
            await pg.get_by_label("Importo (€)").fill("7")
            await pg.get_by_label("Descrizione").fill("Con")
            await pg.locator("#desc-suggestions button").first.click()
            check(f"{label}: importo già scritto non cambia", await pg.get_by_label("Importo (€)").input_value() == "7")
            # tastiera (frecce + invio) solo su PC
            if label == "PC":
                await pg.get_by_label("Descrizione").fill("Cona")
                await pg.get_by_label("Descrizione").press("ArrowDown"); await pg.get_by_label("Descrizione").press("Enter")
                check(f"{label}: scelta con frecce e Invio", await pg.locator("#desc-suggestions").count() == 0 and await pg.get_by_label("Descrizione").input_value() == "Conad")
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
            if await pg.locator("dialog[open]").count(): await pg.get_by_role("button", name=re.compile("Chiudi")).first.click()
            # niente suggerimenti per un'entrata
            await open_new(pg)
            await pg.get_by_role("radio", name="Entrata").click()
            await pg.get_by_label("Descrizione").fill("co")
            check(f"{label}: suggerimenti solo dello stesso tipo", await pg.locator("#desc-suggestions button").count() == 0)
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
            # 3) scorciatoie dell'icona
            await pg.goto(BASE + "/#/movimenti/nuova-entrata"); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: scorciatoia Nuova entrata", await pg.get_by_role("radio", name="Entrata").is_checked())
            check(f"{label}: indirizzo ripulito", pg.url.endswith("#/movimenti"), pg.url)
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti/nuova-uscita"); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: scorciatoia Nuova uscita", await pg.get_by_role("radio", name="Uscita").is_checked())
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
            # 4) ricerca per importo
            await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name=re.compile("^Filtri")).click()
            await pg.get_by_label("Importo da (€)").fill("16"); await pg.wait_for_timeout(200)
            check(f"{label}: filtro importo minimo", await pg.get_by_text("1 movimento", exact=True).count() == 1)
            await pg.get_by_label("Importo da (€)").fill(""); await pg.get_by_label("Importo a (€)").fill("15,70"); await pg.wait_for_timeout(200)
            check(f"{label}: filtro importo massimo (estremo compreso)", await pg.get_by_text("1 movimento", exact=True).count() == 1)
            await pg.get_by_label("Importo a (€)").fill("abc"); await pg.wait_for_timeout(200)
            check(f"{label}: avviso importo non valido", await pg.get_by_role("alert").filter(has_text="Importo non valido").count() == 1)
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        # manifest
        ctx = await b.new_context(); pg = await ctx.new_page()
        r = await pg.goto(BASE + "/manifest.webmanifest"); m = json.loads(await r.text())
        sc = m.get("shortcuts", [])
        check("manifest: tre scorciatoie con icona", len(sc) == 3 and all(s.get("icons") for s in sc), json.dumps(sc)[:200])
        for s in sc:
            ic = await pg.goto(BASE + "/" + s["icons"][0]["src"])
            check(f"manifest: icona {s['short_name']} raggiungibile", ic.status == 200)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
