"""Collaudo v0.30: movimento di pannelli e finestre (dati di esempio).

Su Android (pannello dal basso) e PC (finestra centrata): durate e curve uguali ai token, uscita in
--ease-exit con la <dialog> ancora aperta finché non finisce, apertura e chiusura da tastiera, Esc e
«Chiudi», focus che resta nel pannello e torna al pulsante, riapertura durante l'uscita, schermata di
blocco sopra un pannello che si sta chiudendo. Poi le stesse prove con «riduci animazioni».
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
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)

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

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        phone = {**p.devices["Pixel 7"]}
        pc = {"viewport": {"width": 1366, "height": 800}}
        await run(b, p, "Android", phone, True)
        await run(b, p, "PC", {**pc, "color_scheme": "dark"}, False)
        await run_reduced(b, p, "Android", phone)
        await run_reduced(b, p, "PC", pc)
        await b.close()
    print(f"\n{sum(results)}/{len(results)} superati")
    raise SystemExit(0 if all(results) else 1)

asyncio.run(main())
