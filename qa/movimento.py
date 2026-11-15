"""Collaudo v0.30: movimento di pannelli, finestre e schermate (dati di esempio).

Su Android (pannello dal basso) e PC (finestra centrata): durate e curve uguali ai token, uscita in
--ease-exit con la <dialog> ancora aperta finché non finisce, apertura e chiusura da tastiera, Esc e
«Chiudi», focus che resta nel pannello e torna al pulsante, riapertura durante l'uscita, schermata di
blocco sopra un pannello che si sta chiudendo. Sul telefono il pannello sale senza scatti: la
posizione, fotogramma per fotogramma, scende sempre e la finestra non scorre (v0.30.1).
Cambio di schermata (v0.30.1) con un anno di movimenti e processore rallentato: la nuova schermata compare
intera (nessun importo che cambia e nessun riquadro che si sposta dopo la comparsa), in dissolvenza tra le
sezioni, con spostamento verso il dettaglio conto e al ritorno. Avvisi e tastierino (v0.30.2): l'avviso a comparsa entra salendo (--duration-base, --ease-standard) ed esce
in dissolvenza (--ease-exit); «Annulla» lo sostituisce senza sovrapporne due; il tastierino nel pannello si apre in
altezza e si chiude con «Fatto» con --ease-exit, quello in fondo a Cerca sale dal basso e resta fermo passando
da un importo all'altro.
Righe e barre (v0.30.3): un movimento salvato apre la sua riga (o il suo giorno) in altezza, uno eliminato la chiude
con --ease-exit e «Annulla» la riapre (dato ripristinato); cambiando mese nessuna riga si anima; la barra del
budget scorre al nuovo valore in --duration-slow. Poi le stesse prove con «riduci animazioni».
"""
import asyncio, re, json
from playwright.async_api import async_playwright
BASE = "http://localhost:4173"
PIN = "274913"
results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

ANIMS = """() => document.getAnimations().map(a => ({
  name: a.animationName || '', pseudo: a.effect.pseudoElement || '',
  target: a.effect.target ? (a.effect.target.className || a.effect.target.tagName).toString() : '',
  dur: a.effect.getTiming().duration, easing: (a.effect.getKeyframes()[0] || {}).easing || '' }))"""
# I token arrivano minimizzati dalla build (".28s", "cubic-bezier(.2, 0, 0, 1)"): si confrontano i numeri
TOKENS = """() => { const s = getComputedStyle(document.documentElement); const g = (n) => s.getPropertyValue(n).trim();
  const ms = (v) => parseFloat(v) * (/ms$/.test(v) ? 1 : 1000);
  return { slow: ms(g('--duration-slow')), base: ms(g('--duration-base')), std: g('--ease-standard'), exit: g('--ease-exit') } }"""
SHEETS = "() => [...document.querySelectorAll('dialog:not(.lock)')].map(d => ({ open: d.open, leaving: d.hasAttribute('data-leaving') }))"
FOCUS = "() => { const a = document.activeElement; return { inDialog: !!a?.closest('dialog[open]:not(.lock)'), tag: a?.tagName, label: a?.getAttribute('aria-label') || a?.textContent?.trim().slice(0, 30) } }"
RISE = """() => new Promise(res => { const out = []; let t0 = null;
  function f() { const d = document.querySelector('dialog[open]:not(.lock)');
    if (d) { if (t0 === null) t0 = performance.now(); const p = d.querySelector('.panel');
      out.push([Math.round(performance.now() - t0), Math.round(p.getBoundingClientRect().top), d.scrollTop, Math.round(document.scrollingElement.scrollTop) === Math.round(window.__sy ?? document.scrollingElement.scrollTop) ? 0 : 1]) }
    if (t0 === null || performance.now() - t0 < 700) requestAnimationFrame(f); else res(out) }
  window.__sy = document.scrollingElement.scrollTop; requestAnimationFrame(f) })"""
norm = lambda s: [float(x) for x in re.findall(r"-?\d*\.?\d+", s)]

async def hide_show(pg):
    await pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true}); document.dispatchEvent(new Event('visibilitychange'))")
    await pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'visible',configurable:true}); document.dispatchEvent(new Event('visibilitychange'))")

async def new_button(pg):
    return pg.get_by_role("button", name="Nuovo movimento").locator("visible=true").first

async def setup(pg):
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill("Conto di prova"); await pg.get_by_label("Tipo").select_option("conto_corrente")
    await pg.get_by_label("Saldo iniziale (€)").fill("1000")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(500)
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)

async def open_with_keyboard(pg):
    btn = await new_button(pg)
    await btn.focus(); await pg.keyboard.press("Enter")
    await pg.wait_for_selector("dialog[open]:not(.lock)")

async def run(b, p, label, opts, phone):
    print(f"\n===== {label} =====")
    ctx = await b.new_context(**opts, locale="it-IT"); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    cdp = await ctx.new_cdp_session(pg); await cdp.send("Animation.enable")
    slow = lambda r: cdp.send("Animation.setPlaybackRate", {"playbackRate": r})
    await setup(pg)
    tok = await pg.evaluate(TOKENS)
    entry, leave_ = ("sheet-in", "sheet-out") if phone else ("window-in", "window-out")

    # sul telefono: il pannello sale in modo continuo, senza che la finestra scorra (era il «rimbalzo»)
    if phone:
        for name, opener in [("Conto", lambda: pg.get_by_role("button", name="Conto").first.tap()), ("Nuovo movimento", None)]:
            if opener:
                await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(600)
            else:
                await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(600)
            prom = pg.evaluate(RISE)
            await (opener() if opener else (await new_button(pg)).tap())
            fr = await prom
            tops = [f[1] for f in fr]
            mono = all(b2 <= a2 + 1 for a2, b2 in zip(tops, tops[1:]))
            moving = [f[0] for f, nx in zip(fr, fr[1:]) if nx[1] < f[1] - 1]
            span = (moving[-1] - moving[0]) if len(moving) > 1 else 0
            check(f"{label}: «{name}»: il pannello sale senza tornare indietro e la finestra non scorre", mono and all(f[2] == 0 and f[3] == 0 for f in fr), json.dumps(fr[:12]))
            check(f"{label}: «{name}»: la salita dura quasi tutto --duration-slow", span >= tok["slow"] * 0.7, f"{span} ms su {tok['slow']}")
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
        await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(500)

    # entrata, rallentata 10 volte per poterla osservare
    await slow(0.1)
    await open_with_keyboard(pg)
    an = await pg.evaluate(ANIMS)
    panel = next((a for a in an if entry in a["name"]), None)
    back = next((a for a in an if a["pseudo"] == "::backdrop"), None)
    check(f"{label}: {'il pannello sale dal basso' if phone else 'la finestra compare'} con --duration-slow e --ease-standard",
          bool(panel) and panel["dur"] == tok["slow"] and norm(panel["easing"]) == norm(tok["std"]), json.dumps(an))
    check(f"{label}: lo sfondo scurito compare insieme", bool(back) and back["dur"] == tok["slow"], json.dumps(an))
    await slow(1); await pg.wait_for_timeout(400)
    f = await pg.evaluate(FOCUS)
    check(f"{label}: aperto da tastiera, il focus è nel pannello", f["inDialog"], json.dumps(f))
    outside = []
    for _ in range(14):
        await pg.keyboard.press("Tab")
        f = await pg.evaluate(FOCUS)
        if not f["inDialog"] and f["tag"] not in ("BODY", None): outside.append(f)
    check(f"{label}: Tab non esce dal pannello", not outside, json.dumps(outside[:3]))
    vis = await pg.evaluate("() => { const r = document.querySelector('dialog[open] .panel').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight + 1 && getComputedStyle(document.querySelector('dialog[open] .panel')).opacity === '1' }")
    check(f"{label}: a fine entrata il pannello è tutto visibile", vis)

    # uscita con Esc, rallentata: la <dialog> resta aperta (e modale) finché l'animazione non finisce
    await slow(0.1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(60)
    st = await pg.evaluate(SHEETS); an = await pg.evaluate(ANIMS)
    out = next((a for a in an if leave_ in a["name"]), None)
    check(f"{label}: Esc avvia l'uscita con la finestra ancora aperta", st == [{"open": True, "leaving": True}], json.dumps(st))
    check(f"{label}: uscita con --duration-base e --ease-exit", bool(out) and out["dur"] == tok["base"] and norm(out["easing"]) == norm(tok["exit"]), json.dumps(an))
    check(f"{label}: durante l'uscita il pannello non riceve tocchi", await pg.evaluate("() => document.querySelector('dialog[data-leaving]').inert"))
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(60)
    await slow(1); await pg.wait_for_timeout(500)
    st = await pg.evaluate(SHEETS)
    check(f"{label}: a fine uscita il pannello è chiuso e tolto (anche con un secondo Esc)", st == [], json.dumps(st))
    f = await pg.evaluate("() => document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent?.trim()")
    check(f"{label}: il focus torna su «Nuovo movimento»", f == "Nuovo movimento", str(f))
    check(f"{label}: l'indirizzo torna a Movimenti", (await pg.evaluate("location.hash")) == "#/movimenti")

    # chiusura con «Chiudi» da tastiera
    await open_with_keyboard(pg); await pg.wait_for_timeout(400)
    await pg.locator("dialog[open]").get_by_role("button", name="Chiudi", exact=True).focus(); await pg.keyboard.press("Enter")
    await pg.wait_for_timeout(500)
    check(f"{label}: «Chiudi» da tastiera chiude", await pg.evaluate(SHEETS) == [])

    # tocco sullo sfondo
    await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await pg.mouse.click(5, 5); await pg.wait_for_timeout(500)
    check(f"{label}: il tocco sullo sfondo chiude", await pg.evaluate(SHEETS) == [])

    # riapertura durante l'uscita: il pannello torna visibile e usabile
    await open_with_keyboard(pg); await pg.wait_for_timeout(400)
    await slow(0.1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(50)
    await pg.evaluate("location.hash = '/movimenti/nuovo'")
    await slow(1); await pg.wait_for_timeout(600)
    st = await pg.evaluate(SHEETS)
    ok = await pg.evaluate("() => { const d = document.querySelector('dialog[open]:not(.lock)'); if (!d) return false; const p = d.querySelector('.panel'); const r = p.getBoundingClientRect(); return !d.inert && getComputedStyle(p).opacity === '1' && r.bottom <= innerHeight + 1 && r.top >= 0 }")
    check(f"{label}: riaperto durante l'uscita, il pannello è visibile e attivo", ok and st == [{"open": True, "leaving": False}], json.dumps(st))
    await pg.get_by_label("Importo (€)").fill("4,20")
    check(f"{label}: e si può scrivere", await pg.get_by_label("Importo (€)").input_value() == "4,20")
    await slow(0.1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(60)
    an = await pg.evaluate(ANIMS)
    check(f"{label}: richiuso, esce di nuovo con l'animazione", any(leave_ in a["name"] for a in an) and await pg.locator("dialog[data-leaving]").count() == 1, json.dumps(an))
    await slow(1); await pg.wait_for_timeout(500)

    # blocco che arriva mentre un pannello si chiude: resta sopra tutto
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(400)
    await pg.get_by_role("button", name="Attiva il blocco").click()
    await pg.get_by_label("PIN (da 4 a 8 cifre)").fill(PIN); await pg.get_by_label("Ripeti il PIN").fill(PIN)
    await pg.get_by_role("button", name="Attiva", exact=True).click(); await pg.wait_for_timeout(1500)
    await pg.locator("select").filter(has=pg.locator("option", has_text="subito")).select_option("0"); await pg.wait_for_timeout(200)
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)
    await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await slow(0.1)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(40)
    await hide_show(pg); await pg.wait_for_timeout(150)
    top = await pg.evaluate("() => { const el = document.elementFromPoint(innerWidth / 2, innerHeight - 60); return !!el?.closest('dialog.lock') }")
    check(f"{label}: il blocco copre il pannello che si sta chiudendo", top and await pg.locator("dialog.lock[open]").count() == 1)
    await slow(1); await pg.wait_for_timeout(500)
    check(f"{label}: chiuso il pannello, il blocco resta aperto col focus sul PIN",
          await pg.locator("dialog.lock[open]").count() == 1 and await pg.evaluate(SHEETS) == []
          and await pg.evaluate("() => !!document.activeElement?.closest('dialog.lock')"))
    await pg.get_by_label("PIN").fill(PIN); await pg.wait_for_timeout(1500)
    await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    check(f"{label}: dopo lo sblocco i pannelli si aprono come prima", await pg.evaluate(SHEETS) == [{"open": True, "leaving": False}])
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
    check(f"{label}: nessun errore (CSP compresa)", not errs, " | ".join(errs[:3]))
    await ctx.close()

async def run_reduced(b, p, label, opts):
    print(f"\n===== {label}, riduci animazioni =====")
    ctx = await b.new_context(**opts, locale="it-IT", reduced_motion="reduce"); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    await setup(pg)
    await open_with_keyboard(pg)
    d = await pg.evaluate("() => [getComputedStyle(document.querySelector('dialog[open] .panel')).animationDuration, getComputedStyle(document.querySelector('dialog[open]'), '::backdrop').animationDuration]")
    check(f"{label}: entrata di pannello e sfondo ridotta a 0,01 ms", all(float(x.rstrip('ms')) <= 0.00001 for x in d), json.dumps(d))
    await pg.wait_for_timeout(50)
    pos = await pg.evaluate("() => { const p = document.querySelector('dialog[open] .panel'); return [getComputedStyle(p).transform, getComputedStyle(p).opacity] }")
    check(f"{label}: il pannello è subito al suo posto", pos[0] in ("none", "matrix(1, 0, 0, 1, 0, 0)") and pos[1] == "1", json.dumps(pos))
    check(f"{label}: aperto da tastiera, focus nel pannello", (await pg.evaluate(FOCUS))["inDialog"])
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(40)
    check(f"{label}: Esc chiude subito, senza attendere l'uscita", await pg.evaluate(SHEETS) == [], json.dumps(await pg.evaluate(SHEETS)))
    f = await pg.evaluate("() => document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent?.trim()")
    check(f"{label}: il focus torna su «Nuovo movimento»", f == "Nuovo movimento", str(f))
    check(f"{label}: nessun errore", not errs, " | ".join(errs[:3]))
    await ctx.close()

async def run_notices(b, p, label, opts, phone, reduced=False):
    print(f"\n===== {label}: avvisi e tastierino{', riduci animazioni' if reduced else ''} =====")
    ctx = await b.new_context(**opts, locale="it-IT", **({"reduced_motion": "reduce"} if reduced else {})); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    cdp = await ctx.new_cdp_session(pg); await cdp.send("Animation.enable")
    slow = lambda r: cdp.send("Animation.setPlaybackRate", {"playbackRate": r})
    await setup(pg)
    tok = await pg.evaluate(TOKENS)
    toasts = pg.locator(".toast[role=status]")
    # preferito di esempio, per avere un avviso con «Annulla»
    await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(500)
    await pg.get_by_label("Importo (€)").fill("1,20"); await pg.get_by_label("Descrizione").fill("Caffè")
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Pasti fuori")).click()
    await pg.get_by_label("Salva anche tra i preferiti").check()
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(800)
    chip = pg.locator("section.fav .chip:not(.manage)").first
    if not reduced:
        await slow(0.1)
        await chip.click(); await toasts.first.wait_for()
        an = await pg.evaluate(ANIMS)
        a = next((x for x in an if "toast-in" in x["name"]), None)
        check(f"{label}: l'avviso entra con --duration-base e --ease-standard", bool(a) and a["dur"] == tok["base"] and norm(a["easing"]) == norm(tok["std"]), json.dumps(an))
        await slow(1); await pg.wait_for_timeout(300)
        await toasts.get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(120)
        n = await pg.evaluate("() => [...document.querySelectorAll('.toast[role=status]')].map(t => [t.hasAttribute('data-leaving'), t.textContent.trim()])")
        check(f"{label}: «Annulla» sostituisce l'avviso senza sovrapporne due", len(n) == 1 and not n[0][0] and "annullata" in n[0][1], json.dumps(n))
        # uscita da sola dopo 6 secondi, rallentata per osservarla
        await pg.wait_for_timeout(5700); await slow(0.1); await pg.wait_for_timeout(400)
        an = await pg.evaluate(ANIMS)
        a = next((x for x in an if "fade-out" in x["name"] and "toast" in x["target"]), None)
        check(f"{label}: l'avviso esce in dissolvenza con --ease-exit", bool(a) and a["dur"] == tok["base"] and norm(a["easing"]) == norm(tok["exit"]) and await pg.locator(".toast[data-leaving]").count() == 1, json.dumps(an))
        await slow(1); await pg.wait_for_timeout(500)
        check(f"{label}: poi l'avviso è tolto", await toasts.count() == 0)
    else:
        await chip.click(); await toasts.first.wait_for()
        d = await pg.evaluate("() => getComputedStyle(document.querySelector('.toast')).animationDuration")
        check(f"{label}: avviso senza animazione", float(d.rstrip('ms')) <= 0.00001, d)
        await toasts.get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(60)
        check(f"{label}: «Annulla» lo sostituisce subito", await toasts.count() == 1)
    if phone:
        # tastierino nel pannello: si apre in altezza, «Fatto» lo chiude con --ease-exit
        await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(400)
        if not reduced: await slow(0.1)
        await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]")
        await pg.wait_for_selector("dialog .slot.grow"); await pg.wait_for_timeout(100)
        an = await pg.evaluate(ANIMS)
        a = next((x for x in an if "grow-in" in x["name"]), None)
        if not reduced:
            check(f"{label}: il tastierino nel pannello si apre in altezza (--duration-base)", bool(a) and a["dur"] == tok["base"], json.dumps(an))
            await slow(1); await pg.wait_for_timeout(700)
            await slow(0.1)
        else:
            check(f"{label}: tastierino nel pannello senza animazione", float((await pg.evaluate("() => getComputedStyle(document.querySelector('dialog .slot')).animationDuration")).rstrip('ms')) <= 0.00001)
        await pg.locator("dialog .keypad").get_by_role("button", name="Fatto").click(); await pg.wait_for_timeout(80)
        if not reduced:
            an = await pg.evaluate(ANIMS)
            a = next((x for x in an if "grow-out" in x["name"]), None)
            check(f"{label}: «Fatto» lo chiude con --ease-exit", bool(a) and norm(a["easing"]) == norm(tok["exit"]), json.dumps(an))
            await slow(1)
        await pg.wait_for_timeout(400)
        check(f"{label}: poi il tastierino è tolto", await pg.locator("dialog .keypad").count() == 0)
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
        # in fondo a Cerca: sale dal basso e resta fermo tra «Importo da» e «Importo a»
        await pg.goto(BASE + "/#/cerca"); await pg.wait_for_timeout(500)
        await pg.get_by_role("button", name=re.compile("^Filtri")).click(); await pg.wait_for_timeout(200)
        await pg.get_by_label("Importo da (€)").click(); await pg.wait_for_timeout(60)
        an = await pg.evaluate(ANIMS)
        if not reduced:
            check(f"{label}: in Cerca il tastierino sale dal basso", any("keypad-up" in x["name"] for x in an), json.dumps(an))
        await pg.wait_for_timeout(500)
        await pg.evaluate("() => document.querySelector('.keypad.floating').dataset.prova = '1'")
        await pg.get_by_label("Importo a (€)").click(); await pg.wait_for_timeout(60)
        an = await pg.evaluate(ANIMS)
        same = await pg.evaluate("() => document.querySelectorAll('.keypad.floating').length === 1 && document.querySelector('.keypad.floating').dataset.prova === '1'")
        check(f"{label}: passando a «Importo a» resta fermo", same and not any("keypad" in x["name"] for x in an), json.dumps(an))
        await pg.locator(".keypad.floating").get_by_role("button", name="Fatto").click(); await pg.wait_for_timeout(500)
        check(f"{label}: «Fatto» lo toglie", await pg.locator(".keypad.floating").count() == 0)
    check(f"{label}: nessun errore", not errs, " | ".join(errs[:3]))
    await ctx.close()

async def run_rows(b, p, label, opts, reduced=False):
    import datetime
    print(f"\n===== {label}: righe e barre{', riduci animazioni' if reduced else ''} =====")
    ctx = await b.new_context(**opts, locale="it-IT", **({"reduced_motion": "reduce"} if reduced else {})); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    cdp = await ctx.new_cdp_session(pg); await cdp.send("Animation.enable")
    slow = lambda r: cdp.send("Animation.setPlaybackRate", {"playbackRate": r})
    await setup(pg)
    tok = await pg.evaluate(TOKENS)
    today = datetime.date.today(); other = today.replace(day=1 if today.day != 1 else 2)
    async def save(amount, desc, day=None, watch=False):
        await (await new_button(pg)).click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(500)
        await pg.get_by_label("Importo (€)").fill(amount); await pg.get_by_label("Descrizione").fill(desc)
        await pg.locator(".cat-list").get_by_role("radio", name=re.compile("^Spesa alimentare")).click()
        if day: await pg.locator("dialog input[type=date]").fill(day.isoformat())
        if watch and not reduced: await slow(0.1)
        await pg.get_by_role("button", name="Salva", exact=True).click()
        await pg.wait_for_timeout(150 if watch else 700)
    FOLD = """() => ({ entering: [...document.querySelectorAll('.fold[data-entering]')].map(e => e.className.split(' ').filter(c => c !== 'fold' && !c.startsWith('svelte'))[0] || e.tagName),
      leaving: document.querySelectorAll('.fold[data-leaving]').length,
      anims: document.getAnimations().filter(a => /grow-(in|out)/.test(a.animationName || '') && a.effect.target.closest('.screen')).map(a => ({ name: a.animationName, dur: a.effect.getTiming().duration, easing: (a.effect.getKeyframes()[0] || {}).easing })) })"""
    await save("10,00", "Pane")  # il primo del mese crea l'elenco: nessuna animazione di riga
    await save("12,50", "Latte", watch=True)
    f = await pg.evaluate(FOLD)
    if not reduced:
        check(f"{label}: movimento salvato: la sua riga si apre (--duration-base)", f["entering"] == ["LI"] and any(a["dur"] == tok["base"] and norm(a["easing"]) == norm(tok["std"]) for a in f["anims"]), json.dumps(f))
        await slow(1); await pg.wait_for_timeout(500)
    else:
        await pg.wait_for_timeout(500)
    check(f"{label}: a fine animazione la riga è normale", (await pg.evaluate(FOLD))["entering"] == [] and await pg.locator(".screen li.fold").count() == 2)
    await save("3,00", "Giornale", day=other, watch=True)
    f = await pg.evaluate(FOLD)
    if not reduced:
        check(f"{label}: movimento in un giorno nuovo: si apre il giorno intero", f["entering"] == ["day-group"], json.dumps(f))
        await slow(1)
    await pg.wait_for_timeout(500)
    # una descrizione lunga va coi puntini: la riga non si allarga oltre la scheda
    await save("2,00", "Descrizione molto lunga di prova per controllare i puntini in fondo alla riga")
    wide = await pg.evaluate("() => [...document.querySelectorAll('.screen li.fold')].filter(li => li.getBoundingClientRect().width > li.closest('ul').getBoundingClientRect().width + 1).length")
    check(f"{label}: una descrizione lunga non allarga la riga", wide == 0, str(wide))
    # cambio mese: nessuna riga si anima
    await pg.get_by_role("button", name="Mese precedente").click(); await pg.wait_for_timeout(500)
    await pg.evaluate("() => { window.__grow = 0; document.addEventListener('animationstart', e => { if (/grow/.test(e.animationName)) window.__grow++ }) }")
    await pg.get_by_role("button", name="Mese successivo").click(); await pg.wait_for_timeout(600)
    check(f"{label}: tornando al mese nessuna riga si anima", await pg.evaluate("window.__grow") == 0 and await pg.locator(".screen li.fold").count() == 4)
    # eliminazione con «Annulla»
    await pg.locator(".screen .list-row", has_text="Latte").click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(500)
    await pg.get_by_role("button", name="Elimina", exact=True).click()
    if not reduced: await slow(0.1)
    await pg.get_by_role("button", name="Conferma eliminazione").click(); await pg.wait_for_timeout(150)
    f = await pg.evaluate(FOLD)
    if not reduced:
        check(f"{label}: movimento eliminato: la riga si chiude con --ease-exit", f["leaving"] == 1 and any("grow-out" in a["name"] and norm(a["easing"]) == norm(tok["exit"]) for a in f["anims"]), json.dumps(f))
        await slow(1)
    await pg.wait_for_timeout(500)
    check(f"{label}: poi la riga è tolta e c'è «Annulla»", await pg.locator(".screen .list-row", has_text="Latte").count() == 0 and await pg.locator(".toast", has_text="Movimento eliminato").count() == 1)
    if not reduced: await slow(0.1)
    await pg.locator(".toast").get_by_role("button", name="Annulla").click(); await pg.wait_for_timeout(150)
    f = await pg.evaluate(FOLD)
    if not reduced:
        check(f"{label}: «Annulla» riapre la riga", f["entering"] == ["LI"], json.dumps(f))
        await slow(1)
    await pg.wait_for_timeout(500)
    alive = await pg.evaluate("""() => new Promise(res => { const q = indexedDB.open('statera-locale'); q.onsuccess = () => {
      const r = q.result.transaction('transactions').objectStore('transactions').getAll();
      r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null).map(t => t.description)) } } })""")
    check(f"{label}: «Annulla» ripristina il movimento", "Latte" in alive and len(alive) == 4 and await pg.locator(".screen .list-row", has_text="Latte").count() == 1, json.dumps(alive))
    # barra del budget: scorre al nuovo valore
    await pg.goto(BASE + "/#/analisi"); await pg.wait_for_timeout(600)
    await pg.get_by_role("button", name="Imposta budget").click(); await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await pg.get_by_label("Budget Spesa alimentare (€)").fill("100")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(800)
    w1 = await pg.evaluate("() => document.querySelector('.meters .fill').getBoundingClientRect().width")
    await pg.get_by_role("button", name="Modifica", exact=True).first.click()
    await pg.wait_for_selector("dialog[open]"); await pg.wait_for_timeout(400)
    await pg.get_by_label("Budget Spesa alimentare (€)").fill("50")
    if not reduced: await slow(0.1)
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(250)
    tr = await pg.evaluate("() => document.getAnimations().filter(a => a.transitionProperty === 'width' && a.effect.target.classList.contains('fill')).map(a => ({ dur: a.effect.getTiming().duration }))")
    if not reduced:
        check(f"{label}: la barra del budget scorre al nuovo valore (--duration-slow)", len(tr) == 1 and tr[0]["dur"] == tok["slow"], json.dumps(tr))
        await slow(1)
    else:
        check(f"{label}: barra senza animazione", all(t["dur"] <= 0.01 for t in tr), json.dumps(tr))
    await pg.wait_for_timeout(800)
    w2 = await pg.evaluate("() => document.querySelector('.meters .fill').getBoundingClientRect().width")
    check(f"{label}: e arriva al nuovo valore", w2 > w1 * 1.5, f"{w1} → {w2}")
    check(f"{label}: nessun errore", not errs, " | ".join(errs[:3]))
    await ctx.close()

# Per ogni fotogramma dopo il tocco: schermata visibile?, importo del riquadro principale, sua posizione
FRAMES = """() => { const r = window.__fr = []; const t0 = performance.now();
  const f = () => { const sc = document.querySelector('.screen'); const box = sc?.querySelector('.balance-box');
    r.push({ t: Math.round(performance.now() - t0), state: sc?.dataset.reveal, h1: sc?.querySelector('h1, h2')?.textContent.trim(),
      amount: box?.textContent.replace(/\\s+/g, ' ').trim() ?? '', y: box ? Math.round(box.getBoundingClientRect().top) : null });
    if (performance.now() - t0 < 1500) requestAnimationFrame(f) }; requestAnimationFrame(f) }"""

async def run_screens(b, p, label, opts, reduced=False):
    print(f"\n===== {label}: cambio di schermata{', riduci animazioni' if reduced else ''} =====")
    ctx = await b.new_context(**opts, locale="it-IT", **({"reduced_motion": "reduce"} if reduced else {})); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(500)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill("Conto"); await pg.get_by_label("Saldo iniziale (€)").fill("3000")
    await pg.locator("dialog input[type=date]").fill("2025-12-01")
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(500)
    await pg.evaluate(open(__import__("os").path.join(__import__("os").path.dirname(__file__), "anno-di-esempio.js")).read())
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(1500)
    cdp = await ctx.new_cdp_session(pg); await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 6})
    async def go(do, name, kind):
        await pg.evaluate(FRAMES); await do(); await pg.wait_for_timeout(1600)
        fr = await pg.evaluate("window.__fr")
        vis = [f for f in fr if f["state"] not in ("wait", None)]
        an = await pg.evaluate("() => [...document.querySelectorAll('.screen > *')].map(e => getComputedStyle(e).animationName)")
        final = fr[-1]
        steady = [f for f in vis if f["h1"] == final["h1"]]
        same = all(f["amount"] == final["amount"] and f["y"] == final["y"] for f in steady)
        check(f"{label}: {name}: compare intera (importo e posizione non cambiano dopo la comparsa)", bool(steady) and same,
              json.dumps([(f["t"], f["state"], f["amount"][:30], f["y"]) for f in fr if f in steady][:6]))
        if not reduced:
            check(f"{label}: {name}: animazione {kind}", all(kind in a for a in an), json.dumps(an))
        return fr
    nav = lambda t: (lambda: pg.locator("nav").get_by_role("link", name=t, exact=True).locator("visible=true").first.click())
    for tab in ["Conti", "Analisi", "Altro", "Movimenti"]:
        await go(nav(tab), f"scheda {tab}", "screen-fade")
    await nav("Conti")(); await pg.wait_for_timeout(1500)
    await go(lambda: pg.locator(".screen a.list-row[href^='#/conto/']").first.click(), "dettaglio conto", "screen-forward")
    await go(lambda: pg.get_by_role("link", name="Torna a Conti").first.click(), "ritorno a Conti", "screen-back")
    # il modulo aperto sopra Movimenti non rifà comparire la schermata
    await nav("Movimenti")(); await pg.wait_for_timeout(1500)
    await pg.evaluate(FRAMES); await (await new_button(pg)).click(); await pg.wait_for_timeout(800)
    fr = await pg.evaluate("window.__fr")
    check(f"{label}: aprire il modulo non nasconde Movimenti", all(f["state"] != "wait" for f in fr))
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(600)
    if reduced:
        d = await pg.evaluate("() => [...document.querySelectorAll('.screen > *')].map(e => getComputedStyle(e).animationDuration)")
        check(f"{label}: comparsa delle schermate ridotta a 0,01 ms", all(float(x.rstrip('ms')) <= 0.00001 for x in d), json.dumps(d))
    check(f"{label}: nessun errore", not errs, " | ".join(errs[:3]))
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        phone = {**p.devices["Pixel 7"]}
        pc = {"viewport": {"width": 1366, "height": 800}}
        await run(b, p, "Android", phone, True)
        await run(b, p, "PC", {**pc, "color_scheme": "dark"}, False)
        await run_screens(b, p, "Android", phone)
        await run_screens(b, p, "PC", pc)
        await run_notices(b, p, "Android", phone, True)
        await run_notices(b, p, "PC", pc, False)
        await run_rows(b, p, "Android", phone)
        await run_rows(b, p, "PC", pc)
        await run_reduced(b, p, "Android", phone)
        await run_rows(b, p, "Android", phone, reduced=True)
        await run_notices(b, p, "Android", phone, True, reduced=True)
        await run_screens(b, p, "Android", phone, reduced=True)
        await run_reduced(b, p, "PC", pc)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} superati")
    raise SystemExit(0 if all(results) else 1)

asyncio.run(main())
