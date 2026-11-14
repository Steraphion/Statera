#!/usr/bin/env python3
"""Sei palette di Coolors adattate allo stile Vivace (B), tema chiaro e scuro."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import gen
from gen import icon, tint, page, btn_icon, MOV, MONTHS, DIRS, W, H, OUT
from palettes import B_nav, cr

# ---------------------------------------------------------------- palette
# Chiavi oltre a quelle solite: fab/onfab (pulsante +), expense (colore degli
# importi in uscita; assente = colore del testo), inIcon/outIcon (icone dei
# riquadri Entrate/Uscite), sw (8 tinte di conti e categorie).
P = [
 dict(id='corallo', name='Blu ardesia e corallo', src=['#3D5A80', '#98C1D9', '#E0FBFC', '#EE6C4D', '#293241'],
   roles='Principale blu ardesia, + e uscite nei grafici in corallo, sfondo dal celeste, scuro dal blu notte.',
   fix="Il corallo coincide quasi con l'arancio delle uscite nei grafici: lo uso apposta per entrambi (il + serve quasi sempre a registrare una spesa). Le entrate nei grafici sono il blu della palette; nel testo restano verdi perché la palette non ha un verde.",
   light=dict(bg='#EEF5F7', surf='#FFFFFF', surf2='#E1EDF2', border='#D3E2E9', text='#293241', muted='#55657A',
              primary='#3D5A80', onp='#FFFFFF', accent='#3D5A80', accentSoft='#DCEBF4', income='#1D7A5F',
              fab='#EE6C4D', onfab='#1E2633', inIcon='#1D7A5F', outIcon='#C2472A',
              chIn='#3D5A80', chOut='#EE6C4D', track='#E1EDF2', backdrop='rgba(41,50,65,0.5)'),
   dark=dict(bg='#1A202A', surf='#293241', surf2='#333E50', border='#3D4A5E', text='#E0FBFC', muted='#A3B7C6',
             primary='#98C1D9', onp='#1A202A', accent='#A6CBE0', accentSoft='#2E4560', income='#6FD6A8',
             fab='#EE6C4D', onfab='#1A202A', inIcon='#6FD6A8', outIcon='#F28B70',
             chIn='#98C1D9', chOut='#EE6C4D', track='#333E50', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#2A8C6E', s2='#E0603F', s3='#3D5A80', s4='#8A6E52', s5='#7D62AD', s6='#2E8FB0', s7='#C2577A', s8='#B8892A')),

 dict(id='navy', name='Navy, salvia e crema', src=['#001427', '#708D81', '#F4D58D', '#BF0603', '#8D0801'],
   roles='Navy per testo e pulsanti, crema per le azioni rapide, rosso per il + e le uscite, salvia per le entrate.',
   fix="Qui rosso e verde nascono dalla palette: uscite in rosso, entrate in salvia scurito (quello originale è troppo chiaro per il testo). Il rosso scuro resta per «budget superato». Il tema scuro sul navy con il crema è il più riuscito.",
   light=dict(bg='#FAF6EC', surf='#FFFFFF', surf2='#F3EBD6', border='#E8DEC5', text='#001427', muted='#4F5C66',
              primary='#001427', onp='#F4D58D', accent='#001427', accentSoft='#F4D58D', income='#46695A', expense='#B00502',
              fab='#BF0603', onfab='#FFFFFF', inIcon='#46695A', outIcon='#B00502',
              chIn='#708D81', chOut='#BF0603', track='#F3EBD6', backdrop='rgba(0,20,39,0.5)'),
   dark=dict(bg='#001427', surf='#0A2236', surf2='#132D44', border='#1F3A54', text='#F7EFD9', muted='#A9B6C0',
             primary='#F4D58D', onp='#001427', accent='#F4D58D', accentSoft='#2A3A45', income='#A3C7B6', expense='#FF7A70',
             fab='#D9302A', onfab='#FFFFFF', inIcon='#A3C7B6', outIcon='#FF7A70',
             chIn='#A3C7B6', chOut='#F0564F', track='#132D44', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#4E7A6A', s2='#C8812A', s3='#2F5F8A', s4='#7A6A58', s5='#6E5A94', s6='#2E8584', s7='#A84B6B', s8='#7E8B3A')),

 dict(id='zafferano', name='Blu, oliva e zafferano', src=['#33658A', '#86BBD8', '#758E4F', '#F6AE2D', '#F26419'],
   roles='Principale blu, + in zafferano, entrate in oliva, uscite nei grafici in arancio.',
   fix="Contiene già la coppia blu/arancio adatta ai daltonici: la uso per i grafici. Lo zafferano va solo sul + (con l'icona scura), così l'arancio resta riservato alle uscite. L'oliva è scurito per essere leggibile come testo.",
   light=dict(bg='#F2F6F9', surf='#FFFFFF', surf2='#E3EDF4', border='#D6E3EC', text='#16293A', muted='#526577',
              primary='#33658A', onp='#FFFFFF', accent='#33658A', accentSoft='#DDEBF5', income='#506B2B',
              fab='#F6AE2D', onfab='#16293A', inIcon='#506B2B', outIcon='#C24E0F',
              chIn='#33658A', chOut='#F26419', track='#E3EDF4', backdrop='rgba(22,41,58,0.5)'),
   dark=dict(bg='#0D1822', surf='#16242F', surf2='#20323F', border='#2A3E4D', text='#EEF4F8', muted='#A1B3C2',
             primary='#86BBD8', onp='#0D1822', accent='#93C4DE', accentSoft='#1E3A50', income='#AFCB7A',
             fab='#F6AE2D', onfab='#0D1822', inIcon='#AFCB7A', outIcon='#F68A4E',
             chIn='#86BBD8', chOut='#F26419', track='#20323F', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#758E4F', s2='#E0590F', s3='#33658A', s4='#8A6E4B', s5='#7D5BA6', s6='#2A9187', s7='#C2477A', s8='#C98A12')),

 dict(id='mattone', name='Mattone e acqua', src=['#231F20', '#BB4430', '#7EBDC2', '#F3DFA2', '#EFE6DD'],
   roles="Sfondo avorio, principale e + in mattone, crema per le azioni rapide, acqua per le entrate. È la più vicina ad Ardesia e ottone.",
   fix="Il mattone fa da colore principale, quindi le uscite restano col colore del testo per non sembrare tutte un allarme. Le entrate prendono l'acqua scurito (verde-azzurro), anche nei grafici: acqua chiaro contro mattone scuro si distingue bene anche per i daltonici.",
   light=dict(bg='#EFE6DD', surf='#FFFCF9', surf2='#E6DBCF', border='#DCCFC1', text='#231F20', muted='#5E5550',
              primary='#B03E2B', onp='#FFFFFF', accent='#9C3726', accentSoft='#F3DFA2', income='#2A6E73',
              fab='#BB4430', onfab='#FFFFFF', inIcon='#2A6E73', outIcon='#9C3726',
              chIn='#47939A', chOut='#BB4430', track='#E6DBCF', backdrop='rgba(35,31,32,0.5)'),
   dark=dict(bg='#231F20', surf='#2E2829', surf2='#3A3334', border='#473F40', text='#EFE6DD', muted='#B5A99F',
             primary='#E8806C', onp='#231F20', accent='#F3DFA2', accentSoft='#4A3F2A', income='#8FD0D5',
             fab='#E8806C', onfab='#231F20', inIcon='#8FD0D5', outIcon='#E8806C',
             chIn='#7EBDC2', chOut='#E26A55', track='#3A3334', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#3E8F95', s2='#BB4430', s3='#4F6FA0', s4='#8A6E52', s5='#7C5E99', s6='#B8862A', s7='#B0507A', s8='#6D8040')),

 dict(id='pesca', name='Nero, blu e pesca', src=['#02070A', '#0297DE', '#FC734D'],
   roles='Pulsanti blu con testo nero, + in pesca, testo quasi nero. La più «neobank».',
   fix="Il blu della palette è troppo chiaro per il testo bianco: i pulsanti lo usano con testo nero (6,5:1), e dove il blu fa da testo uso una versione più scura. Blu e pesca sono anche i colori dei grafici; il + in pesca richiama la spesa.",
   light=dict(bg='#F3F6F8', surf='#FFFFFF', surf2='#E6ECF0', border='#DCE3E8', text='#02070A', muted='#56626B',
              primary='#0297DE', onp='#02070A', accent='#026EA3', accentSoft='#DDF0FB', income='#0E7A57',
              fab='#FC734D', onfab='#02070A', inIcon='#0E7A57', outIcon='#D2502A',
              chIn='#0290D4', chOut='#EC5A33', track='#E6ECF0', backdrop='rgba(2,7,10,0.5)'),
   dark=dict(bg='#02070A', surf='#0D161C', surf2='#16222A', border='#1F2E37', text='#EEF4F7', muted='#9AA9B3',
             primary='#0297DE', onp='#02070A', accent='#3DB2F0', accentSoft='#0B2A3D', income='#4FD9A0',
             fab='#FC734D', onfab='#02070A', inIcon='#4FD9A0', outIcon='#FC8A6A',
             chIn='#2AA6EA', chOut='#FC734D', track='#16222A', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#1E8A63', s2='#E8592F', s3='#0287C8', s4='#7A6A58', s5='#8B4FD9', s6='#0C8EA6', s7='#C2417F', s8='#6E8A1F')),

 dict(id='persiano', name='Blu persiano e fucsia', src=['#0931BD', '#FCFFFF', '#D83995'],
   roles='Principale blu persiano, + in fucsia. In pratica Indaco e Ciclamino insieme, le due che ti erano piaciute.',
   fix="Blu e fucsia sono difficili da distinguere per chi non vede il rosso, quindi nei grafici le uscite restano arancio. Il fucsia sta solo sul + (icona, non testo) e nelle tinte delle categorie.",
   light=dict(bg='#F3F5FC', surf='#FCFFFF', surf2='#E6EAF8', border='#DCE1F3', text='#0A1033', muted='#565D7A',
              primary='#0931BD', onp='#FCFFFF', accent='#0931BD', accentSoft='#E1E7FB', income='#0E7A57',
              fab='#D83995', onfab='#FFFFFF', inIcon='#0E7A57', outIcon='#B34A17',
              chIn='#0931BD', chOut='#EB6834', track='#E6EAF8', backdrop='rgba(10,16,51,0.5)'),
   dark=dict(bg='#070B1F', surf='#111735', surf2='#1B2247', border='#262E58', text='#F2F4FF', muted='#A3AACB',
             primary='#8197FF', onp='#070B1F', accent='#8FA3FF', accentSoft='#1E2A66', income='#4FD9A0',
             fab='#E14FA3', onfab='#FFFFFF', inIcon='#4FD9A0', outIcon='#F29A6B',
             chIn='#5C82FF', chOut='#D95926', track='#1B2247', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#1E8A63', s2='#D9622B', s3='#0931BD', s4='#7A6A58', s5='#8B4FD9', s6='#0C8EA6', s7='#D83995', s8='#6E8A1F')),
]

# ---------------------------------------------------------------- Movimenti (B, con colori parametrici)
def mov(d, t, dark):
    sw = d['sw']; exp = t.get('expense', t['text'])
    rows = ''
    for day, net, items in MOV:
        lis = ''
        for ic, s, desc, cat, src, amt, inc in items:
            lis += (f'<li style="display: flex; align-items: center; gap: 14px; padding: 10px 0">'
                    f'<span style="width: 44px; height: 44px; border-radius: 50%; background: {tint(sw[s], 0.15 if not dark else 0.3)}; color: {sw[s] if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center">{icon(ic, 20, sw=2)}</span>'
                    f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 700">{desc}</span>'
                    f'<span style="font-size: 13px; color: {t["muted"]}">{cat} · {src}</span></span>'
                    f'<span style="font-size: 15px; font-weight: 700; color: {t["income"] if inc else exp}">{amt}</span></li>')
        rows += (f'<h2 style="margin: 14px 0 2px; font-size: 13px; font-weight: 600; color: {t["muted"]}; display: flex; justify-content: space-between"><span>{day}</span><span>{net}</span></h2>'
                 f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>')
    qa = ''
    for ic, lab in [('out', 'Spesa'), ('in', 'Entrata'), ('swap', 'Trasferisci'), ('star', 'Preferiti')]:
        qa += (f'<button type="button" style="flex: 1; border: none; background: transparent; padding: 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 8px; font-size: 13px; font-weight: 600">'
               f'<span style="width: 52px; height: 52px; border-radius: 50%; background: {t["accentSoft"]}; color: {t["accent"] if t["accentSoft"] != t["accent"] else t["onp"]}; display: flex; align-items: center; justify-content: center">{icon(ic, 22, sw=2.1)}</span>{lab}</button>')
    tilebox = lambda ic, col, lab, val: (
        f'<div style="flex: 1; background: {t["surf"]}; border-radius: 20px; padding: 14px; display: flex; align-items: center; gap: 10px">'
        f'<span style="width: 32px; height: 32px; border-radius: 50%; background: {tint(col, 0.16 if not dark else 0.22)}; color: {col}; display: flex; align-items: center; justify-content: center">{icon(ic, 18, sw=2.2)}</span>'
        f'<span style="display: flex; flex-direction: column"><span style="font-size: 12px; color: {t["muted"]}">{lab}</span><span style="font-size: 16px; font-weight: 800">{val}</span></span></div>')
    return f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 20px">
<header style="display: flex; align-items: center; gap: 10px">
<span aria-hidden="true" style="width: 40px; height: 40px; border-radius: 50%; background: {t['primary']}; color: {t['onp']}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px">L</span>
<button type="button" style="height: 40px; padding: 0 14px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 6px">Novembre 2026{icon('chevD', 18)}</button>
<span style="flex: 1"></span>
{btn_icon('search', 'Cerca', t, bg=t['surf'])}
</header>
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center; padding: 6px 0 2px">
<span style="font-size: 14px; color: {t['muted']}; font-weight: 500">Saldo del mese</span>
<span style="font-family: {d['head']}; font-size: 46px; font-weight: 800; letter-spacing: -0.03em">+1.325<span style="font-size: 28px">,65 €</span></span>
<span style="font-size: 13px; color: {t['muted']}">Patrimonio 8.412,90 €</span></div>
<div style="display: flex">{qa}</div>
<div style="display: flex; gap: 10px">{tilebox('in', t['inIcon'], 'Entrate', '2.010,00 €')}{tilebox('out', t['outIcon'], 'Uscite', '684,35 €')}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 4px 18px 10px">{rows}</div>
</div>
{B_nav(t, 'Movimenti')}'''

# ---------------------------------------------------------------- scheda palette
def swatch_grid(t):
    rows = [('Sfondo', 'bg'), ('Superficie', 'surf'), ('Testo', 'text'), ('Attenuato', 'muted'),
            ('Principale', 'primary'), ('Accento tenue', 'accentSoft'), ('Pulsante +', 'fab'), ('Entrate', 'income')]
    if 'expense' in t: rows.append(('Uscite', 'expense'))
    out = ''
    for lab, k in rows:
        out += (f'<div style="display: flex; flex-direction: column; gap: 3px"><span style="height: 30px; border-radius: 9px; background: {t[k]}; border: 1px solid {t["border"]}"></span>'
                f'<span style="font-size: 10px; line-height: 1.25; color: {t["muted"]}">{lab}<br><span style="font-family: ui-monospace, monospace; color: {t["text"]}">{t[k]}</span></span></div>')
    return f'<div style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px">{out}</div>'

def mini_chart(t):
    mx = 2240; out = ''
    for m, i, o in MONTHS:
        out += (f'<div style="flex: 1; display: flex; align-items: flex-end; justify-content: center; gap: 3px; height: 44px">'
                f'<span style="width: 9px; height: {round(i/mx*44)}px; border-radius: 3px 3px 0 0; background: {t["chIn"]}"></span>'
                f'<span style="width: 9px; height: {round(o/mx*44)}px; border-radius: 3px 3px 0 0; background: {t["chOut"]}"></span></div>')
    return (f'<div role="img" aria-label="Esempio di grafico entrate e uscite" style="display: flex; align-items: flex-end; gap: 10px; background: {t["surf"]}; border-radius: 16px; padding: 10px 12px">'
            f'<div style="flex: 1; display: flex; border-bottom: 1px solid {t["border"]}">{out}</div>'
            f'<div style="display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: {t["muted"]}">'
            f'<span style="display: flex; align-items: center; gap: 5px"><span style="width: 8px; height: 8px; border-radius: 2px; background: {t["chIn"]}"></span>Entrate</span>'
            f'<span style="display: flex; align-items: center; gap: 5px"><span style="width: 8px; height: 8px; border-radius: 2px; background: {t["chOut"]}"></span>Uscite</span></div></div>')

def mini(t):
    exp = t.get('expense', t['text'])
    return f'''<div style="display: flex; align-items: center; gap: 10px">
<button type="button" style="flex: 1; height: 42px; border-radius: 21px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 14px; font-weight: 800">Salva spesa</button>
<span style="width: 42px; height: 42px; border-radius: 50%; background: {t['accentSoft']}; color: {t['accent'] if t['accentSoft'] != t['accent'] else t['onp']}; display: flex; align-items: center; justify-content: center">{icon('swap', 19, sw=2.1)}</span>
<span style="width: 42px; height: 42px; border-radius: 50%; background: {t['fab']}; color: {t['onfab']}; display: flex; align-items: center; justify-content: center">{icon('plus', 21, sw=2.4)}</span></div>
<div style="display: flex; justify-content: space-between; align-items: center; background: {t['surf']}; border-radius: 14px; padding: 9px 14px; font-size: 13px; font-weight: 700">
<span>Stipendio</span><span style="color: {t['income']}">+1.850,00 €</span><span>Conad</span><span style="color: {exp}">−42,30 €</span></div>
{mini_chart(t)}'''

def tile(p):
    L, K = p['light'], p['dark']
    hdr = 'font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em'
    src = ''.join(f'<span style="flex: 1; height: 26px; background: {c}"></span>' for c in p['src'])
    tints = ''.join(f'<span style="flex: 1; height: 14px; border-radius: 3px; background: {c}"></span>' for c in p['sw'].values())
    return f'''<div style="height: 100%; display: flex; flex-direction: column">
<div style="flex: 1; padding: 18px 18px 14px; display: flex; flex-direction: column; gap: 10px; background: {L['bg']}; color: {L['text']}">
<h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">{p['name']}</h1>
<div style="display: flex; flex-direction: column; gap: 4px"><span style="{hdr}; color: {L['muted']}">Palette originale (Coolors)</span>
<div style="display: flex; border-radius: 8px; overflow: hidden; border: 1px solid {L['border']}">{src}</div></div>
<span style="{hdr}; color: {L['muted']}">Tema chiaro</span>{swatch_grid(L)}{mini(L)}
<div style="display: flex; flex-direction: column; gap: 4px"><span style="{hdr}; color: {L['muted']}">Tinte categorie s1…s8</span><div style="display: flex; gap: 3px">{tints}</div></div></div>
<div style="flex: 1; padding: 14px 18px 18px; display: flex; flex-direction: column; gap: 10px; background: {K['bg']}; color: {K['text']}">
<span style="{hdr}; color: {K['muted']}">Tema scuro</span>{swatch_grid(K)}{mini(K)}</div></div>'''

# ---------------------------------------------------------------- contrasti
def check():
    bad = 0
    print('palette     tema  testo attenuato suPrincipale accento entrate uscite iconaPiù')
    for p in P:
        for k in ('light', 'dark'):
            t = p[k]
            acc = t['accent'] if t['accentSoft'] != t['accent'] else t['onp']
            v = [cr(t['text'], t['bg']), min(cr(t['muted'], t['surf']), cr(t['muted'], t['bg'])), cr(t['onp'], t['primary']),
                 cr(acc, t['accentSoft']), cr(t['income'], t['surf']), cr(t.get('expense', t['text']), t['surf']), cr(t['onfab'], t['fab'])]
            low = [i for i, x in enumerate(v[:6]) if x < 4.5] + ([6] if v[6] < 3 else [])
            bad += len(low)
            print(f"{p['id']:10} {k:5} " + ' '.join(f'{x:5.1f}' for x in v) + ('   <-- ' + str(low) if low else ''))
    return bad

def main():
    if check():
        print('CONTRASTI INSUFFICIENTI'); return
    canvas = json.load(open(sys.argv[1]))
    pages = [pg['id'] for pg in canvas['pages']]
    if 'coolors' not in pages:
        canvas['pages'].append({'id': 'coolors', 'name': 'Palette da Coolors'})
    canvas['launch'] = {'view': 'canvas', 'page': 'coolors'}
    X = [i * 470 for i in range(6)]
    ROWS = [('chiaro', 0), ('scuro', 1224), ('palette', 2448)]
    written = []
    for ci, p in enumerate(P):
        d = dict(DIRS['B']); d['sw'] = p['sw']; n = ci + 1
        for kind, y in ROWS:
            fn = f'cool-{n}-{p["id"]}-{kind}.dc.html'
            if kind == 'chiaro':
                html = page(f'{p["name"]} — Movimenti chiaro', d, p['light'], mov(d, p['light'], False)); title = f'{n} · {p["name"]} — chiaro'
            elif kind == 'scuro':
                html = page(f'{p["name"]} — Movimenti scuro', d, p['dark'], mov(d, p['dark'], True)); title = f'{n} · {p["name"]} — scuro'
            else:
                html = page(f'{p["name"]} — colori', d, p['light'], tile(p)); title = f'{n} · {p["name"]} — colori'
            open(os.path.join(OUT, fn), 'w').write(html)
            canvas['boards'][fn] = {'x': X[ci], 'y': y, 'w': W, 'h': H, 'title': title, 'page': 'coolors'}
            if fn not in canvas['order']: canvas['order'].append(fn)
            written.append(fn)
        canvas['notes'][f'coolFix{n}'] = {'x': X[ci], 'y': 2448 + H + 80, 'w': 390, 'size': 's', 'fill': 'teal', 'page': 'coolors',
                                          'text': f"{p['name']}. {p['roles']} Conflitti: {p['fix']}"}
    canvas['notes']['coolT1'] = {'x': 0, 'y': -260, 'text': 'Palette da Coolors · tema chiaro', 'kind': 'title1', 'maxW': 2740, 'page': 'coolors'}
    canvas['notes']['coolT2'] = {'x': 0, 'y': 964, 'text': 'Palette da Coolors · tema scuro', 'kind': 'title1', 'maxW': 2740, 'page': 'coolors'}
    canvas['notes']['coolT3'] = {'x': 0, 'y': 2188, 'text': 'Colori, contrasti e grafici', 'kind': 'title1', 'maxW': 2740, 'page': 'coolors'}
    json.dump(canvas, open(os.path.join(OUT, 'canvas.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(written))

if __name__ == '__main__':
    main()
