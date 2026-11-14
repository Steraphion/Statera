#!/usr/bin/env python3
"""Le due palette scelte (Zafferano e Indaco ammorbidito) su Movimenti, Nuova spesa e Analisi."""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import gen
from gen import icon, tint, page, btn_icon, seg, cols, PICK, CATS, DIRS, W, H, OUT
from palettes import B_nav, cr
import coolors
from coolors import mov, swatch_grid, mini

# ---------------------------------------------------------------- OKLCH -> hex
def oklch(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s]
    def g(x):
        x = max(0.0, min(1.0, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return '#' + ''.join(f'{round(g(x) * 255):02X}' for x in rgb)

HUE = 277  # indaco
IND_L = dict(bg=oklch(.972, .007, HUE), surf='#FFFFFF', surf2=oklch(.935, .014, HUE), border=oklch(.905, .016, HUE),
             text=oklch(.22, .03, HUE), muted=oklch(.50, .03, HUE),
             primary=oklch(.50, .12, HUE), onp='#FFFFFF', accent=oklch(.50, .12, HUE), accentSoft=oklch(.935, .035, HUE),
             income='#1D7A5A', fab=oklch(.50, .12, HUE), onfab='#FFFFFF', inIcon='#1D7A5A', outIcon='#B4562A',
             chIn='#2A78D6', chOut='#EB6834', backdrop='rgba(20,22,40,0.5)')
IND_L['track'] = IND_L['surf2']
IND_D = dict(bg=oklch(.17, .015, HUE), surf=oklch(.215, .02, HUE), surf2=oklch(.26, .025, HUE), border=oklch(.30, .025, HUE),
             text=oklch(.955, .008, HUE), muted=oklch(.74, .025, HUE),
             primary=oklch(.78, .085, HUE), accent=oklch(.80, .08, HUE), accentSoft=oklch(.32, .05, HUE),
             income='#5CCB98', inIcon='#5CCB98', outIcon='#EE9A70',
             chIn='#3987E5', chOut='#D95926', backdrop='rgba(0,0,0,0.6)')
IND_D.update(onp=IND_D['bg'], fab=IND_D['primary'], onfab=IND_D['bg'], track=IND_D['surf2'])
IND_SW = {f's{i+1}': oklch(L, C, h) for i, (L, C, h) in enumerate(
    [(.55, .11, 155), (.60, .12, 50), (.55, .11, 250), (.52, .05, 60), (.55, .11, 305), (.57, .09, 200), (.56, .12, 355), (.58, .10, 115)])}

ZAF = coolors.P[2]
PAL = [
 dict(id='zafferano', name='Blu, oliva e zafferano', light=ZAF['light'], dark=ZAF['dark'], sw=dict(ZAF['sw'], s8='#A8750C'),
      strips=[('Palette originale (Coolors)', ZAF['src'])]),
 dict(id='indaco', name='Indaco morbido', light=IND_L, dark=IND_D, sw=IND_SW,
      strips=[('Indaco di prima', ['#3B38D6', '#E7E6FC', '#8F8CFF', '#262551']),
              ('Indaco morbido', [IND_L['primary'], IND_L['accentSoft'], IND_D['primary'], IND_D['accentSoft']])]),
]

# ---------------------------------------------------------------- Nuova spesa (sopra la lista, scurita)
def new(d, t, dark):
    sw = d['sw']
    grid = ''
    for ic, s, lab in PICK:
        on = lab == 'Spesa alimentare'
        ring = f'box-shadow: 0 0 0 3px {t["bg"]}, 0 0 0 5px {sw[s]};' if on else ''
        grid += (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="border: none; background: transparent; padding: 0; font: inherit; color: {t["text"]}; display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 11px; font-weight: {700 if on else 500}; text-align: center">'
                 f'<span style="width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; '
                 f'background: {sw[s] if on else tint(sw[s], 0.15 if not dark else 0.3)}; color: {"#FFFFFF" if on or dark else sw[s]}; {ring}">{icon(ic, 22, sw=2)}</span>{lab}</button>')
    chip = lambda ic, lab: (f'<button type="button" style="height: 40px; padding: 0 14px; border-radius: 20px; border: none; background: {t["surf"]}; color: {t["text"]}; font: inherit; font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px">'
                            f'{icon(ic, 16, t["accent"])}{lab}</button>')
    sheet = f'''<div style="display: flex; align-items: center; justify-content: space-between">
{btn_icon('x', 'Chiudi', t, bg=t['surf'])}
<div style="width: 230px">{seg(['Uscita', 'Entrata', 'Trasf.'], 'Uscita', t, d, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div>
<span style="width: 40px"></span></div>
<label style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0 0; font-size: 14px; color: {t['muted']}; font-weight: 500">Quanto hai speso?
<span style="display: flex; align-items: baseline; gap: 4px"><input type="text" value="42,30" readonly size="5" style="width: 160px; text-align: right; border: none; outline: none; background: transparent; font-family: {d['head']}; font-size: 56px; font-weight: 800; letter-spacing: -0.03em; color: {t['text']}"><span style="font-size: 34px; font-weight: 800; color: {t['muted']}">€</span></span></label>
<div style="display: flex; gap: 8px; justify-content: center">{chip('cal', 'Oggi')}{chip('card', 'Bancomat')}</div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 16px 12px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: 14px; column-gap: 4px">{grid}</div>
<label style="display: flex; align-items: center; gap: 10px; height: 52px; padding: 0 16px; background: {t['surf']}; border-radius: 16px; font-size: 14px; color: {t['muted']}">{icon('pen', 18, t['muted'])}<span style="position: absolute; width: 1px; height: 1px; overflow: hidden">Descrizione</span>
<input type="text" value="Conad" readonly style="flex: 1; border: none; outline: none; background: transparent; font: inherit; font-size: 16px; color: {t['text']}"></label>
<span style="flex: 1"></span>
<button type="button" style="height: 58px; border-radius: 29px; border: none; background: {t['primary']}; color: {t['onp']}; font: inherit; font-size: 17px; font-weight: 800">Salva spesa</button>
<button type="button" style="height: 24px; border: none; background: transparent; color: {t['accent']}; font: inherit; font-size: 14px; font-weight: 700; margin-top: -6px">Salva e aggiungine un'altra</button>'''
    return f'''{mov(d, t, dark)}
<div aria-hidden="true" style="position: absolute; inset: 0; background: {t['backdrop']}"></div>
<div role="dialog" aria-label="Nuova uscita" style="position: absolute; left: 0; right: 0; bottom: 0; top: 56px; background: {t['bg']}; border-radius: 32px 32px 0 0; padding: 10px 20px 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">
<span aria-hidden="true" style="align-self: center; width: 40px; height: 4px; border-radius: 2px; background: {t['border']}"></span>
{sheet}
</div>'''

# ---------------------------------------------------------------- Analisi
def an(d, t, dark):
    sw = d['sw']
    hero_bg = t['accentSoft'] if dark else t['primary']
    hero_fg = t['text'] if dark else t['onp']
    lst = ''
    for (name, v, s, p, ic), k in zip(CATS[:5], ['s7', 's1', 's4', 's2', 's5']):
        lst += (f'<li style="display: flex; align-items: center; gap: 12px">'
                f'<span style="width: 40px; height: 40px; border-radius: 50%; background: {tint(sw[k], 0.15 if not dark else 0.3)}; color: {sw[k] if not dark else "#FFFFFF"}; display: flex; align-items: center; justify-content: center">{icon(ic, 19, sw=2)}</span>'
                f'<span style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="display: flex; justify-content: space-between; font-size: 14px"><span style="font-weight: 700">{name}</span><span style="font-weight: 700">{s}</span></span>'
                f'<span style="height: 6px; border-radius: 3px; background: {t["track"]}; display: block"><span style="display: block; height: 6px; width: {round(p/35*100)}%; border-radius: 3px; background: {t["chOut"]}"></span></span></span></li>')
    pill = lambda txt: (f'<span style="height: 30px; padding: 0 12px; border-radius: 15px; background: {tint(hero_fg, 0.16)}; display: flex; align-items: center; font-size: 13px; font-weight: 700">{txt}</span>')
    return f'''<div style="padding: 16px 20px 0; display: flex; flex-direction: column; gap: 16px">
<header style="display: flex; align-items: center; justify-content: space-between"><h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em">Analisi</h1>
<div style="width: 170px">{seg(['Mese', 'Anno'], 'Mese', t, d, h=40, radius=20, act_bg=t['primary'], act_col=t['onp'])}</div></header>
<div style="background: {hero_bg}; color: {hero_fg}; border-radius: 24px; padding: 20px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 14px; font-weight: 600; opacity: 0.85">A novembre hai risparmiato</span>
<span style="font-size: 40px; font-weight: 800; letter-spacing: -0.03em">1.325,65 €</span>
<span style="display: flex; gap: 8px; flex-wrap: wrap">{pill('66% delle entrate')}{pill('Stima uscite 1.480 €')}</span></div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 18px; display: flex; flex-direction: column; gap: 14px">
<h2 style="margin: 0; font-size: 17px; font-weight: 800">Categorie</h2>
<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px">{lst}</ul></div>
<div style="background: {t['surf']}; border-radius: 24px; padding: 18px; display: flex; flex-direction: column; gap: 10px">
<h2 style="margin: 0; font-size: 17px; font-weight: 800">Ultimi 6 mesi</h2>{cols(t, 70, barw=12, radius=6)}</div>
</div>
{B_nav(t, 'Analisi')}'''

# ---------------------------------------------------------------- scheda colori
def tile(p):
    L, K = p['light'], p['dark']
    hdr = 'font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em'
    strips = ''
    for lab, cs in p['strips']:
        bar = ''.join(f'<span style="flex: 1; height: 26px; background: {c}"></span>' for c in cs)
        strips += (f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="{hdr}; color: {L["muted"]}">{lab}</span>'
                   f'<div style="display: flex; border-radius: 8px; overflow: hidden; border: 1px solid {L["border"]}">{bar}</div></div>')
    tints = ''.join(f'<span style="flex: 1; height: 14px; border-radius: 3px; background: {c}"></span>' for c in p['sw'].values())
    return f'''<div style="height: 100%; display: flex; flex-direction: column">
<div style="flex: 1; padding: 18px 18px 14px; display: flex; flex-direction: column; gap: 10px; background: {L['bg']}; color: {L['text']}">
<h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.02em">{p['name']}</h1>
{strips}
<span style="{hdr}; color: {L['muted']}">Tema chiaro</span>{swatch_grid(L)}{mini(L)}
<div style="display: flex; flex-direction: column; gap: 4px"><span style="{hdr}; color: {L['muted']}">Tinte categorie s1…s8</span><div style="display: flex; gap: 3px">{tints}</div></div></div>
<div style="flex: 1; padding: 14px 18px 18px; display: flex; flex-direction: column; gap: 10px; background: {K['bg']}; color: {K['text']}">
<span style="{hdr}; color: {K['muted']}">Tema scuro</span>{swatch_grid(K)}{mini(K)}</div></div>'''

# ---------------------------------------------------------------- controlli
def check():
    bad = 0
    for p in PAL:
        for k in ('light', 'dark'):
            t = p[k]
            acc = t['accent'] if t['accentSoft'] != t['accent'] else t['onp']
            hero_bg = t['accentSoft'] if k == 'dark' else t['primary']; hero_fg = t['text'] if k == 'dark' else t['onp']
            v = dict(testo=cr(t['text'], t['bg']), attenuato=min(cr(t['muted'], t['surf']), cr(t['muted'], t['bg'])),
                     suPrincipale=cr(t['onp'], t['primary']), accento=cr(acc, t['accentSoft']), accentoSuSfondo=cr(t['accent'], t['bg']),
                     entrate=cr(t['income'], t['surf']), riquadro=cr(hero_fg, hero_bg))
            low = [n for n, x in v.items() if x < 4.5]
            g = dict(iconaPiu=cr(t['onfab'], t['fab']), graficoIn=cr(t['chIn'], t['surf']), graficoOut=cr(t['chOut'], t['surf']))
            low += [n for n, x in g.items() if x < 3]
            bad += len(low)
            print(f"{p['id']:10} {k:5} " + ' '.join(f'{n}={x:.1f}' for n, x in {**v, **g}.items()) + ('  <-- ' + ','.join(low) if low else ''))
        # tinte delle categorie: icona sul cerchio tenue (chiaro) >= 3:1
        worst = min(cr(c, '#FFFFFF') for c in p['sw'].values())
        print(f"{p['id']:10} tinte: contrasto minimo su bianco {worst:.1f}")
    return bad

def main():
    print('indaco morbido:', {k: IND_L[k] for k in ('bg', 'primary', 'accentSoft', 'text', 'muted')}, {k: IND_D[k] for k in ('bg', 'surf', 'primary', 'accentSoft')})
    if check():
        print('CONTRASTI INSUFFICIENTI'); return
    canvas = json.load(open(sys.argv[1]))
    if 'scelta' not in [pg['id'] for pg in canvas['pages']]:
        canvas['pages'].append({'id': 'scelta', 'name': 'Scelta: Zafferano e Indaco'})
    canvas['launch'] = {'view': 'canvas', 'page': 'scelta'}
    written = []
    for ri, p in enumerate(PAL):
        d = dict(DIRS['B']); d['sw'] = p['sw']; y = ri * 1224
        screens = [('movimenti', 'Movimenti', mov), ('nuova-spesa', 'Nuova spesa', new), ('analisi', 'Analisi', an)]
        ci = 0
        for theme, tl in (('chiaro', 'light'), ('scuro', 'dark')):
            for sid, sname, fn_ in screens:
                fn = f'sc-{p["id"]}-{sid}-{theme}.dc.html'
                html = page(f'{p["name"]} — {sname} {theme}', d, p[tl], fn_(d, p[tl], tl == 'dark'))
                open(os.path.join(OUT, fn), 'w').write(html)
                canvas['boards'][fn] = {'x': ci * 470 + (80 if theme == 'scuro' else 0), 'y': y, 'w': W, 'h': H, 'title': f'{sname} · {theme}', 'page': 'scelta'}
                if fn not in canvas['order']: canvas['order'].append(fn)
                written.append(fn); ci += 1
        canvas['notes'][f'scT{ri}'] = {'x': 0, 'y': y - 260, 'text': p['name'], 'kind': 'title1', 'maxW': 2900, 'page': 'scelta'}
        fn = f'sc-{p["id"]}-colori.dc.html'
        open(os.path.join(OUT, fn), 'w').write(page(f'{p["name"]} — colori', d, p['light'], tile(p)))
        canvas['boards'][fn] = {'x': ri * 470, 'y': 2448, 'w': W, 'h': H, 'title': f'{p["name"]} — colori', 'page': 'scelta'}
        if fn not in canvas['order']: canvas['order'].append(fn)
        written.append(fn)
    canvas['notes']['scT2'] = {'x': 0, 'y': 2188, 'text': 'Colori delle due palette', 'kind': 'title1', 'maxW': 2900, 'page': 'scelta'}
    canvas['notes']['scInd'] = {'x': 960, 'y': 2448, 'w': 380, 'size': 'm', 'fill': 'blue', 'page': 'scelta',
        'text': "Indaco morbido: stessa tinta, saturazione quasi dimezzata e un filo più chiaro. In scuro il viola neon diventa un lilla polvere. Anche le 8 tinte delle categorie sono più tenui, per non fare a gara col colore principale. Se lo vuoi ancora più quieto, si può scendere di un altro gradino."}
    json.dump(canvas, open(os.path.join(OUT, 'canvas.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(written))

if __name__ == '__main__':
    main()
