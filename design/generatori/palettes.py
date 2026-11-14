#!/usr/bin/env python3
"""Cinque palette per la direzione B (Vivace), applicate a Movimenti chiaro/scuro."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import gen
from gen import icon, tint, page, NAV, DIRS, W, H, OUT

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def cr(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)

BASE = dict(chIn='#2A78D6', chOut='#EB6834')
BASED = dict(chIn='#3987E5', chOut='#D95926')
P = [
 dict(id='indaco', name='Indaco', mood='fredda e tecnologica: la proposta di partenza',
   light=dict(bg='#F2F3F8', surf='#FFFFFF', surf2='#E9EBF3', border='#E1E4EE', text='#0E1220', muted='#596075',
              primary='#3B38D6', onp='#FFFFFF', accent='#3B38D6', accentSoft='#E7E6FC', income='#0E7A57', track='#E9EBF3', backdrop='rgba(14,18,32,0.5)'),
   dark=dict(bg='#0B0D14', surf='#161925', surf2='#20243A', border='#2A2F45', text='#F2F3F8', muted='#A0A6BB',
             primary='#8F8CFF', onp='#0B0D14', accent='#9C99FF', accentSoft='#262551', income='#4FD9A0', track='#20243A', backdrop='rgba(0,0,0,0.6)')),
 dict(id='petrolio', name='Petrolio', mood='fresca e rassicurante, tra il blu e il verde',
   light=dict(bg='#EFF4F4', surf='#FFFFFF', surf2='#E2EBEB', border='#D7E2E2', text='#0C1B1E', muted='#52656A',
              primary='#0A6670', onp='#FFFFFF', accent='#0A6670', accentSoft='#DAEFF0', income='#17803B', track='#E2EBEB', backdrop='rgba(12,27,30,0.5)'),
   dark=dict(bg='#071214', surf='#0F1D20', surf2='#18292D', border='#22363A', text='#ECF5F5', muted='#9DB2B5',
             primary='#4CC9D3', onp='#04181B', accent='#5AD3DC', accentSoft='#113539', income='#7ADF8E', track='#18292D', backdrop='rgba(0,0,0,0.6)')),
 dict(id='ciclamino', name='Ciclamino', mood='calda ed energica, si distingue dalle app bancarie',
   light=dict(bg='#F7F2F5', surf='#FFFFFF', surf2='#EFE6EC', border='#E8DCE4', text='#1C0F17', muted='#695A63',
              primary='#B0216B', onp='#FFFFFF', accent='#B0216B', accentSoft='#FBE3EF', income='#0E7A57', track='#EFE6EC', backdrop='rgba(28,15,23,0.5)'),
   dark=dict(bg='#120C10', surf='#1D161B', surf2='#2A2128', border='#372C34', text='#F7EEF3', muted='#B4A4AE',
             primary='#F27AB8', onp='#1A0812', accent='#F58CC2', accentSoft='#3E1A2F', income='#4FD9A0', track='#2A2128', backdrop='rgba(0,0,0,0.6)')),
 dict(id='ottone', name='Ardesia e ottone', mood='lo stile Vivace con i colori di oggi: continuità con la bilancia',
   light=dict(bg='#F4F1EA', surf='#FFFFFF', surf2='#EAE5DA', border='#E0D9CB', text='#1C2A31', muted='#5B676C',
              primary='#1C2A31', onp='#F4F1EA', accent='#7E5615', accentSoft='#F3E6C9', income='#1C7546', track='#EAE5DA', backdrop='rgba(18,23,26,0.5)',
              fab='#C08A2E', onfab='#1B1408'),
   dark=dict(bg='#101518', surf='#1A2125', surf2='#242D32', border='#303A40', text='#EEEAE2', muted='#A0A8AC',
             primary='#D9A955', onp='#1B1408', accent='#E0B465', accentSoft='#3B3021', income='#62C990', track='#242D32', backdrop='rgba(0,0,0,0.6)')),
 dict(id='lime', name='Notte e lime', mood='contrasto forte, nero e un verde acido come segno distintivo',
   light=dict(bg='#F3F3EF', surf='#FFFFFF', surf2='#E9E9E3', border='#E2E2DA', text='#121410', muted='#5C5F57',
              primary='#15171C', onp='#FFFFFF', accent='#4B6600', accentSoft='#E8F6C4', income='#0E7A57', track='#E9E9E3', backdrop='rgba(18,20,16,0.5)',
              fab='#C5F04A', onfab='#15171C'),
   dark=dict(bg='#0C0D0B', surf='#171915', surf2='#22251F', border='#2E3229', text='#F1F3EC', muted='#A4A99C',
             primary='#C5F04A', onp='#121410', accent='#CDF262', accentSoft='#2A3414', income='#6FE3B0', track='#22251F', backdrop='rgba(0,0,0,0.6)')),
]
for p in P:
    p['light'].update(BASE); p['dark'].update(BASED)

# ---- barra di navigazione con "+" che può avere un colore proprio
def B_nav(t, active):
    fab, onfab = t.get('fab', t['primary']), t.get('onfab', t['onp'])
    def it(ic, lab):
        on = lab == active
        return (f'<a href="#" style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; text-decoration: none; font-size: 11px; font-weight: {700 if on else 500}; color: {t["accent"] if on else t["muted"]}">'
                f'{icon(ic, 22, sw=2 if on else 1.8)}{lab}</a>')
    plus = (f'<button type="button" aria-label="Nuovo movimento" style="width: 56px; height: 56px; margin-top: -26px; border-radius: 50%; border: 4px solid {t["bg"]}; background: {fab}; color: {onfab}; '
            f'display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px {tint(fab, 0.35)}; flex-shrink: 0">{icon("plus", 26, sw=2.4)}</button>')
    return (f'<nav aria-label="Sezioni" style="position: absolute; left: 12px; right: 12px; bottom: 14px; height: 66px; border-radius: 33px; background: {t["surf"]}; '
            f'box-shadow: 0 6px 24px rgba(0,0,0,0.10); border: 1px solid {t["border"]}; display: flex; align-items: center; padding: 0 8px">'
            f'{it(*NAV[0])}{it(*NAV[1])}{plus}{it(*NAV[2])}{it(*NAV[3])}</nav>')
gen.B_nav = B_nav

D = dict(DIRS['B'])

def swatches(t, dark):
    rows = [('Sfondo', 'bg'), ('Superficie', 'surf'), ('Superficie 2', 'surf2'), ('Bordo', 'border'), ('Testo', 'text'), ('Testo attenuato', 'muted'),
            ('Principale', 'primary'), ('Accento', 'accent'), ('Accento tenue', 'accentSoft'), ('Entrate', 'income')]
    if 'fab' in t: rows.append(('Pulsante +', 'fab'))
    out = ''
    for lab, k in rows:
        out += (f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="height: 36px; border-radius: 10px; background: {t[k]}; border: 1px solid {t["border"]}"></span>'
                f'<span style="font-size: 10px; line-height: 1.3; color: {t["muted"]}">{lab}<br><span style="font-family: ui-monospace, monospace; color: {t["text"]}">{t[k]}</span></span></div>')
    return f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px">{out}</div>'

def mini(t):
    fab, onfab = t.get('fab', t['primary']), t.get('onfab', t['onp'])
    return f'''<div style="display: flex; align-items: center; gap: 10px">
<button type="button" style="flex: 1; height: 44px; border-radius: 22px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 14px; font-weight: 800">Salva spesa</button>
<span style="width: 44px; height: 44px; border-radius: 50%; background: {t['accentSoft']}; color: {t['accent']}; display: flex; align-items: center; justify-content: center">{icon('swap', 20, sw=2.1)}</span>
<span style="width: 44px; height: 44px; border-radius: 50%; background: {fab}; color: {onfab}; display: flex; align-items: center; justify-content: center">{icon('plus', 22, sw=2.4)}</span></div>
<div style="display: flex; justify-content: space-between; align-items: center; background: {t['surf']}; border-radius: 16px; padding: 10px 14px; font-size: 14px; font-weight: 700">
<span>Stipendio</span><span style="color: {t['income']}">+1.850,00 €</span><span>Conad</span><span>−42,30 €</span></div>'''

def tile(p):
    L, K = p['light'], p['dark']
    hdr = 'font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em'
    return f'''<div style="height: 100%; display: flex; flex-direction: column">
<div style="flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 12px; background: {L['bg']}; color: {L['text']}">
<div style="display: flex; flex-direction: column; gap: 2px"><h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em">{p['name']}</h1>
<p style="margin: 0; font-size: 13px; color: {L['muted']}">{p['mood']}</p></div>
<span style="{hdr}; color: {L['muted']}">Tema chiaro</span>{swatches(L, False)}{mini(L)}</div>
<div style="flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 12px; background: {K['bg']}; color: {K['text']}">
<span style="{hdr}; color: {K['muted']}">Tema scuro</span>{swatches(K, True)}{mini(K)}</div></div>'''

def main():
    # ---- controllo contrasti (WCAG AA 4.5:1 per il testo)
    print('contrasti (testo/sfondo, attenuato/superficie, su principale, accento/accento tenue, entrate/superficie):')
    for p in P:
        for k in ('light', 'dark'):
            t = p[k]
            vals = [cr(t['text'], t['bg']), cr(t['muted'], t['surf']), cr(t['onp'], t['primary']), cr(t['accent'], t['accentSoft']), cr(t['income'], t['surf']), cr(t['muted'], t['bg'])]
            if 'fab' in t: vals.append(cr(t['onfab'], t['fab']))
            flag = '' if min(vals) >= 4.5 else '  <-- SOTTO 4.5'
            print(f"{p['id']:10} {k:5} " + ' '.join(f'{v:4.1f}' for v in vals) + flag)

    # ---- scrittura
    canvas = json.load(open(os.path.join(OUT, 'canvas.json')))
    canvas['createdOnFiles']['at'] = '2026-11-14T13:02:11Z'
    canvas['pages'] = [{'id': 'direzioni', 'name': 'Direzioni'}, {'id': 'palette', 'name': 'Palette per Vivace'}]
    canvas['launch'] = {'view': 'canvas', 'page': 'palette'}
    for b in canvas['boards'].values(): b['page'] = 'direzioni'
    for n in canvas['notes'].values(): n['page'] = 'direzioni'
    X = [i * 470 for i in range(5)]
    ROWS = [('chiaro', 0), ('scuro', 1224), ('palette', 2448)]
    written = []
    for ci, (n, p) in enumerate(zip(range(1, 6), P)):
        d = dict(D)
        for kind, y in ROWS:
            fn = f'pal-{n}-{p["id"]}-{kind}.dc.html'
            if kind == 'chiaro':
                html = page(f'Palette {p["name"]} — Movimenti chiaro', d, p['light'], gen.B_mov(d, p['light'], False)); title = f'{n} · {p["name"]} — chiaro'
            elif kind == 'scuro':
                html = page(f'Palette {p["name"]} — Movimenti scuro', d, p['dark'], gen.B_mov(d, p['dark'], True)); title = f'{n} · {p["name"]} — scuro'
            else:
                html = page(f'Palette {p["name"]} — colori', d, p['light'], tile(p)); title = f'{n} · {p["name"]} — colori'
            open(os.path.join(OUT, fn), 'w').write(html)
            canvas['boards'][fn] = {'x': X[ci], 'y': y, 'w': W, 'h': H, 'title': title, 'page': 'palette'}
            if fn not in canvas['order']: canvas['order'].append(fn)
            written.append(fn)
    canvas['notes']['palTitle1'] = {'x': 0, 'y': -260, 'text': 'Vivace · tema chiaro', 'kind': 'title1', 'maxW': 2270, 'page': 'palette'}
    canvas['notes']['palTitle2'] = {'x': 0, 'y': 964, 'text': 'Vivace · tema scuro', 'kind': 'title1', 'maxW': 2270, 'page': 'palette'}
    canvas['notes']['palTitle3'] = {'x': 0, 'y': 2188, 'text': 'Le palette: colori e contrasti', 'kind': 'title1', 'maxW': 2270, 'page': 'palette'}
    canvas['notes']['palNote'] = {'x': 2350, 'y': 0, 'w': 320, 'size': 'm', 'fill': 'blue', 'page': 'palette',
      'text': "Colonna = palette. Fissi in tutte: grafici blu/arancio (verificati per daltonismo), uscite col colore del testo, entrate in verde, tinte delle categorie s1…s8. Ogni testo supera il contrasto 4,5:1. Si possono mescolare: es. sfondo di una, colore principale di un'altra."}
    json.dump(canvas, open(os.path.join(OUT, 'canvas.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(written))

if __name__ == '__main__':
    main()
