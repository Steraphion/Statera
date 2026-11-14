#!/usr/bin/env python3
"""Le due palette scelte (Coolors 3 «Blu, oliva e zafferano» e Indaco) su Movimenti, Nuova spesa, Analisi."""
import json, os, sys, copy
sys.path.insert(0, os.path.dirname(__file__))
import gen
from gen import icon, tint, seg, cols, CATS, DIRS, W, OUT
import palettes, coolors
from palettes import B_nav

ZAF = copy.deepcopy(next(p for p in coolors.P if p['id'] == 'zafferano'))
IND = copy.deepcopy(palettes.P[0])
IND['name'] = 'Indaco'
IND['sw'] = dict(DIRS['B']['sw'])
IND['light'].update(fab='#3B38D6', onfab='#FFFFFF', inIcon='#0E7A57', outIcon='#B34A17')
IND['dark'].update(fab='#8F8CFF', onfab='#0B0D14', inIcon='#4FD9A0', outIcon='#F29A6B')
for p in (ZAF, IND):
    p['light'].setdefault('warn', '#B37400'); p['dark'].setdefault('warn', '#FAB219')
ZAF['name'] = 'Blu, oliva e zafferano'

def analisi(d, t, dark):
    sw = d['sw']; onp = t['onp']
    chip = tint(onp, 0.16)
    # budget: stato sempre scritto e con simbolo, mai solo colore
    def budget(name, spent, tot, pct, ok):
        col = t['primary'] if ok else t['warn']
        state_ic = icon('check', 14, t['income'], sw=2.4) if ok else icon('alert', 14, t['text'], sw=2.2)
        state = 'In regola' if ok else 'Quasi esaurito'
        return (f'<li style="display: flex; flex-direction: column; gap: 7px">'
                f'<span style="display: flex; justify-content: space-between; align-items: baseline; font-size: 14px"><span style="font-weight: 700">{name}</span>'
                f'<span><span style="font-weight: 700">{spent}</span><span style="color: {t["muted"]}"> di {tot}</span></span></span>'
                f'<span style="height: 8px; border-radius: 4px; background: {t["track"]}; display: block"><span style="display: block; height: 8px; width: {pct}%; border-radius: 4px; background: {col}"></span></span>'
                f'<span style="display: flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; color: {t["muted"]}">{state_ic}{state} · {pct}%</span></li>')
    lst = ''
    for (name, v, s, p, ic), k in zip(CATS[:5], ['s7', 's1', 's4', 's2', 's5']):
        lst += (f'<li style="display: flex; align-items: center; gap: 12px">'
                f'<span style="width: 40px; height: 40px; border-radius: 50%; background: {tint(sw[k], 0.15 if not dark else 0.3)}; color: {sw[k] if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center">{icon(ic, 19, sw=2)}</span>'
                f'<span style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="display: flex; justify-content: space-between; font-size: 14px"><span style="font-weight: 700">{name}</span>'
                f'<span><span style="color: {t["muted"]}">{p}% · </span><span style="font-weight: 700">{s}</span></span></span>'
                f'<span style="height: 6px; border-radius: 3px; background: {t["track"]}; display: block"><span style="display: block; height: 6px; width: {round(p/35*100)}%; border-radius: 3px; background: {t["chOut"]}"></span></span></span></li>')
    card = f'background: {t["surf"]}; border-radius: 24px; padding: 18px; display: flex; flex-direction: column; gap: 14px'
    return f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 16px">
<header style="display: flex; align-items: center; justify-content: space-between"><h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em">Analisi</h1>
<div style="width: 170px">{seg(['Mese', 'Anno'], 'Mese', t, d, h=40, radius=20, act_bg=t['primary'], act_col=onp)}</div></header>
<div style="background: {t['primary']}; color: {onp}; border-radius: 24px; padding: 20px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 14px; font-weight: 600">A novembre hai risparmiato</span>
<span style="font-size: 40px; font-weight: 800; letter-spacing: -0.03em">1.325,65 €</span>
<span style="display: flex; gap: 8px; flex-wrap: wrap">
<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: {chip}; display: flex; align-items: center; font-size: 13px; font-weight: 700">66% delle entrate</span>
<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: {chip}; display: flex; align-items: center; font-size: 13px; font-weight: 700">Stima uscite 1.480 €</span></span></div>
<section style="{card}"><h2 style="margin: 0; font-size: 17px; font-weight: 800">Budget del mese</h2>
<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">
{budget('Spesa alimentare', '168,40 €', '300 €', 56, True)}{budget('Pasti fuori', '72,00 €', '80 €', 90, False)}</ul>
<span style="font-size: 13px; color: {t['muted']}">Circa 9 € al giorno per i 16 giorni che restano</span></section>
<section style="{card}"><h2 style="margin: 0; font-size: 17px; font-weight: 800">Dove vanno i soldi</h2>
<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">{lst}</ul></section>
<section style="{card}; gap: 12px"><h2 style="margin: 0; font-size: 17px; font-weight: 800">Ultimi 6 mesi</h2>{cols(t, 90, barw=12, radius=6)}</section>
<div style="height: 96px"></div>
</div>
{B_nav(t, 'Analisi')}'''

AN_H = 1440
def page_h(title, d, t, body, h):
    old = gen.H; gen.H = h
    try:
        return gen.page(title, d, t, body)
    finally:
        gen.H = old

def main():
    canvas = json.load(open(sys.argv[1]))
    if not any(pg['id'] == 'scelte' for pg in canvas['pages']):
        canvas['pages'].append({'id': 'scelte', 'name': 'Scelte: Zafferano e Indaco'})
    canvas['launch'] = {'view': 'canvas', 'page': 'scelte'}
    X = [i * 470 for i in range(6)]
    row_y = [0, AN_H + 120 + 260]
    written = []
    for ri, (p, slug) in enumerate([(ZAF, 'zafferano'), (IND, 'indaco')]):
        d = dict(DIRS['B']); d['sw'] = p['sw']; y = row_y[ri]
        L, K = p['light'], p['dark']
        items = [
          ('movimenti-chiaro', 'Movimenti, chiaro', gen.page(f'{p["name"]} — Movimenti', d, L, coolors.mov(d, L, False)), 844),
          ('movimenti-scuro', 'Movimenti, scuro', gen.page(f'{p["name"]} — Movimenti scuro', d, K, coolors.mov(d, K, True)), 844),
          ('nuova-chiaro', 'Nuova spesa, chiaro', gen.page(f'{p["name"]} — Nuova spesa', d, L, gen.B_new(d, L, False)), 844),
          ('nuova-scuro', 'Nuova spesa, scuro', gen.page(f'{p["name"]} — Nuova spesa scuro', d, K, gen.B_new(d, K, True)), 844),
          ('analisi-chiaro', 'Analisi, chiaro (pagina intera)', page_h(f'{p["name"]} — Analisi', d, L, analisi(d, L, False), AN_H), AN_H),
          ('analisi-scuro', 'Analisi, scuro (pagina intera)', page_h(f'{p["name"]} — Analisi scuro', d, K, analisi(d, K, True), AN_H), AN_H),
        ]
        for ci, (key, label, html, h) in enumerate(items):
            fn = f'sc-{slug}-{key}.dc.html'
            open(os.path.join(OUT, fn), 'w').write(html)
            canvas['boards'][fn] = {'x': X[ci], 'y': y, 'w': W, 'h': h, 'title': f'{p["name"]} · {label}', 'page': 'scelte'}
            if fn not in canvas['order']: canvas['order'].append(fn)
            written.append(fn)
        canvas['notes'][f'scT{ri}'] = {'x': 0, 'y': y - 260, 'text': p['name'], 'kind': 'title1', 'maxW': 2740, 'page': 'scelte'}
    canvas['notes']['scNote'] = {'x': 2820, 'y': 0, 'w': 340, 'size': 'm', 'fill': 'teal', 'page': 'scelte',
      'text': "Novità rispetto alle prove: in Analisi c'è il budget del mese, con lo stato scritto e un simbolo (mai solo colore). Analisi è disegnata a pagina intera, come se la scorressi. Le tinte delle categorie seguono la palette."}
    json.dump(canvas, open(os.path.join(OUT, 'canvas.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(written))

if __name__ == '__main__':
    main()
