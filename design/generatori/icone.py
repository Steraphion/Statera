#!/usr/bin/env python3
"""Pagina «Icone delle categorie»: Lucide, Tabler e Phosphor a confronto sulle categorie iniziali,
nel modulo Nuova spesa e in Movimenti; scelta dell'icona nel modulo della categoria (Lucide).
Le forme delle icone sono in icone_set.json (estratte con estrai.py; licenze in LICENZE-ICONE.md).
Uso: icone.py  → scrive le tavole in $STATERA_CANVAS (o out/project) e voci-icone.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import tint, W, H, OUT
import palettes, coolors, scelta, chosen, altre
from altre import L, K, SW, D, THEMES, page_h, h1, h2, card, muted, pill, texts, top, wrap, seg

SET = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icone_set.json')))
SETS = ['lucide', 'tabler', 'phosphor']
INFO = {'lucide': ('Lucide', 'licenza ISC · 2.359 icone · tratto', 'ind-ico-lucide'),
        'tabler': ('Tabler Icons', 'licenza MIT · 5.491 icone · tratto', 'ind-ico-tabler'),
        'phosphor': ('Phosphor duotone', 'licenza MIT · 1.512 icone in 6 pesi · pieno tenue', 'ind-ico-phosphor')}

def seticon(s, key, size=20, color='currentColor', sw=2, label=None):
    meta = SET[s]; ic = meta['icone'][key]
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    if meta['modo'] == 'tratto':
        paint = f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
    else:
        paint = f'fill="{color}"'
    inner = ''.join('<' + tag + ''.join(f' {k}="{v}"' for k, v in at.items()) + '/>' for tag, at in ic['forme'])
    return (f'<svg width="{size}" height="{size}" viewBox="{meta["viewBox"]}" {paint} {aria} style="flex-shrink: 0; display: block">{inner}</svg>')

# chiavi degli script esistenti → chiavi del set
GEN2KEY = {'cart': 'spesa', 'food': 'pasti', 'fuel': 'carburante', 'repeat': 'abbonamenti', 'work': 'stipendio', 'bus': 'mezzi',
           'home': 'casa', 'heart': 'salute', 'shirt': 'abbigliamento', 'game': 'svago', 'plane': 'viaggi', 'gift': 'regali', 'ticket': 'buoni',
           'search': 'u-search', 'plus': 'u-plus', 'list': 'u-list', 'wallet': 'u-wallet', 'chart': 'u-chart', 'more': 'u-more', 'in': 'u-in',
           'out': 'u-out', 'swap': 'u-swap', 'star': 'u-star', 'cal': 'u-cal', 'x': 'u-x', 'pen': 'u-pen', 'chevD': 'u-chevD', 'chevL': 'u-chevL',
           'chevR': 'u-chevR', 'check': 'u-check', 'card': 'c-carta', 'alert': 'u-alert'}
MODS = [gen, palettes, coolors, scelta, chosen, altre]
ORIG = {m: m.icon for m in MODS}

def use_set(s):
    def f(name, size=20, color='currentColor', sw=1.8, label=None):
        key = name if name in SET[s]['icone'] else GEN2KEY.get(name)
        if key is None:
            return ORIG[gen](name, size, color, sw, label)
        return seticon(s, key, size, color, sw if sw >= 1.8 else 1.8, label)
    for m in MODS:
        m.icon = f
    scelta.PICK = [(GEN2KEY.get(ic, ic), s_, lab) if lab != 'Altro' else ('altro', s_, lab) for ic, s_, lab in gen.PICK]

def reset():
    for m in MODS:
        m.icon = ORIG[m]
    scelta.PICK = gen.PICK

# ---------------------------------------------------------------- le categorie
USCITE = [('spesa', 's1', 'Spesa alimentare'), ('pasti', 's2', 'Pasti fuori'), ('casa', 's3', 'Casa'), ('affitto', 's3', 'Affitto o mutuo'),
          ('bollette', 's3', 'Bollette'), ('manutenzione', 's3', 'Manutenzione'), ('trasporti', 's4', 'Trasporti'), ('carburante', 's4', 'Carburante'),
          ('mezzi', 's4', 'Mezzi pubblici'), ('auto', 's4', 'Auto'), ('salute', 's5', 'Salute'), ('abbigliamento', 's6', 'Abbigliamento'),
          ('sport', 's7', 'Sport'), ('svago', 's8', 'Svago'), ('viaggi', 's1', 'Viaggi'), ('regali', 's2', 'Regali'), ('abbonamenti', 's3', 'Abbonamenti'),
          ('altro', 's4', 'Altro')]
ENTRATE = [('stipendio', 's5', 'Stipendio'), ('buoni', 's6', 'Buoni pasto'), ('rimborsi', 's7', 'Rimborsi'), ('regali', 's8', 'Regali ricevuti'),
           ('altro', 's1', 'Altro'), ('rettifica', 's4', 'Rettifica saldo')]
CONTI = [('c-corrente', 's3', 'Conto corrente'), ('c-contanti', 's1', 'Contanti'), ('buoni', 's2', 'Buoni pasto'), ('c-risparmi', 's6', 'Risparmi'), ('c-carta', 's3', 'Carta')]
UI = ['u-search', 'u-plus', 'u-list', 'u-wallet', 'u-chart', 'u-more', 'u-in', 'u-out', 'u-swap', 'u-star', 'u-cal', 'u-pen', 'u-check', 'u-x',
      'u-lock', 'u-finger', 'u-cloud', 'u-shield', 'u-repeat', 'u-alert', 'u-trash', 'u-download', 'u-tag', 'u-target']

def circ(s, key, c, t, dark, size=52, isz=24, on=False):
    col = SW[c]
    ring = f'box-shadow: 0 0 0 3px {t["bg"]}, 0 0 0 5px {col};' if on else ''
    return (f'<span aria-hidden="true" style="width: {size}px; height: {size}px; border-radius: 50%; background: {col if on else tint(col, 0.15 if not dark else 0.3)}; '
            f'color: {"#FFFFFF" if on or dark else col}; display: flex; align-items: center; justify-content: center; flex-shrink: 0; {ring}">{seticon(s, key, isz, sw=2)}</span>')

def grid(s, items, t, dark, cols=4):
    cells = ''.join(f'<li style="display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; font-size: 11px; font-weight: 600; line-height: 1.25">'
                    f'{circ(s, k, c, t, dark)}{lab}</li>' for k, c, lab in items)
    return f'<ul style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); row-gap: 14px; column-gap: 6px">{cells}</ul>'

def sheet(s, t, dark):
    name, sub, _ = INFO[s]
    ui = ''.join(f'<span title="{SET[s]["icone"][k]["nome"]}" style="width: 36px; height: 36px; border-radius: 12px; background: {t["bg"]}; color: {t["text"]}; display: flex; align-items: center; justify-content: center">{seticon(s, k, 20, sw=2)}</span>' for k in UI)
    lab = lambda txt: f'<h2 style="margin: 0; font-size: 11px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: {t["muted"]}">{txt}</h2>'
    body = f'''<div style="display: flex; flex-direction: column; gap: 4px">{h1(name)}{muted(sub + ' · versione ' + SET[s]['versione'], t, 14)}</div>
{card(lab('Uscite, con le sottocategorie') + grid(s, USCITE, t, dark), t, gap=14)}
{card(lab('Entrate') + grid(s, ENTRATE, t, dark), t, gap=14)}
{card(lab('Conti e carte') + grid(s, CONTI, t, dark, 5), t, gap=14)}
{card(lab('Interfaccia') + f'<div style="display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 6px; justify-items: center">{ui}</div>', t, gap=12)}'''
    return wrap(body, gap=14, pad='20px 20px 0')
SHEET_H = 1300

# ---------------------------------------------------------------- scelta dell'icona nel modulo della categoria (Lucide)
GROUPS = [('Suggerite', ['pasti', 'x-coffee', 'x-pizza', 'x-wine', 'x-beer', 'x-icecream', 'x-croissant', 'spesa', 'x-party', 'regali', 'x-heart', 'x-handheart']),
          ('Casa', ['casa', 'affitto', 'bollette', 'manutenzione', 'x-sofa', 'x-washing', 'x-wifi', 'x-phone', 'x-tv', 'x-plant', 'x-paw', 'x-baby']),
          ('Trasporti e viaggi', ['trasporti', 'auto', 'carburante', 'mezzi', 'x-train', 'x-bike', 'x-taxi', 'x-parking', 'viaggi', 'x-ship', 'x-hotel', 'x-tent']),
          ('Salute e tempo libero', ['salute', 'x-pill', 'x-stetho', 'x-scissors', 'x-sparkles', 'x-glasses', 'sport', 'svago', 'x-music', 'x-film', 'x-book', 'x-game']),
          ('Soldi e lavoro', ['stipendio', 'x-laptop', 'x-graduation', 'x-coins', 'x-percent', 'x-receipt', 'x-trend', 'x-umbrella', 'rimborsi', 'abbonamenti', 'x-globe', 'altro'])]

def picker(t, dark, s='lucide', color='s2', sel='pasti'):
    col = SW[color]
    swatches = ''
    for k, c in SW.items():
        on = k == color
        swatches += (f'<button type="button" aria-label="Colore {k[1]}" aria-pressed="{"true" if on else "false"}" style="width: 36px; height: 36px; border-radius: 50%; border: none; padding: 0; background: {c}; color: #FFFFFF; display: flex; align-items: center; justify-content: center; '
                     f'{"box-shadow: 0 0 0 3px " + t["surf"] + ", 0 0 0 5px " + c + ";" if on else ""}">{seticon(s, "u-check", 18, sw=2.6) if on else ""}</button>')
    chips = ''.join(f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}" style="height: 34px; padding: 0 12px; border-radius: 17px; border: none; background: {t["accentSoft"] if i == 0 else t["bg"]}; color: {t["accent"] if i == 0 else t["text"]}; font: inherit; font-size: 13px; font-weight: 700; white-space: nowrap; flex-shrink: 0">{g}</button>'
                    for i, (g, _) in enumerate(GROUPS))
    icons = ''
    for k in GROUPS[0][1]:
        on = k == sel
        icons += (f'<button type="button" aria-label="{SET[s]["icone"][k]["nome"]}" aria-pressed="{"true" if on else "false"}" style="border: none; background: transparent; padding: 0; display: flex; justify-content: center">'
                  f'<span style="width: 46px; height: 46px; border-radius: 50%; background: {col if on else tint(col, 0.15 if not dark else 0.3)}; color: {"#FFFFFF" if on or dark else col}; display: flex; align-items: center; justify-content: center; '
                  f'{"box-shadow: 0 0 0 3px " + t["surf"] + ", 0 0 0 5px " + col + ";" if on else ""}">{seticon(s, k, 22, sw=2)}</span></button>')
    fieldbox = f'height: 52px; box-sizing: border-box; border-radius: 16px; background: {t["surf"]}; display: flex; align-items: center; gap: 10px; padding: 0 16px'
    lab = lambda txt: f'<span style="font-size: 13px; font-weight: 700; color: {t["muted"]}">{txt}</span>'
    inner = f'''<div style="display: flex; align-items: center; justify-content: space-between">
{gen.btn_icon('x', 'Chiudi', t, bg=t['surf'])}<h1 style="margin: 0; font-size: 18px; font-weight: 800">Modifica categoria</h1>{pill('Salva', t, None, 'primary', h=40)}</div>
<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 4px 0">
<span aria-hidden="true" style="width: 76px; height: 76px; border-radius: 50%; background: {col}; color: #FFFFFF; display: flex; align-items: center; justify-content: center">{seticon(s, sel, 36, sw=2)}</span>
<span style="font-size: 20px; font-weight: 800">Pasti fuori</span>{muted('Uscita · budget 80 € al mese', t)}</div>
<label style="display: flex; flex-direction: column; gap: 6px">{lab('Nome')}<span style="{fieldbox}"><input type="text" value="Pasti fuori" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 16px; color: {t['text']}"></span></label>
<div style="display: flex; flex-direction: column; gap: 8px">{lab('Colore')}<div style="background: {t['surf']}; border-radius: 20px; padding: 12px 14px; display: flex; justify-content: space-between">{swatches}</div></div>
<div style="display: flex; flex-direction: column; gap: 8px">{lab('Icona')}
<div style="background: {t['surf']}; border-radius: 22px; padding: 14px; display: flex; flex-direction: column; gap: 12px">
<label style="height: 44px; box-sizing: border-box; border-radius: 22px; background: {t['bg']}; display: flex; align-items: center; gap: 8px; padding: 0 14px; color: {t['muted']}">{seticon(s, 'u-search', 18, sw=2)}{altre.sr('Cerca un’icona')}<input type="text" placeholder="Cerca: caffè, gatto, treno…" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; color: {t['text']}"></label>
<div role="group" aria-label="Gruppi di icone" style="display: flex; gap: 6px; overflow: hidden">{chips}</div>
<div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); row-gap: 12px">{icons}</div>
<span style="font-size: 12px; color: {t['muted']}">Senza icona compare l’iniziale del nome.</span></div></div>
<a href="#" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 18px; background: {t['surf']}; text-decoration: none; color: {t['text']}">{texts('Budget mensile', '80,00 € al mese', t)}{seticon(s, 'u-chevR', 18, sw=2)}</a>
<a href="#" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 18px; background: {t['surf']}; text-decoration: none; color: {t['text']}">{texts('Sottocategorie', 'Nessuna · aggiungine una', t)}{seticon(s, 'u-chevR', 18, sw=2)}</a>'''
    return f'''<div aria-hidden="true" style="position: absolute; inset: 0; background: {t['bg']}"></div>
<div role="dialog" aria-label="Modifica categoria" style="position: absolute; inset: 0; padding: 16px 20px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">{inner}</div>'''
PICK_H = 1000

def categorie_lucide(d, t, dark):
    use_set('lucide')
    old = altre.CATL
    altre.CATL = [('abbigliamento', 's6', 'Abbigliamento', None, []), ('abbonamenti', 's3', 'Abbonamenti', None, []), ('altro', 's4', 'Altro', None, []),
                  ('casa', 's3', 'Casa', None, [('affitto', 'Affitto o mutuo'), ('bollette', 'Bollette'), ('manutenzione', 'Manutenzione')]),
                  ('pasti', 's2', 'Pasti fuori', '80 € al mese', []), ('regali', 's2', 'Regali', None, []), ('salute', 's5', 'Salute', None, []),
                  ('spesa', 's1', 'Spesa alimentare', '300 € al mese', []), ('sport', 's7', 'Sport', None, []), ('svago', 's8', 'Svago', None, []),
                  ('trasporti', 's4', 'Trasporti', '150 € al mese', [('auto', 'Auto'), ('carburante', 'Carburante'), ('mezzi', 'Mezzi pubblici')]),
                  ('viaggi', 's1', 'Viaggi', None, [])]
    try:
        return altre.categorie(d, t, dark)
    finally:
        altre.CATL = old; reset()

# ---------------------------------------------------------------- pagina
PAGE = {'id': 'icone', 'name': 'Icone delle categorie'}

def build():
    boards, notes = {}, {}
    rows = []
    # riga 1: le tre raccolte
    r = []
    for s in SETS:
        for theme, t, dark in THEMES:
            r.append((f'{INFO[s][2]}-raccolta-{theme}.dc.html', f'{INFO[s][0]} · categorie e interfaccia, {theme}', page_h(f'{INFO[s][0]} — raccolta, {theme}', t, sheet(s, t, dark), SHEET_H), SHEET_H))
    rows.append(('Le icone delle categorie in tre set', r))
    # riga 2: in contesto (Movimenti chiaro, Nuova spesa scuro)
    r = []
    for s in SETS:
        use_set(s)
        try:
            r.append((f'{INFO[s][2]}-movimenti-chiaro.dc.html', f'{INFO[s][0]} · Movimenti, chiaro', gen.page(f'{INFO[s][0]} — Movimenti', D, L, coolors.mov(D, L, False)), H))
            r.append((f'{INFO[s][2]}-nuova-scuro.dc.html', f'{INFO[s][0]} · Nuova spesa, scuro', gen.page(f'{INFO[s][0]} — Nuova spesa', D, K, scelta.new(D, K, True)), H))
        finally:
            reset()
    rows.append(('Nel contesto: Movimenti e Nuova spesa', r))
    # riga 3: Lucide, scelta dell'icona e Categorie
    r = []
    use_set('lucide')
    try:
        for theme, t, dark in THEMES:
            r.append((f'ind-ico-lucide-modulo-{theme}.dc.html', f'Lucide · Modifica categoria, {theme}', page_h(f'Lucide — Modifica categoria, {theme}', t, picker(t, dark), PICK_H), PICK_H))
    finally:
        reset()
    for theme, t, dark in THEMES:
        r.append((f'ind-ico-lucide-categorie-{theme}.dc.html', f'Lucide · Categorie, {theme}', page_h(f'Lucide — Categorie, {theme}', t, categorie_lucide(D, t, dark), altre.CAT_H), altre.CAT_H))
    rows.append(('Con Lucide: scegliere l’icona di una categoria', r))
    y = 0
    for ri, (title, items) in enumerate(rows):
        x = 0; maxh = 0
        for name, label, html, h in items:
            open(os.path.join(OUT, name), 'w').write(html)
            boards[name] = {'x': x, 'y': y, 'w': W, 'h': h, 'title': label, 'page': PAGE['id']}
            x += W + 80; maxh = max(maxh, h)
        notes[f'icoT{ri}'] = {'x': 0, 'y': y - 260, 'text': title, 'kind': 'title1', 'maxW': x - 80, 'page': PAGE['id']}
        if ri == 0:
            notes['icoConfronto'] = {'x': x, 'y': y, 'w': 400, 'size': 'm', 'fill': 'teal', 'page': PAGE['id'], 'text':
                "Lucide (ISC): tratto di 2 px su griglia 24, lo stesso stile delle icone già disegnate e di quelle dell'app oggi, quindi il resto dell'interfaccia non cambia. "
                "Tabler (MIT): stesso tratto, forme un po' più squadrate e più del doppio delle icone, utile per le categorie create da te. "
                "Phosphor duotone (MIT): il riempimento tenue dà più carattere nei cerchi colorati, ma è un linguaggio diverso dal tratto e andrebbe usato anche per l'interfaccia. "
                "Consiglio Lucide."}
        if ri == 2:
            notes['icoDati'] = {'x': x, 'y': y, 'w': 400, 'size': 'm', 'fill': 'blue', 'page': PAGE['id'], 'text':
                "Dati: un campo facoltativo «icon» nella categoria, con una chiave dell'elenco (es. «pasti»), come per i colori. Non serve una nuova versione del database: Dexie la chiede solo per gli indici e il campo non va indicizzato, come il budget. "
                "Le categorie iniziali prendono l'icona predefinita dal loro id fisso, senza migrazione. Chiave assente o sconosciuta: l'iniziale. Le icone stanno nel codice (circa 100), mai lette dai dati come disegno."}
        y += maxh + 380
    data = {'page': PAGE, 'boards': boards, 'order': list(boards), 'notes': notes}
    json.dump(data, open(os.path.join(OUT, 'voci-icone.json'), 'w'), ensure_ascii=False, indent=1)
    return boards

if __name__ == '__main__':
    print('\n'.join(build()))
