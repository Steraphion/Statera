"""Collaudo Fase 4.3: guida al primo avvio, Allinea saldo, budget al giorno (dati di esempio)."""
import asyncio, re, json, datetime, calendar
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
async def store(pg, name):
    return await pg.evaluate("""(name) => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction(name).objectStore(name).getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null)) } } })""", name)
async def main():
    t = datetime.date.today(); days_left = calendar.monthrange(t.year, t.month)[1] - t.day + 1
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT", accept_downloads=True); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(600)
            guide = pg.locator("section.guide")
            check(f"{label}: guida al primo avvio", await guide.count() == 1 and "0 di 3" in await guide.inner_text())
            check(f"{label}: senza conti non si può nascondere", await pg.get_by_role("button", name="Nascondi la guida").count() == 0)
            await guide.get_by_role("link", name="Vai ai conti").click(); await pg.wait_for_timeout(300)
            check(f"{label}: porta ai conti", pg.url.endswith("#/conti"))
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Tipo").select_option("conto_corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.locator("dialog input[type=date]").fill(t.replace(day=1).isoformat())
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
            check(f"{label}: passo 1 fatto", "1 di 3" in await guide.inner_text() and "Crea i tuoi conti — fatto" in await guide.inner_text())
            await guide.get_by_role("button", name="Nuovo movimento").click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Importo (€)").fill("120")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            check(f"{label}: passo 2 fatto", "2 di 3" in await guide.inner_text())
            # passo 3 con un backup esportato
            await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Esporta backup").click()
            await pg.get_by_label(re.compile("Proteggi il file")).uncheck()
            async with pg.expect_download():
                await pg.get_by_role("button", name="Scarica il backup").click()
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
            check(f"{label}: completata, la guida sparisce", await guide.count() == 0)
            # budget al giorno
            await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Imposta budget").click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Budget Spesa alimentare (€)").fill("400")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
            per = 28000 // days_left
            txt = await pg.locator(".per-day").first.inner_text() if await pg.locator(".per-day").count() else ""
            exp = f"{per // 100},{per % 100:02d}"
            check(f"{label}: quanto resta al giorno", exp in txt and (str(days_left) in txt or "ultimo giorno" in txt), f"{txt} / atteso {exp}")
            await pg.get_by_role("button", name="Periodo precedente").click(); await pg.wait_for_timeout(300)
            check(f"{label}: mese passato senza importo al giorno", await pg.locator(".per-day").count() == 0)
            # allinea saldo
            accs = await store(pg, "accounts")
            await pg.goto(BASE + f"/#/conto/{accs[0]['id']}"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Allinea al saldo reale").click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: saldo attuale mostrato", "880,00" in await pg.locator(".now").inner_text())
            await pg.get_by_label("Saldo reale (€)").fill("867,45")
            check(f"{label}: anteprima della differenza", "12,55" in await pg.get_by_role("status").filter(has_text="Differenza").inner_text())
            await pg.get_by_role("button", name="Allinea", exact=True).click(); await pg.wait_for_timeout(500)
            check(f"{label}: saldo allineato", "867,45" in await pg.locator(".summary .value").inner_text())
            tx = await store(pg, "transactions")
            adj = [x for x in tx if x["description"] == "Allineamento saldo"]
            check(f"{label}: movimento di rettifica", len(adj) == 1 and adj[0]["type"] == "uscita" and adj[0]["parts"][0]["amount"] == 1255)
            await pg.get_by_role("button", name="Allinea al saldo reale").click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_label("Saldo reale (€)").fill("867,45")
            check(f"{label}: già giusto", await pg.get_by_text("Il saldo è già giusto").count() == 1)
            await pg.get_by_role("button", name="Allinea", exact=True).click(); await pg.wait_for_timeout(400)
            check(f"{label}: nessuna rettifica in più", len([x for x in await store(pg, "transactions") if x["description"] == "Allineamento saldo"]) == 1)
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
