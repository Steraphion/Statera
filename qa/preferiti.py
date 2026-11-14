"""Collaudo Fase 4.2: movimenti preferiti (dati di esempio)."""
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
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            check(f"{label}: senza preferiti la barra non c'è", await pg.locator("section.fav").count() == 0)
            # preferito con importo
            await open_new(pg)
            await pg.get_by_label("Importo (€)").fill("1,20")
            await pg.get_by_label("Descrizione").fill("Caffè")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Pasti fuori")).click()
            await pg.get_by_label("Salva anche tra i preferiti").check()
            check(f"{label}: nome proposto dalla descrizione", await pg.get_by_label("Nome del preferito").get_attribute("placeholder") == "Caffè")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            check(f"{label}: movimento e preferito salvati", len(await store(pg, "transactions")) == 1 and len(await store(pg, "templates")) == 1)
            # preferito senza importo
            await open_new(pg)
            await pg.get_by_label("Importo (€)").fill("30")
            await pg.get_by_label("Descrizione").fill("Supermercato")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
            await pg.get_by_label("Salva anche tra i preferiti").check()
            await pg.get_by_label("Nome del preferito").fill("Spesa")
            await pg.get_by_label("Ricorda anche l'importo").uncheck()
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            chips = pg.locator("section.fav .chip:not(.manage)")
            names = await chips.locator(".name").all_text_contents()
            check(f"{label}: due preferiti nella barra", names == ["Caffè", "Spesa"], str(names))
            check(f"{label}: importo sul pulsante", "1,20" in await chips.nth(0).inner_text() and "scrivi l'importo" in await chips.nth(1).inner_text())
            # un tocco registra
            await chips.nth(0).click(); await pg.wait_for_timeout(500)
            t = await store(pg, "transactions")
            check(f"{label}: un tocco registra il movimento", len(t) == 3 and sum(1 for x in t if x["description"] == "Caffè") == 2)
            toast = pg.locator(".toast[role=status]")
            check(f"{label}: avviso con Annulla", "Caffè registrato" in await toast.inner_text() and await toast.get_by_role("button", name="Annulla").count() == 1)
            await toast.get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(500)
            check(f"{label}: Annulla elimina il movimento", len(await store(pg, "transactions")) == 2)
            # preferito senza importo: apre il modulo compilato
            await chips.nth(1).click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: modulo dal preferito: descrizione e categoria", await pg.get_by_label("Descrizione").input_value() == "Supermercato" and await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).is_checked())
            check(f"{label}: importo da scrivere", await pg.get_by_label("Importo (€)").input_value() == "")
            check(f"{label}: niente doppio preferito dal preferito", await pg.get_by_label("Salva anche tra i preferiti").count() == 0)
            await pg.get_by_label("Importo (€)").fill("42,10")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            t = await store(pg, "transactions")
            check(f"{label}: registrato con l'importo scritto", any(x["parts"][0]["amount"] == 4210 for x in t))
            # gestione
            await pg.locator("section.fav .manage").click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Nome del preferito 1").fill("Caffè al bar"); await pg.get_by_label("Nome del preferito 1").press("Tab"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Sposta Spesa prima").click(); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Elimina Spesa", exact=True).click()
            await pg.get_by_role("button", name="Conferma: elimina Spesa").click(); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Fatto").click(); await pg.wait_for_timeout(300)
            tps = await store(pg, "templates")
            check(f"{label}: rinominato ed eliminato", [x["name"] for x in tps] == ["Caffè al bar"], json.dumps([x["name"] for x in tps]))
            await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
            check(f"{label}: preferiti dopo il riavvio", await pg.locator("section.fav .chip:not(.manage) .name").all_text_contents() == ["Caffè al bar"])
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
