"""Collaudo v0.36: categoria nuova creata dal modulo del movimento, senza perdere l'inserimento (dati di esempio)."""
import asyncio, re
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
    await pg.wait_for_timeout(300)
async def amount(pg, pc, v):
    amt = pg.get_by_label("Importo (€)")
    if pc: await amt.fill(v); return
    await amt.click()
    for k in v: await pg.locator(".keypad").get_by_role("button", name=k, exact=True).click()
    await pg.locator(".keypad").get_by_role("button", name="Fatto").click()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1440, "height": 900}})]:
            print(f"\n===== {label} =====")
            pc = label == "PC"
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(500)
            await pg.get_by_role("button", name="Conto", exact=True).first.click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Nome", exact=True).fill("Conto principale"); await pg.get_by_label("Tipo").select_option("conto_corrente")
            await pg.get_by_label("Saldo iniziale (€)").fill("500"); await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(450)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)

            # 1) uscita: categoria nuova a metà inserimento
            await open_new(pg)
            await amount(pg, pc, "12")
            await pg.get_by_label("Descrizione").fill("Visita")
            await pg.get_by_role("button", name="+ Nuova categoria").click(); await pg.wait_for_timeout(500)
            dl = pg.locator("dialog[open]"); top = dl.last
            check(f"{label}: la scheda si apre sopra il movimento", await dl.count() == 2 and await top.get_by_role("heading", name="Nuova categoria").count() == 1)
            check(f"{label}: niente rinnovo dell'accesso Google nella scheda", await pg.locator("dialog[open][data-no-autoauth]").count() == 2)
            r_u = top.get_by_role("radio", name="Uscita")
            check(f"{label}: tipo fissato come il movimento", await r_u.is_checked() and await r_u.is_disabled() and await top.get_by_text(re.compile("^Come il movimento")).count() == 1)
            await top.get_by_label("Nome").fill("Veterinario")
            txt = await top.inner_text()
            check(f"{label}: icona proposta dal nome", "Zampa" in txt and "in base al nome" in txt)
            if pc: await top.get_by_label("Nome").press("Enter")
            else: await top.get_by_role("button", name="Salva").click()
            await pg.wait_for_timeout(600)
            check(f"{label}: {'Invio salva la categoria, non il movimento' if pc else 'salvata, resta aperto il movimento'}", await dl.count() == 1)
            mv_open = await pg.get_by_label("Descrizione").input_value() == "Visita" and "12" in await pg.get_by_label("Importo (€)").input_value()
            check(f"{label}: importo e descrizione restano", mv_open)
            check(f"{label}: la categoria nuova è già scelta", await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Veterinario")).is_checked())
            check(f"{label}: e compare nell'intestazione", "Veterinario" in await pg.locator("dialog[open] legend", has_text="Categoria").inner_text())
            await pg.locator("dialog[open]").get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(600)
            cats = {c["name"]: c for c in await store(pg, "categories")}
            txs = await store(pg, "transactions")
            check(f"{label}: movimento salvato con la categoria nuova", any(t["description"] == "Visita" and t["categoryId"] == cats.get("Veterinario", {}).get("id") for t in txs))
            check(f"{label}: icona automatica non scritta nei dati", "icon" not in cats.get("Veterinario", {"icon": 1}))

            # 2) doppione: errore nella scheda, Esc chiude solo la scheda
            await open_new(pg)
            await pg.get_by_role("button", name="+ Nuova categoria").click(); await pg.wait_for_timeout(500)
            top = pg.locator("dialog[open]").last
            await top.get_by_label("Nome").fill(" veterinario ")
            await top.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
            err = await top.locator(".sheet-error").all_inner_texts()
            check(f"{label}: doppione fermato con un messaggio chiaro", any("esiste già tra le uscite" in e for e in err), str(err))
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
            check(f"{label}: Esc chiude solo la scheda della categoria", await pg.locator("dialog[open]").count() == 1)

            # 3) entrata, icona scelta a mano
            await pg.locator("dialog[open]").get_by_role("radio", name="Entrata").click(); await pg.wait_for_timeout(200)
            await pg.get_by_role("button", name="+ Nuova categoria").click(); await pg.wait_for_timeout(500)
            top = pg.locator("dialog[open]").last
            check(f"{label}: per un'entrata il tipo è Entrata", await top.get_by_role("radio", name="Entrata").is_checked())
            await top.get_by_label("Nome").fill("Vendite usato")
            await top.get_by_role("button", name=re.compile("^(Cambia|Scegli)$")).click()
            await top.get_by_role("radio", name="Monete", exact=True).click()
            await top.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(600)
            check(f"{label}: entrata nuova scelta nel movimento", await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Vendite usato")).is_checked())
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(600)
            cats = {c["name"]: c for c in await store(pg, "categories")}
            v = cats.get("Vendite usato", {})
            check(f"{label}: resta anche chiudendo il movimento senza salvarlo", v.get("kind") == "entrata" and v.get("icon") == "monete" and v.get("parentId") is None, str(v))

            # 4) nell'elenco di riferimento
            await pg.goto(BASE + "/#/categorie"); await pg.wait_for_timeout(500)
            out = await pg.locator(".list").first.inner_text()
            await pg.get_by_role("radio", name="Entrate").click(); await pg.wait_for_timeout(300)
            inc = await pg.locator(".list").first.inner_text()
            check(f"{label}: in Altro → Categorie, ognuna al suo posto", "Veterinario" in out and "Vendite usato" not in out and "Vendite usato" in inc)
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
