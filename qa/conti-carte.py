"""Collaudo v0.35: conti divisi per tipo, carte di debito sotto il loro conto, carte prepagate a parte (dati di esempio)."""
import asyncio, re, json
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))
def sel(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(label)}$"))).locator("select")
async def store(pg, name):
    return await pg.evaluate("""(name) => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction(name).objectStore(name).getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null)) } } })""", name)
async def new_account(pg, name, typ, saldo, card=None):
    await pg.get_by_role("button", name="Conto", exact=True).first.click(); await pg.wait_for_selector("dialog[open]")
    await pg.get_by_label("Nome", exact=True).fill(name)
    await pg.get_by_label("Tipo").select_option(typ)
    await pg.get_by_label("Saldo iniziale (€)").fill(saldo)
    has_card_field = await pg.get_by_label("Carta collegata (facoltativa)").count() == 1
    if card: await pg.get_by_label("Carta collegata (facoltativa)").fill(card)
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(450)
    return has_card_field
async def open_account(pg, name):
    await pg.locator("#conti-list a.list-row", has_text=name).first.click(); await pg.wait_for_timeout(450)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts in [("Android", {**p.devices["Pixel 7"]}), ("PC", {"viewport": {"width": 1440, "height": 900}})]:
            print(f"\n===== {label} =====")
            pc = label == "PC"
            ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(500)
            f1 = await new_account(pg, "Conto principale", "conto_corrente", "1500", card="Carta del conto")
            f2 = await new_account(pg, "Prepagata viaggi", "carta_prepagata", "200")
            await new_account(pg, "Ricaricabile", "carta_prepagata", "35")
            await new_account(pg, "Contanti", "contanti", "50")
            check(f"{label}: campo carta collegata per il conto corrente, non per la prepagata", f1 and not f2)
            heads = [re.sub(r"\s+", " ", t).strip() for t in await pg.locator("#conti-list h2.group-title").all_inner_texts()]
            check(f"{label}: gruppi in ordine con il totale", len(heads) == 3 and heads[0].lower().startswith("conti correnti") and "1.500,00" in heads[0] and heads[1].lower().startswith("carte prepagate") and "235,00" in heads[1] and heads[2].lower().startswith("contanti") and "50,00" in heads[2], str(heads))
            check(f"{label}: patrimonio di tutti i gruppi", "1.785,00" in await pg.locator(".total .bb-amount").inner_text())
            check(f"{label}: nessuna sezione Carte di debito", await pg.get_by_text("Carte di debito").count() == 0)
            first = await pg.locator("#conti-list .list").first.inner_text()
            check(f"{label}: la carta sta sotto il suo conto", first.index("Conto principale") < first.index("Carta del conto") and "Carta collegata" in first, first.replace("\n", " | "))
            # dettaglio: carte del conto e aggiunta
            await open_account(pg, "Conto principale")
            check(f"{label}: carta nel dettaglio del conto", await pg.get_by_role("button", name="Carta Carta del conto: modifica").count() == 1)
            await pg.get_by_role("button", name="Carta", exact=True).click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: carta nuova già sul conto giusto", "Conto principale" in await sel(pg, "Conto collegato").evaluate("e => e.options[e.selectedIndex].text"))
            await pg.get_by_label("Nome").fill("Carta di riserva"); await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(450)
            if not pc:
                await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(450)
            first = await pg.locator("#conti-list .list").first.inner_text()
            check(f"{label}: seconda carta sotto il conto", "Carta di riserva" in first)
            await open_account(pg, "Prepagata viaggi")
            check(f"{label}: una prepagata non propone carte collegate", await pg.get_by_role("button", name=re.compile("Aggiungi una carta|^Carta$")).count() == 0)
            if not pc:
                await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(450)
            # carta dall'elenco: si apre e si archivia
            await pg.locator("#conti-list li.nested button", has_text="Carta di riserva").click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: tocco sulla carta apre la sua scheda", await pg.get_by_role("heading", name="Modifica carta").count() == 1)
            await pg.get_by_role("button", name="Archivia").click(); await pg.wait_for_timeout(450)
            check(f"{label}: carta archiviata segnata", "archiviata" in await pg.locator("#conti-list li.nested", has_text="Carta di riserva").inner_text())
            # movimento: la carta come modo di pagare il conto, la prepagata come conto
            await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)
            await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
            opts_ = await sel(pg, "Con").evaluate("e => [...e.options].map(o => o.text)")
            check(f"{label}: nel campo Con la carta col suo conto e le prepagate", "Carta del conto (Conto principale)" in opts_ and "Prepagata viaggi" in opts_ and "Conto principale" not in opts_ and not any("Carta di riserva" in o for o in opts_), str(opts_))
            amt = pg.get_by_label("Importo (€)")
            if pc: await amt.fill("20")
            else:
                await amt.click()
                for k in ["2", "0"]: await pg.locator(".keypad").get_by_role("button", name=k, exact=True).click()
                await pg.locator(".keypad").get_by_role("button", name="Fatto").click()
            await sel(pg, "Con").select_option(label="Prepagata viaggi")
            await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Viaggi")).click()
            await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
            # entrata: solo conti, la carta torna al suo conto
            await pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$")).first.click(); await pg.wait_for_selector("dialog[open]")
            await sel(pg, "Con").select_option(label="Carta del conto (Conto principale)")
            await pg.locator("dialog[open]").get_by_role("radio", name="Entrata").click(); await pg.wait_for_timeout(200)
            su = await sel(pg, "Su").evaluate("e => [...e.options].map(o => o.text)")
            check(f"{label}: nel campo Su solo conti", "Conto principale" in su and "Prepagata viaggi" in su and not any("Carta" in o for o in su), str(su))
            await pg.locator("dialog[open]").get_by_role("radio", name="Uscita").click(); await pg.wait_for_timeout(200)
            back = await sel(pg, "Con").evaluate("e => e.options[e.selectedIndex].text")
            check(f"{label}: tornando a Uscita si riprende l'ultima fonte", back == "Prepagata viaggi", back)
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
            await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(450)
            heads = [re.sub(r"\s+", " ", t).strip() for t in await pg.locator("#conti-list h2.group-title").all_inner_texts()]
            check(f"{label}: spesa con la prepagata scala dal suo gruppo", "215,00" in heads[1], str(heads))
            # ordina dentro il gruppo
            await pg.get_by_role("button", name="Ordina").click()
            await pg.get_by_role("button", name="Sposta su Ricaricabile").click(); await pg.wait_for_timeout(300)
            check(f"{label}: il primo di un gruppo non sale oltre", await pg.get_by_role("button", name="Sposta su Conto principale").is_disabled())
            await pg.get_by_role("button", name="Fatto").click(); await pg.wait_for_timeout(300)
            second = await pg.locator("#conti-list .list").nth(1).inner_text()
            check(f"{label}: ordine cambiato solo nelle prepagate", second.index("Ricaricabile") < second.index("Prepagata viaggi"))
            # un conto «Altro» usato come prepagata passa al tipo giusto e tiene la sua carta
            await new_account(pg, "Vecchia prepagata", "altro", "80", card="Carta vecchia")
            heads = [re.sub(r"\s+", " ", t).strip().lower() for t in await pg.locator("#conti-list h2.group-title").all_inner_texts()]
            check(f"{label}: gruppo Altri conti", any(h.startswith("altri conti") and "80,00" in h for h in heads), str(heads))
            await open_account(pg, "Vecchia prepagata")
            await pg.get_by_role("button", name="Modifica", exact=True).click(); await pg.wait_for_selector("dialog[open]")
            check(f"{label}: nessun campo carta modificando un conto", await pg.get_by_label("Carta collegata (facoltativa)").count() == 0)
            await pg.get_by_label("Tipo").select_option("carta_prepagata")
            await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(450)
            if not pc:
                await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(450)
            heads = [re.sub(r"\s+", " ", t).strip().lower() for t in await pg.locator("#conti-list h2.group-title").all_inner_texts()]
            check(f"{label}: passato tra le carte prepagate col suo saldo", not any(h.startswith("altri conti") for h in heads) and "295,00" in heads[1], str(heads))
            second = await pg.locator("#conti-list .list").nth(1).inner_text()
            check(f"{label}: la carta che aveva resta sotto", "Carta vecchia" in second)
            await pg.locator("#conti-list li.nested button", has_text="Carta vecchia").click(); await pg.wait_for_selector("dialog[open]")
            chosen = await sel(pg, "Conto collegato").evaluate("e => e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''")
            check(f"{label}: la sua scheda mostra il conto giusto", chosen == "Vecchia prepagata", chosen)
            await pg.get_by_label("Nome").fill("Carta vecchia rinominata"); await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(450)
            check(f"{label}: e si può rinominare", "Carta vecchia rinominata" in await pg.locator("#conti-list .list").nth(1).inner_text() and await pg.locator("dialog[open]").count() == 0)
            cards_, prepaid = await store(pg, "cards"), [a["id"] for a in await store(pg, "accounts") if a["type"] == "carta_prepagata"]
            check(f"{label}: sempre collegata alla prepagata", any(c["name"] == "Carta vecchia rinominata" and c["accountId"] in prepaid for c in cards_))
            check(f"{label}: nessun errore in console", not errs, "; ".join(errs[:3]))
            await ctx.close()
        await b.close()
    print(f"\n{sum(results)}/{len(results)} controlli superati")
asyncio.run(main())
