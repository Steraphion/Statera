#!/usr/bin/env python3
"""Indaco morbido: versione per PC (dati di esempio).
Barra laterale al posto di quella flottante, moduli in finestre centrate, scorciatoie da tastiera.
Tavole fluide ("expand": "fill"): a 1280 px si vedono come su PC, a larghezza di telefono la barra va sopra."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import icon, tint, btn_icon, seg, MOV, PICK, CATS
import altre
from altre import (L, K, SW, D, THEMES, cat_circle, ui_circle, texts, muted, pill, card, h2, bar, ring, kbd, switch,
                   search_field, GOALS, CONTI, DET, tickets, goal_row)

PW = 1280

def page_pc(title, t, body, h):
    d = D
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{d['fonts']}&display=swap">
<style>
body{{margin:0}}
a{{color:{t['accent']}}}a:hover{{color:{t['text']}}}
</style>
</helmet>
<div style="width: 100%; min-height: {h}px; position: relative; box-sizing: border-box; padding: 16px; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 16px; background: {t['bg']}; color: {t['text']}; font-family: {d['body']}; font-variant-numeric: tabular-nums">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{PW},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

# ---------------------------------------------------------------- barra laterale
def side(t, active):
    items = [('list', 'Movimenti', None), ('wallet', 'Conti', None), ('chart', 'Analisi', None), ('search', 'Cerca', '/'), ('more', 'Altro', None)]
    links = ''
    for ic, lab, k in items:
        on = lab == active
        links += (f'<a href="#"{" aria-current=\"page\"" if on else ""} style="flex: 1 1 160px; height: 44px; box-sizing: border-box; padding: 0 12px; border-radius: 14px; display: flex; align-items: center; gap: 12px; '
                  f'text-decoration: none; font-size: 15px; font-weight: {800 if on else 600}; background: {t["accentSoft"] if on else "transparent"}; color: {t["accent"] if on else t["text"]}">'
                  f'{icon(ic, 20, sw=2.1 if on else 1.8)}<span style="flex: 1">{lab}</span>{kbd(k, t) if k else ""}</a>')
    ok = t['income']
    return f'''<aside style="flex: 1 1 232px; max-width: 100%; align-self: stretch; box-sizing: border-box; background: {t['surf']}; border-radius: 24px; padding: 18px 14px; display: flex; flex-direction: column; gap: 18px; box-shadow: 0 6px 24px rgba(14,18,32,0.06)">
<div style="display: flex; align-items: center; gap: 10px; padding: 0 6px">
<span aria-hidden="true" style="width: 36px; height: 36px; border-radius: 50%; background: {t['primary']}; color: {t['onp']}; display: flex; align-items: center; justify-content: center">{icon('scale', 20, sw=2.1)}</span>
<span style="font-size: 20px; font-weight: 800; letter-spacing: -0.02em">Statera</span></div>
<button type="button" style="height: 48px; border-radius: 24px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 15px; font-weight: 800; display: flex; align-items: center; gap: 8px; padding: 0 12px 0 16px">{icon('plus', 20, sw=2.4)}<span style="flex: 1; text-align: left">Nuovo movimento</span>{kbd('N', t, True)}</button>
<nav aria-label="Sezioni" style="display: flex; flex-wrap: wrap; gap: 4px">{links}</nav>
<span style="flex: 1"></span>
<div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 16px; background: {t['bg']}">
<span style="color: {ok}">{icon('cloudok', 20, sw=2)}</span><span style="display: flex; flex-direction: column"><span style="font-size: 13px; font-weight: 800">Sincronizzato</span><span style="font-size: 12px; color: {t['muted']}">2 minuti fa</span></span></div>
<a href="#" style="display: flex; align-items: center; gap: 10px; padding: 0 6px; text-decoration: none; color: {t['text']}">
<span aria-hidden="true" style="width: 36px; height: 36px; border-radius: 50%; background: {t['accentSoft']}; color: {t['accent']}; display: flex; align-items: center; justify-content: center; font-weight: 800">L</span>
<span style="flex: 1; display: flex; flex-direction: column"><span style="font-size: 14px; font-weight: 800">Livio</span><span style="font-size: 12px; color: {t['muted']}">Profilo personale</span></span>{icon('chevD', 18, t['muted'])}</a>
</aside>'''

def main(inner, gap=20):
    return f'<main style="flex: 999 1 560px; min-width: 0; box-sizing: border-box; padding: 6px 6px 6px 4px; display: flex; flex-direction: column; gap: {gap}px">{inner}</main>'

def month_nav(t, title='Novembre 2026', size=28):
    return (f'{btn_icon("chevL", "Mese precedente (freccia a sinistra)", t, bg=t["surf"])}'
            f'<h1 style="margin: 0; font-size: {size}px; font-weight: 800; letter-spacing: -0.02em">{title}</h1>'
            f'{btn_icon("chevR", "Mese successivo (freccia a destra)", t, bg=t["surf"])}')

def tile(ic, col, lab, val, t, dark, big=False, note=None):
    nt = f'<span style="font-size: 12px; color: {t["muted"]}">{note}</span>' if note else ''
    lead = (f'<span style="width: 36px; height: 36px; border-radius: 50%; background: {tint(col, 0.16 if not dark else 0.22)}; color: {col}; display: flex; align-items: center; justify-content: center; flex-shrink: 0">{icon(ic, 19, sw=2.2)}</span>') if ic else ''
    return (f'<div style="flex: 1 1 180px; min-width: 0; background: {t["surf"]}; border-radius: 22px; padding: 16px 18px; display: flex; align-items: center; gap: 12px">{lead}'
            f'<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0"><span style="font-size: 13px; color: {t["muted"]}; font-weight: 600">{lab}</span>'
            f'<span style="font-size: {28 if big else 20}px; font-weight: 800; letter-spacing: -0.02em; white-space: nowrap">{val}</span>{nt}</span></div>')

def shortcut_hint(t):
    return (f'<p style="margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 13px; color: {t["muted"]}">'
            f'{kbd("N", t)}nuovo<span style="width: 8px"></span>{kbd("/", t)}cerca<span style="width: 8px"></span>{kbd("←", t)}{kbd("→", t)}mese<span style="width: 8px"></span>{kbd("?", t)}tutte le scorciatoie</p>')

def budget(name, spent, tot, pct, ok, t):
    col = t['primary'] if ok else t['warn']
    state_ic = icon('check', 14, t['income'], sw=2.4) if ok else icon('alert', 14, t['text'], sw=2.2)
    state = 'In regola' if ok else 'Quasi esaurito'
    return (f'<li style="display: flex; flex-direction: column; gap: 7px">'
            f'<span style="display: flex; justify-content: space-between; align-items: baseline; font-size: 14px"><span style="font-weight: 700">{name}</span>'
            f'<span><span style="font-weight: 700">{spent}</span><span style="color: {t["muted"]}"> di {tot}</span></span></span>'
            f'{bar(pct, col, t)}'
            f'<span style="display: flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; color: {t["muted"]}">{state_ic}{state} · {pct}%</span></li>')

# ================================================================ Movimenti
def mov_list(t, dark, hover='Q8 via Appia'):
    rows = ''
    for day, net, items in MOV:
        lis = ''
        for ic, s, desc, cat, src, amt, inc in items:
            hv = desc == hover
            acts = (f'<span style="display: flex; gap: 4px">{btn_icon("pen", "Modifica", t, size=36, bg=t["surf"])}{btn_icon("trash", "Elimina", t, size=36, bg=t["surf"])}</span>') if hv else ''
            lis += (f'<li style="display: flex; align-items: center; gap: 14px; padding: 8px 12px; margin: 0 -12px; border-radius: 16px; {"background: " + t["surf2"] + ";" if hv else ""}">'
                    f'{cat_circle(ic, s, t, dark, size=40, isz=19)}{texts(desc, cat, t)}'
                    f'<span style="flex: 0 1 160px; min-width: 0; font-size: 14px; color: {t["muted"]}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{src}</span>{acts}'
                    f'<span style="flex: 0 0 110px; text-align: right; font-size: 15px; font-weight: 700; color: {t["income"] if inc else t["text"]}">{amt}</span></li>')
        rows += (f'<h2 style="margin: 14px 0 4px; font-size: 13px; font-weight: 600; color: {t["muted"]}; display: flex; justify-content: space-between"><span>{day}</span><span>{net}</span></h2>'
                 f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>')
    return f'<div style="background: {t["surf"]}; border-radius: 24px; padding: 4px 22px 14px">{rows}</div>'

def favs(t, dark):
    out = ''
    for ic, s, lab, amt in [('star', 's2', 'Caffè', '1,20 €'), ('food', 's2', 'Pranzo con buono', '1 buono'), ('fuel', 's3', 'Carburante', 'chiede l’importo'), ('cart', 's1', 'Spesa Conad', 'chiede l’importo')]:
        out += (f'<button type="button" style="flex: 1 1 150px; min-width: 0; height: 54px; border-radius: 16px; border: none; background: {t["bg"]}; color: {t["text"]}; font: inherit; display: flex; align-items: center; gap: 10px; padding: 0 12px; text-align: left">'
                f'{cat_circle(ic, s, t, dark, size=32, isz=16)}<span style="display: flex; flex-direction: column; min-width: 0"><span style="font-size: 13px; font-weight: 700; white-space: nowrap">{lab}</span>'
                f'<span style="font-size: 12px; color: {t["muted"]}; white-space: nowrap">{amt}</span></span></button>')
    return f'<div style="display: flex; flex-wrap: wrap; gap: 8px">{out}</div>'

def mov_main(t, dark):
    head = f'''<header style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px">
{month_nav(t)}<span style="flex: 1"></span>
<div style="flex: 0 1 340px; min-width: 220px; display: flex">{search_field('', t, 'Cerca movimenti', focus=False, h=44, kb='/')}</div>
{btn_icon('cal', 'Calendario del mese', t, bg=t['surf'])}</header>'''
    left = f'''<div style="flex: 999 1 460px; min-width: 0; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; flex-wrap: wrap; gap: 12px">{tile(None, None, 'Saldo del mese', '+1.325,65 €', t, dark, True, 'Patrimonio 8.412,90 €')}{tile('in', t['inIcon'], 'Entrate', '2.010,00 €', t, dark)}{tile('out', t['outIcon'], 'Uscite', '684,35 €', t, dark)}</div>
{mov_list(t, dark)}</div>'''
    due = f'''<div style="display: flex; align-items: center; gap: 12px">{cat_circle('home', 's7', t, dark, size=40, isz=19)}{texts('Bolletta acqua', 'Dovuta il 12 novembre', t)}<span style="font-size: 15px; font-weight: 800">−48,60 €</span></div>
<div style="display: flex; gap: 8px">{pill('Registra', t, 'check', 'primary', h=36, fs=13)}{pill('Salta', t, None, 'surf2', h=36, fs=13)}</div>'''
    right = f'''<div style="flex: 1 1 300px; min-width: 0; display: flex; flex-direction: column; gap: 16px">
{card(h2('Preferiti', pill('Gestisci', t, None, 'bg', h=32, fs=12)) + favs(t, dark), t, gap=12)}
{card(h2('Da registrare') + due, t, gap=12)}
{card(h2('Budget del mese') + '<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">' + budget('Spesa alimentare', '168,40 €', '300 €', 56, True, t) + budget('Pasti fuori', '72,00 €', '80 €', 90, False, t) + '</ul>', t, gap=14)}
{shortcut_hint(t)}</div>'''
    return main(head + f'<div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start">{left}{right}</div>')

def movimenti(t, dark):
    return side(t, 'Movimenti') + mov_main(t, dark)

# ================================================================ finestra centrata
def modal(inner, t, label, maxw=680, top=44, role='dialog'):
    return (f'<div aria-hidden="true" style="position: absolute; inset: 0; background: {t["backdrop"]}"></div>'
            f'<div style="position: absolute; inset: 0; box-sizing: border-box; padding: {top}px 16px 16px; display: flex; justify-content: center; align-items: flex-start">'
            f'<div role="{role}" aria-modal="true" aria-label="{label}" style="width: 100%; max-width: {maxw}px; box-sizing: border-box; background: {t["bg"]}; border-radius: 28px; padding: 22px 24px 24px; '
            f'display: flex; flex-direction: column; gap: 18px; box-shadow: 0 24px 64px rgba(0,0,0,0.28)">{inner}</div></div>')

def flabel(txt, t):
    return f'<span style="font-size: 13px; font-weight: 700; color: {t["muted"]}">{txt}</span>'

def nuova(t, dark):
    grid = ''
    for ic, s, lab in PICK:
        on = lab == 'Spesa alimentare'
        c = SW[s]
        ring_ = f'box-shadow: 0 0 0 3px {t["bg"]}, 0 0 0 5px {c};' if on else ''
        grid += (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="border: none; background: transparent; padding: 4px 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 11px; font-weight: {800 if on else 500}; text-align: center">'
                 f'<span style="width: 46px; height: 46px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: {c if on else tint(c, 0.15 if not dark else 0.3)}; color: {"#FFFFFF" if on or dark else c}; {ring_}">{icon(ic, 21, sw=2)}</span>{lab}</button>')
    chip = lambda lab, on=False, ic=None: (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="height: 38px; padding: 0 14px; border-radius: 19px; border: none; background: {t["accentSoft"] if on else t["surf"]}; color: {t["accent"] if on else t["text"]}; font: inherit; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px">{icon(ic, 15, sw=2.1) if ic else ""}{lab}</button>')
    fieldbox = f'height: 48px; box-sizing: border-box; border-radius: 16px; background: {t["surf"]}; display: flex; align-items: center; gap: 10px; padding: 0 14px'
    sugg = f'''<ul role="listbox" aria-label="Movimenti già usati" style="list-style: none; margin: 0; padding: 6px; border-radius: 16px; background: {t['surf']}; box-shadow: 0 8px 24px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 2px">
<li role="option" aria-selected="true" style="display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 12px; background: {t['accentSoft']}">{cat_circle('cart', 's1', t, dark, size=30, isz=15)}{texts('<span style="color: ' + t['accent'] + '">Con</span>ad', 'Spesa alimentare · Bancomat · ultima volta 42,30 €', t, 14)}</li>
<li role="option" aria-selected="false" style="display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 12px">{cat_circle('cart', 's1', t, dark, size=30, isz=15)}{texts('<span style="color: ' + t['accent'] + '">Con</span>ad City', 'Spesa alimentare · Contanti · ultima volta 18,70 €', t, 14)}</li></ul>'''
    inner = f'''<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px">
<h2 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em; flex: 1">Nuova uscita</h2>
<div style="flex: 0 1 330px">{seg(['Uscita', 'Entrata', 'Trasferimento'], 'Uscita', t, D, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div>
<button type="button" aria-label="Chiudi (Esc)" style="height: 40px; padding: 0 10px 0 12px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; display: flex; align-items: center; gap: 8px">{icon('x', 18, sw=2.2)}{kbd('Esc', t)}</button></div>
<div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start">
<div style="flex: 1 1 260px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
<label style="display: flex; flex-direction: column; gap: 6px">{flabel('Importo', t)}
<span style="{fieldbox}; height: 72px; box-shadow: 0 0 0 2px {t['primary']}"><input type="text" value="42,30" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 40px; font-weight: 800; letter-spacing: -0.03em; color: {t['text']}"><span style="font-size: 28px; font-weight: 800; color: {t['muted']}">€</span></span>
<span style="font-size: 12px; color: {t['muted']}">Puoi scrivere anche un calcolo, per esempio 12,50+3,20</span></label>
<label style="display: flex; flex-direction: column; gap: 6px">{flabel('Descrizione', t)}
<span style="{fieldbox}">{icon('pen', 17, t['muted'], sw=2)}<input type="text" value="Con" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; color: {t['text']}"></span></label>
{sugg}
<div style="display: flex; flex-direction: column; gap: 6px">{flabel('Data', t)}<div style="display: flex; flex-wrap: wrap; gap: 8px">{chip('Oggi', True, 'cal')}{chip('Ieri')}{chip('14/11/2026')}</div></div>
<label style="display: flex; flex-direction: column; gap: 6px">{flabel('Con', t)}
<span style="{fieldbox}">{icon('card', 17, t['accent'], sw=2)}<select style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; font-weight: 700; color: {t['text']}; appearance: none"><option>Bancomat · Conto corrente</option></select>{icon('chevD', 17, t['muted'])}</span></label>
</div>
<div style="flex: 1 1 280px; min-width: 0; display: flex; flex-direction: column; gap: 6px">{flabel('Categoria', t)}
<div style="background: {t['surf']}; border-radius: 22px; padding: 14px 10px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: 12px; column-gap: 4px">{grid}</div>
<button type="button" style="height: 40px; border: none; background: transparent; color: {t['accent']}; font: inherit; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px; align-self: flex-start; padding: 0 4px">{icon('plus', 15, sw=2.2)}Dividi su più categorie</button></div></div>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding-top: 14px; border-top: 1px solid {t['border']}">
<label style="display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600"><input type="checkbox" style="width: 20px; height: 20px; accent-color: {t['primary']}; margin: 0">Salva anche tra i preferiti</label>
<span style="flex: 1"></span>
<button type="button" style="height: 48px; padding: 0 18px; border-radius: 24px; border: none; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 15px; font-weight: 700">Salva e aggiungine un’altra</button>
<button type="button" style="height: 48px; padding: 0 12px 0 22px; border-radius: 24px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 15px; font-weight: 800; display: flex; align-items: center; gap: 10px">Salva spesa{kbd('Invio', t, True)}</button></div>'''
    return movimenti(t, dark) + modal(inner, t, 'Nuova uscita', 760, 36)

# ================================================================ Analisi
M12 = [('Dic', 1960, 1510), ('Gen', 1960, 1720), ('Feb', 1960, 1180), ('Mar', 1960, 1390), ('Apr', 2010, 1450), ('Mag', 2010, 1260),
       ('Giu', 2010, 1420), ('Lug', 2010, 1610), ('Ago', 2240, 1980), ('Set', 2010, 1240), ('Ott', 2050, 1380), ('Nov', 2010, 684)]

def cols12(t, height=200):
    mx = 2500
    grid = ''
    for v, lab in [(0, '0 €'), (1000, '1.000 €'), (2000, '2.000 €')]:
        y = 24 + round(v / mx * height)
        grid += (f'<span style="position: absolute; left: 56px; right: 0; bottom: {y}px; border-top: 1px solid {t["border"]}"></span>'
                 f'<span style="position: absolute; left: 0; bottom: {y - 7}px; font-size: 11px; color: {t["muted"]}">{lab}</span>')
    bars_ = ''
    for m, i, o in M12:
        bars_ += (f'<div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px">'
                  f'<div style="height: {height}px; display: flex; align-items: flex-end; gap: 4px">'
                  f'<span style="width: 14px; height: {round(i / mx * height)}px; background: {t["chIn"]}; border-radius: 6px 6px 0 0"></span>'
                  f'<span style="width: 14px; height: {round(o / mx * height)}px; background: {t["chOut"]}; border-radius: 6px 6px 0 0"></span></div>'
                  f'<span style="height: 18px; font-size: 12px; color: {t["muted"]}">{m}</span></div>')
    legend = (f'<div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 13px; color: {t["muted"]}">'
              f'<span style="display: flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: {t["chIn"]}"></span>Entrate</span>'
              f'<span style="display: flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: {t["chOut"]}"></span>Uscite</span>'
              f'<span>Novembre è in corso</span></div>')
    return (f'<div role="img" aria-label="Entrate e uscite degli ultimi 12 mesi" style="display: flex; flex-direction: column; gap: 14px">{legend}'
            f'<div style="position: relative; height: {height + 24}px">{grid}<div style="position: absolute; left: 64px; right: 0; bottom: 0; display: flex; gap: 6px; align-items: flex-end">{bars_}</div></div></div>')

def analisi(t, dark):
    hero_bg = t['accentSoft'] if dark else t['primary']; hero_fg = t['text'] if dark else t['onp']
    hp = lambda txt: f'<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: {tint(hero_fg, 0.16)}; display: flex; align-items: center; font-size: 13px; font-weight: 700">{txt}</span>'
    lst = ''
    for (name, v, s, p, ic), k in zip(CATS[:5], ['s7', 's1', 's4', 's2', 's5']):
        lst += (f'<li style="display: flex; align-items: center; gap: 12px">{cat_circle(ic, k, t, dark, size=38, isz=18)}'
                f'<span style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="display: flex; justify-content: space-between; font-size: 14px"><span style="font-weight: 700">{name}</span>'
                f'<span><span style="color: {t["muted"]}">{p}% · </span><span style="font-weight: 700">{s}</span></span></span>{bar(round(p / 35 * 100), t["chOut"], t, 6)}</span></li>')
    def chg(ic, s, name, detail, up, pct):
        arrow = icon('up' if up else 'down', 14, sw=2.4)
        return (f'<li style="display: flex; align-items: center; gap: 12px">{cat_circle(ic, s, t, dark, size=38, isz=18)}{texts(name, detail, t, 14)}'
                f'<span style="display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 800; white-space: nowrap">{arrow}{pct} {"in aumento" if up else "in calo"}</span></li>')
    head = f'''<header style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px">
<h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.02em">Analisi</h1>
<div style="width: 180px">{seg(['Mese', 'Anno'], 'Mese', t, D, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div>
<span style="flex: 1"></span>
<div style="display: flex; align-items: center; gap: 6px">{month_nav(t, 'Novembre 2026', 18)}</div>
{pill('Esporta CSV', t, 'download', 'surf', h=40)}</header>'''
    row1 = f'''<div style="display: flex; flex-wrap: wrap; gap: 16px">
<div style="flex: 2 1 380px; min-width: 0; background: {hero_bg}; color: {hero_fg}; border-radius: 24px; padding: 22px 24px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 14px; font-weight: 600">A novembre hai risparmiato</span>
<span style="font-size: 44px; font-weight: 800; letter-spacing: -0.03em">1.325,65 €</span>
<span style="display: flex; gap: 8px; flex-wrap: wrap">{hp('66% delle entrate')}{hp('Stima uscite a fine mese 1.480 €')}</span></div>
<div style="flex: 3 1 420px; min-width: 0; display: flex; flex-wrap: wrap; gap: 12px">
{tile('in', t['inIcon'], 'Entrate', '2.010,00 €', t, dark, note='novembre')}
{tile('out', t['outIcon'], 'Uscite', '684,35 €', t, dark, note='stima 1.480 € a fine mese')}
{tile('cal', t['accent'], 'Media al giorno', '48,88 €', t, dark, note='su 14 giorni')}</div></div>'''
    row2 = f'''<div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start">
<div style="flex: 3 1 380px; min-width: 0">{card(h2('Dove vanno i soldi', seg(['Uscite', 'Entrate'], 'Uscite', t, D, h=34, radius=17, act_bg=t['surf'], act_col=t['text'])) + f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">{lst}</ul>', t)}</div>
<div style="flex: 2 1 300px; min-width: 0; display: flex; flex-direction: column; gap: 16px">
{card(h2('Budget del mese') + '<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">' + budget('Spesa alimentare', '168,40 €', '300 €', 56, True, t) + budget('Pasti fuori', '72,00 €', '80 €', 90, False, t) + '</ul>' + muted('Circa 9 € al giorno per i 16 giorni che restano', t), t)}
{card(h2('Rispetto alla media di 3 mesi') + '<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">' + chg('food', 's2', 'Pasti fuori', '72,00 € contro 58,00 €', True, '+24%') + chg('fuel', 's3', 'Carburante', '50,00 € contro 66,00 €', False, '−24%') + '</ul>', t)}</div></div>'''
    row3 = card(h2('Ultimi 12 mesi', f'<a href="#" style="font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px">{icon("table", 15, sw=2)}Vedi come tabella</a>') + cols12(t, 190), t, gap=16, pad='20px 22px')
    return side(t, 'Analisi') + main(head + row1 + row2 + row3, gap=16)

# ================================================================ Conti (elenco + dettaglio affiancati)
def conti(t, dark):
    acc = ''
    for i, (ic, s, name, sub, amt) in enumerate(CONTI + [('ticket', 's2', 'Buoni pasto', '12 buoni da 8,00 €', '96,00 €')]):
        on = i == 0
        acc += (f'<li><a href="#"{" aria-current=\"true\"" if on else ""} style="display: flex; align-items: center; gap: 12px; padding: 10px 12px; margin: 0 -10px; border-radius: 16px; text-decoration: none; color: {t["text"]}; {"background: " + t["accentSoft"] + ";" if on else ""}">'
                f'{cat_circle(ic, s, t, dark, size=40, isz=19)}{texts(name, sub, t, 14)}<span style="font-size: 14px; font-weight: 800; white-space: nowrap">{amt}</span></a></li>')
    goals = ''.join(goal_row(g, t, dark, size=52) for g in GOALS)
    left = f'''<div style="flex: 1 1 340px; min-width: 0; display: flex; flex-direction: column; gap: 16px">
<div style="background: {t['surf']}; border-radius: 24px; padding: 18px 20px; display: flex; flex-direction: column; gap: 2px">{muted('Patrimonio', t, 13, 'font-weight: 600')}<span style="font-size: 34px; font-weight: 800; letter-spacing: -0.03em">8.412,90 €</span>{muted('4 conti attivi · 1 archiviato', t)}</div>
{card(h2('I tuoi conti', pill('Ordina', t, 'list', 'bg', h=32, fs=12)) + f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px">{acc}</ul>', t, gap=10)}
{card(h2('Obiettivi di risparmio') + f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 16px">{goals}</ul>', t, gap=14)}</div>'''
    trs = ''
    dates = {'Sabato 14 novembre': '14 nov', 'Venerdì 13 novembre': '13 nov', 'Giovedì 12 novembre': '12 nov', 'Martedì 10 novembre': '10 nov', 'Lunedì 2 novembre': '2 nov'}
    for day, items in DET:
        for ic, s, desc, sub, amt, bal, inc, before in items:
            parts = sub.split(' · ')
            catn = parts[0]; src = parts[1] if len(parts) > 1 else ('Conto corrente' if s else '')
            lead = cat_circle(ic, s, t, dark, size=32, isz=16) if s else ui_circle(ic, t, 32, 16)
            saldo = (f'<span style="color: {t["muted"]}">{bal}</span>' if bal else
                     f'<span style="height: 22px; padding: 0 8px; border-radius: 11px; background: {t["surf2"]}; color: {t["muted"]}; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px">{icon("info", 12, sw=2.2)}non incide</span>')
            trs += (f'<tr style="border-top: 1px solid {t["border"]}"><td style="padding: 10px 8px; color: {t["muted"]}; white-space: nowrap">{dates[day]}</td>'
                    f'<td style="padding: 10px 8px"><span style="display: flex; align-items: center; gap: 10px">{lead}<span style="display: flex; flex-direction: column"><span style="font-weight: 700">{desc}</span>'
                    f'<span style="font-size: 12px; color: {t["muted"]}">{src}</span></span></span></td>'
                    f'<td style="padding: 10px 8px">{catn}</td>'
                    f'<td style="padding: 10px 8px; text-align: right; font-weight: 700; white-space: nowrap; color: {t["income"] if inc else t["text"]}">{amt}</td>'
                    f'<td style="padding: 10px 8px; text-align: right; white-space: nowrap">{saldo}</td></tr>')
    th = lambda txt, right=False: f'<th scope="col" style="padding: 8px; font-size: 12px; font-weight: 700; color: {t["muted"]}; text-align: {"right" if right else "left"}">{txt}</th>'
    table = f'''<div style="overflow-x: auto"><table style="width: 100%; min-width: 560px; border-collapse: collapse; font-size: 14px">
<thead><tr>{th('Data')}{th('Descrizione')}{th('Categoria')}{th('Importo', True)}{th('Saldo', True)}</tr></thead>
<tbody>{trs}</tbody>
<tfoot><tr style="border-top: 1px dashed {t['border']}"><td colspan="4" style="padding: 12px 8px; font-weight: 700">Saldo iniziale <span style="font-weight: 500; color: {t['muted']}">· dal 3 novembre 2026: i movimenti precedenti contano nei totali, non nel saldo</span></td>
<td style="padding: 12px 8px; text-align: right; font-weight: 800; white-space: nowrap">5.294,84 €</td></tr></tfoot></table></div>'''
    tot = lambda lab, val, col=None: f'<span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; color: {t["muted"]}">{lab}</span><span style="font-size: 15px; font-weight: 800; color: {col or t["text"]}">{val}</span></span>'
    right = f'''<section style="flex: 999 1 520px; min-width: 0; background: {t['surf']}; border-radius: 24px; padding: 22px 24px; display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 14px">{cat_circle('bank', 's3', t, dark, size=52, isz=24)}
<span style="flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 180px"><h2 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">Conto corrente</h2>{muted('Carta collegata: Bancomat', t)}</span>
<span style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px">{muted('Saldo di oggi', t, 13, 'font-weight: 600')}<span style="font-size: 30px; font-weight: 800; letter-spacing: -0.03em">6.940,55 €</span></span></div>
<div style="display: flex; flex-wrap: wrap; gap: 8px">{pill('Allinea saldo', t, 'scale', 'soft', h=38, fs=13)}{pill('Trasferisci', t, 'swap', 'bg', h=38, fs=13)}{pill('Modifica', t, 'pen', 'bg', h=38, fs=13)}{pill('Archivia', t, None, 'bg', h=38, fs=13)}</div>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 20px; padding: 12px 16px; border-radius: 18px; background: {t['bg']}">
<div style="display: flex; align-items: center; gap: 6px">{month_nav(t, 'Novembre 2026', 17)}</div><span style="flex: 1"></span>
{tot('Entrate', '+1.850,00 €', t['income'])}{tot('Uscite', '−200,29 €')}{tot('Trasferimenti', '−100,00 €')}</div>
{table}</section>'''
    head = f'''<header style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px"><h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.02em">Conti</h1>
<span style="flex: 1"></span>{pill('Nuovo obiettivo', t, 'target', 'surf', h=40)}{pill('Nuovo conto', t, 'plus', 'primary', h=40)}</header>'''
    return side(t, 'Conti') + main(head + f'<div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start">{left}{right}</div>', gap=16)

# ================================================================ Scorciatoie
def scorciatoie(t, dark):
    def grp(title, items):
        rows = ''.join(f'<li style="display: flex; align-items: center; gap: 12px; padding: 8px 0; border-top: 1px solid {t["border"]}"><span style="display: flex; gap: 4px; min-width: 96px">{"".join(kbd(k, t) for k in keys)}</span>'
                       f'<span style="flex: 1; font-size: 14px; font-weight: 600">{what}</span>{"<span style=\"font-size: 11px; font-weight: 800; color: " + t["accent"] + "\">nuova</span>" if new else ""}</li>' for keys, what, new in items)
        return (f'<section style="flex: 1 1 240px; min-width: 0; display: flex; flex-direction: column; gap: 4px"><h3 style="margin: 0 0 6px; font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: {t["muted"]}">{title}</h3>'
                f'<ul style="list-style: none; margin: 0; padding: 0">{rows}</ul></section>')
    inner = f'''<div style="display: flex; align-items: center; gap: 12px">{ui_circle('keyboard', t, 44, 22)}
<h2 style="margin: 0; flex: 1; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">Scorciatoie da tastiera</h2>
<button type="button" aria-label="Chiudi (Esc)" style="height: 40px; padding: 0 10px 0 12px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; display: flex; align-items: center; gap: 8px">{icon('x', 18, sw=2.2)}{kbd('Esc', t)}</button></div>
<div style="display: flex; flex-wrap: wrap; gap: 24px">
{grp('Ovunque', [(['N'], 'Nuovo movimento', False), (['/'], 'Cerca', False), (['?'], 'Mostra questo elenco', True), (['Esc'], 'Chiude la finestra', True)])}
{grp('Movimenti e Analisi', [(['←'], 'Mese precedente', False), (['→'], 'Mese successivo', False)])}
{grp('Nei moduli', [(['Invio'], 'Salva', True), (['Tab'], 'Campo successivo', False)])}</div>
<p style="margin: 0; font-size: 13px; color: {t['muted']}">Mentre scrivi in un campo le lettere restano lettere: N e / funzionano solo fuori dai campi.</p>'''
    return movimenti(t, dark) + modal(inner, t, 'Scorciatoie da tastiera', 720, 120)

PC_SCREENS = [('movimenti', 'Movimenti', movimenti, 820), ('nuova-spesa', 'Nuova spesa in finestra', nuova, 820),
              ('analisi', 'Analisi', analisi, 1060), ('conti', 'Conti con dettaglio', conti, 900), ('scorciatoie', 'Scorciatoie', scorciatoie, 820)]
