#!/usr/bin/env python3
"""Genera le tavole delle tre direzioni di stile di Statera (dati finti)."""
import json, os, datetime

OUT = os.environ.get('STATERA_CANVAS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'project'))
os.makedirs(OUT, exist_ok=True)
W, H = 390, 844

# ---------------------------------------------------------------- icone
IC = {
 'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
 'chevL': '<path d="M15 6l-6 6 6 6"/>',
 'chevR': '<path d="M9 6l6 6-6 6"/>',
 'chevD': '<path d="M6 9l6 6 6-6"/>',
 'plus': '<path d="M12 5v14M5 12h14"/>',
 'list': '<path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
 'wallet': '<rect x="3" y="6" width="18" height="14" rx="2.5"/><path d="M3 10h18M16 15h2"/>',
 'chart': '<path d="M3 20h18"/><path d="M6 17v-6M11 17V6M16 17v-8"/>',
 'more': '<circle cx="5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="19" cy="12" r="1.2"/>',
 'cart': '<path d="M3 4h2l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.2"/><circle cx="9.5" cy="19.5" r="1.2"/><circle cx="17" cy="19.5" r="1.2"/>',
 'food': '<path d="M7 3v18M4.5 3v5a2.5 2.5 0 0 0 5 0V3M17.5 21V3c-2 1.2-3 3.8-3 7v4h3"/>',
 'fuel': '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h12M4 10h10M14 9h2a2 2 0 0 1 2 2v5a1.5 1.5 0 0 0 3 0V8l-3-3"/>',
 'work': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
 'repeat': '<path d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/>',
 'bus': '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 21v-3M16 21v-3"/>',
 'home': '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
 'in': '<path d="M17 7L7 17M7 9v8h8"/>',
 'out': '<path d="M7 17L17 7M9 7h8v8"/>',
 'swap': '<path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/>',
 'cal': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 'card': '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6 15h4"/>',
 'ticket': '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M15 7v10"/>',
 'x': '<path d="M6 6l12 12M18 6L6 18"/>',
 'star': '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
 'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
 'gift': '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13M12 8c-1.5-3-5-3-5-1s3 1 5 1c2 0 5 1 5-1s-3.5-2-5 1"/>',
 'shirt': '<path d="M8 3l-5 3 2 4 2-1v12h10V9l2 1 2-4-5-3c-.5 1.5-2 2.5-4 2.5S8.5 4.5 8 3z"/>',
 'game': '<rect x="2.5" y="7" width="19" height="11" rx="4"/><path d="M7 11v3M5.5 12.5h3M15.5 12h.01M18 13.5h.01"/>',
 'plane': '<path d="M2 16l20-8-6 12-3-5z"/><path d="M13 15l-11 1"/>',
 'pen': '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
 'check': '<path d="M5 12l5 5 9-10"/>',
 'alert': '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
}

def icon(name, size=20, color='currentColor', sw=1.8, label=None):
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {aria} '
            f'style="flex-shrink: 0; display: block">{IC[name]}</svg>')

# ---------------------------------------------------------------- dati finti
MOV = [
  ('Sabato 14 novembre', '−50,30 €', [
    ('cart', 's1', 'Conad', 'Spesa alimentare', 'Bancomat', '−42,30 €', False),
    ('food', 's2', 'Pranzo', 'Pasti fuori', '1 buono pasto', '−8,00 €', False)]),
  ('Venerdì 13 novembre', '−61,99 €', [
    ('fuel', 's3', 'Q8 via Appia', 'Carburante', 'Bancomat', '−50,00 €', False),
    ('repeat', 's5', 'Musica in streaming', 'Abbonamenti', 'Conto corrente', '−11,99 €', False)]),
  ('Giovedì 12 novembre', '+1.815,00 €', [
    ('work', 's6', 'Stipendio ottobre', 'Stipendio', 'Conto corrente', '+1.850,00 €', True),
    ('bus', 's4', 'Abbonamento bus', 'Mezzi pubblici', 'Contanti', '−35,00 €', False)]),
]
CATS = [('Casa', 240.00, '240,00 €', 35, 'home'), ('Spesa alimentare', 168.40, '168,40 €', 25, 'cart'),
        ('Trasporti', 120.00, '120,00 €', 18, 'bus'), ('Pasti fuori', 72.00, '72,00 €', 11, 'food'),
        ('Abbonamenti', 41.97, '41,97 €', 6, 'repeat'), ('Altro', 41.98, '41,98 €', 6, 'more')]
MONTHS = [('Giu', 2010, 1420), ('Lug', 2010, 1610), ('Ago', 2240, 1980), ('Set', 2010, 1240), ('Ott', 2050, 1380), ('Nov', 2010, 684)]
PICK = [('cart', 's1', 'Spesa alimentare'), ('food', 's2', 'Pasti fuori'), ('fuel', 's3', 'Carburante'),
        ('bus', 's4', 'Mezzi pubblici'), ('home', 's7', 'Casa'), ('heart', 's6', 'Salute'),
        ('shirt', 's8', 'Abbigliamento'), ('game', 's5', 'Svago'), ('plane', 's3', 'Viaggi'),
        ('gift', 's2', 'Regali'), ('repeat', 's5', 'Abbonamenti'), ('more', 's4', 'Altro')]

# ---------------------------------------------------------------- direzioni
DIRS = {
 'A': dict(
   name='Bilancia', sub='ardesia e ottone, sobria e calda',
   head="'Fraunces', Georgia, serif", body="'Inter', system-ui, sans-serif", num="'Inter', system-ui, sans-serif",
   fonts='family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600',
   r=16, rs=10, light=dict(
     bg='#F4F1EA', surf='#FFFFFF', surf2='#ECE7DC', border='#DED7C8', text='#1C2A31', muted='#5B676C',
     primary='#1C2A31', onp='#F4F1EA', accent='#7E5615', accentSoft='#F1E4C8', income='#1C7546',
     chIn='#2A78D6', chOut='#EB6834', track='#ECE7DC', backdrop='rgba(18,23,26,0.45)'),
   dark=dict(
     bg='#12171A', surf='#1B2226', surf2='#242C31', border='#323C42', text='#ECE8E0', muted='#9EA7AB',
     primary='#D4A24C', onp='#1B1408', accent='#D9A955', accentSoft='#3A3020', income='#62C990',
     chIn='#3987E5', chOut='#D95926', track='#2A3338', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#3F7D6E', s2='#B5653A', s3='#4A6FA5', s4='#7A6A58', s5='#7B5EA7', s6='#2F8F9D', s7='#A24F7A', s8='#6B7A3A')),
 'B': dict(
   name='Vivace', sub='stile neobank: grande, colorata, a tocchi',
   head="'Plus Jakarta Sans', system-ui, sans-serif", body="'Plus Jakarta Sans', system-ui, sans-serif", num="'Plus Jakarta Sans', system-ui, sans-serif",
   fonts='family=Plus+Jakarta+Sans:wght@400;500;600;700;800',
   r=24, rs=16, light=dict(
     bg='#F2F3F8', surf='#FFFFFF', surf2='#E9EBF3', border='#E1E4EE', text='#0E1220', muted='#596075',
     primary='#3B38D6', onp='#FFFFFF', accent='#3B38D6', accentSoft='#E7E6FC', income='#0E7A57',
     chIn='#2A78D6', chOut='#EB6834', track='#E9EBF3', backdrop='rgba(14,18,32,0.5)'),
   dark=dict(
     bg='#0B0D14', surf='#161925', surf2='#20243A', border='#2A2F45', text='#F2F3F8', muted='#A0A6BB',
     primary='#8F8CFF', onp='#0B0D14', accent='#9C99FF', accentSoft='#262551', income='#4FD9A0',
     chIn='#3987E5', chOut='#D95926', track='#20243A', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#1E8A63', s2='#D9622B', s3='#2F6FDB', s4='#7A6A58', s5='#8B4FD9', s6='#0C8EA6', s7='#C2417F', s8='#6E8A1F')),
 'C': dict(
   name='Registro', sub='essenziale e densa, da strumento di lavoro',
   head="'IBM Plex Sans', system-ui, sans-serif", body="'IBM Plex Sans', system-ui, sans-serif", num="'IBM Plex Mono', ui-monospace, monospace",
   fonts='family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600',
   r=6, rs=4, light=dict(
     bg='#FFFFFF', surf='#FFFFFF', surf2='#F3F4F3', border='#E1E4E2', text='#111413', muted='#58605C',
     primary='#0E5C52', onp='#FFFFFF', accent='#0E5C52', accentSoft='#E2F0ED', income='#0D7049',
     chIn='#2A78D6', chOut='#EB6834', track='#EEF0EF', backdrop='rgba(17,20,19,0.45)'),
   dark=dict(
     bg='#0F1211', surf='#151918', surf2='#1D2220', border='#2B3230', text='#E8ECEA', muted='#9CA5A1',
     primary='#5FC4B0', onp='#0F1211', accent='#6CCDB9', accentSoft='#1C3330', income='#6BD39B',
     chIn='#3987E5', chOut='#D95926', track='#232927', backdrop='rgba(0,0,0,0.6)'),
   sw=dict(s1='#3F7D6E', s2='#B5653A', s3='#4A6FA5', s4='#7A6A58', s5='#7B5EA7', s6='#2F8F9D', s7='#A24F7A', s8='#6B7A3A')),
}
# tinte chiare per lo sfondo delle icone (B)
def tint(hexc, a):
    h = hexc.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r},{g},{b},{a})'

# ---------------------------------------------------------------- pagina
def page(title, d, t, body):
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
<div style="width: {W}px; height: {H}px; position: relative; overflow: hidden; box-sizing: border-box; background: {t['bg']}; color: {t['text']}; font-family: {d['body']}; font-variant-numeric: tabular-nums">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

def btn_icon(name, label, t, size=40, bg='transparent', color=None, radius='50%', border='none'):
    color = color or t['text']
    return (f'<button type="button" aria-label="{label}" style="width: {size}px; height: {size}px; border-radius: {radius}; '
            f'border: {border}; background: {bg}; color: {color}; display: flex; align-items: center; justify-content: center; padding: 0; cursor: pointer">'
            f'{icon(name, 20)}</button>')

NAV = [('list', 'Movimenti'), ('wallet', 'Conti'), ('chart', 'Analisi'), ('more', 'Altro')]

# ================================================================ A — Bilancia
def A_nav(t, active):
    items = ''
    for ic, lab in NAV:
        on = lab == active
        pill = f'background: {t["accentSoft"]}; color: {t["accent"]}' if on else f'color: {t["muted"]}'
        items += (f'<a href="#" style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; text-decoration: none; '
                  f'color: {t["accent"] if on else t["muted"]}; font-size: 12px; font-weight: {600 if on else 500}">'
                  f'<span style="width: 56px; height: 30px; border-radius: 15px; display: flex; align-items: center; justify-content: center; {pill}">{icon(ic, 20)}</span>{lab}</a>')
    return (f'<nav aria-label="Sezioni" style="position: absolute; left: 0; right: 0; bottom: 0; height: 76px; box-sizing: border-box; padding: 8px 8px 12px; '
            f'background: {t["surf"]}; border-top: 1px solid {t["border"]}; display: flex">{items}</nav>')

def A_mov(d, t, dark):
    sw = d['sw']
    rows = ''
    for day, net, items in MOV:
        lis = ''
        for i, (ic, s, desc, cat, src, amt, inc) in enumerate(items):
            sep = f'border-top: 1px solid {t["border"]};' if i else ''
            lis += (f'<li style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; {sep}">'
                    f'<span style="width: 36px; height: 36px; border-radius: 10px; background: {t["surf2"]}; color: {sw[s] if not dark else t["text"]}; display: flex; align-items: center; justify-content: center">{icon(ic, 18)}</span>'
                    f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 500">{desc}</span>'
                    f'<span style="font-size: 13px; color: {t["muted"]}">{cat} · {src}</span></span>'
                    f'<span style="font-size: 15px; font-weight: 600; color: {t["income"] if inc else t["text"]}">{amt}</span></li>')
        rows += (f'<section style="display: flex; flex-direction: column; gap: 8px"><h2 style="margin: 0; padding: 0 4px; display: flex; justify-content: space-between; font-size: 13px; font-weight: 500; color: {t["muted"]}">'
                 f'<span>{day}</span><span>{net}</span></h2>'
                 f'<ul style="list-style: none; margin: 0; padding: 0; background: {t["surf"]}; border: 1px solid {t["border"]}; border-radius: {d["r"]}px">{lis}</ul></section>')
    favs = ''.join(f'<button type="button" style="height: 36px; padding: 0 14px; border-radius: 18px; border: 1px solid {t["border"]}; background: {t["surf"]}; color: {t["text"]}; font: inherit; font-size: 14px; display: flex; align-items: center; gap: 6px; white-space: nowrap">{icon(i, 16, t["accent"])}{l}</button>'
                   for i, l in [('star', 'Caffè 1,20'), ('food', 'Pranzo con buono'), ('fuel', 'Carburante')])
    body = f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 18px">
<header style="display: flex; align-items: center; gap: 4px">
{btn_icon('chevL', 'Mese precedente', t)}
<h1 style="margin: 0; font-family: {d['head']}; font-size: 24px; font-weight: 600; letter-spacing: -0.01em">Novembre 2026</h1>
{btn_icon('chevR', 'Mese successivo', t)}
<span style="flex: 1"></span>
{btn_icon('search', 'Cerca', t, bg=t['surf'], border=f"1px solid {t['border']}")}
</header>
<div style="background: {t['primary'] if not dark else t['surf']}; color: {t['onp'] if not dark else t['text']}; border-radius: {d['r']+4}px; padding: 20px; display: flex; flex-direction: column; gap: 16px; {'' if not dark else 'border: 1px solid '+t['border']}">
<div style="display: flex; flex-direction: column; gap: 4px"><span style="font-size: 13px; opacity: 0.8">Saldo del mese</span>
<span style="font-family: {d['head']}; font-size: 38px; font-weight: 500; letter-spacing: -0.02em">+1.325,65 €</span></div>
<div style="display: flex; gap: 12px; border-top: 1px solid {'rgba(244,241,234,0.18)' if not dark else t['border']}; padding-top: 14px">
<div style="flex: 1; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; opacity: 0.75">Entrate</span><span style="font-size: 16px; font-weight: 600">2.010,00 €</span></div>
<div style="flex: 1; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; opacity: 0.75">Uscite</span><span style="font-size: 16px; font-weight: 600">684,35 €</span></div>
<div style="flex: 1; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; opacity: 0.75">Al giorno</span><span style="font-size: 16px; font-weight: 600">48,88 €</span></div>
</div></div>
<div style="display: flex; gap: 8px; overflow: hidden">{favs}</div>
{rows}
</div>
<button type="button" aria-label="Nuovo movimento" style="position: absolute; right: 20px; bottom: 92px; width: 60px; height: 60px; border-radius: 20px; border: none; background: {t['accent'] if not dark else t['primary']}; color: {'#FFFFFF' if not dark else t['onp']}; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 20px rgba(28,42,49,0.28)">{icon('plus', 26, sw=2.2)}</button>
{A_nav(t, 'Movimenti')}'''
    return body

def field(label, value, t, d, ic=None, h=52, extra=''):
    ico = icon(ic, 18, t['muted']) if ic else ''
    return (f'<label style="display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: {t["muted"]}; font-weight: 500">{label}'
            f'<span style="height: {h}px; box-sizing: border-box; display: flex; align-items: center; gap: 10px; padding: 0 14px; background: {t["surf"]}; border: 1px solid {t["border"]}; border-radius: {d["rs"]}px; {extra}">{ico}'
            f'<input type="text" value="{value}" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 16px; color: {t["text"]}"></span></label>')

def seg(opts, active, t, d, h=40, radius=None, act_bg=None, act_col=None):
    radius = radius if radius is not None else d['rs']
    act_bg = act_bg or t['surf']; act_col = act_col or t['text']
    out = ''
    for o in opts:
        on = o == active
        out += (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="flex: 1; height: {h-8}px; border: none; border-radius: {max(radius-3,2)}px; font: inherit; font-size: 14px; font-weight: {600 if on else 500}; '
                f'background: {act_bg if on else "transparent"}; color: {act_col if on else t["muted"]}; {"box-shadow: 0 1px 3px rgba(0,0,0,0.12);" if on else ""}">{o}</button>')
    return f'<div style="display: flex; gap: 4px; padding: 4px; background: {t["surf2"]}; border-radius: {radius}px">{out}</div>'

def sheet_wrap(t, d, inner, top=96, radius=None):
    radius = radius if radius is not None else d['r'] + 8
    return f'''<div aria-hidden="true" style="position: absolute; inset: 0; background: {t['bg']}"></div>
<div aria-hidden="true" style="position: absolute; inset: 0; background: {t['backdrop']}"></div>
<div role="dialog" aria-label="Nuova uscita" style="position: absolute; left: 0; right: 0; bottom: 0; top: {top}px; background: {t['bg']}; border-radius: {radius}px {radius}px 0 0; padding: 10px 20px 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">
<span aria-hidden="true" style="align-self: center; width: 40px; height: 4px; border-radius: 2px; background: {t['border']}"></span>
{inner}
</div>'''

def A_new(d, t, dark):
    chips = ''
    for ic, s, lab in PICK[:8]:
        on = lab == 'Spesa alimentare'
        chips += (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="height: 38px; padding: 0 12px; border-radius: 19px; font: inherit; font-size: 14px; display: flex; align-items: center; gap: 6px; '
                  f'border: 1px solid {t["accent"] if on else t["border"]}; background: {t["accentSoft"] if on else t["surf"]}; color: {t["text"]}; font-weight: {600 if on else 400}">{icon(ic, 16, d["sw"][s] if not dark else t["muted"])}{lab}</button>')
    inner = f'''<div style="display: flex; align-items: center; justify-content: space-between">
<h1 style="margin: 0; font-family: {d['head']}; font-size: 22px; font-weight: 600">Nuova uscita</h1>{btn_icon('x', 'Chiudi', t)}</div>
{seg(['Uscita', 'Entrata', 'Trasferimento'], 'Uscita', t, d)}
<label style="display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 8px 0; font-size: 13px; color: {t['muted']}">Importo
<span style="display: flex; align-items: baseline; gap: 6px"><input type="text" value="42,30" readonly size="5" style="width: 150px; text-align: right; border: none; outline: none; background: transparent; font-family: {d['head']}; font-size: 48px; font-weight: 500; color: {t['text']}"><span style="font-family: {d['head']}; font-size: 32px; color: {t['muted']}">€</span></span></label>
<div style="display: flex; gap: 8px">
<button type="button" style="height: 38px; padding: 0 14px; border-radius: 19px; border: 1px solid {t['accent']}; background: {t['accentSoft']}; color: {t['text']}; font: inherit; font-size: 14px; font-weight: 600">Oggi</button>
<button type="button" style="height: 38px; padding: 0 14px; border-radius: 19px; border: 1px solid {t['border']}; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 14px">Ieri</button>
<button type="button" style="height: 38px; padding: 0 14px; border-radius: 19px; border: 1px solid {t['border']}; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 14px; display: flex; align-items: center; gap: 6px">{icon('cal', 16, t['muted'])}14/11/2026</button></div>
{field('Con', 'Bancomat · Conto corrente', t, d, 'card')}
<div style="display: flex; flex-direction: column; gap: 8px"><span style="font-size: 13px; color: {t['muted']}; font-weight: 500">Categoria</span>
<div style="display: flex; flex-wrap: wrap; gap: 8px">{chips}</div></div>
{field('Descrizione', 'Conad', t, d)}
<span style="flex: 1"></span>
<div style="display: flex; gap: 10px">
<button type="button" style="flex: 1; height: 52px; border-radius: {d['rs']+4}px; border: 1px solid {t['border']}; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 15px; font-weight: 600">Salva e nuovo</button>
<button type="button" style="flex: 1; height: 52px; border-radius: {d['rs']+4}px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 15px; font-weight: 600">Salva</button></div>'''
    return sheet_wrap(t, d, inner, top=70)

def cols(t, height=120, barw=14, gap=4, labcol=None, radius=3, font=None):
    mx = 2240
    out = ''
    for m, i, o in MONTHS:
        out += (f'<div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px">'
                f'<div style="height: {height}px; display: flex; align-items: flex-end; gap: {gap}px">'
                f'<span style="width: {barw}px; height: {round(i/mx*height)}px; background: {t["chIn"]}; border-radius: {radius}px {radius}px 0 0"></span>'
                f'<span style="width: {barw}px; height: {round(o/mx*height)}px; background: {t["chOut"]}; border-radius: {radius}px {radius}px 0 0"></span></div>'
                f'<span style="font-size: 12px; color: {labcol or t["muted"]}">{m}</span></div>')
    legend = (f'<div style="display: flex; gap: 16px; font-size: 13px; color: {t["muted"]}">'
              f'<span style="display: flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: {t["chIn"]}"></span>Entrate</span>'
              f'<span style="display: flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: {t["chOut"]}"></span>Uscite</span></div>')
    return f'<div role="img" aria-label="Entrate e uscite degli ultimi 6 mesi" style="display: flex; flex-direction: column; gap: 12px">{legend}<div style="display: flex; gap: 4px; border-bottom: 1px solid {t["border"]}; padding-bottom: 0">{out}</div></div>'

def A_an(d, t, dark):
    bars = ''
    for name, v, s, p, ic in CATS[:5]:
        bars += (f'<li style="display: flex; flex-direction: column; gap: 6px"><span style="display: flex; justify-content: space-between; font-size: 14px">'
                 f'<span style="font-weight: 500">{name}</span><span><span style="color: {t["muted"]}">{p}% · </span>{s}</span></span>'
                 f'<span style="height: 8px; border-radius: 4px; background: {t["track"]}; display: block"><span style="display: block; height: 8px; width: {round(p/35*100)}%; border-radius: 4px; background: {t["chOut"]}"></span></span></li>')
    tile = lambda lab, val, note: (f'<div style="flex: 1; background: {t["surf"]}; border: 1px solid {t["border"]}; border-radius: {d["r"]}px; padding: 12px; display: flex; flex-direction: column; gap: 4px">'
                                   f'<span style="font-size: 12px; color: {t["muted"]}">{lab}</span><span style="font-family: {d["head"]}; font-size: 19px; font-weight: 600">{val}</span>'
                                   f'<span style="font-size: 12px; color: {t["muted"]}">{note}</span></div>')
    body = f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 16px">
<header style="display: flex; align-items: center; justify-content: space-between"><h1 style="margin: 0; font-family: {d['head']}; font-size: 28px; font-weight: 600">Analisi</h1>
<div style="width: 160px">{seg(['Mese', 'Anno'], 'Mese', t, d, h=40)}</div></header>
<div style="display: flex; gap: 8px">{tile('Entrate', '2.010 €', 'novembre')}{tile('Uscite', '684 €', 'stima 1.480 €')}{tile('Risparmio', '66%', '1.325,65 €')}</div>
<section style="background: {t['surf']}; border: 1px solid {t['border']}; border-radius: {d['r']}px; padding: 16px; display: flex; flex-direction: column; gap: 14px">
<h2 style="margin: 0; font-family: {d['head']}; font-size: 18px; font-weight: 600">Dove vanno i soldi</h2>
<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px">{bars}</ul></section>
<section style="background: {t['surf']}; border: 1px solid {t['border']}; border-radius: {d['r']}px; padding: 16px; display: flex; flex-direction: column; gap: 12px">
<h2 style="margin: 0; font-family: {d['head']}; font-size: 18px; font-weight: 600">Ultimi 6 mesi</h2>{cols(t, 100)}</section>
</div>
{A_nav(t, 'Analisi')}'''
    return body

# ================================================================ B — Vivace
def B_nav(t, active):
    def it(ic, lab):
        on = lab == active
        return (f'<a href="#" style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; text-decoration: none; font-size: 11px; font-weight: {700 if on else 500}; color: {t["primary"] if on else t["muted"]}">'
                f'{icon(ic, 22, sw=2 if on else 1.8)}{lab}</a>')
    plus = (f'<button type="button" aria-label="Nuovo movimento" style="width: 56px; height: 56px; margin-top: -26px; border-radius: 50%; border: 4px solid {t["bg"]}; background: {t["primary"]}; color: {t["onp"]}; '
            f'display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px {tint(t["primary"] if t["primary"].startswith("#") else "#3B38D6", 0.35)}; flex-shrink: 0">{icon("plus", 26, sw=2.4)}</button>')
    return (f'<nav aria-label="Sezioni" style="position: absolute; left: 12px; right: 12px; bottom: 14px; height: 66px; border-radius: 33px; background: {t["surf"]}; '
            f'box-shadow: 0 6px 24px rgba(14,18,32,0.10); display: flex; align-items: center; padding: 0 8px">'
            f'{it(*NAV[0])}{it(*NAV[1])}{plus}{it(*NAV[2])}{it(*NAV[3])}</nav>')

def B_mov(d, t, dark):
    sw = d['sw']
    rows = ''
    for day, net, items in MOV:
        lis = ''
        for ic, s, desc, cat, src, amt, inc in items:
            lis += (f'<li style="display: flex; align-items: center; gap: 14px; padding: 10px 0">'
                    f'<span style="width: 44px; height: 44px; border-radius: 50%; background: {tint(sw[s], 0.16 if not dark else 0.28)}; color: {sw[s] if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center">{icon(ic, 20, sw=2)}</span>'
                    f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 700">{desc}</span>'
                    f'<span style="font-size: 13px; color: {t["muted"]}">{cat} · {src}</span></span>'
                    f'<span style="font-size: 15px; font-weight: 700; color: {t["income"] if inc else t["text"]}">{amt}</span></li>')
        rows += (f'<h2 style="margin: 14px 0 2px; font-size: 13px; font-weight: 600; color: {t["muted"]}; display: flex; justify-content: space-between"><span>{day}</span><span>{net}</span></h2>'
                 f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>')
    qa = ''
    for ic, lab in [('out', 'Spesa'), ('in', 'Entrata'), ('swap', 'Trasferisci'), ('star', 'Preferiti')]:
        qa += (f'<button type="button" style="flex: 1; border: none; background: transparent; padding: 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 8px; font-size: 13px; font-weight: 600">'
               f'<span style="width: 52px; height: 52px; border-radius: 50%; background: {t["accentSoft"]}; color: {t["accent"]}; display: flex; align-items: center; justify-content: center">{icon(ic, 22, sw=2.1)}</span>{lab}</button>')
    body = f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 20px">
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
<div style="display: flex; gap: 10px">
<div style="flex: 1; background: {t['surf']}; border-radius: {d['rs']+4}px; padding: 14px; display: flex; align-items: center; gap: 10px">
<span style="width: 32px; height: 32px; border-radius: 50%; background: {tint('#1E8A63', 0.16 if not dark else 0.3)}; color: {t['income']}; display: flex; align-items: center; justify-content: center">{icon('in', 18, sw=2.2)}</span>
<span style="display: flex; flex-direction: column"><span style="font-size: 12px; color: {t['muted']}">Entrate</span><span style="font-size: 16px; font-weight: 800">2.010,00 €</span></span></div>
<div style="flex: 1; background: {t['surf']}; border-radius: {d['rs']+4}px; padding: 14px; display: flex; align-items: center; gap: 10px">
<span style="width: 32px; height: 32px; border-radius: 50%; background: {tint('#D9622B', 0.16 if not dark else 0.3)}; color: {'#B34A17' if not dark else '#F29A6B'}; display: flex; align-items: center; justify-content: center">{icon('out', 18, sw=2.2)}</span>
<span style="display: flex; flex-direction: column"><span style="font-size: 12px; color: {t['muted']}">Uscite</span><span style="font-size: 16px; font-weight: 800">684,35 €</span></span></div></div>
<div style="background: {t['surf']}; border-radius: {d['r']}px; padding: 4px 18px 10px">{rows}</div>
</div>
{B_nav(t, 'Movimenti')}'''
    return body

def B_new(d, t, dark):
    sw = d['sw']
    grid = ''
    for ic, s, lab in PICK:
        on = lab == 'Spesa alimentare'
        grid += (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="border: none; background: transparent; padding: 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 11px; font-weight: {700 if on else 500}; text-align: center">'
                 f'<span style="width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; '
                 f'background: {sw[s] if on else tint(sw[s], 0.16 if not dark else 0.28)}; color: {"#FFFFFF" if on or dark else sw[s]}; {"box-shadow: 0 0 0 3px "+t["bg"]+", 0 0 0 5px "+sw[s]+";" if on else ""}">{icon(ic, 22, sw=2)}</span>{lab}</button>')
    inner = f'''<div style="display: flex; align-items: center; justify-content: space-between">
{btn_icon('x', 'Chiudi', t, bg=t['surf'])}
<div style="width: 230px">{seg(['Uscita', 'Entrata', 'Trasf.'], 'Uscita', t, d, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div>
<span style="width: 40px"></span></div>
<label style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0 0; font-size: 14px; color: {t['muted']}; font-weight: 500">Quanto hai speso?
<span style="display: flex; align-items: baseline; gap: 4px"><input type="text" value="42,30" readonly size="5" style="width: 160px; text-align: right; border: none; outline: none; background: transparent; font-family: {d['head']}; font-size: 56px; font-weight: 800; letter-spacing: -0.03em; color: {t['text']}"><span style="font-size: 34px; font-weight: 800; color: {t['muted']}">€</span></span></label>
<div style="display: flex; gap: 8px; justify-content: center">
<button type="button" style="height: 40px; padding: 0 14px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px">{icon('cal', 16, t['accent'])}Oggi</button>
<button type="button" style="height: 40px; padding: 0 14px; border-radius: 20px; border: none; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px">{icon('card', 16, t['accent'])}Bancomat</button></div>
<div style="background: {t['surf']}; border-radius: {d['r']}px; padding: 16px 12px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: 14px; column-gap: 4px">{grid}</div>
<label style="display: flex; align-items: center; gap: 10px; height: 52px; padding: 0 16px; background: {t['surf']}; border-radius: {d['rs']}px; font-size: 14px; color: {t['muted']}">{icon('pen', 18, t['muted'])}<span style="position: absolute; width: 1px; height: 1px; overflow: hidden">Descrizione</span>
<input type="text" value="Conad" readonly style="flex: 1; border: none; outline: none; background: transparent; font: inherit; font-size: 16px; color: {t['text']}"></label>
<span style="flex: 1"></span>
<button type="button" style="height: 58px; border-radius: 29px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 17px; font-weight: 800">Salva spesa</button>
<button type="button" style="height: 24px; border: none; background: transparent; color: {t['accent']}; font: inherit; font-size: 14px; font-weight: 700; margin-top: -6px">Salva e aggiungine un'altra</button>'''
    return sheet_wrap(t, d, inner, top=56, radius=32)

def B_an(d, t, dark):
    sw = d['sw']
    lst = ''
    sws = ['s7', 's1', 's4', 's2', 's5']
    for (name, v, s, p, ic), k in zip(CATS[:5], sws):
        lst += (f'<li style="display: flex; align-items: center; gap: 12px">'
                f'<span style="width: 40px; height: 40px; border-radius: 50%; background: {tint(sw[k], 0.16 if not dark else 0.28)}; color: {sw[k] if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center">{icon(ic, 19, sw=2)}</span>'
                f'<span style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="display: flex; justify-content: space-between; font-size: 14px"><span style="font-weight: 700">{name}</span><span style="font-weight: 700">{s}</span></span>'
                f'<span style="height: 6px; border-radius: 3px; background: {t["track"]}; display: block"><span style="display: block; height: 6px; width: {round(p/35*100)}%; border-radius: 3px; background: {t["chOut"]}"></span></span></span></li>')
    body = f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 16px">
<header style="display: flex; align-items: center; justify-content: space-between"><h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em">Analisi</h1>
<div style="width: 170px">{seg(['Mese', 'Anno'], 'Mese', t, d, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div></header>
<div style="background: {t['primary']}; color: {t['onp']}; border-radius: {d['r']}px; padding: 20px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 14px; font-weight: 600; opacity: 0.85">A novembre hai risparmiato</span>
<span style="font-size: 40px; font-weight: 800; letter-spacing: -0.03em">1.325,65 €</span>
<span style="display: flex; gap: 8px; flex-wrap: wrap">
<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: rgba(255,255,255,0.18); display: flex; align-items: center; font-size: 13px; font-weight: 700">66% delle entrate</span>
<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: rgba(255,255,255,0.18); display: flex; align-items: center; font-size: 13px; font-weight: 700">Stima uscite 1.480 €</span></span></div>
<div style="background: {t['surf']}; border-radius: {d['r']}px; padding: 18px; display: flex; flex-direction: column; gap: 14px">
<h2 style="margin: 0; font-size: 17px; font-weight: 800">Categorie</h2>
<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">{lst}</ul></div>
<div style="background: {t['surf']}; border-radius: {d['r']}px; padding: 18px; display: flex; flex-direction: column; gap: 10px">
<h2 style="margin: 0; font-size: 17px; font-weight: 800">Ultimi 6 mesi</h2>{cols(t, 70, barw=12, radius=6)}</div>
</div>
{B_nav(t, 'Analisi')}'''
    return body

# ================================================================ C — Registro
def C_nav(t, active):
    items = ''
    for ic, lab in NAV:
        on = lab == active
        items += (f'<a href="#" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; text-decoration: none; font-size: 11px; font-weight: {600 if on else 400}; '
                  f'color: {t["text"] if on else t["muted"]}; border-top: 2px solid {t["primary"] if on else "transparent"}; margin-top: -1px">{icon(ic, 20, sw=1.6)}{lab}</a>')
    return (f'<nav aria-label="Sezioni" style="position: absolute; left: 0; right: 0; bottom: 0; height: 60px; background: {t["surf"]}; border-top: 1px solid {t["border"]}; display: flex">{items}</nav>')

def C_mov(d, t, dark):
    sw = d['sw']; N = d['num']
    rows = ''
    for day, net, items in MOV:
        rows += (f'<h2 style="margin: 0; height: 30px; padding: 0 16px; background: {t["surf2"]}; display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 600; color: {t["muted"]}; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid {t["border"]}">'
                 f'<span>{day}</span><span style="font-family: {N}; letter-spacing: 0; text-transform: none">{net}</span></h2>')
        lis = ''
        for ic, s, desc, cat, src, amt, inc in items:
            lis += (f'<li style="display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 16px; border-bottom: 1px solid {t["border"]}">'
                    f'<span aria-hidden="true" style="width: 4px; height: 32px; border-radius: 2px; background: {sw[s]}"></span>'
                    f'<span style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px"><span style="font-size: 15px; font-weight: 500">{desc}</span>'
                    f'<span style="font-size: 12px; color: {t["muted"]}">{cat} · {src}</span></span>'
                    f'<span style="font-family: {N}; font-size: 14px; font-weight: 500; color: {t["income"] if inc else t["text"]}">{amt}</span></li>')
        rows += f'<ul style="list-style: none; margin: 0; padding: 0">{lis}</ul>'
    stat = lambda lab, val, col: (f'<div style="flex: 1; padding: 10px 12px; display: flex; flex-direction: column; gap: 3px"><span style="font-size: 11px; color: {t["muted"]}; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600">{lab}</span>'
                                  f'<span style="font-family: {N}; font-size: 15px; font-weight: 600; color: {col}">{val}</span></div>')
    body = f'''<header style="height: 56px; padding: 0 8px 0 4px; display: flex; align-items: center; gap: 0; border-bottom: 1px solid {t['border']}">
{btn_icon('chevL', 'Mese precedente', t, size=44)}
<h1 style="margin: 0; font-size: 17px; font-weight: 600">Novembre 2026</h1>
{btn_icon('chevR', 'Mese successivo', t, size=44)}
<span style="flex: 1"></span>
{btn_icon('search', 'Cerca', t, size=44)}{btn_icon('cal', 'Calendario', t, size=44)}
</header>
<div style="display: flex; border-bottom: 1px solid {t['border']}">
{stat('Entrate', '2.010,00', t['income'])}<span style="width: 1px; background: {t['border']}"></span>{stat('Uscite', '684,35', t['text'])}<span style="width: 1px; background: {t['border']}"></span>{stat('Saldo', '+1.325,65', t['text'])}</div>
<div style="padding: 10px 16px; display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid {t['border']}">
<span style="display: flex; justify-content: space-between; font-size: 12px; color: {t['muted']}"><span>Budget del mese · 1.600,00</span><span style="font-family: {N}">43% usato</span></span>
<span style="height: 4px; background: {t['track']}; display: block; border-radius: 2px"><span style="display: block; height: 4px; width: 43%; background: {t['primary']}; border-radius: 2px"></span></span></div>
{rows}
<button type="button" style="position: absolute; right: 16px; bottom: 76px; height: 48px; padding: 0 18px 0 14px; border-radius: {d['r']}px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.18)">{icon('plus', 20, sw=2)}Nuovo</button>
{C_nav(t, 'Movimenti')}'''
    return body

def C_new(d, t, dark):
    N = d['num']; sw = d['sw']
    def row(label, value, ic=None, sub=None, active=False):
        ico = f'<span style="width: 10px; height: 10px; border-radius: 2px; background: {ic}"></span>' if ic and ic.startswith('#') else (icon(ic, 18, t['muted']) if ic else '')
        return (f'<label style="display: flex; align-items: center; gap: 12px; height: 52px; padding: 0 16px; border-bottom: 1px solid {t["border"]}; font-size: 14px; color: {t["muted"]}">'
                f'<span style="width: 92px">{label}</span>{ico}<input type="text" value="{value}" readonly style="flex: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; color: {t["text"]}">'
                f'{icon("chevR", 16, t["muted"]) if sub else ""}</label>')
    keys = ''
    for k in ['7', '8', '9', '+', '4', '5', '6', '−', '1', '2', '3', '⌫', ',', '0', '00', 'OK']:
        ok = k == 'OK'
        keys += (f'<button type="button" {"aria-label=\"Cancella\"" if k=="⌫" else ""} style="height: 48px; border-radius: {d["rs"]}px; border: {"none" if ok else "1px solid "+t["border"]}; '
                 f'background: {t["primary"] if ok else t["surf"]}; color: {t["onp"] if ok else t["text"]}; font-family: {N}; font-size: 18px; font-weight: {600 if ok else 400}">{k}</button>')
    inner = f'''<div style="display: flex; align-items: center; justify-content: space-between; margin: 0 -8px">
{btn_icon('x', 'Chiudi', t, size=44)}<h1 style="margin: 0; font-size: 17px; font-weight: 600">Nuovo movimento</h1>
<button type="button" style="height: 36px; padding: 0 14px; border-radius: {d['rs']}px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 14px; font-weight: 600">Salva</button></div>
{seg(['Uscita', 'Entrata', 'Trasferimento'], 'Uscita', t, d, h=38)}
<label style="display: flex; justify-content: space-between; align-items: baseline; padding: 4px 0; border-bottom: 2px solid {t['primary']}; font-size: 13px; color: {t['muted']}">Importo
<span style="display: flex; align-items: baseline; gap: 6px"><input type="text" value="42,30" readonly size="7" style="width: 170px; text-align: right; border: none; outline: none; background: transparent; font-family: {N}; font-size: 40px; font-weight: 500; color: {t['text']}"><span style="font-family: {N}; font-size: 22px; color: {t['muted']}">€</span></span></label>
<div style="margin: 0 -20px; border-top: 1px solid {t['border']}">
{row('Data', 'Oggi, sab 14/11/2026', 'cal', True)}
{row('Con', 'Bancomat · Conto corrente', 'card', True)}
{row('Categoria', 'Spesa alimentare', sw['s1'], True)}
{row('Descrizione', 'Conad', 'pen')}
{row('Note', 'Aggiungi una nota', None)}
</div>
<span style="flex: 1"></span>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px">{keys}</div>'''
    return sheet_wrap(t, d, inner, top=48, radius=12)

def C_an(d, t, dark):
    N = d['num']; sw = d['sw']
    rows = ''
    sws = ['s7', 's1', 's4', 's2', 's5', 's8']
    for (name, v, s, p, ic), k in zip(CATS, sws):
        rows += (f'<tr style="height: 40px; border-bottom: 1px solid {t["border"]}">'
                 f'<td style="padding: 0 0 0 16px"><span style="display: flex; align-items: center; gap: 8px"><span style="width: 8px; height: 8px; border-radius: 2px; background: {sw[k]}"></span>{name}</span></td>'
                 f'<td style="width: 80px; padding: 0 8px"><span style="display: block; height: 6px; background: {t["track"]}"><span style="display: block; height: 6px; width: {round(p/35*100)}%; background: {t["chOut"]}"></span></span></td>'
                 f'<td style="text-align: right; font-family: {N}; color: {t["muted"]}; width: 36px">{p}%</td>'
                 f'<td style="text-align: right; font-family: {N}; padding: 0 16px 0 8px; width: 84px">{s.replace(" €", "")}</td></tr>')
    kpi = lambda lab, val, note: (f'<div style="padding: 12px 16px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 11px; color: {t["muted"]}; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600">{lab}</span>'
                                  f'<span style="font-family: {N}; font-size: 18px; font-weight: 600">{val}</span><span style="font-size: 12px; color: {t["muted"]}">{note}</span></div>')
    body = f'''<header style="height: 56px; padding: 0 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {t['border']}">
<h1 style="margin: 0; font-size: 17px; font-weight: 600">Analisi · Novembre 2026</h1>
<div style="width: 120px">{seg(['Mese', 'Anno'], 'Mese', t, d, h=34)}</div></header>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); border-bottom: 1px solid {t['border']}">
{kpi('Uscite', '684,35', 'stima fine mese 1.480')}
<div style="border-left: 1px solid {t['border']}">{kpi('Risparmio', '1.325,65', '66% delle entrate')}</div>
<div style="border-top: 1px solid {t['border']}">{kpi('Media al giorno', '48,88', 'su 14 giorni')}</div>
<div style="border-top: 1px solid {t['border']}; border-left: 1px solid {t['border']}">{kpi('Vs media 3 mesi', '−3%', 'Pasti fuori +24%')}</div></div>
<h2 style="margin: 0; padding: 14px 16px 8px; font-size: 12px; font-weight: 600; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.05em">Uscite per categoria</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 14px; border-top: 1px solid {t['border']}"><tbody>{rows}</tbody></table>
<h2 style="margin: 0; padding: 16px 16px 8px; font-size: 12px; font-weight: 600; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.05em">Ultimi 6 mesi</h2>
<div style="padding: 0 16px">{cols(t, 64, barw=12, gap=2, radius=1)}</div>
{C_nav(t, 'Analisi')}'''
    return body

# ================================================================ scheda stile (comune)
def tile(key, d):
    t = d['light']; k = d['dark']; N = d['num']
    def swatch(c, name, txt='#FFFFFF'):
        return (f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="height: 44px; border-radius: {d["rs"]}px; background: {c}; border: 1px solid rgba(0,0,0,0.08)"></span>'
                f'<span style="font-size: 11px; color: {t["muted"]}; line-height: 1.3">{name}<br><span style="font-family: ui-monospace, monospace">{c}</span></span></div>')
    pal = ''.join(swatch(c, n) for c, n in [(t['bg'], 'Sfondo'), (t['surf'], 'Superficie'), (t['text'], 'Testo'), (t['primary'], 'Principale'),
                                             (t['accent'], 'Accento'), (t['income'], 'Entrate'), (t['chIn'], 'Grafico entrate'), (t['chOut'], 'Grafico uscite')])
    palD = ''.join(f'<span title="{n}" style="flex: 1; height: 28px; background: {c}"></span>' for c, n in [(k['bg'], 'Sfondo'), (k['surf'], 'Superficie'), (k['surf2'], 'Superficie 2'), (k['text'], 'Testo'), (k['primary'], 'Principale'), (k['income'], 'Entrate')])
    tints = ''.join(f'<span style="flex: 1; height: 20px; background: {c}; border-radius: 3px"></span>' for c in d['sw'].values())
    hdr = f'font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: {t["muted"]}'
    body = f'''<div style="padding: 24px 22px; display: flex; flex-direction: column; gap: 20px">
<div style="display: flex; flex-direction: column; gap: 4px"><span style="{hdr}">Direzione {key}</span>
<h1 style="margin: 0; font-family: {d['head']}; font-size: 34px; font-weight: {800 if key=='B' else 600}; letter-spacing: -0.02em">{d['name']}</h1>
<p style="margin: 0; font-size: 15px; color: {t['muted']}">{d['sub']}</p></div>
<section style="display: flex; flex-direction: column; gap: 10px"><h2 style="margin: 0; {hdr}">Colori · chiaro</h2>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">{pal}</div>
<span style="{hdr}; margin-top: 4px">Scuro</span><div style="display: flex; border-radius: {d['rs']}px; overflow: hidden; border: 1px solid {t['border']}">{palD}</div>
<span style="{hdr}; margin-top: 4px">Tinte conti e categorie s1…s8</span><div style="display: flex; gap: 4px">{tints}</div></section>
<section style="display: flex; flex-direction: column; gap: 6px"><h2 style="margin: 0 0 4px; {hdr}">Caratteri</h2>
<span style="font-family: {d['head']}; font-size: 30px; font-weight: {800 if key=='B' else 600}; letter-spacing: -0.02em">Novembre 2026</span>
<span style="font-family: {N}; font-size: 26px; font-weight: {800 if key=='B' else 500}">1.234,56 €</span>
<span style="font-size: 16px">Testo dei movimenti e dei moduli</span>
<span style="font-size: 13px; color: {t['muted']}">Etichette e note · {d['head'].split(',')[0].strip("'")}{' + '+N.split(',')[0].strip("'") if N!=d['head'] else ''}</span></section>
<section style="display: flex; flex-direction: column; gap: 10px"><h2 style="margin: 0; {hdr}">Componenti</h2>
<div style="display: flex; gap: 10px">
<button type="button" style="flex: 1; height: 48px; border-radius: {24 if key=='B' else d['rs']+4}px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 15px; font-weight: 700">Salva</button>
<button type="button" style="flex: 1; height: 48px; border-radius: {24 if key=='B' else d['rs']+4}px; border: 1px solid {t['border']}; background: {t['surf']}; color: {t['text']}; font: inherit; font-size: 15px; font-weight: 600">Annulla</button></div>
<div style="display: flex; gap: 8px">
<span style="height: 34px; padding: 0 14px; border-radius: {17 if key!='C' else d['rs']}px; background: {t['accentSoft']}; color: {t['text']}; display: flex; align-items: center; font-size: 14px; font-weight: 600; border: 1px solid {t['accent']}">Selezionato</span>
<span style="height: 34px; padding: 0 14px; border-radius: {17 if key!='C' else d['rs']}px; background: {t['surf']}; color: {t['text']}; display: flex; align-items: center; font-size: 14px; border: 1px solid {t['border']}">Normale</span>
<span style="height: 34px; padding: 0 12px; border-radius: {17 if key!='C' else d['rs']}px; background: {t['surf2']}; color: {t['text']}; display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600">{icon('alert', 15, t['text'])}Quasi esaurito</span></div>
<span style="font-size: 13px; color: {t['muted']}">Arrotondamenti {d['rs']}/{d['r']} px · spaziatura base 4 px · aree di tocco da 44 px</span></section>
</div>'''
    return body

def main():
    # ================================================================ scrittura
    SCREENS = {
     'A': (A_mov, A_new, A_an), 'B': (B_mov, B_new, B_an), 'C': (C_mov, C_new, C_an)}
    boards, order, notes = {}, [], {}
    ROW_GAP = 1224
    X = [0, 470, 940, 1410, 1880]
    for ri, key in enumerate(['A', 'B', 'C']):
        d = DIRS[key]; L = d['light']; D = d['dark']
        mov, new, an = SCREENS[key]
        files = [
          ('Main.dc.html' if key == 'A' else f'{key}-movimenti.dc.html', f'{key} · Movimenti', page(f'Statera {key} — Movimenti', d, L, mov(d, L, False))),
          (f'{key}-movimenti-scuro.dc.html', f'{key} · Movimenti, tema scuro', page(f'Statera {key} — Movimenti scuro', d, D, mov(d, D, True))),
          (f'{key}-nuova-spesa.dc.html', f'{key} · Nuova spesa', page(f'Statera {key} — Nuova spesa', d, L, new(d, L, False))),
          (f'{key}-analisi.dc.html', f'{key} · Analisi', page(f'Statera {key} — Analisi', d, L, an(d, L, False))),
          (f'{key}-stile.dc.html', f'{key} · Colori, caratteri, componenti', page(f'Statera {key} — Scheda stile', d, L, tile(key, d))),
        ]
        y = ri * ROW_GAP
        for ci, (fn, title, html) in enumerate(files):
            with open(os.path.join(OUT, fn), 'w') as f:
                f.write(html)
            boards[fn] = {'x': X[ci], 'y': y, 'w': W, 'h': H, 'title': title}
            order.append(fn)
        notes[f'title{key}'] = {'x': 0, 'y': y - 260, 'text': f'{key} — {d["name"]}: {d["sub"]}', 'kind': 'title1', 'maxW': 2270}

    REF = {
     'A': "Ispirata alle app di private banking e ai gestori di spesa 'calmi': un riquadro scuro con il saldo, liste in schede con bordo sottile, numeri grandi con un carattere con grazie (Fraunces), ottone solo per le azioni. Evoluzione dell'aspetto attuale.",
     'B': "Ispirata alle neobank: saldo enorme al centro, azioni rapide in cerchi, icone colorate per categoria, angoli molto arrotondati, barra di navigazione flottante con il + al centro. La più 'app di consumo'; carattere Plus Jakarta Sans.",
     'C': "Ispirata ai gestori di budget per utenti esperti e ai fogli di calcolo: righe dense, numeri monospaziati allineati, bande per i giorni, poca decorazione e un solo colore (verde petrolio). Massima informazione per schermo, ottima anche su PC; IBM Plex.",
    }
    for ri, key in enumerate(['A', 'B', 'C']):
        notes[f'note{key}'] = {'x': 2350, 'y': ri * ROW_GAP, 'w': 320, 'text': REF[key], 'fill': 'yellow' if False else 'orange', 'size': 'm'}

    canvas = {
     'v': 3, 'createdOnFiles': {'v': 1, 'at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')},
     'title': 'Statera — Proposte di stile', 'launch': {'view': 'canvas'}, 'pages': [],
     'boards': boards, 'order': order, 'notes': notes, 'designSystems': []}
    with open(os.path.join(OUT, 'canvas.json'), 'w') as f:
        json.dump(canvas, f, ensure_ascii=False, indent=1)
    print('\n'.join(order))

if __name__ == '__main__':
    main()
