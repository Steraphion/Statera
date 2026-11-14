import json, math
from logo_simboli import S, gruppo, bbox, variante_per

PX = {('A',16):'7f88f35e832aae703478b2c12e615c4a',('A',32):'eed98395e363482518e669e81d2fb3e3',
      ('B',16):'c7832e615ef29215b75b0691661e7e94',('B',32):'a65011ab043f7f6453d448be0aa68828',
      ('C',16):'f33f144ee3c2aeae0e341475df295c29',('C',32):'7b0b898da6744bbe9a83f39982d697b6',
      ('D',16):'0f9ecc9034378b3aecd7eb463e8facfd',('D',32):'84ee11e76069c889d4d68f4ff9218ddb',
      ('E',16):'c3dce924d47fb21a3e086c6ee86e889b',('E',32):'608022dfcb9a3015c45e15442b04b4e5',
      ('F',16):'b22286d356b6125aa054cae735f0b702',('F',32):'4d3237fefb5a8f098d1c1d0b71a5fb2d',
      ('G',16):'6c1ef80fd7b12f9d37c69d845c62c094',('G',32):'26f6ddef736aabbb94e768e030f961b6'}
IND, LIL, BG, BGD, SUR, SURD, TX, TXD, MU, MUD, ACC, ACCD = '#535AA6','#A9B3EE','#F4F5FB','#0E0F16','#FFFFFF','#171923','#171928','#EEF0F6','#5F6275','#A6AABB','#E3E8FF','#2C305E'
FONT = "font-family: 'Plus Jakarta Sans', system-ui, sans-serif"

def ico(k, px, fg='#FFFFFF', bg=IND, forma='squircle', var=None, area=None, extra=''):
    """Icona inline: px = dimensione mostrata; la variante dipende da px (o var)."""
    n = 512
    v = var or variante_per(k, px)
    if forma == 'adattiva':   # pieno, simbolo dentro la zona sicura del 66%
        x0,y0,x1,y1 = bbox(k, v); half = math.hypot(x1-x0, y1-y0)/2
        box = max(x1-x0, y1-y0) * (0.33*n*0.97/half)
        shape = f'<rect width="{n}" height="{n}" fill="{bg}"/>'
    else:
        box = n*(area or (0.68 if v=='sm' else 0.60))
        shape = {'squircle': f'<rect width="{n}" height="{n}" rx="115" fill="{bg}"/>',
                 'cerchio': f'<circle cx="256" cy="256" r="256" fill="{bg}"/>',
                 'quadrato': f'<rect width="{n}" height="{n}" fill="{bg}"/>',
                 'nessuna': ''}[forma]
    return (f'<svg width="{px}" height="{px}" viewBox="0 0 {n} {n}" aria-hidden="true" style="display: block; flex-shrink: 0{extra}">'
            f'{shape}<g transform="translate(256 256)">{gruppo(k, v, fg, box)}</g></svg>')

def page(title, w, h, body, bg=BG):
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap">
<style>
body{{margin:0}}
a{{color:{IND}}}a:hover{{color:{TX}}}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; box-sizing: border-box; overflow: hidden; background: {bg}; color: {TX}; {FONT}; padding: 40px; display: flex; flex-direction: column; gap: 24px">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

def label(t, c=MU):
    return f'<p style="margin: 0; font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {c}">{t}</p>'

def card(inner, bg=SUR, extra=''):
    return f'<div style="background: {bg}; border-radius: 24px; padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px{extra}">{inner}</div>'

def caption(t, c=MU):
    return f'<span style="font-size: 12px; font-weight: 600; color: {c}">{t}</span>'

def wordmark(k, tile, fs, dark=False, tile_style='tile'):
    tx = TXD if dark else TX
    if tile_style == 'tile':
        sym = ico(k, tile, fg=(BGD if dark else '#FFFFFF'), bg=(LIL if dark else IND))
    else:  # simbolo senza riquadro, nel colore principale
        sym = ico(k, tile, fg=(LIL if dark else IND), forma='nessuna', area=0.92)
    return (f'<div style="display: flex; align-items: center; gap: {round(fs*0.32)}px">{sym}'
            f'<span style="font-size: {fs}px; font-weight: 800; letter-spacing: -0.03em; line-height: 1; color: {tx}">Statera</span></div>')

def sizes_row(k, sizes, dark=False):
    bg = BGD if dark else BG
    cells = ''.join(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; justify-content: flex-end">{ico(k, s)}{caption(f"{s} px", MUD if dark else MU)}</div>' for s in sizes)
    return f'<div style="display: flex; align-items: flex-end; gap: 28px; padding: 20px 24px; border-radius: 16px; background: {bg}">{cells}</div>'

def pixel(k, s, scale):
    return (f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center"><img src="/_blob/{PX[(k,s)]}" alt="Icona a {s} px ingrandita" width="{s*scale}" height="{s*scale}" style="display: block; image-rendering: pixelated; border-radius: 4px">'
            f'{caption(f"{s} px reali, ingrandita ×{scale}")}</div>')

# ---------- Tavola 1: simbolo e marchio ----------
def tavola_simbolo(k, desc):
    nome = S[k]['nome']
    hero = card(label('Simbolo') + f'<div style="display: flex; justify-content: center; padding: 8px 0">{ico(k, 300)}</div>'
                + f'<p style="margin: 0; font-size: 14px; line-height: 1.5; color: {MU}">{desc}</p>', extra='; width: 380px; flex-shrink: 0')
    marchi = card(label('Marchio con la scritta')
        + f'<div style="display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 28px; border-radius: 16px; background: {BG}">{wordmark(k, 72, 60)}{wordmark(k, 44, 34, tile_style="free")}</div>'
        + f'<div style="display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 28px; border-radius: 16px; background: {BGD}">{wordmark(k, 72, 60, dark=True)}{wordmark(k, 44, 34, dark=True, tile_style="free")}</div>'
        + f'<div style="display: flex; gap: 24px; align-items: center">'
          f'<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 20px 28px; border-radius: 16px; background: {BG}">{ico(k, 64)}<span style="font-size: 22px; font-weight: 800; letter-spacing: -0.03em">Statera</span></div>'
          f'<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 20px 28px; border-radius: 16px; background: {BGD}">{ico(k, 64, fg=BGD, bg=LIL)}<span style="font-size: 22px; font-weight: 800; letter-spacing: -0.03em; color: {TXD}">Statera</span></div>'
          f'<p style="margin: 0; font-size: 13px; line-height: 1.5; color: {MU}; max-width: 300px">Orizzontale per intestazioni e guida, verticale per la schermata d’avvio. In tema scuro il riquadro passa al lilla #A9B3EE con il simbolo scuro.</p></div>',
        extra='; flex: 1; min-width: 0')
    dims = card(label('Dimensioni reali, chiaro e scuro')
        + f'<div style="display: flex; gap: 24px; align-items: flex-end; flex-wrap: wrap">'
        + f'<div style="display: flex; flex-direction: column; gap: 12px">{sizes_row(k, (16,24,32,48,64,96))}{sizes_row(k, (16,24,32,48,64,96), dark=True)}</div>'
        + pixel(k, 16, 8) + pixel(k, 32, 4) + '</div>'
        + f'<p style="margin: 0; font-size: 13px; color: {MU}">Fino a 32 px si usa una versione semplificata del simbolo, con tratti più spessi{" e senza tacche" if "xl" in S[k] else ""}.</p>')
    them = lambda fg, bg, cap, capc=MU: f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center">{ico(k, 96, fg=fg, bg=bg, forma="cerchio")}{caption(cap, capc)}</div>'
    mono = card(label('Monocromatico')
        + f'<div style="display: flex; gap: 28px; align-items: flex-end; flex-wrap: wrap">'
        + f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center"><div style="width: 96px; height: 96px; border-radius: 16px; background: #FFFFFF; border: 1px solid #DADCE6; box-sizing: border-box; display: flex; align-items: center; justify-content: center">{ico(k, 80, forma="nessuna", fg=TX, area=0.8)}</div>{caption("Un colore, su chiaro")}</div>'
        + f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center"><div style="width: 96px; height: 96px; border-radius: 16px; background: {TX}; display: flex; align-items: center; justify-content: center">{ico(k, 80, forma="nessuna", fg="#FFFFFF", area=0.8)}</div>{caption("Un colore, su scuro")}</div>'
        + them('#2B3170', '#DCE0F5', 'Android a tema, chiaro')
        + them('#C9D0F7', '#2C305E', 'Android a tema, scuro')
        + f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center"><div style="width: 96px; height: 96px; border-radius: 16px; border: 1px dashed #9A9DB0; box-sizing: border-box; display: flex; align-items: center; justify-content: center">{ico(k, 94, forma="nessuna", fg="#000000", area=0.66*0.92)}</div>{caption("Maschera «monochrome»")}</div>'
        + f'<div style="display: flex; flex-direction: column; gap: 8px; align-items: center"><div style="width: 96px; height: 96px; border-radius: 16px; background: {TX}; display: flex; align-items: center; justify-content: center">{ico(k, 80, forma="nessuna", fg="#FFFFFF", area=0.8, var="sm")}</div>{caption("Versione piccola")}</div>'
        + '</div>')
    body = (f'<div style="display: flex; align-items: baseline; gap: 16px"><h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.02em">{k} · {nome}</h1><span style="font-size: 15px; color: {MU}">Simbolo e marchio</span></div>'
            f'<div style="display: flex; gap: 24px; align-items: stretch">{hero}{marchi}</div>{dims}{mono}')
    return page(f'Logo {k} · {nome} — simbolo e marchio', 1280, 1500, body)

# ---------- Tavola 2: sui dispositivi ----------
GENERICI = [('Note', '#C7CBD6', 'sq'), ('Meteo', '#BFC8D9', 'ci'), ('Foto', '#CCC6D6', 'tr'), ('Mappe', '#C2CFCB', 'ci'),
            ('Orologio', '#C9CBD2', 'sq'), ('Calcolo', '#C8C6CF', 'tr'), ('Posta', '#C3C9D4', 'sq')]
def generico(px, col, sh, radius):
    g = {'sq': '<rect x="34" y="34" width="28" height="28" rx="6" fill="#FFFFFF" fill-opacity="0.85"/>',
         'ci': '<circle cx="48" cy="48" r="16" fill="#FFFFFF" fill-opacity="0.85"/>',
         'tr': '<path d="M48 32L64 62H32Z" fill="#FFFFFF" fill-opacity="0.85"/>'}[sh]
    return f'<svg width="{px}" height="{px}" viewBox="0 0 96 96" aria-hidden="true" style="display: block; flex-shrink: 0"><rect width="96" height="96" rx="{radius}" fill="{col}"/>{g}</svg>'

def mascherata(k, px, radius_css):
    return f'<div style="width: {px}px; height: {px}px; border-radius: {radius_css}; overflow: hidden; flex-shrink: 0">{ico(k, px, forma="adattiva")}</div>'

def telefono(k, dark, maschera, nome_maschera):
    wall = '#1D2030' if dark else '#DCE3EE'
    tc = '#EEF0F6' if dark else '#1E2230'
    rad = {'cerchio': '50%', 'squircle': '30%', 'goccia': '50% 50% 50% 14%'}[maschera]
    radsvg = {'cerchio': 48, 'squircle': 29, 'goccia': 48}[maschera]
    apps = []
    for i, (n, col, sh) in enumerate(GENERICI[:3]):
        apps.append((n, generico(52, '#3A3F55' if dark else col, sh, radsvg)))
    apps.insert(1, ('Statera', mascherata(k, 52, rad)))
    for n, col, sh in GENERICI[3:7]:
        apps.append((n, generico(52, '#3A3F55' if dark else col, sh, radsvg)))
    cells = ''.join(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 6px; width: 60px">{s}<span style="font-size: 11px; font-weight: {700 if n=="Statera" else 500}; color: {tc}">{n}</span></div>' for n, s in apps)
    return (f'<div style="display: flex; flex-direction: column; gap: 10px; align-items: center">'
            f'<div style="width: 300px; height: 560px; border-radius: 40px; border: 8px solid #1A1B22; background: {wall}; box-sizing: border-box; padding: 64px 14px 20px; display: flex; flex-direction: column; justify-content: space-between">'
            f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 0 10px"><span style="font-size: 44px; font-weight: 300; color: {tc}; letter-spacing: -0.02em">9:41</span><span style="font-size: 13px; color: {tc}; opacity: 0.8">sabato 14 novembre</span></div>'
            f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: 18px; justify-items: center">{cells}</div></div>'
            f'{caption("Android " + ("scuro" if dark else "chiaro") + ", maschera " + nome_maschera)}</div>')

def adattiva(k):
    masks = [('Cerchio', '50%'), ('Squircle', '30%'), ('Arrotondata', '18%'), ('Goccia', '50% 50% 50% 14%')]
    small = ''.join(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">{mascherata(k, 64, r)}{caption(n)}</div>' for n, r in masks)
    return card(label('Icona adattiva Android')
        + f'<div style="position: relative; width: 216px; height: 216px; align-self: center">{ico(k, 216, forma="adattiva")}'
          f'<div style="position: absolute; left: 36.7px; top: 36.7px; width: 142.6px; height: 142.6px; border-radius: 50%; border: 2px dashed #FFFFFF; box-sizing: border-box; opacity: 0.85"></div>'
          f'<div style="position: absolute; left: 20px; top: 20px; width: 176px; height: 176px; border-radius: 50%; border: 1px solid #FFFFFF; box-sizing: border-box; opacity: 0.4"></div></div>'
        + f'<p style="margin: 0; font-size: 12px; line-height: 1.5; color: {MU}">Primo piano dentro la zona sicura del 66% (tratteggio), sfondo indaco pieno a parte. Il cerchio sottile è la maschera rotonda.</p>'
        + f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px">{small}</div>', extra='; width: 300px; flex-shrink: 0')

def avvio(k, dark):
    bg = BGD if dark else BG; tc = TXD if dark else TX
    return (f'<div style="display: flex; flex-direction: column; gap: 10px; align-items: center">'
            f'<div style="width: 180px; height: 360px; border-radius: 28px; border: 6px solid #1A1B22; background: {bg}; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px">{ico(k, 72)}<span style="font-size: 18px; font-weight: 800; letter-spacing: -0.03em; color: {tc}">Statera</span></div>'
            f'{caption("Avvio, " + ("scuro" if dark else "chiaro"))}</div>')

def barra_win(k, dark):
    bg = '#202020' if dark else '#EEF0F4'
    gen = '#4A4E5E' if dark else '#B9BECB'
    items = [generico(24, gen, 'sq', 6), generico(24, gen, 'ci', 6), ico(k, 24), generico(24, gen, 'tr', 6), generico(24, gen, 'sq', 6)]
    cells = ''
    for i, it in enumerate(items):
        act = i == 2
        hi = ('#2E2E2E' if dark else '#FFFFFF') if act else 'transparent'
        ind = f'<span style="position: absolute; bottom: 3px; left: 15px; width: 10px; height: 3px; border-radius: 2px; background: {LIL if dark else IND}"></span>' if act else ''
        cells += f'<div style="position: relative; width: 40px; height: 40px; border-radius: 6px; background: {hi}; display: flex; align-items: center; justify-content: center">{it}{ind}</div>'
    tc = '#FFFFFF' if dark else '#1E2230'
    return (f'<div style="height: 48px; background: {bg}; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px">'
            f'<span style="width: 60px"></span><div style="display: flex; gap: 4px">{cells}</div><span style="font-size: 12px; color: {tc}; width: 60px; text-align: right">9:41</span></div>')

def start_win(k, dark):
    bg = '#2B2B2B' if dark else '#F6F7FA'; tc = '#FFFFFF' if dark else '#1E2230'; mc = '#B4B7C2' if dark else '#5F6275'
    gen = '#4A4E5E' if dark else '#B9BECB'
    pins = [('Note', generico(32, gen, 'sq', 8)), ('Statera', ico(k, 32)), ('Meteo', generico(32, gen, 'ci', 8)), ('Foto', generico(32, gen, 'tr', 8))]
    pin = ''.join(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 6px; width: 70px; padding: 10px 0; border-radius: 6px; background: {("#3A3A3A" if dark else "#FFFFFF") if n=="Statera" else "transparent"}">{s}<span style="font-size: 11px; color: {tc}">{n}</span></div>' for n, s in pins)
    return (f'<div style="background: {bg}; border-radius: 12px; padding: 18px 20px; display: flex; flex-direction: column; gap: 12px; flex: 1; min-width: 0">'
            f'<span style="font-size: 13px; font-weight: 700; color: {tc}">Aggiunte</span><div style="display: flex; gap: 6px">{pin}</div>'
            f'<span style="font-size: 13px; font-weight: 700; color: {tc}">Tutte le app</span>'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 6px 8px; border-radius: 6px; background: {"#3A3A3A" if dark else "#FFFFFF"}">{ico(k, 24)}<span style="font-size: 13px; color: {tc}">Statera</span><span style="font-size: 11px; color: {mc}; margin-left: auto">App</span></div>'
            f'<div style="display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; border: 1px solid {"#444" if dark else "#DADCE6"}">{ico(k, 16)}<span style="font-size: 12px; color: {tc}">Statera — finestra dell’app</span></div></div>')

def scheda_browser(k, dark):
    bar = '#202124' if dark else '#DEE1E8'; tab = '#35363A' if dark else '#FFFFFF'; tc = '#E8EAED' if dark else '#1E2230'; mc = '#9AA0A6' if dark else '#6B6F7E'
    return (f'<div style="background: {bar}; border-radius: 10px; padding: 8px 8px 0; display: flex; gap: 4px">'
            f'<div style="background: {tab}; border-radius: 8px 8px 0 0; padding: 9px 12px; display: flex; align-items: center; gap: 8px; width: 200px">{ico(k, 16)}<span style="font-size: 12px; color: {tc}">Statera</span></div>'
            f'<div style="padding: 9px 12px; display: flex; align-items: center; gap: 8px; width: 160px"><span style="width: 16px; height: 16px; border-radius: 50%; background: {mc}; opacity: 0.5"></span><span style="font-size: 12px; color: {mc}">Altra scheda</span></div></div>')

def tavola_dispositivi(k):
    nome = S[k]['nome']
    android = card(label('Android: schermata home e avvio')
        + f'<div style="display: flex; gap: 20px; align-items: flex-start">{telefono(k, False, "cerchio", "rotonda")}{telefono(k, True, "squircle", "squircle")}{adattiva(k)}'
          f'<div style="display: flex; flex-direction: column; gap: 20px">{avvio(k, False)}</div></div>')
    windows = card(label('Windows: barra delle applicazioni, menu Start, finestra (16–48 px)')
        + f'<div style="display: flex; gap: 20px">'
          f'<div style="display: flex; flex-direction: column; gap: 12px; width: 420px; flex-shrink: 0">{barra_win(k, False)}{barra_win(k, True)}'
          f'<div style="display: flex; gap: 20px; align-items: flex-end; padding: 12px 4px">' + ''.join(f'<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">{ico(k, s)}{caption(f"{s}")}</div>' for s in (16, 20, 24, 32, 40, 48)) + '</div></div>'
          f'{start_win(k, False)}{start_win(k, True)}</div>')
    browser = card(label('Favicon nel browser, 16 e 32 px')
        + f'<div style="display: flex; gap: 20px; align-items: flex-end">{scheda_browser(k, False)}{scheda_browser(k, True)}'
          f'<div style="display: flex; gap: 16px; align-items: flex-end">{pixel(k, 16, 4)}{pixel(k, 32, 2)}</div></div>')
    body = (f'<div style="display: flex; align-items: baseline; gap: 16px"><h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.02em">{k} · {nome}</h1><span style="font-size: 15px; color: {MU}">Sui dispositivi</span></div>'
            f'{android}{windows}{browser}')
    return page(f'Logo {k} · {nome} — sui dispositivi', 1280, 1600, body)

# ---------- Confronto ----------
def tavola_confronto(keys='ABCD', titolo='Quattro direzioni a confronto', doc='Logo e icona — confronto delle direzioni'):
    cols = ''
    for k in keys:
        cols += card(f'<span style="font-size: 18px; font-weight: 800">{k} · {S[k]["nome"]}</span>'
            + f'<div style="display: flex; justify-content: center">{ico(k, 120)}</div>'
            + f'<div style="display: flex; gap: 14px; align-items: flex-end; justify-content: center; padding: 14px; border-radius: 12px; background: {BG}">' + ''.join(ico(k, s) for s in (16, 24, 32, 48)) + '</div>'
            + f'<div style="display: flex; gap: 14px; align-items: flex-end; justify-content: center; padding: 14px; border-radius: 12px; background: {BGD}">' + ''.join(ico(k, s) for s in (16, 24, 32, 48)) + '</div>'
            + f'<div style="display: flex; justify-content: center">{pixel(k, 16, 6)}</div>'
            + f'<div style="display: flex; justify-content: center">{wordmark(k, 36, 28)}</div>', extra='; flex: 1; min-width: 0; align-items: stretch')
    body = (f'<div style="display: flex; align-items: baseline; gap: 16px"><h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.02em">{titolo}</h1><span style="font-size: 15px; color: {MU}">16, 24, 32 e 48 px reali, chiaro e scuro</span></div>'
            f'<div style="display: flex; gap: 20px">{cols}</div>')
    return page(doc, 1280, 820, body)

DESC = {
 'A': 'La stadera disegnata: gancio di sospensione, braccio con le tacche, piatto sul braccio corto e il peso (il «romano») su quello lungo. È la più letterale e racconta il nome.',
 'B': 'Della stadera resta il gesto: il peso che scorre sul braccio graduato finché tutto torna in pari. Un cursore, come quando si aggiusta il budget.',
 'C': 'Una leva in equilibrio asimmetrico: il blocco pesante vicino al fulcro, la pallina leggera lontana. Il principio della stadera in tre forme piene.',
 'E': 'La bilancia a due piatti disegnata a tratto: colonna, base, braccio e piatti appesi. Tratto pieno e arrotondato, più spesso delle icone dell’app, così regge anche da piccola.',
 'F': 'La stessa bilancia, ma col braccio appena inclinato: un piatto scende e l’altro sale. Racconta il movimento dei soldi che entrano ed escono.',
 'G': 'Un incrocio con la S: la colonna è la S a due piatti, che regge il braccio e finisce nella base. Tiene insieme l’iniziale e la bilancia.',
 'D': 'Una S geometrica fatta di due mezzi cerchi sfalsati, come i due bracci diversi della stadera. La più compatta e la più leggibile da piccola.',
}

if __name__ == '__main__':
    import os
    out = os.environ.get('STATERA_CANVAS', 'out/project') + '/'
    os.makedirs(out, exist_ok=True)
    open(out + 'logo-confronto.dc.html', 'w').write(tavola_confronto())
    open(out + 'logo-confronto-bilance.dc.html', 'w').write(tavola_confronto('DEFG', 'La S a confronto con tre bilance', 'Logo e icona — la S e tre bilance'))
    for k in S:
        open(out + f'logo-{k}-simbolo.dc.html', 'w').write(tavola_simbolo(k, DESC[k]))
        open(out + f'logo-{k}-dispositivi.dc.html', 'w').write(tavola_dispositivi(k))
    print('ok')
