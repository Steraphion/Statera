"""Collaudo dei profili sul dispositivo (v0.36.1), con soli dati di esempio.

Riproduce il caso segnalato con la 0.36.0: su un dispositivo non collegato a Google «Aggiungi un altro
account» apriva un profilo vuoto e nascondeva quello con i dati, che sembravano persi.
Uso: `npm run build && npx vite preview --port 4173` e poi `python3 qa/profili.py`.
"""
import asyncio, re
from playwright.async_api import async_playwright

BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

async def add_account(pg, name, saldo):
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill(name); await pg.get_by_label("Saldo iniziale (€)").fill(saldo)
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(250)

async def add_expense(pg, amount, desc, cat="Svago"):
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click()
    await pg.wait_for_selector("dialog[open]")
    await pg.get_by_label("Importo (€)").fill(amount)
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile(f"^{cat}")).click()
    await pg.get_by_label("Descrizione").fill(desc)
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(300)

async def open_profiles(pg):
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(400)
    await pg.get_by_role("button", name=re.compile("Account e profili")).click()
    await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(600)

async def databases(pg):
    return sorted(await pg.evaluate("async () => (await indexedDB.databases()).map(d => d.name)"))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in (("telefono", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})):
            ctx = await b.new_context(**opts, locale="it-IT")
            pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(f"PAGEERROR {e}"))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(500)
            await add_account(pg, "Conto di prova", "500")
            await add_expense(pg, "7", "Spesa di prova")

            # Situazione lasciata dalla 0.36.0: profilo nuovo in uso, quello iniziale fuori dall'elenco
            await pg.evaluate("""() => { localStorage.setItem('statera.profili', JSON.stringify([{db: 'statera-1ecead2b', email: '', name: ''}]));
                                         localStorage.setItem('statera.profiloAttivo', 'statera-1ecead2b') }""")
            await pg.goto(BASE + "/#/conti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
            check(f"{label}: profilo vuoto in uso (come nella 0.36.0)", await pg.get_by_text("Conto di prova").count() == 0)
            await open_profiles(pg)
            other = pg.get_by_role("button", name=re.compile("Profilo non collegato a Google"))
            txt = (await other.inner_text()) if await other.count() == 1 else ""
            check(f"{label}: il profilo nascosto con i dati ricompare nell'elenco", "1 conto" in txt and "1 movimento" in txt, txt)
            cur = await pg.locator("li.current").inner_text()
            check(f"{label}: quello in uso è segnato «In uso · Nessun dato»", "In uso" in cur and "Nessun dato" in cur, cur)
            await other.click(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1000)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
            check(f"{label}: toccandolo si ritrovano i dati", await pg.get_by_text("Conto di prova").count() >= 1)

            # Il profilo vuoto rimasto si può togliere; quello con i dati no
            await open_profiles(pg)
            check(f"{label}: «Rimuovi» solo per il profilo vuoto", await pg.get_by_role("button", name="Rimuovi").count() == 1)
            await pg.get_by_role("button", name="Rimuovi").click()
            await pg.get_by_role("button", name="Conferma: rimuovi").click(); await pg.wait_for_timeout(800)
            check(f"{label}: profilo vuoto rimosso dall'elenco", await pg.get_by_role("button", name=re.compile("tocca per passare")).count() == 0)
            check(f"{label}: e il suo database eliminato", "statera-1ecead2b" not in await databases(pg), str(await databases(pg)))

            # Nuovo profilo: prima una conferma che spiega come tornare
            await pg.get_by_role("button", name="Nuovo profilo vuoto").click()
            body = await pg.locator("dialog[open]").inner_text()
            check(f"{label}: conferma con «per tornarci» e il rimando ad «Attiva la sincronizzazione»", "per tornarci" in body and "Attiva la sincronizzazione" in body)
            await pg.get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(300)
            check(f"{label}: «Annulla» torna all'elenco senza creare nulla", await pg.get_by_role("button", name="Nuovo profilo vuoto").count() == 1 and len([d for d in await databases(pg) if d.startswith("statera-")]) == 1)
            await pg.get_by_role("button", name="Nuovo profilo vuoto").click()
            await pg.get_by_role("button", name="Crea profilo vuoto").click(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1000)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
            check(f"{label}: profilo nuovo vuoto", await pg.get_by_text("Conto di prova").count() == 0)
            await open_profiles(pg)
            back = pg.get_by_role("button", name=re.compile("1 conto"))
            check(f"{label}: dal profilo nuovo si vede quello di prima", await back.count() == 1)
            await back.click(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1000)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
            check(f"{label}: e ci si torna", await pg.get_by_text("Conto di prova").count() >= 1)

            check(f"{label}: nessun errore in console", not errs, " | ".join(errs[:3]))
            await ctx.close()
        await b.close()
    fails = [r for r in results if not r[1]]
    print(f"\nTOTALE: {len(results)-len(fails)}/{len(results)} superati")

asyncio.run(main())
