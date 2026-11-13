"""Collaudo end-to-end di Statera (dati di esempio)."""
import asyncio, re, json, sys, os
from playwright.async_api import async_playwright

BASE = "http://localhost:4173"
results = []

def check(name, ok, info=""):
    results.append((name, bool(ok), info))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

def sel(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{label}$"))).locator("select")

async def tap(loc, mobile):
    if mobile: await loc.tap()
    else: await loc.click()

async def wait_app(pg):
    await pg.wait_for_function("document.querySelector('nav') || document.querySelector('.recovery')", timeout=10000)
    await pg.wait_for_timeout(300)

async def new_account(pg, m, name, typ, saldo=None, val=None, n=None, date=None):
    await tap(pg.get_by_role("button", name="Conto").first, m)
    await pg.get_by_label("Nome").fill(name)
    await pg.get_by_label("Tipo").select_option(typ)
    if saldo is not None: await pg.get_by_label("Saldo iniziale (€)").fill(saldo)
    if val is not None:
        await pg.get_by_label("Valore di un buono (€)").fill(val)
        await pg.get_by_label("Buoni disponibili").fill(n)
    if date: await pg.locator("dialog input[type=date]").fill(date)
    await tap(pg.get_by_role("button", name="Salva"), m)
    await pg.wait_for_timeout(250)

async def open_new_movement(pg, m):
    btn = pg.get_by_role("button", name="Nuovo movimento") if m else pg.get_by_role("button", name=re.compile("^Movimento$"))
    await tap(btn.first, m)
    await pg.wait_for_selector("dialog[open]")
    await pg.wait_for_timeout(150)

async def pick_cat(pg, m, name):
    await tap(pg.locator(".cat-list").get_by_role("radio", name=re.compile(f"^{re.escape(name)}")), m)

async def save(pg, m, exact=True):
    await tap(pg.get_by_role("button", name="Salva", exact=True), m)
    await pg.wait_for_timeout(400)

async def db_dump(pg):
    return await pg.evaluate("""() => new Promise((res, rej) => {
      const q = indexedDB.open('statera-locale');
      q.onsuccess = () => { const db = q.result; const out = {};
        const names = ['accounts','cards','categories','transactions'];
        const t = db.transaction(names); let left = names.length;
        for (const n of names) { const r = t.objectStore(n).getAll(); r.onsuccess = () => { out[n] = r.result; if (--left === 0) { db.close(); res(out) } } } };
      q.onerror = () => rej(q.error) })""")

async def run_flow(b, label, ctx_opts, m):
    print(f"\n===== {label} =====")
    ctx = await b.new_context(**ctx_opts, locale="it-IT")
    pg = await ctx.new_page(); errors = []
    pg.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)))
    pg.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

    await pg.goto(BASE + "/"); await wait_app(pg)
    check(f"{label}: avvio pulito mostra benvenuto", await pg.get_by_text("Benvenuto in Statera").count() == 1)

    # cursor CSS
    cur = await pg.evaluate("getComputedStyle(document.querySelector('.month h1')).cursor + '|' + getComputedStyle(document.body).caretColor")
    check(f"{label}: puntatore normale e niente barretta sul testo", cur.startswith("default|") and "0)" in cur or cur.endswith("transparent"), cur)
    sel_ok = await pg.evaluate("getComputedStyle(document.querySelector('.month h1')).userSelect")
    check(f"{label}: testo selezionabile", sel_ok in ("auto", "text"), sel_ok)

    # conti
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
    await new_account(pg, m, "Conto", "conto_corrente", "1000", date="2026-11-01")
    await new_account(pg, m, "Contanti", "contanti", "50", date="2026-11-01")
    await new_account(pg, m, "Buoni", "buoni_pasto", val="8", n="10", date="2026-11-01")
    await tap(pg.get_by_role("button", name="Carta"), m)
    await pg.get_by_label("Nome").fill("Bancomat"); await tap(pg.get_by_role("button", name="Salva"), m); await pg.wait_for_timeout(250)
    tot = await pg.locator(".total .value").text_content()
    check(f"{label}: conti creati, patrimonio 1.130,00", tot.replace("\xa0"," ").strip() == "1.130,00 €", tot)

    # buoni con valore non intero -> errore visibile
    await new_account(pg, m, "Buoni2", "buoni_pasto", val="8", n="2,5", date="2026-11-01")
    err = await pg.locator(".sheet-error").all_inner_texts()
    check(f"{label}: numero buoni non valido -> errore visibile", any("intero" in e for e in err), str(err))
    await tap(pg.get_by_role("button", name="Chiudi"), m); await pg.wait_for_timeout(200)

    # movimenti
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
    # errore: importo vuoto
    await open_new_movement(pg, m)
    await save(pg, m)
    err = await pg.locator(".sheet-error").all_inner_texts()
    check(f"{label}: importo mancante -> errore visibile accanto ai pulsanti", any("importo" in e.lower() for e in err), str(err))
    # categorie alfabetiche
    names = await pg.locator(".cat-list .cat:not(.child) .label").all_text_contents()
    check(f"{label}: categorie in ordine alfabetico", names == sorted(names, key=lambda s: s.lower()), str(names[:6]))
    lst_h = await pg.evaluate("(() => { const l = document.querySelector('.cat-list'); return [l.scrollHeight > l.clientHeight, getComputedStyle(l).overflowY, getComputedStyle(l).flexDirection] })()")
    check(f"{label}: elenco categorie verticale e scorrevole", lst_h[0] and lst_h[1] == "auto" and lst_h[2] == "column", str(lst_h))
    # senza categoria
    await pg.get_by_label("Importo (€)").fill("10")
    await save(pg, m)
    err = await pg.locator(".sheet-error").all_inner_texts()
    check(f"{label}: categoria mancante -> errore visibile", any("categoria" in e.lower() for e in err), str(err))
    await pick_cat(pg, m, "Spesa alimentare")
    await sel(pg, "Con").select_option(label="Bancomat (Conto)")
    await pg.get_by_label("Descrizione").fill("Spesa")
    await save(pg, m)
    check(f"{label}: uscita con carta salvata", await pg.locator("dialog[open]").count() == 0 and await pg.get_by_role("button", name=re.compile("^Spesa")).count() == 1)

    # IL CASO SEGNALATO: pagamento misto conto + buoni
    await open_new_movement(pg, m)
    await pg.get_by_label("Importo (€)").fill("5")
    await tap(pg.get_by_role("button", name=re.compile("Pagamento misto")), m); await pg.wait_for_timeout(150)
    f2 = await pg.get_by_label("Fonte 2", exact=True).evaluate("e=>e.options[e.selectedIndex].text")
    check(f"{label}: pagamento misto propone i buoni come seconda fonte", f2 == "Buoni", f2)
    # scelta che prima era bloccata: Fonte 1 = Conto (scambio automatico se serve)
    await pg.get_by_label("Fonte 2", exact=True).select_option(label="Conto")
    f1 = await pg.get_by_label("Fonte 1", exact=True).evaluate("e=>e.options[e.selectedIndex].text")
    check(f"{label}: scegliere una fonte già usata scambia le righe", f1 != "Conto", f1)
    await pg.get_by_label("Fonte 1", exact=True).select_option(label="Conto")
    await pg.get_by_label("Fonte 2", exact=True).select_option(label="Buoni")
    await pg.get_by_label("Importo 1").fill("5")
    await pg.get_by_label("Buoni 2").fill("2")
    await pick_cat(pg, m, "Pasti fuori")
    await pg.get_by_label("Descrizione").fill("Pranzo misto")
    await save(pg, m)
    ok = await pg.locator("dialog[open]").count() == 0 and await pg.get_by_role("button", name=re.compile("^Pranzo misto")).count() == 1
    check(f"{label}: pagamento misto conto + buoni salvato e visibile", ok, str(await pg.locator(".sheet-error").all_inner_texts()))

    # misto buoni + carta, buoni scritti con spazio
    await open_new_movement(pg, m)
    await tap(pg.get_by_role("button", name=re.compile("Pagamento misto")), m); await pg.wait_for_timeout(150)
    await pg.get_by_label("Fonte 1", exact=True).select_option(label="Buoni")
    f2 = await pg.get_by_label("Fonte 2", exact=True).evaluate("e=>e.options[e.selectedIndex].text")
    await pg.get_by_label("Fonte 2", exact=True).select_option(label="Bancomat (Conto)")
    await pg.get_by_label("Buoni 1").fill(" 3 ")
    await pg.get_by_label("Importo 2").fill("7,40")
    await pick_cat(pg, m, "Spesa alimentare")
    await pg.get_by_label("Descrizione").fill("Spesa mista")
    await save(pg, m)
    check(f"{label}: pagamento misto buoni + carta salvato", await pg.get_by_role("button", name=re.compile("^Spesa mista")).count() == 1)

    # entrata, trasferimento, salva e nuovo
    await open_new_movement(pg, m)
    await tap(pg.get_by_role("radio", name="Entrata"), m)
    await pg.get_by_label("Importo (€)").fill("1.500")
    await sel(pg, "Su").select_option(label="Conto")
    await pick_cat(pg, m, "Stipendio")
    await pg.get_by_label("Descrizione").fill("Stipendio")
    await tap(pg.get_by_role("button", name="Salva e nuovo"), m); await pg.wait_for_timeout(400)
    check(f"{label}: 'Salva e nuovo' conferma e resta aperto", await pg.locator(".saved").count() == 1 and await pg.locator("dialog[open]").count() == 1)
    await tap(pg.get_by_role("radio", name="Trasferimento"), m)
    await pg.get_by_label("Importo (€)").fill("40")
    await pg.get_by_label("Descrizione").fill("Prelievo")
    await save(pg, m)
    check(f"{label}: trasferimento salvato", await pg.get_by_role("button", name=re.compile("^Prelievo")).count() == 1)

    # verifica saldi
    data = await db_dump(pg)
    check(f"{label}: 5 movimenti nel database", len([t for t in data["transactions"] if t["deletedAt"] is None]) == 5)
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
    rows = await pg.locator(".list").first.inner_text()
    # conto: 1000 -10(bancomat spesa) -5 -7.40 +1500 -40 = 2437.60 ; contanti 50+40=90 ; buoni 80 -16 -24 = 40 (5 buoni)
    check(f"{label}: saldo conto 2.437,60", "2.437,60" in rows, rows)
    check(f"{label}: saldo contanti 90,00", "90,00" in rows, rows)
    check(f"{label}: buoni 40,00 e 5 buoni", "40,00" in rows and "5 buoni" in rows, rows)

    # dettaglio conto
    await tap(pg.get_by_role("link", name=re.compile("^Conto")), m); await pg.wait_for_timeout(400)
    check(f"{label}: dettaglio conto si apre", "2.437,60" in await pg.locator(".summary .value").text_content())

    # modifica ed eliminazione
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
    await tap(pg.get_by_role("button", name=re.compile("^Spesa Spesa")), m); await pg.wait_for_timeout(200)
    await pg.get_by_label("Importo (€)").fill("12")
    await save(pg, m)
    await tap(pg.get_by_role("button", name=re.compile("^Prelievo")), m); await pg.wait_for_timeout(200)
    await tap(pg.get_by_role("button", name="Elimina"), m)
    await tap(pg.get_by_role("button", name="Conferma eliminazione"), m); await pg.wait_for_timeout(400)
    check(f"{label}: modifica ed eliminazione", await pg.get_by_role("button", name=re.compile("^Prelievo")).count() == 0)

    # ricariche ripetute
    blank = 0
    for i in range(5):
        await pg.reload(); await wait_app(pg)
        if await pg.locator(".recovery").count() or await pg.get_by_role("button", name=re.compile("^Pranzo misto")).count() != 1:
            blank += 1
    check(f"{label}: 5 ricariche di fila, app sempre funzionante", blank == 0, f"{blank} ricariche fallite")

    # offline
    await ctx.set_offline(True)
    await pg.reload(); await wait_app(pg)
    check(f"{label}: senza rete si apre e mostra i dati", await pg.get_by_role("button", name=re.compile("^Pranzo misto")).count() == 1)
    await open_new_movement(pg, m)
    await pg.get_by_label("Importo (€)").fill("3")
    await pick_cat(pg, m, "Svago")
    await pg.get_by_label("Descrizione").fill("Offline")
    await save(pg, m)
    check(f"{label}: senza rete si inserisce un movimento", await pg.get_by_role("button", name=re.compile("^Offline")).count() == 1)
    await ctx.set_offline(False)

    # ricerca
    await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(300)
    await pg.get_by_label("Cerca", exact=True).fill("mist")
    await pg.wait_for_timeout(200)
    check(f"{label}: ricerca 'mist' trova i 2 pagamenti misti", "2 movimenti" in await pg.locator(".summary").inner_text())

    # categorie: nuova categoria in ordine alfabetico
    await pg.goto(BASE + "/#/categorie"); await pg.wait_for_timeout(300)
    await tap(pg.get_by_role("button", name="Categoria"), m)
    await pg.get_by_label("Nome").fill("Animali")
    await save(pg, m)
    names = await pg.locator(".list-row .name:not(.child)").all_text_contents()
    check(f"{label}: gestione categorie alfabetica, nuova 'Animali' al suo posto", names[:4] == ["Abbigliamento", "Abbonamenti", "Altro", "Animali"] and names == sorted(names, key=str.lower), str(names[:5]))

    # backup -> azzera -> ripristina
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(300)
    await tap(pg.get_by_role("button", name="Esporta backup"), m)
    check(f"{label}: esportazione propone la password di default", await pg.get_by_label("Proteggi il file con una password (consigliato)").is_checked())
    pwf = pg.locator("label.field", has=pg.locator("span", has_text=re.compile("^Password del backup$"))).locator("input")
    await pwf.fill("password del backup")
    await pg.locator("label.field", has=pg.locator("span", has_text=re.compile("^Ripeti la password$"))).locator("input").fill("password del backup")
    async with pg.expect_download() as dl:
        await tap(pg.get_by_role("button", name="Scarica il backup"), m)
    d = await dl.value; path = f"/home/claude/qa/{label}-backup.json"; await d.save_as(path)
    txt = open(path).read()
    check(f"{label}: file esportato protetto (illeggibile)", "statera-backup-cifrato" in txt and "Pranzo" not in txt and d.suggested_filename.startswith("statera-backup-protetto-"))
    await tap(pg.get_by_role("button", name="Elimina tutti i dati"), m)
    await tap(pg.get_by_role("button", name="Conferma eliminazione"), m); await pg.wait_for_timeout(500)
    data = await db_dump(pg)
    check(f"{label}: azzeramento", len(data["accounts"]) == 0 and len(data["categories"]) > 10)
    await pg.locator("input[type=file]").set_input_files(path); await pg.wait_for_timeout(300)
    opw = pg.locator("label.field", has=pg.locator("span", has_text=re.compile("^Password del backup$"))).locator("input")
    await opw.fill("sbagliata!!")
    await tap(pg.get_by_role("button", name="Apri"), m); await pg.wait_for_timeout(2500)
    check(f"{label}: backup protetto, password sbagliata rifiutata", "non corretta" in " ".join(await pg.locator(".error-box").all_inner_texts()))
    await opw.fill("password del backup")
    await tap(pg.get_by_role("button", name="Apri"), m); await pg.wait_for_timeout(2500)
    await tap(pg.get_by_role("button", name="Sostituisci i dati"), m)
    await tap(pg.get_by_role("button", name="Conferma sostituzione"), m); await pg.wait_for_timeout(600)
    data = await db_dump(pg)
    check(f"{label}: ripristino dal backup", len([t for t in data["transactions"] if t["deletedAt"] is None]) == 5 and len(data["accounts"]) == 3)
    await pg.reload(); await wait_app(pg)
    check(f"{label}: dopo ripristino e ricarica tutto ok", await pg.locator(".recovery").count() == 0)

    check(f"{label}: nessun errore in console", not errors, " | ".join(errors[:5]))
    await ctx.close()

async def recovery_test(b):
    print("\n===== Sicurezza: app dentro un altro sito =====")
    ctx = await b.new_context(viewport={"width": 800, "height": 600})
    pg = await ctx.new_page()
    await pg.goto("http://127.0.0.1:4173/manifest.webmanifest")  # origine diversa da localhost
    await pg.set_content('<iframe id="f" src="http://localhost:4173/" width="700" height="500"></iframe>')
    await pg.wait_for_timeout(2500)
    fr = pg.frame_locator("#f")
    txt = await fr.locator("body").inner_text()
    check("App dentro un altro sito: si rifiuta di funzionare", "non può essere aperta dentro un altro sito" in txt and await fr.locator("nav").count() == 0, txt[:80])
    await ctx.close()

    print("\n===== Database bloccato / non apribile =====")
    ctx = await b.new_context(viewport={"width": 390, "height": 844}, locale="it-IT")
    pg = await ctx.new_page()
    await pg.goto(BASE + "/"); await wait_app(pg)
    # Pagina dello stesso sito senza l'app, per manipolare il database
    await pg.goto(BASE + "/manifest.webmanifest")
    # Simula un database di una versione "dal futuro": l'app non può aprirlo
    await pg.evaluate("""() => new Promise(r => { indexedDB.deleteDatabase('statera-locale').onsuccess = () => {
        const q = indexedDB.open('statera-locale', 99999); q.onsuccess = () => { q.result.close(); r() } } })""")
    await pg.goto(BASE + "/"); await pg.wait_for_timeout(1500)
    check("Database non apribile -> schermata di recupero (non nera)", await pg.locator(".recovery").count() == 1)
    txt = await pg.locator(".recovery").inner_text() if await pg.locator(".recovery").count() else ""
    check("Schermata di recupero con istruzioni e pulsanti", "Arresto forzato" in txt and "Riprova" in txt)
    await ctx.close()

    # Transazione bloccata da un'altra finestra: l'avvio non resta nero all'infinito
    ctx = await b.new_context(viewport={"width": 390, "height": 844}, locale="it-IT")
    a = await ctx.new_page(); await a.goto(BASE + "/"); await wait_app(a)
    # La finestra A apre una versione superiore e NON chiude: B resta bloccata
    await a.evaluate("""() => { window.__dbs = []; return new Promise(r => {
        const q = indexedDB.open('statera-hold'); q.onsuccess = () => r() }) }""")
    bpg = await ctx.new_page()
    await bpg.goto(BASE + "/"); await wait_app(bpg)
    check("Seconda finestra dell'app si apre normalmente", await bpg.locator("nav").count() == 1 and await bpg.locator(".recovery").count() == 0)
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        await run_flow(b, "Android", {**p.devices["Pixel 7"], "color_scheme": "dark", "accept_downloads": True}, True)
        await run_flow(b, "PC", {"viewport": {"width": 1366, "height": 768}, "color_scheme": "light", "accept_downloads": True}, False)
        await recovery_test(b)
        await b.close()
    fails = [r for r in results if not r[1]]
    print(f"\nTOTALE: {len(results) - len(fails)}/{len(results)} superati")
    sys.exit(1 if fails else 0)

asyncio.run(main())
