#!/usr/bin/env python3
"""Indaco morbido: le schermate mobili che mancavano (dati di esempio).
Conti con buoni pasto e obiettivi, dettaglio conto, Cerca, Altro, Ricorrenti, Categorie,
blocco col PIN, guida al primo avvio, stati vuoti, avvisi e conferma. Tema chiaro e scuro."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import icon, tint, btn_icon, seg, DIRS, W, H, MOV, PICK
from palettes import B_nav, cr
import coolors, chosen
from scelta import IND_L, IND_D, IND_SW, oklch

# ---------------------------------------------------------------- palette (Indaco morbido + due ruoli nuovi)
# warn: budget "quasi esaurito" (già usato in Analisi). danger: solo azioni distruttive (Elimina).
L = dict(IND_L, warn='#A86A00', danger=oklch(.52, .16, 25), onDanger='#FFFFFF')
K = dict(IND_D, warn='#F2B13C', danger=oklch(.75, .13, 25))
K['onDanger'] = K['bg']
# avviso "a comparsa" (toast): colori invertiti rispetto al tema
L.update(toast=L['text'], onToast='#FFFFFF', toastAction=K['primary'])
K.update(toast=K['text'], onToast=K['bg'], toastAction=L['primary'])
SW = IND_SW
D = dict(DIRS['B']); D['sw'] = SW
THEMES = [('chiaro', L, False), ('scuro', K, True)]

# ---------------------------------------------------------------- icone dell'interfaccia (non categorie)
gen.IC.update({
 'lock': '<rect x="4.5" y="10.5" width="15" height="10" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
 'finger': '<path d="M6.3 7.2A7.5 7.5 0 0 1 19.5 12v1"/><path d="M4.5 12a7.5 7.5 0 0 1 .5-2.6"/><path d="M8 18.5c.6-1.6 1-3.4 1-5.5a3 3 0 0 1 6 0v1.5"/><path d="M12 13v1.5c0 2.6-.6 4.8-1.6 6.5"/><path d="M15 17.5c-.2 1.2-.6 2.4-1 3.5"/><path d="M5.2 15.5c.4 1.2.5 2.3.3 3.5"/>',
 'cloud': '<path d="M7 18.5h10a4 4 0 0 0 .7-7.95A6 6 0 0 0 6.2 9.6 4.5 4.5 0 0 0 7 18.5z"/>',
 'cloudok': '<path d="M7 18.5h10a4 4 0 0 0 .7-7.95A6 6 0 0 0 6.2 9.6 4.5 4.5 0 0 0 7 18.5z"/><path d="M9.5 14l2 2 3.5-3.5"/>',
 'shield': '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
 'download': '<path d="M12 4v11M7.5 10.5L12 15l4.5-4.5M5 20h14"/>',
 'upload': '<path d="M12 15V4M7.5 8.5L12 4l4.5 4.5M5 20h14"/>',
 'trash': '<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13M10 11v5M14 11v5"/>',
 'key': '<circle cx="8" cy="15" r="4"/><path d="M11 12l8-8M16 7l2.5 2.5M14 9l2 2"/>',
 'moon': '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
 'refresh': '<path d="M20 11a8 8 0 0 0-14.3-4.6L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.6L20 16M20 20v-4h-4"/>',
 'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
 'filter': '<path d="M4 6h16M7 12h10M10 18h4"/>',
 'tag': '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.2"/>',
 'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
 'bank': '<path d="M3 9l9-5 9 5M5 9v9M9.5 9v9M14.5 9v9M19 9v9M3 20h18"/>',
 'cash': '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 9.5h.01M18 14.5h.01"/>',
 'piggy': '<path d="M4.5 11.5a6.5 5.5 0 0 1 6.5-5h3a6.5 5.5 0 0 1 5.6 3H21v4h-1.4a6 6 0 0 1-2.6 2.7V20h-3v-2h-3v2H8v-3.2a5.5 5.5 0 0 1-3.5-5.3z"/><path d="M15.5 10.5h.01M10 6.5V4.5"/>',
 'scale': '<path d="M12 4v16M8 20h8M5 7h14M5 7l-2.5 6a2.5 2.5 0 0 0 5 0zM19 7l-2.5 6a2.5 2.5 0 0 0 5 0z"/>',
 'phone': '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
 'wifioff': '<path d="M3 3l18 18M8.5 16.5a5 5 0 0 1 7 0M5 12.5a10 10 0 0 1 4.2-2.3M13 10.1a10 10 0 0 1 6 2.4M2 9a15 15 0 0 1 4.5-2.8M10.5 5.1A15 15 0 0 1 22 9M12 20h.01"/>',
 'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
 'unlink': '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/><path d="M3 3l18 18"/>',
 'keyboard': '<rect x="2.5" y="6" width="19" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/>',
 'receipt': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
 'del': '<path d="M21 6H9l-6 6 6 6h12z"/><path d="M12 9.5l5 5M17 9.5l-5 5"/>',
 'checkc': '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.8L16 10"/>',
 'pause': '<rect x="6.5" y="5" width="3.5" height="14" rx="1"/><rect x="14" y="5" width="3.5" height="14" rx="1"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'table': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9.5h18M3 15h18M9 4v16"/>',
 'arrowR': '<path d="M5 12h14M13 6l6 6-6 6"/>',
 'up': '<path d="M7 17L17 7M9 7h8v8"/>',
 'down': '<path d="M7 7l10 10M17 9v8H9"/>',
 'palette': '<path d="M12 3a9 9 0 0 0 0 18c1.2 0 1.8-.8 1.8-1.7 0-1.3-1.1-1.6-1.1-2.8 0-1 .8-1.7 1.8-1.7H17a4 4 0 0 0 4-4C21 6.6 17 3 12 3z"/><path d="M7.5 11.5h.01M10 7.5h.01M15 7.5h.01"/>',
})

# ---------------------------------------------------------------- mattoni comuni
def page_h(title, t, body, h):
    return chosen.page_h(title, D, t, body, h)

def sr(txt):
    return f'<span style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap">{txt}</span>'

def h1(txt, size=26):
    return f'<h1 style="margin: 0; font-size: {size}px; font-weight: 800; letter-spacing: -0.02em">{txt}</h1>'

def h2(txt, right='', size=17):
    return (f'<div style="display: flex; align-items: center; justify-content: space-between; gap: 8px">'
            f'<h2 style="margin: 0; font-size: {size}px; font-weight: 800">{txt}</h2>{right}</div>')

def card(inner, t, gap=14, pad='18px', extra=''):
    return f'<section style="background: {t["surf"]}; border-radius: 24px; padding: {pad}; display: flex; flex-direction: column; gap: {gap}px; {extra}">{inner}</section>'

def muted(txt, t, size=13, extra=''):
    return f'<span style="font-size: {size}px; color: {t["muted"]}; {extra}">{txt}</span>'

def pill(label, t, ic=None, kind='surf', h=40, fs=14, aria=None):
    bg, fg, icol = {'surf': (t['surf'], t['text'], t['accent']), 'soft': (t['accentSoft'], t['accent'], t['accent']),
                    'primary': (t['primary'], t['onp'], t['onp']), 'bg': (t['bg'], t['text'], t['accent']),
                    'surf2': (t['surf2'], t['text'], t['accent']), 'danger': (t['danger'], t['onDanger'], t['onDanger'])}[kind]
    ico = icon(ic, 16, icol, sw=2.1) if ic else ''
    al = f' aria-label="{aria}"' if aria else ''
    return (f'<button type="button"{al} style="height: {h}px; padding: 0 {14 if ic else 16}px; border-radius: {h // 2}px; border: none; background: {bg}; color: {fg}; '
            f'font: inherit; font-size: {fs}px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 6px; white-space: nowrap; flex-shrink: 0">{ico}{label}</button>')

def big_btn(label, t, kind='primary', ic=None):
    bg, fg = (t['primary'], t['onp']) if kind == 'primary' else ((t['danger'], t['onDanger']) if kind == 'danger' else (t['surf'], t['text']))
    ico = icon(ic, 20, sw=2.2) if ic else ''
    return (f'<button type="button" style="height: 58px; border-radius: 29px; border: none; background: {bg}; color: {fg}; font: inherit; font-size: 17px; font-weight: 800; '
            f'display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%">{ico}{label}</button>')

def link_btn(label, t, size=14):
    return f'<button type="button" style="height: 44px; border: none; background: transparent; color: {t["accent"]}; font: inherit; font-size: {size}px; font-weight: 700; align-self: center">{label}</button>'

def cat_circle(ic, s, t, dark, size=44, isz=20, letter=None):
    """Icona di categoria: colore della tinta su cerchio tenue. Senza icona: l'iniziale."""
    c = SW[s]
    inner = icon(ic, isz, sw=2) if ic else f'<span style="font-size: {round(size * 0.42)}px; font-weight: 800; line-height: 1">{letter}</span>'
    return (f'<span aria-hidden="true" style="width: {size}px; height: {size}px; border-radius: 50%; background: {tint(c, 0.15 if not dark else 0.3)}; '
            f'color: {c if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center; flex-shrink: 0">{inner}</span>')

def ui_circle(ic, t, size=36, isz=18, bg=None, fg=None):
    return (f'<span aria-hidden="true" style="width: {size}px; height: {size}px; border-radius: 50%; background: {bg or t["accentSoft"]}; color: {fg or t["accent"]}; '
            f'display: flex; align-items: center; justify-content: center; flex-shrink: 0">{icon(ic, isz, sw=2)}</span>')

def texts(title, sub, t, tsize=15, extra=''):
    s = f'<span style="font-size: 13px; color: {t["muted"]}">{sub}</span>' if sub else ''
    return (f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; {extra}">'
            f'<span style="font-size: {tsize}px; font-weight: 700">{title}</span>{s}</span>')

def bar(pct, col, t, h=8):
    return (f'<span aria-hidden="true" style="height: {h}px; border-radius: {h // 2}px; background: {t["track"]}; display: block">'
            f'<span style="display: block; height: {h}px; width: {min(pct, 100)}%; border-radius: {h // 2}px; background: {col}"></span></span>')

def ring(pct, col, t, size=60, stroke=6, label=''):
    r = (size - stroke) / 2; c = 2 * math.pi * r; off = c * (1 - pct / 100)
    return (f'<span role="img" aria-label="{label or str(pct) + "% raggiunto"}" style="position: relative; width: {size}px; height: {size}px; flex-shrink: 0; display: flex; align-items: center; justify-content: center">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="position: absolute; left: 0; top: 0; transform: rotate(-90deg)">'
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{t["track"]}" stroke-width="{stroke}"/>'
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{col}" stroke-width="{stroke}" stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}"/></svg>'
            f'<span style="position: relative; font-size: {13 if size >= 56 else 11}px; font-weight: 800">{pct}%</span></span>')

def switch(on, t, label):
    return (f'<button type="button" role="switch" aria-checked="{"true" if on else "false"}" aria-label="{label}" style="width: 52px; height: 32px; border-radius: 16px; border: none; padding: 3px; '
            f'background: {t["primary"] if on else t["border"]}; display: flex; justify-content: {"flex-end" if on else "flex-start"}; align-items: center; flex-shrink: 0">'
            f'<span style="width: 26px; height: 26px; border-radius: 50%; background: {t["onp"] if on else t["surf"]}; color: {t["primary"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.18)">'
            f'{icon("check", 14, sw=2.6) if on else ""}</span></button>')

def srow(ic, label, t, sub=None, value=None, chev=True, color=None, icbg=None, icfg=None):
    val = f'<span style="font-size: 14px; color: {t["muted"]}; white-space: nowrap">{value}</span>' if value else ''
    return (f'<a href="#" style="display: flex; align-items: center; gap: 12px; padding: 8px 0; text-decoration: none; color: {color or t["text"]}">'
            f'{ui_circle(ic, t, bg=icbg, fg=icfg)}{texts(label, sub, t)}{val}{icon("chevR", 18, t["muted"]) if chev else ""}</a>')

def trow(ic, label, t, on, sub=None):
    return (f'<div style="display: flex; align-items: center; gap: 12px; padding: 8px 0">{ui_circle(ic, t)}{texts(label, sub, t)}{switch(on, t, label)}</div>')

def kbd(k, t, on_primary=False):
    bg = tint(t['onp'], 0.18) if on_primary else t['surf2']
    fg = t['onp'] if on_primary else t['muted']
    bd = 'transparent' if on_primary else t['border']
    return (f'<kbd style="min-width: 24px; height: 24px; padding: 0 6px; box-sizing: border-box; border-radius: 7px; background: {bg}; color: {fg}; border: 1px solid {bd}; '
            f'font: inherit; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0">{k}</kbd>')

def qa_row(items, t):
    out = ''
    for ic, lab in items:
        out += (f'<button type="button" style="flex: 1; border: none; background: transparent; padding: 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 8px; font-size: 13px; font-weight: 600">'
                f'<span style="width: 52px; height: 52px; border-radius: 50%; background: {t["accentSoft"]}; color: {t["accent"]}; display: flex; align-items: center; justify-content: center">{icon(ic, 22, sw=2.1)}</span>{lab}</button>')
    return f'<div style="display: flex">{out}</div>'

def top(title, t, right=''):
    return (f'<header style="display: flex; align-items: center; gap: 12px">{btn_icon("chevL", "Indietro", t, bg=t["surf"])}'
            f'<h1 style="margin: 0; flex: 1; min-width: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">{title}</h1>{right}</header>')

def wrap(inner, gap=18, pad='16px 20px 0'):
    return f'<div style="padding: {pad}; display: flex; flex-direction: column; gap: {gap}px">{inner}</div>'

def amount_big(intpart, dec, size=46, small=28):
    return f'<span style="font-size: {size}px; font-weight: 800; letter-spacing: -0.03em">{intpart}<span style="font-size: {small}px">{dec}</span></span>'

SPACER = '<div aria-hidden="true" style="height: 96px"></div>'

# ================================================================ Conti
CONTI = [('bank', 's3', 'Conto corrente', 'Carta collegata: Bancomat', '6.940,55 €'),
         ('cash', 's1', 'Contanti', 'Portafoglio', '148,20 €'),
         ('piggy', 's6', 'Conto risparmi', 'Per «Vacanza estate»', '1.228,15 €')]
GOALS = [('Vacanza estate', 's6', 61, '1.228,15 €', '2.000,00 €', 'Mancano 771,85 € · circa 110 € al mese fino a giugno 2027', 'Sul Conto risparmi'),
         ('Fondo imprevisti', 's5', 20, '600,00 €', '3.000,00 €', 'Mancano 2.400,00 €', 'Accantonati a mano')]

def tickets(t, dark, n_left=12, n_used=6, cols=9, h=22):
    c = SW['s2']
    pips = ''
    for i in range(n_left + n_used):
        if i < n_left:
            pips += f'<span style="height: {h}px; border-radius: 6px; background: {tint(c, 0.85) if not dark else tint(c, 0.9)}"></span>'
        else:
            pips += f'<span style="height: {h}px; box-sizing: border-box; border-radius: 6px; border: 1.5px dashed {t["muted"]}; opacity: 0.6"></span>'
    return (f'<div role="img" aria-label="Novembre: {n_left + n_used} buoni ricevuti, {n_used} usati, {n_left} rimasti" '
            f'style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 5px">{pips}</div>')

def goal_row(g, t, dark, size=60):
    name, s, pct, have, tot, line, where = g
    return (f'<li style="display: flex; align-items: center; gap: 14px">{ring(pct, SW[s], t, size=size, label=f"{name}: {pct}% raggiunto")}'
            f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px">'
            f'<span style="display: flex; justify-content: space-between; gap: 8px; font-size: 15px"><span style="font-weight: 800">{name}</span><span style="font-size: 12px; color: {t["muted"]}; font-weight: 600">{where}</span></span>'
            f'<span style="font-size: 14px"><span style="font-weight: 700">{have}</span><span style="color: {t["muted"]}"> di {tot}</span></span>'
            f'<span style="font-size: 13px; color: {t["muted"]}">{line}</span></span></li>')

def conti(d, t, dark):
    rows = ''
    for ic, s, name, sub, amt in CONTI:
        rows += (f'<li><a href="#" style="display: flex; align-items: center; gap: 14px; padding: 8px 0; text-decoration: none; color: {t["text"]}">{cat_circle(ic, s, t, dark)}'
                 f'{texts(name, sub, t)}<span style="font-size: 15px; font-weight: 800; white-space: nowrap">{amt}</span>{icon("chevR", 18, t["muted"])}</a></li>')
    buoni = card(f'''<div style="display: flex; align-items: center; gap: 14px">{cat_circle('ticket', 's2', t, dark)}
<span style="flex: 1; display: flex; flex-direction: column; gap: 2px"><h2 style="margin: 0; font-size: 17px; font-weight: 800">Buoni pasto</h2>{muted('Valore di un buono: 8,00 €', t)}</span>
<a href="#" aria-label="Apri il conto Buoni pasto" style="color: {t['muted']}">{icon('chevR', 18)}</a></div>
<div style="display: flex; align-items: baseline; gap: 10px"><span style="font-size: 34px; font-weight: 800; letter-spacing: -0.03em">12 buoni</span><span style="font-size: 16px; font-weight: 700; color: {t['muted']}">96,00 €</span></div>
{tickets(t, dark)}
<div style="display: flex; justify-content: space-between; font-size: 13px; color: {t['muted']}"><span>Ricevuti a novembre: 18</span><span>Usati: 6 · Restano: 12</span></div>''', t, gap=12)
    goals = ''.join(goal_row(g, t, dark) for g in GOALS)
    body = f'''{h1('Conti')}
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center; padding: 4px 0 2px">
{muted('Patrimonio', t, 14, 'font-weight: 500')}
{amount_big('8.412', ',90 €')}
{muted('4 conti attivi · 1 archiviato', t)}</div>
{qa_row([('plus', 'Nuovo conto'), ('swap', 'Trasferisci'), ('target', 'Obiettivo'), ('list', 'Ordina')], t)}
{card(h2('I tuoi conti') + f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px">{rows}</ul>', t, gap=8, pad='18px 18px 10px')}
{buoni}
{card(h2('Obiettivi di risparmio', pill('Nuovo', t, 'plus', 'soft', h=36, fs=13)) + f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 18px">{goals}</ul>', t, gap=16)}
{link_btn('Conti archiviati (1)', t)}
{SPACER}'''
    return wrap(body) + B_nav(t, 'Conti')
CONTI_H = 1280

# ================================================================ Dettaglio conto
DET = [
 ('Sabato 14 novembre', [('cart', 's1', 'Conad', 'Spesa alimentare · Bancomat', '−42,30 €', '6.940,55 €', False, False)]),
 ('Venerdì 13 novembre', [('fuel', 's3', 'Q8 via Appia', 'Carburante · Bancomat', '−50,00 €', '6.982,85 €', False, False),
                          ('repeat', 's5', 'Musica in streaming', 'Abbonamenti', '−11,99 €', '7.032,85 €', False, False)]),
 ('Giovedì 12 novembre', [('work', 's6', 'Stipendio ottobre', 'Stipendio', '+1.850,00 €', '7.044,84 €', True, False)]),
 ('Martedì 10 novembre', [('swap', None, 'Prelievo', 'Trasferimento → Contanti', '−100,00 €', '5.194,84 €', False, False)]),
 ('Lunedì 2 novembre', [('home', 's7', 'Bolletta luce e gas', 'Casa › Bollette', '−96,00 €', None, False, True)]),
]

def det_rows(t, dark):
    out = ''
    for day, items in DET:
        lis = ''
        for ic, s, desc, sub, amt, bal, inc, before in items:
            lead = cat_circle(ic, s, t, dark) if s else ui_circle(ic, t, size=44, isz=20)
            right2 = (f'<span style="font-size: 12px; color: {t["muted"]}">saldo {bal}</span>' if bal else
                      f'<span style="height: 22px; padding: 0 8px; border-radius: 11px; background: {t["surf2"]}; color: {t["muted"]}; font-size: 11px; font-weight: 700; display: flex; align-items: center; gap: 4px">{icon("info", 12, sw=2.2)}non incide</span>')
            lis += (f'<li style="display: flex; align-items: center; gap: 14px; padding: 9px 0">{lead}{texts(desc, sub, t)}'
                    f'<span style="display: flex; flex-direction: column; align-items: flex-end; gap: 3px"><span style="font-size: 15px; font-weight: 700; color: {t["income"] if inc else t["text"]}">{amt}</span>{right2}</span></li>')
        out += (f'<h3 style="margin: 12px 0 0; font-size: 13px; font-weight: 600; color: {t["muted"]}">{day}</h3>'
                f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>')
    return out

def dettaglio(d, t, dark):
    tot = lambda lab, val, col=None: (f'<div style="flex: 1; display: flex; flex-direction: column; gap: 2px; align-items: center"><span style="font-size: 12px; color: {t["muted"]}">{lab}</span>'
                                      f'<span style="font-size: 15px; font-weight: 800; color: {col or t["text"]}">{val}</span></div>')
    body = f'''{top('Conto corrente', t, btn_icon('more', 'Altre azioni', t, bg=t['surf']))}
<div style="display: flex; flex-direction: column; gap: 6px; align-items: center">
{cat_circle('bank', 's3', t, dark, size=56, isz=26)}
{muted('Saldo di oggi', t, 14, 'font-weight: 500; margin-top: 4px')}
{amount_big('6.940', ',55 €', 42, 26)}
<span style="height: 28px; padding: 0 12px; border-radius: 14px; background: {t['surf']}; display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600">{icon('card', 15, t['accent'], sw=2)}Carta collegata: Bancomat</span></div>
{qa_row([('out', 'Spesa'), ('in', 'Entrata'), ('swap', 'Trasferisci'), ('scale', 'Allinea saldo')], t)}
<div style="display: flex; align-items: center; justify-content: center; gap: 8px">{btn_icon('chevL', 'Mese precedente', t, bg=t['surf'])}<span style="font-size: 16px; font-weight: 800; min-width: 150px; text-align: center">Novembre 2026</span>{btn_icon('chevR', 'Mese successivo', t, bg=t['surf'])}</div>
<div style="background: {t['surf']}; border-radius: 20px; padding: 12px 8px; display: flex">{tot('Entrate', '+1.850,00 €', t['income'])}{tot('Uscite', '−200,29 €')}{tot('Trasferimenti', '−100,00 €')}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 4px 18px 14px">{det_rows(t, dark)}
<div style="margin-top: 10px; padding-top: 12px; border-top: 1px dashed {t['border']}; display: flex; align-items: center; gap: 12px">
<span style="flex: 1; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 14px; font-weight: 700">Saldo iniziale</span>{muted('Dal 3 novembre 2026: i movimenti precedenti contano nei totali del mese, non nel saldo', t, 12)}</span>
<span style="font-size: 15px; font-weight: 800">5.294,84 €</span></div></div>'''
    return wrap(body, gap=18)
DET_H = 1160

# ================================================================ Cerca
CER = [('Novembre 2026', [('Pranzo', '', '14 nov · 1 buono pasto', '−8,00 €'), ('Pranzo', '', '11 nov · 1 buono pasto', '−8,00 €'),
                          ('Pranzo', ' di lavoro', '6 nov · Bancomat', '−14,50 €')]),
       ('Ottobre 2026', [('Pranzo', '', '29 ott · 3 buoni + Bancomat', '−31,40 €'), ('Pranzo', ' della domenica', '25 ott · Contanti', '−46,00 €'),
                         ('Pranzo', '', '2 ott · 1 buono pasto', '−8,00 €')])]

def chip(label, t, active=False, ic=None, caret=False, remove=False):
    bg = t['accentSoft'] if active else t['surf']; fg = t['accent'] if active else t['text']
    lead = icon(ic, 15, sw=2.2) if ic else ''
    tail = icon('chevD', 15, sw=2.2) if caret else (icon('x', 14, sw=2.4) if remove else '')
    al = f' aria-label="{label}, togli il filtro"' if remove else ''
    return (f'<button type="button"{al} aria-pressed="{"true" if active else "false"}" style="height: 36px; padding: 0 12px; border-radius: 18px; border: none; background: {bg}; color: {fg}; '
            f'font: inherit; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 5px; white-space: nowrap">{lead}{label}{tail}</button>')

def search_field(value, t, placeholder='Cerca', focus=True, h=48, kb=None):
    ring_ = f'box-shadow: 0 0 0 2px {t["primary"]};' if focus else ''
    clear = (f'<button type="button" aria-label="Cancella la ricerca" style="width: 36px; height: 36px; border-radius: 50%; border: none; background: {t["surf2"]}; color: {t["muted"]}; '
             f'display: flex; align-items: center; justify-content: center; padding: 0">{icon("x", 16, sw=2.2)}</button>') if value else (kbd(kb, t) if kb else '')
    return (f'<label style="flex: 1; min-width: 0; height: {h}px; box-sizing: border-box; border-radius: {h // 2}px; background: {t["surf"]}; {ring_} display: flex; align-items: center; gap: 8px; padding: 0 6px 0 16px; color: {t["muted"]}">'
            f'{icon("search", 18, sw=2)}{sr("Cerca")}<input type="text" value="{value}" placeholder="{placeholder}" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 16px; color: {t["text"]}">{clear}</label>')

def cerca(d, t, dark):
    res = ''
    for month, items in CER:
        lis = ''
        for hit, rest, sub, amt in items:
            mark = f'<mark style="background: {t["accentSoft"]}; color: {t["text"]}; border-radius: 4px; padding: 0 2px">{hit}</mark>{rest}'
            lis += (f'<li style="display: flex; align-items: center; gap: 14px; padding: 8px 0">{cat_circle("food", "s2", t, dark, size=40, isz=19)}{texts(mark, "Pasti fuori · " + sub, t)}'
                    f'<span style="font-size: 15px; font-weight: 700">{amt}</span></li>')
        res += (f'<h3 style="margin: 12px 0 0; font-size: 13px; font-weight: 600; color: {t["muted"]}">{month}</h3>'
                f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>')
    chips = (chip('Uscite', t, True, ic='check') + chip('Ultimi 3 mesi', t, True, caret=True) + chip('Pasti fuori', t, True, remove=True) +
             chip('Tutti i conti', t, caret=True) + chip('Etichette', t, caret=True) + chip('Importo', t, caret=True))
    body = f'''<div style="display: flex; align-items: center; gap: 10px">{btn_icon('chevL', 'Indietro', t, bg=t['surf'])}{search_field('pranzo', t)}</div>
<div role="group" aria-label="Filtri" style="display: flex; flex-wrap: wrap; gap: 8px">{chips}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 16px 18px; display: flex; align-items: center; gap: 12px">
<span style="flex: 1; display: flex; flex-direction: column; gap: 2px">{muted('6 risultati negli ultimi 3 mesi', t)}<span style="font-size: 26px; font-weight: 800; letter-spacing: -0.02em">−115,90 €</span></span>
{pill('Esporta CSV', t, 'download', 'soft')}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 4px 18px 12px">{res}</div>'''
    return wrap(body, gap=16)

# ================================================================ Altro
def altro(d, t, dark):
    ok = t['income']
    body = f'''{h1('Altro')}
<a href="#" style="background: {t['surf']}; border-radius: 24px; padding: 16px 18px; display: flex; align-items: center; gap: 14px; text-decoration: none; color: {t['text']}">
<span aria-hidden="true" style="width: 48px; height: 48px; border-radius: 50%; background: {t['primary']}; color: {t['onp']}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 19px; flex-shrink: 0">L</span>
{texts('Livio', 'esempio@gmail.com · profilo attivo', t, 17)}<span style="font-size: 14px; font-weight: 700; color: {t['accent']}">Cambia</span></a>
{card(f"""{h2('Sincronizzazione')}
<div style="display: flex; align-items: center; gap: 12px; background: {t['bg']}; border-radius: 18px; padding: 12px 14px">
{ui_circle('cloudok', t, 40, 20, bg=tint(ok, 0.16 if not dark else 0.22), fg=ok)}
{texts('Sincronizzato', '2 minuti fa · cifrato su Google Drive', t)}
{pill('Ora', t, 'refresh', 'soft', h=36, fs=13, aria='Sincronizza ora')}</div>
<div style="display: flex; flex-direction: column">
{srow('key', 'Password e chiave di recupero', t)}
{srow('users', 'Aggiungi un altro account', t)}
{srow('unlink', 'Scollega questo dispositivo', t, sub='I dati restano qui e su Drive')}</div>""", t, gap=12)}
{card(f"""{h2('Backup')}
<div style="display: flex; flex-direction: column">
{srow('cloud', 'Backup su Drive', t, sub='Ogni giorno, ultimo oggi alle 9:12 · ne tengo 30')}
{srow('download', 'Esporta un backup', t, sub='File protetto da password')}
{srow('upload', 'Ripristina da un backup', t)}</div>""", t, gap=8)}
{card(f"""{h2('Blocco dell’app')}
<div style="display: flex; flex-direction: column">
{trow('lock', 'Blocca con PIN', t, True)}
{trow('finger', 'Sblocca con l’impronta', t, True)}
{srow('clock', 'Blocca dopo', t, value='1 minuto')}</div>""", t, gap=8)}
{card(f"""{h2('Organizza')}
<div style="display: flex; flex-direction: column">
{srow('repeat', 'Ricorrenti', t, value='6 attivi')}
{srow('tag', 'Categorie', t, value='17')}
{srow('star', 'Preferiti', t, value='4')}</div>""", t, gap=8)}
{card(f"""{h2('I tuoi dati')}
<div style="display: flex; flex-direction: column">
{srow('table', 'Importa da CSV', t, sub='Estratti conto della banca')}
{srow('download', 'Esporta per Excel', t)}
{srow('trash', 'Elimina tutti i dati', t, sub='Solo da questo dispositivo', color=t['danger'], icbg=tint(t['danger'], 0.14 if not dark else 0.2), icfg=t['danger'])}</div>""", t, gap=8)}
{card(f"""<div style="display: flex; flex-direction: column">{srow('palette', 'Aspetto', t, value='Automatico')}</div>""", t, gap=0, pad='10px 18px')}
<p style="margin: 0; text-align: center; font-size: 13px; color: {t['muted']}">Statera 0.21.0 · <a href="#" style="color: {t['accent']}; font-weight: 700">Informativa sulla privacy</a></p>
{SPACER}'''
    return wrap(body, gap=16) + B_nav(t, 'Altro')
ALTRO_H = 1820

# ================================================================ Ricorrenti
RIC = [('work', 's6', 'Stipendio', 'Mensile, il 12 · prossimo 12 dic', '+1.850,00 €', True, 'auto'),
       ('bus', 's4', 'Abbonamento bus', 'Mensile, il 12 · prossimo 12 dic', '−35,00 €', False, 'auto'),
       ('repeat', 's5', 'Musica in streaming', 'Mensile, il 13 · prossimo 13 dic', '−11,99 €', False, 'auto'),
       ('home', 's7', 'Bolletta luce e gas', 'Ogni 2 mesi · prossima 2 gen', '−96,00 €', False, 'conf'),
       ('home', 's7', 'Bolletta acqua', 'Ogni 3 mesi · prossima 12 feb', '−48,60 €', False, 'conf'),
       (None, 's4', 'Assicurazione auto', 'Annuale · prossima 3 mar', '−412,00 €', False, 'conf')]

def mode_badge(mode, t):
    ic, lab = {'auto': ('repeat', 'Automatico'), 'conf': ('checkc', 'Da confermare'), 'pause': ('pause', 'Sospeso')}[mode]
    return (f'<span style="height: 22px; padding: 0 8px; border-radius: 11px; background: {t["surf2"] if mode != "auto" else t["accentSoft"]}; color: {t["accent"] if mode == "auto" else t["muted"]}; '
            f'font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; align-self: flex-start">{icon(ic, 12, sw=2.4)}{lab}</span>')

def ric_row(ic, s, name, sub, amt, inc, mode, t, dark, letter=None):
    lead = cat_circle(ic, s, t, dark, letter=letter or name[0])
    return (f'<li><a href="#" style="display: flex; align-items: center; gap: 14px; padding: 9px 0; text-decoration: none; color: {t["text"]}">{lead}'
            f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px"><span style="font-size: 15px; font-weight: 700">{name}</span>'
            f'<span style="font-size: 13px; color: {t["muted"]}">{sub}</span>{mode_badge(mode, t)}</span>'
            f'<span style="font-size: 15px; font-weight: 700; color: {t["income"] if inc else t["text"]}">{amt}</span></a></li>')

def ricorrenti(d, t, dark):
    act = ''.join(ric_row(*r, t, dark) for r in RIC)
    sosp = ric_row(None, 's1', 'Palestra', 'Mensile, il 5 · ferma da ottobre', '−39,00 €', False, 'pause', t, dark)
    due = f'''<section style="background: {t['accentSoft']}; border-radius: 24px; padding: 16px 18px; display: flex; flex-direction: column; gap: 12px">
<h2 style="margin: 0; font-size: 15px; font-weight: 800; color: {t['accent']}; display: flex; align-items: center; gap: 6px">{icon('clock', 16, sw=2.2)}Da registrare</h2>
<div style="display: flex; align-items: center; gap: 12px">{cat_circle('home', 's7', t, dark, size=40, isz=19)}{texts('Bolletta acqua', 'Dovuta il 12 novembre · Conto corrente', t)}<span style="font-size: 15px; font-weight: 800">−48,60 €</span></div>
<div style="display: flex; gap: 8px">{pill('Registra', t, 'check', 'primary', h=40)}{pill('Modifica e registra', t, None, 'surf', h=40)}{pill('Salta', t, None, 'surf', h=40)}</div></section>'''
    body = f'''{top('Ricorrenti', t, pill('Nuovo', t, 'plus', 'surf'))}
<p style="margin: 0; font-size: 14px; line-height: 1.45; color: {t['muted']}">Gli automatici si registrano da soli. Quelli da confermare compaiono qui e in Movimenti, così puoi correggere l’importo.</p>
{due}
{card(h2('Attivi', muted('6', t, 14, 'font-weight: 700')) + f'<ul style="list-style: none; margin: 0; padding: 0">{act}</ul>', t, gap=4, pad='18px 18px 8px')}
{card(h2('Sospesi') + f'<ul style="list-style: none; margin: 0; padding: 0">{sosp}</ul>', t, gap=4, pad='18px 18px 8px')}'''
    return wrap(body, gap=16)
RIC_H = 1120

# ================================================================ Categorie
CATL = [('shirt', 's8', 'Abbigliamento', None, []),
        ('repeat', 's5', 'Abbonamenti', None, []),
        ('more', 's4', 'Altro', None, []),
        ('home', 's7', 'Casa', None, [('home', 'Affitto o mutuo'), (None, 'Bollette'), (None, 'Manutenzione')]),
        ('food', 's2', 'Pasti fuori', '80 € al mese', []),
        ('gift', 's2', 'Regali', None, []),
        ('heart', 's6', 'Salute', None, []),
        ('cart', 's1', 'Spesa alimentare', '300 € al mese', []),
        (None, 's1', 'Sport', None, []),
        ('game', 's5', 'Svago', None, []),
        ('bus', 's4', 'Trasporti', '150 € al mese', [(None, 'Auto'), ('fuel', 'Carburante'), ('bus', 'Mezzi pubblici')]),
        ('plane', 's3', 'Viaggi', None, [])]

def categorie(d, t, dark):
    lis = ''
    for ic, s, name, budget, subs in CATL:
        sub = f'Budget {budget}' if budget else (f'{len(subs)} sottocategorie' if subs else None)
        lis += (f'<li><a href="#" style="display: flex; align-items: center; gap: 14px; padding: 8px 0; text-decoration: none; color: {t["text"]}">{cat_circle(ic, s, t, dark, letter=name[0])}'
                f'{texts(name, sub, t)}{icon("chevR", 18, t["muted"])}</a>')
        if subs:
            sl = ''
            for sic, sname in subs:
                sl += (f'<li><a href="#" style="display: flex; align-items: center; gap: 12px; padding: 6px 0; text-decoration: none; color: {t["text"]}">{cat_circle(sic, s, t, dark, size=32, isz=16, letter=sname[0])}'
                       f'<span style="flex: 1; font-size: 14px; font-weight: 600">{sname}</span>{icon("chevR", 16, t["muted"])}</a></li>')
            lis += (f'<ul aria-label="Sottocategorie di {name}" style="list-style: none; margin: 0 0 4px 21px; padding: 0 0 0 23px; border-left: 2px solid {t["track"]}">{sl}</ul>')
        lis += '</li>'
    body = f'''{top('Categorie', t, pill('Nuova', t, 'plus', 'surf'))}
{seg(['Uscite', 'Entrate'], 'Uscite', t, d, h=44, radius=22, act_bg=t['primary'], act_col=t['onp'])}
<p style="margin: 0; font-size: 14px; line-height: 1.45; color: {t['muted']}">In ordine alfabetico. Tocca una categoria per cambiarne nome, colore e budget o per aggiungere sottocategorie.</p>
{card(f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px">{lis}</ul>', t, gap=0, pad='10px 18px')}
{link_btn('Archiviate (1)', t)}'''
    return wrap(body, gap=16)
CAT_H = 1360

# ================================================================ Blocco col PIN
def blocco(d, t, dark):
    keys = ''
    for k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'F', '0', 'X']:
        if k == 'F':
            keys += (f'<button type="button" aria-label="Sblocca con l’impronta" style="width: 76px; height: 76px; border-radius: 50%; border: none; background: {t["accentSoft"]}; color: {t["accent"]}; '
                     f'display: flex; align-items: center; justify-content: center; justify-self: center; padding: 0">{icon("finger", 30, sw=1.9)}</button>')
        elif k == 'X':
            keys += (f'<button type="button" aria-label="Cancella l’ultima cifra" style="width: 76px; height: 76px; border-radius: 50%; border: none; background: transparent; color: {t["text"]}; '
                     f'display: flex; align-items: center; justify-content: center; justify-self: center; padding: 0">{icon("del", 26, sw=1.9)}</button>')
        else:
            keys += (f'<button type="button" style="width: 76px; height: 76px; border-radius: 50%; border: none; background: {t["surf"]}; color: {t["text"]}; font: inherit; '
                     f'font-size: 28px; font-weight: 700; justify-self: center">{k}</button>')
    dots = ''.join(f'<span style="width: 14px; height: 14px; border-radius: 50%; background: {t["text"]}"></span>' for _ in range(3))
    return f'''<div style="height: 100%; box-sizing: border-box; padding: 84px 32px 36px; display: flex; flex-direction: column; align-items: center; gap: 16px">
{ui_circle('lock', t, 72, 32)}
<h1 style="margin: 8px 0 0; font-size: 24px; font-weight: 800; letter-spacing: -0.02em">Statera è bloccata</h1>
<p style="margin: 0; font-size: 15px; color: {t['muted']}">Inserisci il PIN o usa l’impronta</p>
<div role="status" aria-label="3 cifre inserite" style="height: 40px; display: flex; align-items: center; gap: 14px">{dots}<span aria-hidden="true" style="width: 2px; height: 22px; background: {t['primary']}; border-radius: 1px"></span></div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); row-gap: 16px; column-gap: 20px; width: 100%; max-width: 290px">{keys}</div>
<span style="flex: 1"></span>
{link_btn('Ho dimenticato il PIN', t)}</div>'''

# ================================================================ Guida al primo avvio
def steps(n, t):
    segs = ''.join(f'<span style="flex: 1; height: 6px; border-radius: 3px; background: {t["primary"] if i <= n else t["track"]}"></span>' for i in (1, 2, 3))
    return (f'<div style="display: flex; align-items: center; gap: 14px"><span style="font-size: 13px; font-weight: 700; color: {t["muted"]}; white-space: nowrap">Passo {n} di 3</span>'
            f'<div role="img" aria-label="Passo {n} di 3" style="flex: 1; display: flex; gap: 6px">{segs}</div>'
            f'<button type="button" style="height: 40px; border: none; background: transparent; color: {t["accent"]}; font: inherit; font-size: 14px; font-weight: 700; padding: 0 4px">{"Salta" if n < 3 else "Indietro"}</button></div>')

def hero_ic(ic, t, size=96):
    return (f'<span aria-hidden="true" style="width: {size}px; height: {size}px; border-radius: 50%; background: {t["accentSoft"]}; color: {t["accent"]}; display: flex; align-items: center; justify-content: center; align-self: center; flex-shrink: 0">'
            f'{icon(ic, round(size * 0.45), sw=1.8)}</span>')

def money_in(label, value, t, w=120):
    return (f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {t["muted"]}">{label}'
            f'<span style="height: 40px; width: {w}px; box-sizing: border-box; border-radius: 12px; background: {t["bg"]}; display: flex; align-items: center; padding: 0 12px">'
            f'<input type="text" value="{value}" readonly style="width: 100%; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; font-weight: 700; color: {t["text"]}; text-align: right"></span></label>')

def check_row(ic, s, name, sub, on, t, dark, fields=''):
    box = (f'<span aria-hidden="true" style="width: 26px; height: 26px; border-radius: 8px; box-sizing: border-box; flex-shrink: 0; display: flex; align-items: center; justify-content: center; '
           f'{"background: " + t["primary"] + "; color: " + t["onp"] if on else "border: 2px solid " + t["border"]}">{icon("check", 16, sw=2.8) if on else ""}</span>')
    return (f'<div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 0">'
            f'<label style="display: flex; align-items: center; gap: 12px"><input type="checkbox" {"checked" if on else ""} style="position: absolute; opacity: 0; width: 1px; height: 1px">{box}'
            f'{cat_circle(ic, s, t, dark, size=40, isz=19)}{texts(name, sub, t)}</label>'
            f'{"<div style=\"display: flex; gap: 10px; justify-content: flex-end\">" + fields + "</div>" if fields else ""}</div>')

def guida1(d, t, dark):
    rows = (check_row('bank', 's3', 'Conto corrente', 'Con la carta Bancomat', True, t, dark, money_in('Saldo di oggi', '2.480,00 €', t, 150)) +
            check_row('cash', 's1', 'Contanti', None, True, t, dark, money_in('Nel portafoglio', '60,00 €', t)) +
            check_row('ticket', 's2', 'Buoni pasto', None, True, t, dark, money_in('Quanti ne hai', '12', t, 100) + money_in('Valore di uno', '8,00 €', t, 110)) +
            check_row('piggy', 's6', 'Conto risparmi', 'Puoi aggiungerlo anche dopo', False, t, dark))
    return f'''<div style="height: 100%; box-sizing: border-box; padding: 16px 20px 24px; display: flex; flex-direction: column; gap: 14px">
{steps(1, t)}
{hero_ic('wallet', t, 72)}
<div style="display: flex; flex-direction: column; gap: 6px; text-align: center">{h1('Quali conti usi?', 28)}
<p style="margin: 0; font-size: 15px; line-height: 1.45; color: {t['muted']}">Scegli da dove escono i soldi e quanto c’è oggi. Potrai cambiarli quando vuoi.</p></div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 4px 18px">{rows}</div>
<span style="flex: 1"></span>
{big_btn('Continua', t)}</div>'''

def guida2(d, t, dark):
    tip = lambda ic, title, sub: (f'<li style="display: flex; align-items: center; gap: 14px">{ui_circle(ic, t, 40, 19)}{texts(title, sub, t)}</li>')
    demo = f'''<div aria-hidden="true" style="position: relative; height: 150px; background: {t['surf']}; border-radius: 24px; overflow: hidden">
<div style="position: absolute; left: 18px; right: 18px; top: 18px; display: flex; align-items: center; gap: 12px">{cat_circle('cart', 's1', t, dark, size=40, isz=19)}
<span style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="height: 10px; width: 60%; border-radius: 5px; background: {t['track']}"></span><span style="height: 8px; width: 40%; border-radius: 4px; background: {t['track']}"></span></span>
<span style="height: 10px; width: 54px; border-radius: 5px; background: {t['track']}"></span></div>
<div style="position: absolute; left: 14px; right: 14px; bottom: 14px; height: 54px; border-radius: 27px; background: {t['bg']}; display: flex; align-items: center; justify-content: space-around">
<span style="width: 22px; height: 22px; border-radius: 6px; background: {t['track']}"></span><span style="width: 22px; height: 22px; border-radius: 6px; background: {t['track']}"></span>
<span style="width: 56px; height: 56px; margin-top: -30px; border-radius: 50%; background: {t['fab']}; color: {t['onfab']}; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 6px {tint(t['fab'], 0.22)}, 0 0 0 12px {tint(t['fab'], 0.1)}">{icon('plus', 26, sw=2.4)}</span>
<span style="width: 22px; height: 22px; border-radius: 6px; background: {t['track']}"></span><span style="width: 22px; height: 22px; border-radius: 6px; background: {t['track']}"></span></div></div>'''
    return f'''<div style="height: 100%; box-sizing: border-box; padding: 16px 20px 24px; display: flex; flex-direction: column; gap: 18px">
{steps(2, t)}
{demo}
<div style="display: flex; flex-direction: column; gap: 6px; text-align: center">{h1('Con il + registri tutto', 28)}
<p style="margin: 0; font-size: 15px; line-height: 1.45; color: {t['muted']}">Spese, entrate e trasferimenti. La data è già oggi e Statera ricorda il conto che hai usato l’ultima volta.</p></div>
<ul style="list-style: none; margin: 0; padding: 18px; background: {t['surf']}; border-radius: 24px; display: flex; flex-direction: column; gap: 16px">
{tip('star', 'Preferiti', 'Il caffè o il pranzo di ogni giorno con un tocco')}
{tip('repeat', 'Ricorrenti', 'Stipendio e bollette si registrano da soli')}
{tip('ticket', 'Pagamento misto', 'Buoni pasto e Bancomat nella stessa spesa')}</ul>
<span style="flex: 1"></span>
{big_btn('Registra la prima spesa', t)}
{link_btn('Lo faccio dopo', t)}</div>'''

def radio_card(ic, title, sub, on, t, badge=None):
    dot = (f'<span aria-hidden="true" style="width: 24px; height: 24px; border-radius: 50%; box-sizing: border-box; flex-shrink: 0; border: 2px solid {t["primary"] if on else t["border"]}; display: flex; align-items: center; justify-content: center">'
           f'{"<span style=\"width: 12px; height: 12px; border-radius: 50%; background: " + t["primary"] + "\"></span>" if on else ""}</span>')
    bdg = (f'<span style="height: 22px; padding: 0 8px; border-radius: 11px; background: {t["accentSoft"]}; color: {t["accent"]}; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center">{badge}</span>') if badge else ''
    return (f'<label style="display: flex; gap: 14px; align-items: flex-start; padding: 16px; border-radius: 22px; background: {t["surf"]}; box-shadow: inset 0 0 0 2px {t["primary"] if on else "transparent"}">'
            f'<input type="radio" name="dove" {"checked" if on else ""} style="position: absolute; opacity: 0; width: 1px; height: 1px">{ui_circle(ic, t, 40, 20)}'
            f'<span style="flex: 1; display: flex; flex-direction: column; gap: 4px"><span style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap"><span style="font-size: 15px; font-weight: 800">{title}</span>{bdg}</span>'
            f'<span style="font-size: 13px; line-height: 1.4; color: {t["muted"]}">{sub}</span></span>{dot}</label>')

def guida3(d, t, dark):
    return f'''<div style="height: 100%; box-sizing: border-box; padding: 16px 20px 24px; display: flex; flex-direction: column; gap: 16px">
{steps(3, t)}
{hero_ic('shield', t, 80)}
<div style="display: flex; flex-direction: column; gap: 6px; text-align: center">{h1('I tuoi dati al sicuro', 28)}
<p style="margin: 0; font-size: 15px; line-height: 1.45; color: {t['muted']}">Statera funziona anche senza account. Scegli dove tenere una copia.</p></div>
<div role="radiogroup" aria-label="Dove tenere i dati" style="display: flex; flex-direction: column; gap: 10px">
{radio_card('cloud', 'Google Drive, cifrato', 'Con una password che conosci solo tu, nella cartella nascosta dell’app. Ritrovi tutto su telefono e PC.', True, t, 'Consigliato')}
{radio_card('phone', 'Solo su questo dispositivo', 'Ti ricorderò di esportare un backup ogni tanto.', False, t)}</div>
<p style="margin: 0; display: flex; gap: 8px; align-items: flex-start; font-size: 13px; line-height: 1.4; color: {t['muted']}">{icon('lock', 16, t['muted'], sw=2)}Google conserva il file ma non può leggerlo. Senza password e chiave di recupero i dati non si recuperano.</p>
<span style="flex: 1"></span>
{big_btn('Collega Google Drive', t)}</div>'''

# ================================================================ Stati vuoti
def mov_vuoto(d, t, dark):
    tilebox = lambda ic, col, lab: (
        f'<div style="flex: 1; background: {t["surf"]}; border-radius: 20px; padding: 14px; display: flex; align-items: center; gap: 10px">'
        f'<span style="width: 32px; height: 32px; border-radius: 50%; background: {tint(col, 0.16 if not dark else 0.22)}; color: {col}; display: flex; align-items: center; justify-content: center">{icon(ic, 18, sw=2.2)}</span>'
        f'<span style="display: flex; flex-direction: column"><span style="font-size: 12px; color: {t["muted"]}">{lab}</span><span style="font-size: 16px; font-weight: 800">0,00 €</span></span></div>')
    body = f'''<header style="display: flex; align-items: center; gap: 10px">
<span aria-hidden="true" style="width: 40px; height: 40px; border-radius: 50%; background: {t['primary']}; color: {t['onp']}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px">L</span>
<button type="button" style="height: 40px; padding: 0 14px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 6px">Novembre 2026{icon('chevD', 18)}</button>
<span style="flex: 1"></span>{btn_icon('search', 'Cerca', t, bg=t['surf'])}</header>
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center; padding: 6px 0 2px">
{muted('Saldo del mese', t, 14, 'font-weight: 500')}
{amount_big('0', ',00 €')}
{muted('Patrimonio 2.636,00 €', t)}</div>
{qa_row([('out', 'Spesa'), ('in', 'Entrata'), ('swap', 'Trasferisci'), ('star', 'Preferiti')], t)}
<div style="display: flex; gap: 10px">{tilebox('in', t['inIcon'], 'Entrate')}{tilebox('out', t['outIcon'], 'Uscite')}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 28px 24px; display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center">
{ui_circle('receipt', t, 64, 28)}
<h2 style="margin: 6px 0 0; font-size: 17px; font-weight: 800">Ancora nessun movimento a novembre</h2>
<p style="margin: 0; font-size: 14px; line-height: 1.45; color: {t['muted']}">Tocca + per la prima spesa. Le spese di tutti i giorni puoi salvarle tra i preferiti.</p>
{pill('Aggiungi una spesa', t, 'plus', 'soft')}</div>'''
    return wrap(body, gap=20) + B_nav(t, 'Movimenti')

def vuoti(d, t, dark):
    def ex(where, ic, title, sub, action):
        return (f'<section style="background: {t["surf"]}; border-radius: 24px; padding: 16px; display: flex; gap: 14px; align-items: flex-start">{ui_circle(ic, t, 48, 22)}'
                f'<span style="flex: 1; display: flex; flex-direction: column; gap: 4px"><span style="font-size: 11px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: {t["muted"]}">{where}</span>'
                f'<h2 style="margin: 0; font-size: 16px; font-weight: 800">{title}</h2><span style="font-size: 13px; line-height: 1.4; color: {t["muted"]}">{sub}</span>'
                f'<span style="display: flex; margin-top: 6px">{action}</span></span></section>')
    body = f'''<div style="display: flex; flex-direction: column; gap: 4px">{h1('Stati vuoti')}{muted('Quando non c’è ancora niente da mostrare: cosa manca e come rimediare', t, 14)}</div>
{ex('Cerca', 'search', 'Nessun risultato per «palestra»', 'Prova a togliere un filtro o a cercare in tutto il periodo.', pill('Togli i filtri', t, 'x', 'soft', h=36, fs=13))}
{ex('Conti', 'target', 'Nessun obiettivo di risparmio', 'Una vacanza, un fondo per gli imprevisti: scegli quanto e, se vuoi, entro quando.', pill('Crea un obiettivo', t, 'plus', 'soft', h=36, fs=13))}
{ex('Ricorrenti', 'repeat', 'Niente di ricorrente', 'Stipendio, affitto e abbonamenti: impostali una volta e si registrano da soli.', pill('Aggiungi', t, 'plus', 'soft', h=36, fs=13))}
{ex('Analisi', 'chart', 'Ancora pochi dati', 'I grafici si riempiono con i primi movimenti. Il confronto con la media arriva dal quarto mese.', pill('Registra una spesa', t, 'plus', 'soft', h=36, fs=13))}
{ex('Preferiti', 'star', 'Nessun preferito', 'Nel modulo di una spesa scegli «Salva anche tra i preferiti».', '')}'''
    return wrap(body, gap=14, pad='20px 20px 0')

def avvisi(d, t, dark):
    def toast(txt, action, ic='check'):
        return (f'<div role="status" style="background: {t["toast"]}; color: {t["onToast"]}; border-radius: 18px; padding: 0 8px 0 16px; min-height: 52px; display: flex; align-items: center; gap: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.18)">'
                f'{icon(ic, 18, sw=2.2)}<span style="flex: 1; font-size: 14px; font-weight: 600">{txt}</span>'
                f'<button type="button" style="height: 40px; padding: 0 12px; border-radius: 20px; border: none; background: transparent; color: {t["toastAction"]}; font: inherit; font-size: 14px; font-weight: 800">{action}</button></div>')
    def banner(ic, title, sub, action=None, tone='info'):
        col = {'info': t['accent'], 'ok': t['income'], 'warn': t['text'], 'danger': t['danger']}[tone]
        bg = {'info': t['accentSoft'], 'ok': tint(t['income'], 0.14 if not dark else 0.18), 'warn': tint(t['warn'], 0.2 if not dark else 0.18), 'danger': tint(t['danger'], 0.12 if not dark else 0.18)}[tone]
        act = f'<span style="display: flex; margin-top: 6px">{action}</span>' if action else ''
        return (f'<div role="{"alert" if tone == "danger" else "status"}" style="background: {bg}; border-radius: 18px; padding: 12px 14px; display: flex; gap: 12px; align-items: flex-start">'
                f'<span style="color: {col}; margin-top: 1px">{icon(ic, 20, sw=2.2)}</span><span style="flex: 1; display: flex; flex-direction: column; gap: 2px">'
                f'<span style="font-size: 14px; font-weight: 800">{title}</span><span style="font-size: 13px; line-height: 1.4; color: {t["muted"] if tone != "warn" else t["text"]}">{sub}</span>{act}</span></div>')
    lab = lambda txt: f'<h2 style="margin: 6px 0 0; font-size: 11px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: {t["muted"]}">{txt}</h2>'
    body = f'''<div style="display: flex; flex-direction: column; gap: 4px">{h1('Avvisi')}{muted('Conferme, sincronizzazione ed errori: sempre con testo e simbolo', t, 14)}</div>
{lab('Conferme a comparsa (in basso)')}
{toast('Pranzo con buono registrato', 'Annulla')}
{toast('È disponibile una nuova versione', 'Aggiorna', 'refresh')}
{lab('Sincronizzazione e backup')}
{banner('cloud', 'Accesso a Google scaduto', 'I dati sono al sicuro qui. Ricollegati per riprendere la sincronizzazione.', pill('Riconnetti', t, None, 'primary', h=36, fs=13))}
{banner('wifioff', 'Sei offline', 'Le modifiche restano sul dispositivo e partono al ritorno della rete.')}
{banner('download', 'Ultimo backup 34 giorni fa', 'Senza sincronizzazione il backup è la tua rete di sicurezza.', pill('Esporta ora', t, None, 'surf', h=36, fs=13), 'warn')}
{lab('Budget ed errori')}
{banner('alert', 'Pasti fuori: budget superato', '92,00 € di 80,00 € · 12,00 € oltre il previsto', None, 'warn')}
{banner('alert', 'Spesa non salvata', 'Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.', None, 'danger')}
{banner('lock', 'Troppi tentativi', 'Riprova tra 30 secondi.', None, 'danger')}'''
    return wrap(body, gap=10, pad='20px 20px 0')

def conferma(d, t, dark):
    return f'''{coolors.mov(d, t, dark)}
<div aria-hidden="true" style="position: absolute; inset: 0; background: {t['backdrop']}"></div>
<div role="alertdialog" aria-modal="true" aria-label="Eliminare questa spesa?" style="position: absolute; left: 12px; right: 12px; bottom: 12px; background: {t['bg']}; border-radius: 32px; padding: 24px 20px 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px; align-items: center; text-align: center">
{ui_circle('trash', t, 64, 28, bg=tint(t['danger'], 0.14 if not dark else 0.2), fg=t['danger'])}
<h2 style="margin: 4px 0 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">Eliminare questa spesa?</h2>
<div style="align-self: stretch; background: {t['surf']}; border-radius: 20px; padding: 12px 14px; display: flex; align-items: center; gap: 12px; text-align: left">{cat_circle('cart', 's1', t, dark, size=40, isz=19)}{texts('Conad', 'Sabato 14 novembre · Bancomat', t)}<span style="font-size: 15px; font-weight: 800">−42,30 €</span></div>
<p style="margin: 0; font-size: 14px; line-height: 1.45; color: {t['muted']}">Sparisce anche dagli altri dispositivi collegati alla sincronizzazione.</p>
<div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px">{big_btn('Elimina', t, 'danger', 'trash')}{big_btn('Annulla', t, 'surf')}</div></div>'''

# ---------------------------------------------------------------- elenco delle tavole mobili
# (chiave, titolo, funzione, altezza)
MOBILE_ROWS = [
 ('Conti, Cerca e Altro', [('conti', 'Conti (pagina intera)', conti, CONTI_H), ('dettaglio-conto', 'Dettaglio conto (pagina intera)', dettaglio, DET_H),
                           ('cerca', 'Cerca', cerca, H), ('altro', 'Altro (pagina intera)', altro, ALTRO_H)]),
 ('Ricorrenti, Categorie e blocco', [('ricorrenti', 'Ricorrenti (pagina intera)', ricorrenti, RIC_H), ('categorie', 'Categorie (pagina intera)', categorie, CAT_H),
                                     ('blocco', 'Blocco col PIN', blocco, H)]),
 ('Guida al primo avvio', [('guida-1', 'Guida · 1 conti', guida1, H), ('guida-2', 'Guida · 2 primo movimento', guida2, H), ('guida-3', 'Guida · 3 dati al sicuro', guida3, H)]),
 ('Stati vuoti e avvisi', [('movimenti-vuoto', 'Movimenti senza movimenti', mov_vuoto, H), ('stati-vuoti', 'Stati vuoti (raccolta)', vuoti, 900),
                           ('avvisi', 'Avvisi (raccolta)', avvisi, 980), ('conferma', 'Conferma eliminazione', conferma, H)]),
]

def check():
    """Contrasti dei ruoli nuovi (testo 4,5:1, grafica 3:1)."""
    bad = []
    for name, t in (('chiaro', L), ('scuro', K)):
        v = {'pericolo/superficie': cr(t['danger'], t['surf']), 'pericolo/sfondo': cr(t['danger'], t['bg']), 'suPericolo': cr(t['onDanger'], t['danger']),
             'avviso testo': cr(t['onToast'], t['toast']), 'avviso azione': cr(t['toastAction'], t['toast']),
             'tasto attenuato': cr(t['muted'], t['surf2']), 'accento/superficie': cr(t['accent'], t['surf']), 'accento/tenue': cr(t['accent'], t['accentSoft'])}
        low = [k for k, x in v.items() if x < 4.5]
        g = {'attenzione (barra)': cr(t['warn'], t['surf']), 'interruttore': cr(t['primary'], t['surf'])}
        low += [k for k, x in g.items() if x < 3]
        print(f'{name:7} ' + ' · '.join(f'{k} {x:.1f}' for k, x in {**v, **g}.items()) + ('  <-- ' + ', '.join(low) if low else ''))
        bad += low
    return bad
