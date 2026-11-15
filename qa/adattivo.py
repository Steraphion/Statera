"""Collaudo v0.34: PC adattivo (dati di esempio, orologio fisso al 14/11/2026).

Le colonne dipendono dalla larghezza dell'area dei contenuti (a destra della barra laterale), non della finestra:
classi media (da 720 px), larga (da 1100) e molto larga (da 1440) su main.content, che cambiano anche stringendo la
barra laterale; contenuti fino a --content-max-wide (1880 px), centrati solo oltre. A 1280, 1536, 1920 e 2560 px:
- Movimenti: da larga saldo, entrate e uscite in una riga, azioni rapide compatte nella testata, elenco a colonne
  allineate alle intestazioni; da molto larga calendario e «Dove vanno i soldi» a sinistra (toccando un giorno
  l'elenco ci va), niente scelta Elenco/Calendario. Colonna di destra mai vuota: senza budget «Dove vanno i soldi»,
  senza niente la colonna non c'è e i tasti passano a sinistra.
- Conti: colonna Categoria nella tabella quando il dettaglio è largo; da molto larga terza colonna col saldo del
  conto a fine mese e gli obiettivi (che altrimenti stanno sotto l'elenco).
- Analisi: schede su due colonne, risparmio, entrate e uscite in una riga da larga, tre colonne da molto larga.
- Cerca: filtri sempre aperti a sinistra e ultimi movimenti senza ricerca; da larga tabella con la data in colonna;
  da molto larga, mentre si cerca, riepilogo per categoria e per mese (una categoria restringe la ricerca).
- Maniglia del separatore nascosta finché non serve; in Cerca la barra laterale evidenzia Cerca.
Sul telefono nessuna di queste cose.
"""
import asyncio, re, datetime, os
from playwright.async_api import async_playwright
BASE = os.environ.get("QA_BASE", "http://localhost:4173")
SAMPLE = open(os.path.join(os.path.dirname(__file__), "anno-di-esempio.js")).read()
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

async def box(pg, sel):
    return await pg.locator(sel).first.bounding_box()

async def tok(pg, name):
    v = await pg.evaluate("(n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()", name)
    m = re.match(r"^(-?\d+(?:\.\d+)?)px$", v)
    return float(m.group(1)) if m else v

async def no_hscroll(pg):
    return await pg.evaluate("document.scrollingElement.scrollWidth <= innerWidth")

async def classes(pg):
    return await pg.evaluate("[...document.querySelector('main.content').classList].filter(c => c.startsWith('l-'))")

async def visible(pg, sel):
    return await pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && getComputedStyle(e).display !== 'none' && e.getBoundingClientRect().width > 0 }", sel)

async def conto(pg, nome, saldo, tipo=None):
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill(nome)
    if tipo: await pg.get_by_label("Tipo").select_option(tipo)
    await pg.get_by_label("Saldo iniziale (€)").fill(saldo)
    await pg.locator("dialog input[type=date]").fill("2025-12-01")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)

async def prepara(pg, pieno=True):
    """Pieno: due conti, un anno di movimenti, due budget, un preferito. Altrimenti un conto e una spesa."""
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
    await conto(pg, "Conto corrente", "3000")
    if not pieno:
        await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)
        await pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first.click(); await pg.wait_for_selector("dialog[open]")
        await pg.get_by_label("Importo (€)").fill("12,50"); await pg.get_by_label("Descrizione").fill("Pizza")
        await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Pasti fuori")).click()
        await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)
        return
    await conto(pg, "Contanti", "150", "contanti")
    await pg.evaluate(SAMPLE)
    await pg.goto(BASE + "/#/analisi"); await pg.reload(); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(700)
    await pg.get_by_role("button", name="Imposta budget").click()
    await pg.get_by_label("Budget Spesa alimentare (€)").fill("300")
    await pg.get_by_label("Budget Svago (€)").fill("40")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(400)
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)
    await pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first.click(); await pg.wait_for_selector("dialog[open]")
    await pg.get_by_label("Importo (€)").fill("1,20"); await pg.get_by_label("Descrizione").fill("Caffè")
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Pasti fuori")).click()
    await pg.get_by_label("Salva anche tra i preferiti").check(); await pg.get_by_label("Nome del preferito").fill("Caffè")
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(500)

async def vai(pg, w, route, h=900):
    await pg.set_viewport_size({"width": w, "height": h})
    await pg.goto(BASE + "/#/" + route); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(700)

ATTESE = {1280: ["l-media"], 1536: ["l-media", "l-larga"], 1920: ["l-media", "l-larga", "l-molto"], 2560: ["l-media", "l-larga", "l-molto"]}

async def basi(pg, label):
    for w, cls in ATTESE.items():
        await vai(pg, w, "movimenti")
        check(f"{label} {w}: classi dell'area {cls}", await classes(pg) == cls, str(await classes(pg)))
        check(f"{label} {w}: niente scorrimento orizzontale", await no_hscroll(pg))
    # soglia: si guarda l'area, non la finestra
    area = "(() => { const c = document.querySelector('main.content'); const s = getComputedStyle(c); return c.getBoundingClientRect().width - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight) })()"
    await vai(pg, 1500, "movimenti")
    off = 1500 - await pg.evaluate(area)
    await vai(pg, round(1099 + off), "movimenti")
    a = await pg.evaluate(area)
    check(f"{label}: area di {a:.0f} px ancora media", "l-larga" not in await classes(pg) and a < 1100, str(a))
    await vai(pg, round(1100 + off), "movimenti")
    a = await pg.evaluate(area)
    check(f"{label}: area di {a:.0f} px larga", "l-larga" in await classes(pg) and a >= 1100, str(a))
    await vai(pg, 1300, "movimenti")
    check(f"{label}: 1300 px con la barra intera: media", "l-larga" not in await classes(pg))
    await pg.locator(".side-toggle").click(); await pg.wait_for_timeout(500)
    check(f"{label}: stringendo la barra l'area diventa larga", "l-larga" in await classes(pg))
    await pg.locator(".side-toggle").click(); await pg.wait_for_timeout(400)
    # tetto e posizione
    await vai(pg, 1920, "movimenti")
    s = await box(pg, ".screen")
    nav = await box(pg, "nav.nav")
    check(f"{label} 1920: la schermata parte accanto alla barra", s["x"] - (nav["x"] + nav["width"]) <= 40, f"{s} {nav}")
    await vai(pg, 2560, "movimenti")
    s = await box(pg, ".screen")
    tetto = await tok(pg, "--content-max-wide")
    c = await box(pg, "main.content")
    check(f"{label} 2560: schermata larga {tetto:.0f} px e centrata nell'area", abs(s["width"] - tetto) <= 1 and abs((s["x"] - c["x"]) - (c["x"] + c["width"] - s["x"] - s["width"])) <= 2, f"{s} {c}")
    await vai(pg, 1920, "altro")
    check(f"{label}: Altro resta a una colonna da {await tok(pg, '--content-max'):.0f} px, centrata", abs((await box(pg, "main.content"))["width"] - await tok(pg, "--content-max")) <= 1 and "l-larga" not in await classes(pg))
    # Cerca evidenziata
    await vai(pg, 1280, "cerca")
    cur = await pg.evaluate("[...document.querySelectorAll('nav.nav a[aria-current=page]')].map(a => a.textContent.trim())")
    check(f"{label}: in Cerca la barra evidenzia solo Cerca", cur == ["Cerca"], str(cur))
    # maniglia del separatore
    await vai(pg, 1280, "movimenti")
    op = await pg.evaluate("getComputedStyle(document.querySelector('.splitter .grip')).opacity")
    check(f"{label}: maniglia del separatore nascosta finché non serve", op == "0", op)
    await pg.locator(".splitter").hover(); await pg.wait_for_timeout(300)
    op = await pg.evaluate("getComputedStyle(document.querySelector('.splitter .grip')).opacity")
    check(f"{label}: passando col puntatore la maniglia si vede", op == "1", op)

async def movimenti(pg, label):
    await vai(pg, 1280, "movimenti")
    check(f"{label} 1280: azioni rapide in cerchi accanto al saldo, nessuna nella testata",
          await pg.locator(".quick .circle").count() == 3 and await pg.locator(".quick-pc").count() == 0)
    check(f"{label} 1280: niente colonna sinistra, scelta Elenco/Calendario presente",
          await pg.locator(".cal-col").count() == 0 and await pg.get_by_role("radiogroup", name="Vista").count() == 1)
    check(f"{label} 1280: righe come sul telefono", await pg.locator(".cols-head").count() == 0 and await pg.locator(".list-row.row-cols").count() == 0)
    await vai(pg, 1536, "movimenti")
    hero, tiles = await box(pg, ".hero"), pg.locator(".kpis .tile")
    t1, t2 = await tiles.nth(0).bounding_box(), await tiles.nth(1).bounding_box()
    check(f"{label} 1536: saldo, entrate e uscite in una riga", abs(hero["y"] - t1["y"]) <= 1 and abs(t1["y"] - t2["y"]) <= 1 and hero["x"] < t1["x"] < t2["x"] and hero["width"] > t1["width"], f"{hero} {t1} {t2}")
    pills = pg.locator(".quick-pc .btn")
    check(f"{label} 1536: azioni rapide compatte nella testata, senza cerchi",
          await pills.count() == 3 and await pg.locator(".quick .circle").count() == 0 and await pg.locator(".quick-pc").get_by_role("button", name="Nuova spesa").count() == 1)
    await pills.nth(0).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(300)
    check(f"{label} 1536: «Spesa» apre il modulo di una spesa", await pg.locator("dialog[open]").get_by_role("radio", name="Uscita", checked=True).count() == 1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
    head = await pg.evaluate("[...document.querySelectorAll('.cols-head span')].map(s => s.textContent.trim())")
    check(f"{label} 1536: intestazioni delle colonne", head == ["", "Descrizione", "Categoria", "Conto o carta", "Importo"], str(head))
    al = await pg.evaluate("""() => { const h = [...document.querySelectorAll('.cols-head span')].map(s => Math.round(s.getBoundingClientRect().x));
      return [...document.querySelectorAll('.list-row.row-cols')].slice(0, 6).every(r => { const c = r.querySelectorAll(':scope > .cell'); return c.length === 2 && Math.abs(c[0].getBoundingClientRect().x - h[2]) <= 1 && Math.abs(c[1].getBoundingClientRect().x - h[3]) <= 1 }) }""")
    check(f"{label} 1536: categoria e conto allineati alle intestazioni", al)
    check(f"{label} 1536: niente scorrimento orizzontale", await no_hscroll(pg))
    await vai(pg, 1920, "movimenti")
    cal, body, aside = await box(pg, ".cal-col"), await box(pg, ".layout .body"), await box(pg, "#mov-aside")
    check(f"{label} 1920: tre colonne, calendario a sinistra e colonna di destra",
          cal and cal["x"] + cal["width"] <= body["x"] and body["x"] + body["width"] <= aside["x"], f"{cal} {body} {aside}")
    check(f"{label} 1920: colonna sinistra larga --size-cal", abs(cal["width"] - await tok(pg, "--size-cal")) <= 1, str(cal))
    check(f"{label} 1920: calendario e «Dove vanno i soldi» a sinistra, budget a destra",
          await pg.locator(".cal-col").get_by_role("grid", name="Calendario del mese").count() == 1
          and await pg.locator(".cal-col").get_by_role("heading", name="Dove vanno i soldi").count() == 1
          and await pg.locator("#mov-aside").get_by_role("heading", name="Budget del mese").count() == 1
          and await pg.locator("#mov-aside").get_by_role("heading", name="Dove vanno i soldi").count() == 0)
    check(f"{label} 1920: niente scelta Elenco/Calendario, elenco di tutto il mese", await pg.get_by_role("radiogroup", name="Vista").count() == 0 and await pg.locator(".day-group").count() >= 5)
    check(f"{label} 1920: tasti solo in fondo alla colonna di destra", await visible(pg, "#mov-aside .keys-hint") and not await visible(pg, ".cal-col .keys-hint"))
    await pg.set_viewport_size({"width": 1920, "height": 600}); await pg.wait_for_timeout(300)
    day = await pg.evaluate("[...document.querySelectorAll('.day-group')][2].id.replace('giorno-', '')")
    btn = pg.locator(f".cal-col button[role=gridcell]").nth(int(day[-2:]) - 1)
    await btn.click(); await pg.wait_for_timeout(400)
    top = await pg.evaluate(f"document.getElementById('giorno-{day}').getBoundingClientRect().top")
    check(f"{label} 1920: toccando un giorno l'elenco ci va", 0 <= top <= 60, str(top))
    check(f"{label} 1920: il giorno toccato resta scelto", await btn.get_attribute("aria-selected") == "true")
    await pg.set_viewport_size({"width": 1920, "height": 900})
    # separatore: col calendario a sinistra il massimo tiene conto della colonna in più
    sp = pg.get_by_role("separator", name="Larghezza della colonna di destra")
    await sp.focus(); await pg.keyboard.press("End"); await pg.wait_for_timeout(150)
    body = await box(pg, ".layout .body")
    check(f"{label} 1920: allargando al massimo la colonna di destra l'elenco resta largo almeno il minimo", body["width"] >= await tok(pg, "--size-main-min") - 1, str(body))
    await pg.keyboard.press("Enter"); await pg.wait_for_timeout(150)
    await vai(pg, 2560, "movimenti")
    check(f"{label} 2560: tre colonne anche oltre il tetto, niente scorrimento", await pg.locator(".cal-col").count() == 1 and await no_hscroll(pg))

async def conti(pg, label):
    await vai(pg, 1280, "conti")
    check(f"{label} 1280: obiettivi sotto l'elenco, niente terza colonna",
          await pg.locator("#conti-list").get_by_role("heading", name=re.compile("Obiettivi di risparmio")).count() == 1 and await pg.locator(".extra-col").count() == 0)
    check(f"{label} 1280: dettaglio stretto, niente colonna Categoria", not await visible(pg, ".detail-col th.cat"))
    await vai(pg, 1536, "conti")
    check(f"{label} 1536: dettaglio largo, colonna Categoria", await visible(pg, ".detail-col th.cat") and await visible(pg, ".detail-col td.cat-cell"))
    sub = await pg.locator(".detail-col tbody tr").first.locator(".sub.no-cat").inner_text()
    cat = await pg.locator(".detail-col tbody tr").first.locator("td.cat-cell").inner_text()
    check(f"{label} 1536: la categoria non si ripete sotto la descrizione", cat and cat not in sub, f"{cat!r} {sub!r}")
    check(f"{label} 1536: niente scorrimento orizzontale", await no_hscroll(pg))
    await vai(pg, 1920, "conti")
    lst, det, ext = await box(pg, "#conti-list"), await box(pg, ".detail-col"), await box(pg, ".extra-col")
    check(f"{label} 1920: tre colonne, elenco, dettaglio e andamento",
          ext and lst["x"] + lst["width"] <= det["x"] and det["x"] + det["width"] <= ext["x"] and abs(ext["width"] - await tok(pg, "--size-extra")) <= 1, f"{lst} {det} {ext}")
    check(f"{label} 1920: saldo a fine mese del conto scelto e obiettivi nella terza colonna",
          await pg.locator(".extra-col").get_by_role("heading", name="Saldo a fine mese").count() == 1
          and await pg.locator(".extra-col").get_by_role("heading", name=re.compile("Obiettivi di risparmio")).count() == 1
          and await pg.locator("#conti-list").get_by_role("heading", name=re.compile("Obiettivi di risparmio")).count() == 0)
    t1 = await pg.locator(".extra-col .card-sub").inner_text()
    await pg.locator("#conti-list .list-row", has_text="Contanti").click(); await pg.wait_for_timeout(500)
    t2 = await pg.locator(".extra-col .card-sub").inner_text()
    check(f"{label} 1920: l'andamento segue il conto scelto", t1.startswith("Conto corrente") and t2.startswith("Contanti"), f"{t1} {t2}")
    check(f"{label} 1920: dettaglio largo almeno --size-detail-min e niente scorrimento", det["width"] >= await tok(pg, "--size-detail-min") - 1 and await no_hscroll(pg))
    sp = pg.get_by_role("separator", name="Larghezza dell'elenco dei conti")
    await sp.focus(); await pg.keyboard.press("End"); await pg.wait_for_timeout(150)
    check(f"{label} 1920: elenco al massimo, il dettaglio resta largo almeno il minimo", (await box(pg, ".detail-col"))["width"] >= await tok(pg, "--size-detail-min") - 1)
    await pg.keyboard.press("Enter"); await pg.wait_for_timeout(150)

async def analisi(pg, label):
    await vai(pg, 1280, "analisi")
    check(f"{label} 1280: schede su due colonne", await pg.locator(".acols > .acol").count() == 2)
    save, t = await box(pg, ".save"), await box(pg, ".tiles .tile")
    check(f"{label} 1280: risparmio sopra entrate e uscite", save["y"] + save["height"] <= t["y"] + 1, f"{save} {t}")
    await vai(pg, 1536, "analisi")
    save, tiles = await box(pg, ".save"), pg.locator(".tiles .tile")
    t1, t2 = await tiles.nth(0).bounding_box(), await tiles.nth(1).bounding_box()
    check(f"{label} 1536: risparmio, entrate e uscite in una riga", abs(save["y"] - t1["y"]) <= 1 and abs(t1["y"] - t2["y"]) <= 1 and save["x"] < t1["x"] < t2["x"], f"{save} {t1} {t2}")
    check(f"{label} 1536: due colonne", await pg.locator(".acols > .acol").count() == 2)
    await vai(pg, 1920, "analisi")
    cols = pg.locator(".acols > .acol")
    check(f"{label} 1920: tre colonne", await cols.count() == 3)
    check(f"{label} 1920: categorie a sinistra, andamento al centro, budget a destra",
          await cols.nth(0).get_by_role("heading", name="Uscite per categoria").count() == 1
          and await cols.nth(1).get_by_role("heading", name="Andamento ultimi 12 mesi").count() == 1
          and await cols.nth(2).get_by_role("heading", name="Budget del mese").count() == 1)
    gaps = await pg.evaluate("""() => [...document.querySelectorAll('.acol')].flatMap(c => { const k = [...c.children].map(e => e.getBoundingClientRect()); return k.slice(1).map((r, i) => Math.round(r.top - k[i].bottom)) })""")
    check(f"{label} 1920: schede distanziate di 16 px", all(g == 16 for g in gaps), str(gaps))
    check(f"{label} 1920: niente scorrimento orizzontale", await no_hscroll(pg))

async def cerca(pg, label):
    await vai(pg, 1280, "cerca")
    check(f"{label} 1280: filtri sempre aperti a sinistra, senza pulsante «Filtri»",
          await visible(pg, ".filters-col") and await pg.locator(".filters-col").get_by_label("Categoria").count() == 1
          and await pg.get_by_role("button", name=re.compile("^Filtri")).count() == 0)
    check(f"{label} 1280: senza ricerca, gli ultimi movimenti", await pg.get_by_role("heading", name="Ultimi movimenti").count() == 1 and await pg.locator(".results-col .list-row").count() >= 20)
    check(f"{label} 1280: righe come sul telefono", await pg.locator(".results-col .row-cols").count() == 0)
    await pg.get_by_role("searchbox", name="Cerca").fill("spesa"); await pg.wait_for_timeout(400)
    n = await pg.locator(".summary").first.inner_text()
    check(f"{label} 1280: cercando, il numero dei risultati", "movimenti" in n and await pg.get_by_role("heading", name="Ultimi movimenti").count() == 0, n)
    await pg.get_by_role("searchbox", name="Cerca").fill("")
    await vai(pg, 1536, "cerca")
    head = await pg.evaluate("[...document.querySelectorAll('.results-col .cols-head span')].map(s => s.textContent.trim())")
    check(f"{label} 1536: tabella con la data in colonna", head == ["Data", "", "Descrizione", "Categoria", "Conto o carta", "Importo"], str(head))
    al = await pg.evaluate("""() => { const h = [...document.querySelectorAll('.results-col .cols-head span')].map(s => Math.round(s.getBoundingClientRect().x));
      return [...document.querySelectorAll('.results-col .list-row.with-date')].slice(0, 8).every(r => { const c = r.querySelectorAll(':scope > .cell'); return c.length === 3 && [0, 3, 4].every((k, i) => Math.abs(c[i].getBoundingClientRect().x - h[k]) <= 1) }) }""")
    check(f"{label} 1536: data, categoria e conto allineati alle intestazioni", al)
    check(f"{label} 1536: senza ricerca niente riepilogo", await pg.locator(".summary-col").count() == 0)
    await vai(pg, 1920, "cerca")
    await pg.get_by_role("searchbox", name="Cerca").fill("spesa"); await pg.wait_for_timeout(500)
    sc = pg.locator(".summary-col")
    check(f"{label} 1920: cercando, riepilogo per categoria e per mese",
          await sc.get_by_role("heading", name="Uscite per categoria").count() == 1 and await sc.get_by_role("heading", name="Per mese").count() == 1
          and await sc.locator(".months li").count() >= 3)
    first = (await sc.locator(".months .m-name").first.inner_text()).lower()
    check(f"{label} 1920: mesi dal più recente", first.startswith("novembre"), first)
    await sc.locator(".bars .row").first.click(); await pg.wait_for_timeout(200)
    await sc.get_by_role("button", name=re.compile("Vedi i movimenti")).click(); await pg.wait_for_timeout(400)
    v = await pg.locator(".filters-col").get_by_label("Categoria").input_value()
    check(f"{label} 1920: una categoria del riepilogo restringe la ricerca", v != "" and await pg.locator(".filters-title").first.inner_text() == "Filtri (1)", v)
    await pg.get_by_role("button", name="Azzera ricerca").click(); await pg.wait_for_timeout(300)
    check(f"{label} 1920: niente scorrimento orizzontale", await no_hscroll(pg))

async def pochi(b):
    """Pochi dati: senza budget «Dove vanno i soldi» a destra; da molto larga la colonna di destra non c'è."""
    label = "PC pochi dati"
    print(f"\n===== {label} =====")
    ctx = await b.new_context(viewport={"width": 1280, "height": 900}, locale="it-IT", timezone_id="Europe/Rome")
    pg = await ctx.new_page(); await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 14, 10, 0))
    await prepara(pg, pieno=False)
    await vai(pg, 1280, "movimenti")
    aside = pg.locator("#mov-aside")
    check(f"{label} 1280: senza budget a destra «Dove vanno i soldi», coi tasti in fondo",
          await aside.get_by_role("heading", name="Dove vanno i soldi").count() == 1 and await visible(pg, "#mov-aside .keys-hint"))
    names = await aside.locator(".bars .name").all_inner_texts()
    check(f"{label} 1280: la categoria della spesa", names == ["Pasti fuori"], str(names))
    await aside.locator(".bars .row").first.click(); await pg.wait_for_timeout(200)
    await aside.get_by_role("button", name=re.compile("Vedi i movimenti")).click(); await pg.wait_for_timeout(700)
    check(f"{label}: «Vedi i movimenti» apre Cerca con la categoria del mese", "#/cerca" in pg.url and "Pizza" in await pg.locator(".screen").inner_text())
    await vai(pg, 1920, "movimenti")
    check(f"{label} 1920: colonna di destra assente, separatore compreso", not await visible(pg, "#mov-aside") and not await visible(pg, ".splitter"))
    cal, body = await box(pg, ".cal-col"), await box(pg, ".layout .body")
    c = await box(pg, ".screen")
    check(f"{label} 1920: l'elenco prende lo spazio fino al bordo", abs((body["x"] + body["width"]) - (c["x"] + c["width"])) <= 1, f"{body} {c}")
    check(f"{label} 1920: tasti in fondo alla colonna sinistra", await visible(pg, ".cal-col .keys-hint"))
    check(f"{label} 1920: niente scorrimento orizzontale", await no_hscroll(pg))
    await ctx.close()

async def telefono(b, p):
    label = "Android"
    print(f"\n===== {label} =====")
    ctx = await b.new_context(**p.devices["Pixel 7"], locale="it-IT", timezone_id="Europe/Rome")
    pg = await ctx.new_page(); await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 14, 10, 0))
    await prepara(pg)
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(700)
    check(f"{label}: nessuna classe di larghezza", await classes(pg) == [], str(await classes(pg)))
    check(f"{label}: Movimenti come prima (cerchi, righe su due livelli, niente colonna sinistra)",
          await pg.locator(".quick .circle").count() == 3 and await pg.locator(".row-cols").count() == 0 and await pg.locator(".cal-col").count() == 0
          and await pg.get_by_role("heading", name="Dove vanno i soldi").count() == 0)
    check(f"{label}: niente scorrimento orizzontale", await no_hscroll(pg))
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
    check(f"{label}: Conti come prima (obiettivi sotto l'elenco, niente dettaglio accanto)",
          await pg.get_by_role("heading", name=re.compile("Obiettivi di risparmio")).count() == 1 and await pg.locator(".extra-col, .detail-col").count() == 0)
    await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(600)
    check(f"{label}: Analisi in una colonna", await pg.locator(".acols").count() == 0)
    await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(600)
    check(f"{label}: Cerca come prima (pulsante «Filtri», niente risultati senza ricerca)",
          await pg.get_by_role("button", name=re.compile("^Filtri")).count() == 1 and await pg.locator(".filters-col").count() == 0
          and await pg.get_by_text("Scrivi qualcosa o usa i filtri").count() == 1)
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for label, scheme in [("PC", "light"), ("PC scuro", "dark")]:
            print(f"\n===== {label} =====")
            ctx = await b.new_context(viewport={"width": 1280, "height": 900}, locale="it-IT", color_scheme=scheme, timezone_id="Europe/Rome")
            pg = await ctx.new_page(); errs = []
            await pg.clock.set_fixed_time(datetime.datetime(2026, 11, 14, 10, 0))
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await prepara(pg)
            if scheme == "light":
                await basi(pg, label)
            await movimenti(pg, label)
            await conti(pg, label)
            await analisi(pg, label)
            await cerca(pg, label)
            check(f"{label}: nessun errore", not errs, str(errs[:3]))
            await ctx.close()
        await pochi(b)
        await telefono(b, p)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} superati")

asyncio.run(main())
