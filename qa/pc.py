"""Collaudo v0.31: schermate PC (dati di esempio, orologio fisso al 14/11/2026).

A 900, 1024, 1280 e 1440 px, in chiaro e in scuro: barra laterale stretta (solo icone) sotto i 1200 px e a
scelta da 1200, testo da 16 px, contenuti larghi al massimo 1200 px nelle schermate su due colonne, niente
scorrimento orizzontale. Movimenti con la colonna di destra (preferiti, da registrare, budget, suggerimento
delle scorciatoie). Colonne regolabili: separatore trascinabile e da tastiera, limiti dai token, scelta salvata
per dispositivo e ritrovata dopo il riavvio, doppio clic e Invio per tornare alla larghezza iniziale.
Conti (v0.31.1): elenco e dettaglio affiancati, movimenti del mese in tabella con saldo dopo ogni movimento, frecce
← → per il mese e ↑ ↓ per il conto, cambio di conto senza nascondere la schermata né tornare in cima, Indietro,
elenco regolabile col dettaglio mai sotto --size-detail-min, colonna del saldo nascosta quando il dettaglio è stretto.
Finestra del movimento (v0.31.2): larga e su due colonne da 900 px (importo, conto, data e descrizione a sinistra,
categoria a destra; per i trasferimenti data a sinistra e altre scelte a destra), suggerimenti con frecce e Invio,
Invio sulla categoria che salva, Invio nelle note che va a capo e Ctrl+Invio che salva, Esc; sotto i 900 px una colonna.
Scorciatoie (v0.31.3): ? apre l'elenco (non dentro un campo né sopra un'altra finestra), Esc lo chiude, si apre anche
dalla colonna di destra e da Altro; in Analisi ← → cambiano periodo.
Sul telefono (Pixel 7) nessuna di queste cose: il conto si apre nella sua schermata, il modulo resta in colonna, in
Altro niente scorciatoie.
"""
import asyncio, re, json, datetime, os
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
SAMPLE = open(os.path.join(os.path.dirname(__file__), "anno-di-esempio.js")).read()
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

def field(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(label)}$"))).locator("select")

async def box(pg, sel):
    return await pg.locator(sel).first.bounding_box()

async def tok(pg, name):
    v = await pg.evaluate("(n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()", name)
    m = re.match(r"^(-?\d+(?:\.\d+)?)px$", v)
    return float(m.group(1)) if m else v

async def no_hscroll(pg):
    return await pg.evaluate("document.scrollingElement.scrollWidth <= innerWidth")

async def prefs(pg):
    return await pg.evaluate("JSON.parse(localStorage.getItem('statera.colonne') || 'null')")

async def prepara(pg):
    """Conto, un anno di movimenti, due budget, due preferiti e una bolletta da confermare."""
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill("Conto corrente"); await pg.get_by_label("Saldo iniziale (€)").fill("3000")
    await pg.locator("dialog input[type=date]").fill("2025-12-01")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill("Contanti"); await pg.get_by_label("Tipo").select_option("contanti"); await pg.get_by_label("Saldo iniziale (€)").fill("150")
    await pg.locator("dialog input[type=date]").fill("2025-12-01")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
    await pg.evaluate(SAMPLE)
    await pg.goto(BASE + "/#/analisi"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(700)
    await pg.get_by_role("button", name="Imposta budget").click()
    await pg.get_by_label("Budget Spesa alimentare (€)").fill("300")
    await pg.get_by_label("Budget Svago (€)").fill("40")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
    for desc, amount, cat, fav, keep in [("Caffè", "1,20", "Pasti fuori", "Caffè", True), ("Spesa Conad", "30", "Spesa alimentare", "Spesa Conad", False)]:
        await pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first.click(); await pg.wait_for_selector("dialog[open]")
        await pg.get_by_label("Importo (€)").fill(amount); await pg.get_by_label("Descrizione").fill(desc)
        await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^" + cat)).click()
        await pg.get_by_label("Salva anche tra i preferiti").check(); await pg.get_by_label("Nome del preferito").fill(fav)
        if not keep: await pg.get_by_label("Ricorda anche l'importo").uncheck()
        await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
    await pg.goto(BASE + "/#/ricorrenti"); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name="Ripetizione").click(); await pg.wait_for_selector("dialog[open]")
    await pg.get_by_label("Importo (€)").fill("48,60")
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Bollette")).click()
    await pg.get_by_label("Descrizione").fill("Bolletta acqua")
    await pg.locator("dialog input[type=date]").first.fill("2026-10-12")  # la prima a ottobre, quella di novembre da registrare
    await pg.get_by_role("radio", name="Da confermare").click()
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)

async def layout(pg, w):
    """Larghezze e posizioni dei pezzi principali di Movimenti."""
    return await pg.evaluate("""() => { const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: Math.round(b.x), w: Math.round(b.width), y: Math.round(b.y), r: Math.round(b.right) } }
      return { nav: r('nav.nav'), content: r('main.content'), body: r('.layout .body'), aside: r('#mov-aside'), splitter: r('.splitter'), root: parseFloat(getComputedStyle(document.documentElement).fontSize), text: parseFloat(getComputedStyle(document.body).fontSize) } }""")

async def movimenti(pg, label, w, scheme):
    await pg.set_viewport_size({"width": w, "height": 860})
    await pg.evaluate("localStorage.removeItem('statera.colonne')")
    await pg.goto(BASE + "/#/movimenti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
    L = await layout(pg, w)
    tag = f"{label} {w} px {scheme}"
    check(f"{tag}: testo a 16 px (radice 17 px)", L["root"] == 17 and abs(L["text"] - 15.9375) < 0.01, f"{L['root']} {L['text']}")
    rail = w < 1200
    check(f"{tag}: barra laterale {'stretta' if rail else 'intera'}", L["nav"]["w"] == (await tok(pg, "--size-rail") if rail else await tok(pg, "--size-sidebar")), str(L["nav"]))
    check(f"{tag}: colonna di destra accanto all'elenco", L["aside"]["x"] >= L["body"]["r"] and L["aside"]["y"] < L["body"]["y"], str(L))
    main_min = await tok(pg, "--size-main-min")
    check(f"{tag}: colonna principale non sotto {main_min:.0f} px", L["body"]["w"] >= main_min, str(L["body"]))
    expect = min(await tok(pg, "--size-aside"), L["content"]["w"] - 40 - main_min - 24)
    check(f"{tag}: colonna di destra larga {expect:.0f} px", abs(L["aside"]["w"] - expect) <= 1, str(L["aside"]))
    check(f"{tag}: contenuti al massimo {await tok(pg, '--content-max-wide'):.0f} px", L["content"]["w"] <= await tok(pg, "--content-max-wide"))
    check(f"{tag}: niente scorrimento orizzontale", await no_hscroll(pg))
    aside = pg.locator("#mov-aside")
    check(f"{tag}: nella colonna preferiti, da registrare e budget",
          await aside.locator("section.fav .chip").count() == 3 and await aside.get_by_role("heading", name="Da registrare").count() == 1
          and await aside.get_by_role("heading", name="Budget del mese").count() == 1 and await aside.get_by_role("meter").count() == 2)
    check(f"{tag}: preferiti che vanno a capo, senza scorrere", await pg.evaluate("(() => { const c = document.querySelector('#mov-aside .chips'); return c.scrollWidth <= c.clientWidth })()"))
    check(f"{tag}: suggerimento delle scorciatoie", "nuovo" in await aside.locator(".keys-hint").inner_text())
    await pg.screenshot(path=f"/tmp/pc-movimenti-{w}-{scheme}.png")

async def separatore(pg, label):
    await pg.set_viewport_size({"width": 1280, "height": 860})
    await pg.evaluate("localStorage.removeItem('statera.colonne')")
    await pg.goto(BASE + "/#/movimenti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
    sp = pg.get_by_role("separator", name="Larghezza della colonna di destra")
    check(f"{label}: separatore per la tastiera e gli screen reader", await sp.count() == 1 and await sp.get_attribute("aria-controls") == "mov-aside" and await sp.get_attribute("tabindex") == "0")
    mn, mx, start = await tok(pg, "--size-aside-min"), await tok(pg, "--size-aside-max"), await tok(pg, "--size-aside")
    check(f"{label}: valore iniziale e limiti dai token", await sp.get_attribute("aria-valuenow") == str(int(start)) and await sp.get_attribute("aria-valuemin") == str(int(mn)) and await sp.get_attribute("aria-valuemax") == str(int(mx)),
          f"{await sp.get_attribute('aria-valuenow')} {await sp.get_attribute('aria-valuemin')} {await sp.get_attribute('aria-valuemax')}")
    # trascinare col mouse
    b = await sp.bounding_box(); x, y = b["x"] + b["width"] / 2, b["y"] + 300
    await pg.mouse.move(x, y); await pg.mouse.down(); await pg.mouse.move(x - 40, y, steps=4)
    check(f"{label}: mentre si trascina, puntatore di ridimensionamento ovunque", await pg.evaluate("document.documentElement.classList.contains('resizing')"))
    await pg.mouse.move(x - 80, y, steps=4); await pg.mouse.up(); await pg.wait_for_timeout(100)
    aw = (await box(pg, "#mov-aside"))["width"]
    check(f"{label}: trascinando a sinistra la colonna si allarga di 80 px", abs(aw - (start + 80)) <= 1, str(aw))
    check(f"{label}: larghezza salvata per il dispositivo", (await prefs(pg))["widths"]["aside"] == int(start + 80), str(await prefs(pg)))
    check(f"{label}: finito il trascinamento, puntatore normale", not await pg.evaluate("document.documentElement.classList.contains('resizing')"))
    # oltre il massimo
    b = await sp.bounding_box(); x = b["x"] + b["width"] / 2
    await pg.mouse.move(x, y); await pg.mouse.down(); await pg.mouse.move(x - 600, y, steps=6); await pg.mouse.up(); await pg.wait_for_timeout(100)
    check(f"{label}: non oltre il massimo", abs((await box(pg, "#mov-aside"))["width"] - mx) <= 1)
    check(f"{label}: colonna principale sempre larga almeno il minimo", (await box(pg, ".layout .body"))["width"] >= await tok(pg, "--size-main-min"))
    # dopo il riavvio
    await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
    check(f"{label}: larghezza ritrovata dopo il riavvio", abs((await box(pg, "#mov-aside"))["width"] - mx) <= 1)
    # tastiera
    h1 = await pg.locator("h1").inner_text()
    await sp.focus(); await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(100)
    check(f"{label}: freccia a destra stringe di 16 px", abs((await box(pg, "#mov-aside"))["width"] - (mx - 16)) <= 1)
    await pg.keyboard.press("Shift+ArrowRight"); await pg.wait_for_timeout(100)
    check(f"{label}: con Maiuscole 64 px", abs((await box(pg, "#mov-aside"))["width"] - (mx - 80)) <= 1)
    check(f"{label}: le frecce sul separatore non cambiano mese", await pg.locator("h1").inner_text() == h1)
    check(f"{label}: valore annunciato aggiornato", await sp.get_attribute("aria-valuenow") == str(int(mx - 80)))
    await pg.keyboard.press("Home"); await pg.wait_for_timeout(100)
    check(f"{label}: Inizio porta al minimo", abs((await box(pg, "#mov-aside"))["width"] - mn) <= 1)
    await pg.keyboard.press("Enter"); await pg.wait_for_timeout(100)
    check(f"{label}: Invio torna alla larghezza iniziale", abs((await box(pg, "#mov-aside"))["width"] - start) <= 1 and (await prefs(pg))["widths"]["aside"] is None)
    await pg.keyboard.press("End"); await pg.wait_for_timeout(100)
    await sp.dblclick(); await pg.wait_for_timeout(100)
    check(f"{label}: doppio clic torna alla larghezza iniziale", abs((await box(pg, "#mov-aside"))["width"] - start) <= 1)
    # a 1024 px il massimo si riduce per lasciare spazio all'elenco
    await pg.keyboard.press("End"); await pg.set_viewport_size({"width": 1024, "height": 800}); await pg.wait_for_timeout(300)
    check(f"{label}: finestra più stretta, l'elenco resta largo almeno il minimo", (await box(pg, ".layout .body"))["width"] >= await tok(pg, "--size-main-min") - 1 and await no_hscroll(pg))
    await pg.set_viewport_size({"width": 1280, "height": 860})

async def barra(pg, label):
    await pg.set_viewport_size({"width": 1280, "height": 860})
    await pg.evaluate("localStorage.removeItem('statera.colonne')")
    await pg.goto(BASE + "/#/movimenti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(600)
    btn = pg.get_by_role("button", name="Stringi la barra")
    check(f"{label}: da 1200 px si può stringere la barra", await btn.count() == 1 and await btn.get_attribute("aria-pressed") == "false")
    dur = await pg.evaluate("getComputedStyle(document.querySelector('.shell')).transitionDuration")
    check(f"{label}: la barra cambia larghezza in --duration-base", dur in ("0.2s", "200ms"), dur)
    await btn.click(); await pg.wait_for_timeout(400)
    nav = await box(pg, "nav.nav")
    check(f"{label}: barra stretta, solo icone", abs(nav["width"] - await tok(pg, "--size-rail")) <= 1 and await btn.get_attribute("aria-pressed") == "true")
    check(f"{label}: le voci si trovano ancora per nome", await pg.get_by_role("link", name="Conti").count() == 1 and await pg.get_by_role("link", name="Conti").get_attribute("title") == "Conti")
    check(f"{label}: scelta salvata", (await prefs(pg))["side"] == "stretta")
    await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(600)
    check(f"{label}: barra stretta dopo il riavvio", abs((await box(pg, "nav.nav"))["width"] - await tok(pg, "--size-rail")) <= 1)
    await pg.get_by_role("button", name="Stringi la barra").click(); await pg.wait_for_timeout(400)
    check(f"{label}: e di nuovo intera", abs((await box(pg, "nav.nav"))["width"] - await tok(pg, "--size-sidebar")) <= 1)
    await pg.set_viewport_size({"width": 1024, "height": 800}); await pg.wait_for_timeout(300)
    check(f"{label}: sotto i 1200 px la barra è stretta e il pulsante non c'è", abs((await box(pg, "nav.nav"))["width"] - await tok(pg, "--size-rail")) <= 1 and await pg.get_by_role("button", name="Stringi la barra").count() == 0)
    await pg.set_viewport_size({"width": 1280, "height": 860})

async def conti(pg, label):
    await pg.set_viewport_size({"width": 1280, "height": 860})
    await pg.evaluate("localStorage.removeItem('statera.colonne')")
    await pg.goto(BASE + "/#/conti"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(800)
    lst, det = await box(pg, "#conti-list"), await box(pg, ".detail-col")
    check(f"{label}: Conti con elenco a sinistra e dettaglio a destra", det["x"] > lst["x"] + lst["width"] and abs(lst["width"] - await tok(pg, "--size-pane")) <= 1, f"{lst} {det}")
    check(f"{label}: Conti largo al massimo {await tok(pg, '--content-max-wide'):.0f} px", (await box(pg, "main.content"))["width"] <= await tok(pg, "--content-max-wide"))
    sel = pg.locator("#conti-list a[aria-current=true]")
    check(f"{label}: all'inizio è scelto il primo conto", await sel.count() == 1 and "Conto corrente" in await sel.inner_text())
    panel = pg.locator("section[aria-label='Dettaglio di Conto corrente']")
    check(f"{label}: dettaglio del conto con saldo di oggi", await panel.count() == 1 and "Saldo di oggi" in await panel.inner_text())
    rows = panel.locator("tbody tr")
    n_nov = await rows.count()
    heads = await panel.locator("thead th").all_text_contents()
    check(f"{label}: movimenti di novembre in tabella", n_nov >= 9 and heads == ["Data", "Descrizione", "Importo", "Saldo"], f"{n_nov} {heads}")
    check(f"{label}: saldo dopo ogni movimento", re.search(r"\d\s€$", (await rows.first.locator("td").last.inner_text()).strip()) is not None)
    check(f"{label}: saldo a inizio mese in fondo", "Saldo a inizio mese" in await panel.locator(".opening").inner_text())
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("ArrowLeft"); await pg.wait_for_timeout(200)
    check(f"{label}: freccia a sinistra = ottobre nel dettaglio", await panel.locator("h3").inner_text() == "Ottobre 2026" and await rows.count() >= 7)
    await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(200)
    check(f"{label}: e di nuovo novembre", await panel.locator("h3").inner_text() == "Novembre 2026" and await rows.count() == n_nov)
    # un altro conto: cambia solo il dettaglio, in dissolvenza, senza nascondere la schermata né tornare in cima
    await pg.evaluate("window.scrollTo(0, 120)")
    hist = await pg.evaluate("history.length")
    await pg.evaluate("""() => { window.__anims = []; window.__reveal = []
      document.addEventListener('animationstart', (e) => window.__anims.push([e.animationName, getComputedStyle(e.target).animationDuration]))
      new MutationObserver(() => window.__reveal.push(document.querySelector('.screen').dataset.reveal)).observe(document.querySelector('.screen'), { attributes: true }) }""")
    await pg.locator("#conti-list").get_by_role("link", name=re.compile("Contanti")).click(); await pg.wait_for_timeout(400)
    reveal = await pg.evaluate("window.__reveal")
    anim = [d for n, d in await pg.evaluate("window.__anims") if n.endswith("pane-in")]
    base = await pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--duration-base').trim()")
    check(f"{label}: clic su Contanti: indirizzo del conto", (await pg.evaluate("location.hash")).startswith("#/conto/") and await pg.locator("section[aria-label='Dettaglio di Contanti']").count() == 1)
    check(f"{label}: la schermata resta visibile, il dettaglio compare in --duration-base", "wait" not in reveal and len(anim) == 1 and float(anim[0].rstrip("ms")) * (1 if anim[0].endswith("ms") else 1000) == float(base.rstrip("ms")) * (1 if base.endswith("ms") else 1000), f"{reveal} {anim} {base}")
    check(f"{label}: la pagina non torna in cima", await pg.evaluate("scrollY") > 0)
    check(f"{label}: Contanti evidenziato nell'elenco", "Contanti" in await pg.locator("#conti-list a[aria-current=true]").inner_text())
    check(f"{label}: conto senza movimenti nel mese: avviso", "Nessun movimento su questo conto" in await pg.locator(".detail-col").inner_text())
    await pg.go_back(); await pg.wait_for_timeout(400)
    check(f"{label}: Indietro torna al conto di prima", await pg.locator("section[aria-label='Dettaglio di Conto corrente']").count() == 1)
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("ArrowDown"); await pg.wait_for_timeout(300)
    check(f"{label}: freccia giù passa al conto successivo senza riempire la cronologia", await pg.locator("section[aria-label='Dettaglio di Contanti']").count() == 1 and await pg.evaluate("history.length") == hist + 1)
    await pg.keyboard.press("ArrowUp"); await pg.wait_for_timeout(300)
    check(f"{label}: freccia su torna al primo", await pg.locator("section[aria-label='Dettaglio di Conto corrente']").count() == 1)
    # un movimento della tabella si apre
    await panel.locator("tbody tr").first.locator("button.desc").click(); await pg.wait_for_selector("dialog[open]")
    check(f"{label}: clic su una riga apre il movimento", await pg.get_by_label("Importo (€)").input_value() != "")
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    # separatore dell'elenco
    sp = pg.get_by_role("separator", name="Larghezza dell'elenco dei conti")
    b = await sp.bounding_box(); x, y = b["x"] + b["width"] / 2, b["y"] + 200
    start = (await box(pg, "#conti-list"))["width"]
    await pg.mouse.move(x, y); await pg.mouse.down(); await pg.mouse.move(x + 60, y, steps=5); await pg.mouse.up(); await pg.wait_for_timeout(100)
    check(f"{label}: trascinando a destra l'elenco si allarga", abs((await box(pg, "#conti-list"))["width"] - (start + 60)) <= 1 and (await prefs(pg))["widths"]["pane"] == int(start + 60))
    await pg.mouse.move(x + 60, y); await pg.mouse.down(); await pg.mouse.move(x + 900, y, steps=5); await pg.mouse.up(); await pg.wait_for_timeout(100)
    check(f"{label}: il dettaglio resta largo almeno --size-detail-min", (await box(pg, ".detail-col"))["width"] >= await tok(pg, "--size-detail-min") - 1)
    await sp.dblclick(); await pg.wait_for_timeout(100)
    check(f"{label}: doppio clic: elenco alla larghezza iniziale", abs((await box(pg, "#conti-list"))["width"] - start) <= 1)
    # finestra stretta
    await pg.set_viewport_size({"width": 960, "height": 800}); await pg.wait_for_timeout(300)
    check(f"{label}: a 960 px dettaglio largo almeno il minimo e niente scorrimento", (await box(pg, ".detail-col"))["width"] >= await tok(pg, "--size-detail-min") - 1 and await no_hscroll(pg))
    check(f"{label}: dettaglio stretto: la colonna del saldo si nasconde", not await panel.locator("thead th").last.is_visible() and await panel.locator("thead th").nth(2).is_visible())
    await pg.screenshot(path="/tmp/pc-conti-960.png")
    await pg.set_viewport_size({"width": 1280, "height": 860})

async def count_tx(pg):
    return await pg.evaluate("""() => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction('transactions').objectStore('transactions').getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null).length) } } })""")

async def finestra(pg, label):
    await pg.set_viewport_size({"width": 1280, "height": 860})
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(600)
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("n"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(500)
    d = await box(pg, "dialog[open]")
    check(f"{label}: finestra del movimento larga {await tok(pg, '--size-window-wide'):.0f} px", abs(d["width"] - await tok(pg, "--size-window-wide")) <= 1, str(d))
    amount, cats = await box(pg, "#amount-input"), await box(pg, "dialog .cat-list")
    check(f"{label}: importo a sinistra, categoria a destra alla stessa altezza", cats["x"] > amount["x"] + amount["width"] and abs(cats["y"] - amount["y"]) < 60, f"{amount} {cats}")
    check(f"{label}: elenco delle categorie più lungo che sul telefono", cats["height"] > 300)
    check(f"{label}: niente scorrimento orizzontale nella finestra", await pg.evaluate("(() => { const b = document.querySelector('dialog[open] .body'); return b.scrollWidth <= b.clientWidth })()"))
    # suggerimenti mentre si scrive, frecce e Invio
    await pg.get_by_label("Descrizione").fill("Caf"); await pg.wait_for_timeout(200)
    lb = pg.get_by_role("listbox", name="Suggerimenti")
    check(f"{label}: suggerimenti sotto la descrizione, nella colonna di sinistra", await lb.count() == 1 and (await lb.bounding_box())["x"] < cats["x"])
    await pg.keyboard.press("ArrowDown"); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(200)
    checked = pg.locator(".cat-list").get_by_role("radio", checked=True)
    check(f"{label}: suggerimento scelto: descrizione, categoria e importo dell'ultima volta",
          await pg.get_by_label("Descrizione").input_value() == "Caffè" and "Pasti fuori" in await checked.inner_text() and await pg.get_by_label("Importo (€)").input_value() == "1,20")
    check(f"{label}: Invio sul suggerimento non salva", await pg.locator("dialog[open]").count() == 1)
    # Invio dalla categoria salva
    n0 = await count_tx(pg)
    await checked.focus(); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(600)
    check(f"{label}: Invio sulla categoria salva e chiude", await pg.locator("dialog[open]").count() == 0 and await count_tx(pg) == n0 + 1)
    # Invio nelle note va a capo, Ctrl+Invio salva
    await pg.keyboard.press("n"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await pg.get_by_label("Importo (€)").fill("3")
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Svago")).click()
    await pg.get_by_role("button", name="+ Aggiungi nota").click()
    note = pg.get_by_label("Note"); await note.focus(); await pg.keyboard.type("riga uno"); await pg.keyboard.press("Enter"); await pg.keyboard.type("riga due")
    check(f"{label}: Invio nelle note va a capo", await pg.locator("dialog[open]").count() == 1 and await note.input_value() == "riga uno\nriga due")
    await pg.keyboard.press("Control+Enter"); await pg.wait_for_timeout(600)
    check(f"{label}: Ctrl+Invio salva anche dalle note", await pg.locator("dialog[open]").count() == 0 and await count_tx(pg) == n0 + 2)
    # trasferimento: la data a sinistra, le altre scelte a destra
    await pg.keyboard.press("n"); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await pg.get_by_role("radio", name="Trasferimento").click(); await pg.wait_for_timeout(200)
    dt, rep = await box(pg, "dialog input[type=date]"), await box(pg, "dialog .repeat")
    check(f"{label}: trasferimento: data a sinistra, ripetizione a destra", dt["x"] < rep["x"] and await pg.locator("dialog .cat-list").count() == 0)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    check(f"{label}: Esc chiude la finestra", await pg.locator("dialog[open]").count() == 0)
    # sotto i 900 px finestra a una colonna, come prima
    await pg.set_viewport_size({"width": 800, "height": 860}); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first.click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(500)
    d = await box(pg, "dialog[open]")
    amount, cats = await box(pg, "#amount-input"), await box(pg, "dialog .cat-list")
    check(f"{label}: a 800 px finestra da {await tok(pg, '--size-window'):.0f} px a una colonna", abs(d["width"] - await tok(pg, "--size-window")) <= 1 and cats["y"] > amount["y"] + amount["height"], f"{d} {cats}")
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    await pg.set_viewport_size({"width": 1280, "height": 860})

async def scorciatoie(pg, label):
    await pg.set_viewport_size({"width": 1280, "height": 860})
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(600)
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("?"); await pg.wait_for_timeout(500)
    dlg = pg.get_by_role("dialog", name="Scorciatoie da tastiera")
    heads = await dlg.locator("h3").all_text_contents()
    check(f"{label}: ? apre l'elenco delle scorciatoie", await dlg.count() == 1 and heads == ["Ovunque", "Movimenti, Conti, Analisi", "Nelle finestre", "Colonne (separatore)"], str(heads))
    txt = await dlg.inner_text()
    check(f"{label}: elenco con N, /, ?, Esc, frecce, Invio e Ctrl+Invio", all(k in txt for k in ["Nuovo movimento", "Cerca", "Questo elenco", "Chiude la finestra", "Mese precedente", "Salva anche dalle note", "Larghezza iniziale"]))
    check(f"{label}: tasti scritti come tasti", await dlg.locator("kbd").count() >= 18)
    check(f"{label}: niente scorrimento orizzontale nell'elenco", await pg.evaluate("(() => { const b = document.querySelector('dialog[open] .body'); return b.scrollWidth <= b.clientWidth })()"))
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    check(f"{label}: Esc chiude l'elenco", await pg.locator("dialog[open]").count() == 0)
    await pg.locator("#mov-aside").get_by_role("button", name=re.compile("tutte le scorciatoie")).click(); await pg.wait_for_timeout(400)
    check(f"{label}: si apre anche dalla colonna di destra", await dlg.count() == 1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    # ? scritto in un campo resta un carattere; ? con un'altra finestra aperta non apre nulla
    await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(500)
    inp = pg.get_by_role("searchbox").or_(pg.locator("input[type=search], input[type=text]")).first
    await inp.click(); await pg.keyboard.type("?")
    check(f"{label}: ? in un campo resta un carattere", await pg.locator("dialog[open]").count() == 0 and "?" in await inp.input_value())
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("n"); await pg.wait_for_selector("dialog[open]")
    await pg.get_by_role("radio", name="Entrata").focus(); await pg.keyboard.press("?"); await pg.wait_for_timeout(300)
    check(f"{label}: con la finestra del movimento aperta ? non ne apre un'altra", await pg.locator("dialog[open]").count() == 1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    # da Altro
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(500)
    await pg.get_by_role("button", name=re.compile("^Scorciatoie da tastiera")).click(); await pg.wait_for_timeout(400)
    check(f"{label}: si apre anche da Altro", await dlg.count() == 1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400)
    # frecce in Analisi
    await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(700)
    t0 = await pg.locator("h1").first.inner_text()
    await pg.locator("body").click(position={"x": 5, "y": 5}); await pg.keyboard.press("ArrowLeft"); await pg.wait_for_timeout(400)
    t1 = await pg.locator("h1").first.inner_text()
    await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(400)
    check(f"{label}: in Analisi le frecce cambiano periodo", t1 != t0 and await pg.locator("h1").first.inner_text() == t0, f"{t0} {t1}")

async def telefono(pg, label):
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(600)
    check(f"{label}: niente separatore né budget nella schermata", await pg.locator(".splitter").count() == 0 and await pg.get_by_role("heading", name="Budget del mese").count() == 0)
    check(f"{label}: testo a 15 px", await pg.evaluate("parseFloat(getComputedStyle(document.body).fontSize)") == 15)
    check(f"{label}: preferiti in una riga che scorre", await pg.evaluate("getComputedStyle(document.querySelector('section.fav .chips')).flexWrap") == "nowrap")
    order = await pg.evaluate("""() => [...document.querySelectorAll('.layout h2, .layout .balance-box')].map(e => e.textContent.trim().slice(0, 14))""")
    check(f"{label}: «Da registrare» prima del saldo, come prima", order.index("Da registrare") < [i for i, t in enumerate(order) if t.startswith("Saldo")][0], str(order))
    check(f"{label}: niente scorrimento orizzontale", await no_hscroll(pg))
    await pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first.click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    check(f"{label}: modulo del movimento in colonna, come prima", await pg.evaluate("getComputedStyle(document.querySelector('#movement-form')).display") == "flex")
    await pg.get_by_role("button", name="Chiudi").click(); await pg.wait_for_timeout(500)
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(500)
    check(f"{label}: in Altro niente scorciatoie da tastiera", await pg.get_by_role("button", name=re.compile("^Scorciatoie da tastiera")).count() == 0)
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
    check(f"{label}: Conti senza dettaglio accanto", await pg.locator(".detail-col").count() == 0 and await pg.locator(".splitter").count() == 0)
    await pg.locator(".list-row", has_text="Conto corrente").first.click(); await pg.wait_for_timeout(600)
    check(f"{label}: il conto si apre nella sua schermata, con la freccia indietro", await pg.get_by_role("link", name="Torna a Conti").count() == 1 and await pg.locator("table").count() == 0)

async def ridotte(b):
    """Con «riduci animazioni» anche barra laterale, dettaglio del conto e linea del separatore sono istantanei."""
    print("\n===== PC, riduci animazioni =====")
    ctx = await b.new_context(viewport={"width": 1280, "height": 860}, locale="it-IT", reduced_motion="reduce")
    pg = await ctx.new_page(); await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 14, 10, 0))
    await prepara(pg)
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
    ms = lambda v: float(v.rstrip("ms")) * (1 if v.endswith("ms") else 1000)
    d = await pg.evaluate("""() => ({ side: getComputedStyle(document.querySelector('.shell')).transitionDuration,
      pane: getComputedStyle(document.querySelector('.pane-in')).animationDuration,
      line: getComputedStyle(document.querySelector('.splitter'), '::before').transitionDuration })""")
    check("PC ridotte: barra laterale, dettaglio e separatore a 0,01 ms", all(ms(v.split(",")[0]) <= 0.01 for v in d.values()), str(d))
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, opts, scheme in [("PC", {"viewport": {"width": 1280, "height": 860}}, "light"), ("PC scuro", {"viewport": {"width": 1280, "height": 860}}, "dark"), ("Android", {**p.devices["Pixel 7"]}, "light")]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(**opts, locale="it-IT", color_scheme=scheme, timezone_id="Europe/Rome")
            pg = await ctx.new_page(); errs = []
            await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 14, 10, 0))
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await prepara(pg)
            if label == "Android":
                await telefono(pg, label)
            else:
                for w in ([900, 1024, 1280, 1440] if scheme == "light" else [1024, 1440]):
                    await movimenti(pg, label, w, scheme)
                if scheme == "light":
                    await separatore(pg, label)
                    await conti(pg, label)
                    await finestra(pg, label)
                    await scorciatoie(pg, label)
                    await barra(pg, label)
            check(f"{label}: nessun errore", not errs, str(errs[:3]))
            await ctx.close()
        await ridotte(b)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} superati")

asyncio.run(main())
