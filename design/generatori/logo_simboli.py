# Simboli delle direzioni, in una griglia di 100 unità (centro 50,50).
# Ogni simbolo: 'big' (da 48 px in su) e 'sm' (16-32 px), come frammento SVG con colore {c}.
S = {}
S['A'] = dict(nome='Stadera', xl='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<circle cx="34" cy="19" r="7" stroke-width="6.5"/>
<path d="M34 26V44" stroke-width="7"/>
<path d="M9 44H91" stroke-width="9"/>
<path d="M19 44V56M72 44V54" stroke-width="6"/>
<path d="M50 35V39M60 35V39M82 35V39" stroke-width="4.5"/>
</g>
<g fill="{c}">
<path d="M4 57H34A15 15 0 0 1 4 57Z"/>
<circle cx="72" cy="67" r="14"/>
</g>''', big='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<circle cx="34" cy="19" r="7" stroke-width="6.5"/>
<path d="M34 26V44" stroke-width="7"/>
<path d="M9 44H91" stroke-width="9"/>
<path d="M19 44V56M72 44V54" stroke-width="6"/>
</g>
<g fill="{c}">
<path d="M4 57H34A15 15 0 0 1 4 57Z"/>
<circle cx="72" cy="67" r="14"/>
</g>''', sm='''
<g fill="none" stroke="{c}" stroke-linecap="round"><path d="M36 18V44" stroke-width="10"/><path d="M8 44H92" stroke-width="11"/></g>
<g fill="{c}"><path d="M2 48H38A18 18 0 0 1 2 48Z"/><circle cx="72" cy="66" r="17"/><rect x="68" y="44" width="8" height="10"/></g>''')
S['B'] = dict(nome='Cursore', xl='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M6 50H94" stroke-width="9"/>
<path d="M40 61V69M48 61V69M82 61V69M90 61V69" stroke-width="4.5"/>
</g>
<g fill="{c}"><path d="M22 56L33 76H11Z" stroke="{c}" stroke-width="5" stroke-linejoin="round"/><circle cx="65" cy="50" r="16"/></g>''', big='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M6 50H94" stroke-width="9"/>
</g>
<g fill="{c}"><path d="M22 56L33 76H11Z" stroke="{c}" stroke-width="5" stroke-linejoin="round"/><circle cx="65" cy="50" r="16"/></g>''', sm='''
<g fill="none" stroke="{c}" stroke-linecap="round"><path d="M6 50H94" stroke-width="12"/></g>
<g fill="{c}"><path d="M24 54L38 80H10Z" stroke="{c}" stroke-width="6" stroke-linejoin="round"/><circle cx="66" cy="50" r="21"/></g>''')
S['C'] = dict(nome='Leva', big='''
<g fill="{c}">
<path d="M38 62L49 80H27Z" stroke="{c}" stroke-width="5" stroke-linejoin="round"/>
<rect x="8" y="53" width="84" height="8" rx="4"/>
<rect x="11" y="26" width="25" height="25" rx="5"/>
<circle cx="80" cy="42" r="9"/>
</g>''', sm='''
<g fill="{c}">
<path d="M38 60L52 84H24Z" stroke="{c}" stroke-width="7" stroke-linejoin="round"/>
<rect x="4" y="50" width="92" height="12" rx="6"/>
<rect x="6" y="16" width="32" height="32" rx="6"/>
<circle cx="80" cy="35" r="13"/>
</g>''')
S['D'] = dict(nome='S a due piatti', big='''
<path d="M72 16H42A17 17 0 0 0 42 50H58A17 17 0 0 1 58 84H28" fill="none" stroke="{c}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>''', sm='''
<path d="M74 15H41A17.5 17.5 0 0 0 41 50H59A17.5 17.5 0 0 1 59 85H26" fill="none" stroke="{c}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>''')

def icona(k, size, fg='#FFFFFF', bg='#535AA6', forma='squircle', variante=None, area=0.62):
    v = variante or ('sm' if size <= 32 else 'big')
    s = S[k][v].replace('{c}', fg)
    n = 512
    sc = n*area/100
    off = (n - 100*sc)/2
    shape = {'squircle': f'<rect width="{n}" height="{n}" rx="{n*0.22}" fill="{bg}"/>',
             'cerchio': f'<circle cx="{n/2}" cy="{n/2}" r="{n/2}" fill="{bg}"/>',
             'quadrato': f'<rect width="{n}" height="{n}" fill="{bg}"/>',
             'nessuna': ''}[forma]
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {n} {n}">{shape}<g transform="translate({off:.2f} {off:.2f}) scale({sc:.4f})">{s}</g></svg>'

import subprocess, io
from PIL import Image
_bb = {}
def bbox(k, v):
    """Riquadro del disegno (in unità 0-100) misurato rasterizzando a 1000 px."""
    if (k, v) in _bb: return _bb[(k, v)]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 120 120" width="1200" height="1200">{S[k][v].replace("{c}","#000")}</svg>'
    png = subprocess.run(['rsvg-convert'], input=svg.encode(), capture_output=True, check=True).stdout
    b = Image.open(io.BytesIO(png)).getchannel('A').getbbox()
    r = tuple(x/10 - 10 for x in b)
    _bb[(k, v)] = r
    return r

def gruppo(k, v, fg, box):
    """Frammento <g> che centra il simbolo in un quadrato di lato `box` (unità SVG), centrato in 0,0... restituisce transform per inserire."""
    x0, y0, x1, y1 = bbox(k, v)
    w, h = x1-x0, y1-y0
    sc = box/max(w, h)
    cx, cy = (x0+x1)/2, (y0+y1)/2
    return f'<g transform="scale({sc:.4f}) translate({-cx:.2f} {-cy:.2f})">{S[k][v].replace("{c}", fg)}</g>'

def icona2(k, size, fg='#FFFFFF', bg='#535AA6', forma='squircle', variante=None, area=None, n=512):
    v = variante or variante_per(k, size)
    area = area or (0.68 if v == 'sm' else 0.60)
    shape = {'squircle': f'<rect width="{n}" height="{n}" rx="{n*0.225:.1f}" fill="{bg}"/>',
             'cerchio': f'<circle cx="{n/2}" cy="{n/2}" r="{n/2}" fill="{bg}"/>',
             'quadrato': f'<rect width="{n}" height="{n}" fill="{bg}"/>',
             'nessuna': ''}[forma]
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {n} {n}">{shape}<g transform="translate({n/2} {n/2})">{gruppo(k, v, fg, n*area)}</g></svg>'

def png(svg, size):
    out = subprocess.run(['rsvg-convert', '-w', str(size), '-h', str(size)], input=svg.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(out)).convert('RGBA')

def variante_per(k, size):
    if size <= 32: return 'sm'
    if size >= 96 and 'xl' in S[k]: return 'xl'
    return 'big'

# --- Bilance (seconda tornata) ---
S['E'] = dict(nome='Bilancia a tratto', big='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M50 24V82" stroke-width="7.5"/>
<path d="M33 84H67" stroke-width="8"/>
<path d="M14 30H86" stroke-width="7.5"/>
<path d="M8 58L20 30L32 58M68 58L80 30L92 58" stroke-width="4.5"/>
</g>
<g fill="{c}">
<circle cx="50" cy="20" r="7"/>
<path d="M4 58H36A16 16 0 0 1 4 58Z"/>
<path d="M64 58H96A16 16 0 0 1 64 58Z"/>
</g>''', sm='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M50 22V82M30 86H70M10 28H90" stroke-width="11"/>
<path d="M20 30V50M80 30V50" stroke-width="8"/>
</g>
<g fill="{c}">
<path d="M0 52H40A20 20 0 0 1 0 52Z"/>
<path d="M60 52H100A20 20 0 0 1 60 52Z"/>
</g>''')
S['F'] = dict(nome='Bilancia in movimento', big='''<rect x="45.5" y="30" width="9" height="52" fill="{c}"/><rect x="30" y="80" width="40" height="10" rx="5.0" fill="{c}"/><path d="M12.4 35.3L87.6 24.7" stroke="{c}" stroke-width="9" stroke-linecap="round"/><circle cx="50" cy="30" r="8.5" fill="{c}"/><path d="M12.4 35.3L-0.6 57.3M12.4 35.3L25.4 57.3" fill="none" stroke="{c}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M-3.6 57.3H28.4A16 16 0 0 1 -3.6 57.3Z" fill="{c}"/><path d="M87.6 24.7L74.6 46.7M87.6 24.7L100.6 46.7" fill="none" stroke="{c}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M71.6 46.7H103.6A16 16 0 0 1 71.6 46.7Z" fill="{c}"/>''', sm='''<rect x="44.0" y="28" width="12" height="54" fill="{c}"/><rect x="26" y="80" width="48" height="13" rx="6.5" fill="{c}"/><path d="M8.4 33.8L91.6 22.2" stroke="{c}" stroke-width="12" stroke-linecap="round"/><circle cx="50" cy="28" r="10" fill="{c}"/><path d="M8.4 33.8V47.8" fill="none" stroke="{c}" stroke-width="9" stroke-linecap="round"/><path d="M-11.6 47.8H28.4A20 20 0 0 1 -11.6 47.8Z" fill="{c}"/><path d="M91.6 22.2V36.2" fill="none" stroke="{c}" stroke-width="9" stroke-linecap="round"/><path d="M71.6 36.2H111.6A20 20 0 0 1 71.6 36.2Z" fill="{c}"/>''')
S['G'] = dict(nome='Bilancia con la S', big='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M10 24H90" stroke-width="8"/>
<path d="M46 24A13 13 0 0 0 46 50H54A13 13 0 0 1 54 76H28M54 76H72" stroke-width="8"/>
<path d="M15 26V42M85 26V42" stroke-width="4.5"/>
</g>
<g fill="{c}">
<path d="M1 44H29A14 14 0 0 1 1 44Z"/>
<path d="M71 44H99A14 14 0 0 1 71 44Z"/>
</g>''', sm='''
<g fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">
<path d="M8 22H92" stroke-width="12"/>
<path d="M46 22A14 14 0 0 0 46 50H54A14 14 0 0 1 54 78H30M54 78H70" stroke-width="12"/>
<path d="M14 24V38M86 24V38" stroke-width="8"/>
</g>
<g fill="{c}">
<path d="M0 40H28A14 14 0 0 1 0 40Z"/>
<path d="M72 40H100A14 14 0 0 1 72 40Z"/>
</g>''')
