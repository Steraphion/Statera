"""Collaudo movimenti ricorrenti (dati di esempio)."""
import asyncio, re, datetime
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
def sel(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(label)}$"))).locator("select")
def months_ago(n, day):
    t = datetime.date.today(); m = t.month - n; y = t.year
    while m <= 0: m += 12; y -= 1
    return f"{y}-{m:02d}-{day:02d}"
async def alive(pg):
    return await pg.evaluate("""() => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction('transactions').objectStore('transactions').getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null).map(t => [t.date, t.description, t.parts[0].amount]).sort()) } } })""")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1366, "height": 800}})]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name="Conto").first.click()
            await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Saldo iniziale (€)").fill("1000")
            await pg.locator("dialog input[type=date]").fill(months_ago(6, 1))
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(300)
            # stipendio automatico, iniziato 2 mesi fa
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_role("radio", name="Entrata").click()
            await pg.get_by_label("Importo (€)").fill("1500")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Stipendio")).click()
            await pg.get_by_label("Descrizione").fill("Stipendio")
            await pg.locator("dialog input[type=date]").first.fill(months_ago(2, 1))
            await sel(pg, "Ripeti").select_option("mensile")
            check(f"{label}: descrizione frequenza", await pg.get_by_text("Ogni mese, il giorno 1").count() == 1)
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            a = await alive(pg)
            check(f"{label}: creata la prima occorrenza", [x[0] for x in a] == [months_ago(2, 1)], str(a))
            await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1500)
            a = await alive(pg)
            check(f"{label}: all'avvio recupera le occorrenze scadute", [x[0] for x in a] == [months_ago(2, 1), months_ago(1, 1), months_ago(0, 1)], str(a))
            await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(1200)
            check(f"{label}: nessun doppione riavviando", len(await alive(pg)) == 3)
            # bolletta da confermare
            await pg.goto(BASE + "/#/ricorrenti"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name="Ripetizione").click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: da Ricorrenti la ripetizione è già impostata", await sel(pg, "Ripeti").input_value() == "mensile")
            await pg.get_by_label("Importo (€)").fill("60")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Bollette")).click()
            await pg.get_by_label("Descrizione").fill("Luce")
            await pg.locator("dialog input[type=date]").first.fill(months_ago(1, 2))
            await pg.get_by_role("radio", name="Da confermare").click()
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            items = await pg.locator(".list .name").all_text_contents()
            check(f"{label}: elenco ricorrenti", sorted(items) == ["Luce", "Stipendio"], str(items))
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(600)
            n_pend = await pg.get_by_role("button", name="Registra").count()
            check(f"{label}: 'Da registrare' mostra la bolletta di questo mese", n_pend == 1, str(n_pend))
            await pg.get_by_role("button", name="Registra").first.click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: conferma precompilata", await pg.get_by_label("Importo (€)").input_value() == "60,00")
            await pg.get_by_label("Importo (€)").fill("73,50")
            await pg.locator("dialog").get_by_role("button", name="Registra").click(); await pg.wait_for_timeout(500)
            a = await alive(pg)
            check(f"{label}: bolletta registrata con l'importo corretto", [months_ago(0, 2), "Luce", 7350] in a, str(a))
            check(f"{label}: avviso sparito", await pg.get_by_role("button", name="Registra").count() == 0)
            check(f"{label}: movimenti generati segnati come ricorrenti", await pg.get_by_text("↻ ricorrente").count() >= 2)
            # modifica e sospensione
            await pg.goto(BASE + "/#/ricorrenti"); await pg.wait_for_timeout(300)
            await pg.get_by_role("button", name=re.compile("^Stipendio")).click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: modifica mostra la prossima data", await pg.get_by_text("Prossima data", exact=True).count() == 1)
            await pg.get_by_label("Importo (€)").fill("1600")
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(400)
            check(f"{label}: importo aggiornato nell'elenco", "1.600,00" in await pg.locator(".list").inner_text())
            check(f"{label}: movimenti passati invariati", all(x[2] == 150000 for x in await alive(pg) if x[1] == "Stipendio"))
            await pg.get_by_role("button", name=re.compile("^Luce")).click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_role("button", name="Sospendi").click(); await pg.wait_for_timeout(400)
            check(f"{label}: ripetizione sospesa", "Sospesa" in await pg.locator(".list").inner_text())
            await pg.get_by_role("button", name=re.compile("^Luce")).click(); await pg.wait_for_selector("dialog[open]")
            await pg.get_by_role("button", name="Elimina ripetizione").click(); await pg.get_by_role("button", name="Conferma eliminazione").click(); await pg.wait_for_timeout(400)
            check(f"{label}: ripetizione eliminata, movimento registrato resta", "Luce" not in await pg.locator("main").inner_text() and any(x[1] == "Luce" for x in await alive(pg)))
            check(f"{label}: nessun errore in console", not errs, " | ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\nTOTALE: {sum(results)}/{len(results)} superati")
asyncio.run(main())
