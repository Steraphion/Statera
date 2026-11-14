#!/usr/bin/env python3
"""Pagina «Scelte»: Zafferano e Indaco ammorbidito, sulle schermate già impostate in chosen.py.
Uso: scelta2.py rebuild <canvas-base>   → ricostruisce il canvas.json pubblicato (per confronto)
     scelta2.py build <canvas-attuale>  → genera le tavole e il nuovo canvas.json"""
import json, os, sys, copy, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import gen
from gen import tint, DIRS, W, OUT
import coolors, chosen, scelta
from scelta import IND_L, IND_D, IND_SW, check, PAL

AN_H = chosen.AN_H
ROW_Y = [0, AN_H + 120 + 260]

ZAF = copy.deepcopy(chosen.ZAF); ZAF['sw'] = dict(ZAF['sw'], s8='#A8750C')
IND = dict(name='Indaco morbido', light=dict(IND_L, warn='#A86A00'), dark=dict(IND_D, warn='#F2B13C'), sw=IND_SW)
# le schede colori riusano le definizioni di scelta.py (stessi valori)
PAL[0]['sw'] = ZAF['sw']; PAL[1]['light'] = IND['light']; PAL[1]['dark'] = IND['dark']

def analisi(d, t, dark):
    html = chosen.analisi(d, t, dark)
    if dark:  # riquadro del risparmio meno abbagliante in tema scuro
        html = html.replace(f"background: {t['primary']}; color: {t['onp']}; border-radius: 24px; padding: 20px",
                            f"background: {t['accentSoft']}; color: {t['text']}; border-radius: 24px; padding: 20px", 1)
        html = html.replace(f"background: {tint(t['onp'], 0.16)}", f"background: {tint(t['text'], 0.12)}")
    return html

def rebuild(base):
    """Rifà esattamente ciò che chosen.py aveva pubblicato."""
    sys.argv = ['chosen.py', base]
    # chosen.main scrive i file e il canvas: lo facciamo girare su una cartella temporanea
    old = chosen.OUT; tmp = '/tmp/rebuild'; os.makedirs(tmp, exist_ok=True); chosen.OUT = tmp
    try: chosen.main()
    finally: chosen.OUT = old
    data = open(os.path.join(tmp, 'canvas.json'), 'rb').read()
    print('sha256', hashlib.sha256(data).hexdigest())

def build(cur):
    if check():
        print('CONTRASTI INSUFFICIENTI'); return
    canvas = json.load(open(cur))
    written = []
    for ri, (p, slug) in enumerate([(ZAF, 'zafferano'), (IND, 'indaco')]):
        d = dict(DIRS['B']); d['sw'] = p['sw']; L, K = p['light'], p['dark']
        items = [
          ('movimenti-chiaro', gen.page(f'{p["name"]} — Movimenti', d, L, coolors.mov(d, L, False)), 844),
          ('movimenti-scuro', gen.page(f'{p["name"]} — Movimenti scuro', d, K, coolors.mov(d, K, True)), 844),
          ('nuova-chiaro', gen.page(f'{p["name"]} — Nuova spesa', d, L, scelta.new(d, L, False)), 844),
          ('nuova-scuro', gen.page(f'{p["name"]} — Nuova spesa scuro', d, K, scelta.new(d, K, True)), 844),
          ('analisi-chiaro', chosen.page_h(f'{p["name"]} — Analisi', d, L, analisi(d, L, False), AN_H), AN_H),
          ('analisi-scuro', chosen.page_h(f'{p["name"]} — Analisi scuro', d, K, analisi(d, K, True), AN_H), AN_H),
        ]
        for key, html, h in items:
            fn = f'sc-{slug}-{key}.dc.html'
            open(os.path.join(OUT, fn), 'w').write(html)
            canvas['boards'][fn]['title'] = canvas['boards'][fn]['title'].replace('Indaco ·', 'Indaco morbido ·')
            written.append(fn)
        # scheda colori sotto le due righe
        fn = f'sc-{slug}-colori.dc.html'
        open(os.path.join(OUT, fn), 'w').write(gen.page(f'{p["name"]} — colori', d, L, scelta.tile(PAL[ri])))
        canvas['boards'][fn] = {'x': ri * 470, 'y': ROW_Y[1] + AN_H + 120 + 260, 'w': W, 'h': 844, 'title': f'{p["name"]} — colori', 'page': 'scelte'}
        if fn not in canvas['order']: canvas['order'].append(fn)
        written.append(fn)
    canvas['notes']['scT1']['text'] = 'Indaco morbido'
    ty = ROW_Y[1] + AN_H + 120
    canvas['notes']['scT2'] = {'x': 0, 'y': ty, 'text': 'Colori delle due palette', 'kind': 'title1', 'maxW': 2740, 'page': 'scelte'}
    canvas['notes']['scInd'] = {'x': 960, 'y': ty + 260, 'w': 380, 'size': 'm', 'fill': 'blue', 'page': 'scelte',
        'text': "Indaco morbido: stessa tinta, saturazione quasi dimezzata e un filo più chiaro (#535AA6 al posto di #3B38D6). In scuro il viola neon diventa un lilla polvere (#A9B3EE). Anche le 8 tinte delle categorie sono più tenui. In tema scuro il riquadro del risparmio ora è tenue invece che pieno, in tutte e due le palette."}
    json.dump(canvas, open(os.path.join(OUT, 'canvas.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(written))

if __name__ == '__main__':
    {'rebuild': rebuild, 'build': build}[sys.argv[1]](sys.argv[2])
