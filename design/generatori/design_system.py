#!/usr/bin/env python3
"""Design system «Statera» (tipo Design System di claude.ai): token, carattere, componenti, logo, icone.
Il riferimento è l'app: token, icone, logo e carattere si leggono da un checkout del ramo main (app_main.py),
mai copiati a mano. I nomi dei token sono quelli di src/styles/tokens.css.
Uso: design_system.py <cartella di uscita> <cartella del pacchetto lucide-static> <checkout del ramo main>
Scrive <uscita>/project/… e <uscita>/asset/<gruppo>/<file>.svg (da caricare come asset)."""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icone
from icone import seticon
from app_main import App

OUTDIR, LUCIDE, MAIN = sys.argv[1:4]
APP = App(MAIN)
P = os.path.join(OUTDIR, 'project')
def w(rel, text):
    path = os.path.join(P, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text)

def ic(key, size=20, sw=2):
    return seticon('lucide', key, size, sw=sw)
def ai(name, size=20, sw=2):
    """Icona dell'app (src/lib/icons.ts), per nome Lucide."""
    return APP.icon(name, size, sw)

# ================================================================ token (da src/styles/tokens.css)
TL, TD = APP.tokens_light, APP.tokens_dark
def _hex(v):
    v = v.strip()
    if re.fullmatch(r'#[0-9a-fA-F]{3}', v): v = '#' + ''.join(c * 2 for c in v[1:])
    return v.upper()
def _lum(h):
    h = _hex(h)
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def cr(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
def V(name, theme='light'): return _hex(APP.value(name, theme))
def _mix(a, b, pct):
    """color-mix(in srgb, a pct, b): il cerchio della categoria appoggiato sulla superficie."""
    p = float(str(pct).rstrip('%')) / 100; a, b = _hex(a), _hex(b)
    return '#' + ''.join(f'{round(int(a[i:i + 2], 16) * p + int(b[i:i + 2], 16) * (1 - p)):02X}' for i in (1, 3, 5))
def ratio(a, b, theme='light'):
    return f'{cr(V(a, theme), V(b, theme)):.1f}'.replace('.', ',')
def f1(x): return f'{x:.1f}'.replace('.', ',')
def both(a, b):
    return f'{ratio(a, b)}:1 chiaro, {ratio(a, b, "dark")}:1 scuro'
def css_value(v):
    """Valore di tokens.css nella forma che il design system legge: var() → alias, rgb(a b c / d) → rgba(a, b, c, d)."""
    m = re.fullmatch(r'var\(--([A-Za-z0-9-]+)\)', v)
    if m: return '{' + m.group(1) + '}'
    v = re.sub(r'rgb\((\d+) (\d+) (\d+) / ([\d.]+)\)', lambda m: f'rgba({m[1]}, {m[2]}, {m[3]}, {m[4]})', v)
    return _hex(v) if v.startswith('#') else v

USAGE = {
 'color-bg': 'Sfondo di ogni schermata, dei pannelli che salgono dal basso, del tastierino e delle finestre su PC; dentro una scheda, fondo dei campi.',
 'color-surface': 'Schede, campi, tasti del tastierino, barra di navigazione, barra laterale e pulsanti secondari appoggiati su color-bg.',
 'color-surface-2': 'Secondo livello su color-surface: pulsanti dentro una scheda, tasto premuto, riga al passaggio del puntatore su PC, segmentato.',
 'color-border': 'Linee sottili: separatori, bordo alto del tastierino, righe delle tabelle su PC, maniglia dei pannelli, contorno al passaggio nella scelta dell\'icona. Mai intorno alle schede.',
 'color-text': f'Testo e importi in uscita su color-bg, color-surface, color-surface-2 e color-accent-soft ({both("color-text", "color-bg")} su color-bg). Anello dell\'icona scelta in SceltaIcona.',
 'color-text-muted': f'Testo secondario (categoria · conto, date, voci di ElencoVoci, didascalie) su color-bg, color-surface e color-surface-2: minimo {ratio("color-text-muted", "color-surface-2")}:1 in chiaro, {ratio("color-text-muted", "color-surface-2", "dark")}:1 in scuro. Anche interruttore spento e bordo delle caselle.',
 'color-primary': 'Il colore di Statera, come riempimento: pulsante +, pulsante principale, «Fatto» del tastierino, segmento attivo, interruttore acceso, riquadro dell\'importo principale e riquadro del logo in tema chiaro. Sopra va color-on-primary. In scuro è il lilla del riquadro del logo.',
 'color-on-primary': f'Testo e icone su color-primary ({both("color-on-primary", "color-primary")}); simbolo del logo.',
 'color-accent': f'Testo e icone d\'accento: link, icone delle azioni rapide, tasti + − = del tastierino, voce attiva della barra, pulsante tenue. Su color-surface ({ratio("color-accent", "color-surface")}:1 / {ratio("color-accent", "color-surface", "dark")}:1) e color-accent-soft ({ratio("color-accent", "color-accent-soft")}:1 / {ratio("color-accent", "color-accent-soft", "dark")}:1).',
 'color-accent-soft': 'Fondo tenue: cerchi delle azioni rapide, tasti delle operazioni, chip attivi, avvisi in cima alle schermate, voce attiva della barra laterale; in tema scuro il riquadro dell\'importo principale.',
 'color-income': f'Solo le entrate: importi positivi e icona del riquadro Entrate, su color-surface e color-bg ({ratio("color-income", "color-surface")}:1 / {ratio("color-income", "color-surface", "dark")}:1); stato «Sincronizzato» nella barra laterale. Non su color-accent-soft in chiaro ({ratio("color-income", "color-accent-soft")}:1).',
 'color-expense': 'Importi in uscita: col colore del testo (alias di color-text), mai in rosso. Il segno − basta.',
 'color-expense-icon': 'Solo l\'icona del riquadro Uscite (grafica, almeno 3:1). Gli importi in uscita restano color-expense.',
 'status-warning': f'Attenzione: barra del budget quasi esaurito (da 80%) e fondo dei promemoria, sempre con simbolo e testo. È grafica, non testo: in chiaro arriva a {ratio("status-warning", "color-surface")}:1 su bianco.',
 'status-critical': 'Budget superato (oltre 100%): barra e simbolo, sempre con la parola «Superato».',
 'color-danger': f'Pericolo, solo per ciò che cancella o è fallito: Elimina, Elimina tutti i dati, sincronizzazione o salvataggio non riusciti. Testo su color-surface ({ratio("color-danger", "color-surface")}:1 / {ratio("color-danger", "color-surface", "dark")}:1) e color-bg.',
 'color-on-danger': f'Testo e icone sul pulsante di conferma dell\'eliminazione ({both("color-on-danger", "color-danger")}).',
 'color-focus': 'Anello del focus da tastiera: 2 px pieni, staccato di 2 px. Almeno 3:1 su color-bg, color-surface e color-accent-soft in entrambi i temi.',
 'color-backdrop': 'Velo sotto i pannelli e le finestre.',
 'toast-bg': 'Fondo degli avvisi a comparsa: colori invertiti rispetto al tema.',
 'toast-text': f'Testo degli avvisi a comparsa su toast-bg ({both("toast-text", "toast-bg")}).',
 'toast-action': f'Azione dell\'avviso (Annulla, Aggiorna) su toast-bg ({both("toast-action", "toast-bg")}).',
 'chart-income': 'Grafici: entrate. Coppia blu/arancio scelta per chi non distingue rosso e verde; legenda sempre visibile.',
 'chart-expense': 'Grafici: uscite, e barre delle categorie in Analisi.',
 'chart-worth': 'Grafici: andamento del patrimonio (una sola serie).',
 'chart-track': 'Binario delle barre di budget, obiettivi e categorie.',
 'chart-grid': 'Linee della griglia e asse dei grafici.',
 'cat-icon-dark': 'Icona dentro il cerchio della categoria in tema scuro (bianca sul cerchio al 45%). In chiaro l\'icona ha la tinta piena.',
 'shadow-1': 'Pomello dell\'interruttore.',
 'shadow-2': 'Barra flottante, barra laterale, avvisi a comparsa, suggerimenti.',
 'shadow-3': 'Pannelli e finestre sopra il velo; tastierino fuori da un pannello.',
 'shadow-fab': 'Pulsante + della barra.',
 'space-hair': 'Mezzo passo: distanza minima tra due righe di testo (nome e seconda riga).',
 'space-1': 'Tra icona e testo piccoli; spessore interno del segmentato; tra etichetta e importo nel riquadro.',
 'space-2': 'Tra chip, pulsanti vicini e tasti del tastierino; tra etichetta e campo.',
 'space-3': 'Tra icona e testi di una riga; tra le voci di ElencoVoci; imbottitura verticale del tastierino.',
 'space-4': 'Tra le schede di una schermata; margine della barra flottante; tra riquadro e azioni rapide.',
 'space-5': 'Margine laterale delle schermate del telefono; interno delle schede e del riquadro dell\'importo; sotto il blocco del saldo.',
 'space-6': 'Sopra i titoli di sezione in maiuscolo; interno delle finestre su PC; tra colonne su PC.',
 'space-7': 'Stati vuoti; larghezza in più delle azioni rapide.',
 'space-8': 'Spazio libero in fondo alle schermate; distanza della finestra dal bordo alto su PC.',
 'radius-2xs': 'Angoli delle barre dei grafici.',
 'radius-xs': 'Tasti delle scorciatoie, caselle di spunta.',
 'radius-sm': 'Icone dell\'interfaccia su fondo, elementi piccoli.',
 'radius-md': 'Campi, tasti del tastierino, riga evidenziata, voci della barra laterale, avvisi.',
 'radius-lg': 'Schede, barra laterale, riquadro dell\'importo principale.',
 'radius-xl': 'Pannelli dal basso e tastierino fuori da un pannello (solo gli angoli alti), finestre su PC.',
 'radius-full': 'Pulsanti, chip, segmentato, barra flottante, cerchi, pillola del riquadro.',
 'text-2xs': 'Assi dei grafici (11 px); voci della barra flottante.',
 'text-xs': 'Tasti, titoli di gruppo in maiuscolo, didascalie piccole (12 px).',
 'text-sm': 'Seconde righe, etichette dei campi, pulsanti piccoli, voci di ElencoVoci, avvisi (13 px).',
 'text-md': 'Testo corrente, valori di ElencoVoci sul telefono, «Fatto» del tastierino (15 px).',
 'text-input': 'Testo dentro i campi: 16 px perché il telefono non ingrandisca la pagina.',
 'text-lg': 'Titoli delle schede, marchio nella barra laterale, pulsante grande (17 px).',
 'text-xl': 'Titoli delle schermate secondarie e delle finestre; cifre del tastierino (22 px).',
 'text-2xl': 'Titoli delle quattro sezioni (26 px).',
 'amount-s': 'Importi dei riquadri e dei totali (20 px).',
 'amount-m': 'Patrimonio di un conto, numero di buoni (34 px).',
 'amount-l': 'Importo del riquadro principale: saldo del mese, patrimonio, risparmio (46 px).',
 'amount-xl': 'Importo mentre lo scrivi nel modulo (56 px).',
 'tracking-tight': 'Titoli: −0,02 em.',
 'tracking-tighter': 'Importi grandi: −0,03 em.',
 'tracking-caps': 'Etichette in maiuscolo (titoli di gruppo): +0,06 em.',
 'tracking-code': 'Chiave di recupero: +0,04 em.',
 'tracking-pin': 'Cifre nascoste del PIN: +0,4 em.',
 'leading-tight': 'Titoli e importi grandi.',
 'leading-snug': 'Titoli.',
 'leading-compact': 'Seconde righe che vanno a capo, ElencoVoci.',
 'leading-normal': 'Testo corrente.',
 'size-touch': 'Area di tocco minima di ogni comando; pulsanti normali, pulsanti icona, voci della barra laterale.',
 'size-field': 'Altezza dei campi e degli avvisi a comparsa.',
 'size-row': 'Altezza minima di una riga di elenco.',
 'size-key': 'Altezza dei tasti del tastierino degli importi.',
 'size-btn-l': 'Pulsante grande in fondo a un pannello.',
 'size-btn-s': 'Pulsante piccolo, chip, segmento (l\'area di tocco resta 44 px con il margine).',
 'size-step': 'Numeri dei passi della guida, pulsantini dentro i campi.',
 'size-cat-s': 'Icona di categoria piccola: sottocategorie, preferiti, tabelle su PC.',
 'size-cat': 'Icona di categoria nelle righe e nella griglia di SceltaIcona.',
 'size-cat-l': 'Icona di categoria grande (anteprima di SceltaIcona); cerchi delle azioni rapide.',
 'size-fab': 'Pulsante + al centro della barra.',
 'size-hero-icon': 'Icona grande della schermata di blocco.',
 'nav-height': 'Altezza della barra flottante del telefono.',
 'size-sidebar': 'Larghezza della barra laterale su PC.',
 'content-max': 'Larghezza massima dei contenuti e delle finestre su PC.',
 'opacity-disabled': 'Comandi disattivati: opacità, niente ombra né movimento.',
 'focus-width': 'Spessore dell\'anello del focus; anello dell\'icona scelta.',
 'focus-offset': 'Distanza dell\'anello dal comando.',
 'cat-tint': f'Intensità del cerchio dell\'icona di categoria: tinta al {TL.get("cat-tint")} in chiaro, al {TD.get("cat-tint")} in scuro (il valore scuro sta in bundle.css, perché fuori dai colori i token non hanno temi).',
 'duration-fast': 'Pressione di un pulsante o di un tasto, cambio di colore.',
 'duration-base': 'Interruttore, segmentato, avvisi che compaiono.',
 'duration-slow': 'Pannello che sale dal basso, finestra che si apre.',
 'ease-standard': 'Ingressi e cambi di stato.',
 'ease-exit': 'Uscite: pannelli che si chiudono, avvisi che spariscono.',
}
SWATCH_NAMES = ['verde', 'terracotta', 'blu', 'nocciola', 'viola', 'petrolio', 'rosa', 'oliva']

def family(name):
    if name.startswith(('color-', 'toast-', 'chart-', 'status-', 'swatch-')) or name == 'cat-icon-dark': return 'color'
    if name.startswith('shadow-'): return 'shadow'
    if name.startswith('space-'): return 'spacing'
    if name.startswith('radius-'): return 'radius'
    if name.startswith(('text-', 'amount-', 'leading-', 'tracking-')): return 'testo'
    if name.startswith('size-') or name in ('nav-height', 'content-max'): return 'dimensioni'
    if name in ('opacity-disabled', 'focus-width', 'focus-offset', 'cat-tint'): return 'stati'
    if name.startswith(('duration-', 'ease-')): return 'animazione'
    if name.startswith('font-'): return 'font'
    raise SystemExit(f'Token --{name} di tokens.css senza famiglia nel design system: aggiungilo a family()')

FAM = {k: [] for k in ('color', 'shadow', 'spacing', 'radius', 'testo', 'dimensioni', 'stati', 'animazione')}
names = list(TL) + [n for n in TD if n not in TL]
for n in names:
    f = family(n)
    if f == 'font': continue  # type.families
    u = USAGE.get(n)
    if n.startswith('swatch-'):
        k = n[len('swatch-'):]; i = int(k[1:]) - 1
        u = f'Tinta {k} ({SWATCH_NAMES[i]}) di conti, categorie e obiettivi: i dati salvano solo «{k}». Uguale nei due temi; nel cerchio della categoria vedi IconaCategoria.'
    if u is None:
        print(f'  attenzione: --{n} senza uso descritto in USAGE'); u = 'Da src/styles/tokens.css.'
    lv, dv = TL.get(n), TD.get(n)
    if f in ('color', 'shadow'):
        if lv is None: lv = dv  # solo in scuro (cat-icon-dark): stesso valore, usato solo lì
        val = {'light': css_value(lv), 'dark': css_value(dv)} if dv is not None and css_value(dv) != css_value(lv) else css_value(lv)
    else:
        val = lv
    FAM[f].append({'name': n, 'value': val, 'usage': u})

FAMILY = TL['font-sans'].replace("'", '"')
def px(token):
    v = TL[token]
    return f'{round(float(v[:-3]) * 16, 2):g}px' if v.endswith('rem') else v
def st(name, size, lead, weight, sample, usage, track=None):
    """Stile di testo dai token: size = --text-*/--amount-*, lead = --leading-*, track = --tracking-*."""
    d = {'name': name, 'fontSize': px(size), 'lineHeight': TL[lead] if lead in TL else lead, 'fontWeight': weight, 'sample': sample,
         'usage': f'{usage} (--{size}{", --" + lead if lead in TL else ""}{", --" + track if track else ""})'}
    if track: d['letterSpacing'] = TL[track]
    return d
TYPE = {
 'fonts': [{'family': 'Plus Jakarta Sans', 'file': 'fonts/plus-jakarta-sans-latin-wght-normal.woff2', 'weight': '200 800', 'style': 'normal'}],
 'families': {'sans': FAMILY, 'num': FAMILY},
 'groups': [
  {'name': 'Importi', 'family': 'sans', 'styles': [
    st('importo-xl', 'amount-xl', 'leading-tight', 800, '42,30 €', 'Importo mentre lo scrivi nel modulo.', 'tracking-tighter'),
    st('importo-l', 'amount-l', 'leading-tight', 800, '+1.325,65 €', 'RiquadroImporto: saldo del mese, patrimonio, risparmio.', 'tracking-tighter'),
    st('importo-m', 'amount-m', 'leading-tight', 800, '8.412,90 €', 'Saldo di un conto, numero di buoni.', 'tracking-tighter'),
    st('importo-s', 'amount-s', 'leading-snug', 800, '2.010,00 €', 'Totali di Cerca e di Analisi.', 'tracking-tight'),
    st('tastierino', 'text-xl', 'leading-snug', 700, '7', 'Cifre e operazioni del Tastierino degli importi.')]},
  {'name': 'Titoli', 'family': 'sans', 'styles': [
    st('titolo-1', 'text-2xl', 'leading-snug', 800, 'Analisi', 'Titolo delle sezioni principali (Movimenti, Conti, Analisi, Altro).', 'tracking-tight'),
    st('titolo-2', 'text-xl', 'leading-snug', 800, 'Conto corrente', 'Schermate aperte da un\'altra, finestre e pannelli.', 'tracking-tight'),
    st('titolo-3', 'text-lg', 'leading-snug', 800, 'Budget del mese', 'Titolo di una scheda; marchio nella barra laterale.', 'tracking-tight')]},
  {'name': 'Testo', 'family': 'sans', 'styles': [
    st('corpo', 'text-md', 'leading-normal', 400, 'Gli automatici si registrano da soli.', 'Spiegazioni e messaggi.'),
    st('corpo-forte', 'text-md', 'leading-snug', 700, 'Q8 via Appia', 'Titolo di una riga, importo in un elenco, voce della barra laterale.'),
    st('campo', 'text-input', 'leading-snug', 500, 'Conad', 'Testo dentro i campi: 16 px perché il telefono non ingrandisca la pagina.'),
    st('secondario', 'text-sm', 'leading-compact', 500, 'Carburante · Bancomat', 'Seconda riga, date, didascalie, voci di ElencoVoci, in color-text-muted.'),
    st('pulsante', 'text-md', 'leading-snug', 800, 'Salva spesa', 'Etichetta dei pulsanti normali e di «Fatto»; i piccoli usano text-sm.'),
    st('pulsante-l', 'text-lg', 'leading-snug', 800, 'Registra la prima spesa', 'Pulsante grande in fondo a un pannello.')]},
  {'name': 'Etichette', 'family': 'sans', 'styles': [
    st('etichetta-campo', 'text-sm', 'leading-compact', 700, 'Descrizione', 'Nome sopra un campo, in color-text-muted.'),
    st('etichetta', 'text-xs', 'leading-compact', 800, 'USCITE', 'Titolo di un gruppo, scritto in maiuscolo con text-transform.', 'tracking-caps'),
    st('nav', 'text-2xs', 'leading-compact', 600, 'Movimenti', 'Voci della barra di navigazione (attiva: peso 800).'),
    st('badge', 'text-2xs', 'leading-compact', 700, 'non incide', 'Etichette piccole nelle righe (Automatico, non incide).'),
    st('tasto', 'text-xs', 'leading-compact', 700, 'Esc', 'Tasti delle scorciatoie.')]},
 ]}
lst = lambda rows: {'tokens': rows}
TOKENS = {'name': 'Statera', 'version': 2,
          'meta': {'source': f'Statera {APP.version}, src/styles/tokens.css (ramo main)'},
          'color': {'themes': [{'id': 'light', 'name': 'Chiaro'}, {'id': 'dark', 'name': 'Scuro'}], 'tokens': FAM['color']},
          'type': TYPE, 'spacing': lst(FAM['spacing']), 'radius': lst(FAM['radius']), 'shadow': lst(FAM['shadow']),
          'testo': lst(FAM['testo']), 'dimensioni': lst(FAM['dimensioni']), 'stati': lst(FAM['stati']), 'animazione': lst(FAM['animazione'])}
C = FAM['color']
DARK_TINT = TD.get('cat-tint', TL['cat-tint'])

# ================================================================ foglio dei componenti
CSS = r'''/* Statera — componenti di riferimento. Tutti i valori vengono da tokens.css (tokens.json):
   qui ci sono solo struttura e stati. Prefisso st-. */
.st { font-family: var(--font-sans); color: var(--color-text); font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; --st-ground: var(--color-bg); }
.st *, .st *::before, .st *::after { box-sizing: border-box; }
/* :where() tiene bassa la specificità, così le classi dei componenti e degli stili di testo vincono */
:where(.st) :where(button, input, select) { font: inherit; color: inherit; margin: 0; }
:where(.st) :where(h1, h2, h3, p) { margin: 0; }
:where(.st) :where(ul) { list-style: none; margin: 0; padding: 0; }
.st svg { display: block; flex-shrink: 0; }
.st-stage { background: var(--color-bg); padding: var(--space-5); display: flex; flex-wrap: wrap; gap: var(--space-4); align-items: center; min-height: 100%; }
.st-stage--col { flex-direction: column; align-items: stretch; }
.st-line { display: flex; flex-wrap: wrap; gap: var(--space-3); align-items: center; }
.st-stack { display: flex; flex-direction: column; gap: var(--space-2); }
.st-caption { color: var(--color-text-muted); text-transform: uppercase; }
.st-muted { color: var(--color-text-muted); }
.st-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.st :focus-visible, .st .is-focus { outline: var(--focus-width) solid var(--color-focus); outline-offset: var(--focus-offset); }

/* Pulsante */
.st-btn { height: var(--size-touch); padding: 0 var(--space-5); border: none; border-radius: var(--radius-full); display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); cursor: pointer; white-space: nowrap; text-decoration: none;
  transition: transform var(--duration-fast) var(--ease-standard), box-shadow var(--duration-fast) var(--ease-standard); }
.st-btn--l { height: var(--size-btn-l); width: 100%; padding: 0 var(--space-6); }
.st-btn--s { height: var(--size-btn-s); padding: 0 var(--space-3); font-size: var(--text-sm); }
.st-btn--primary { background: var(--color-primary); color: var(--color-on-primary); }
.st-btn--secondary { background: var(--color-surface); color: var(--color-text); }
.st-btn--tonal { background: var(--color-surface-2); color: var(--color-text); }
.st-btn--soft { background: var(--color-accent-soft); color: var(--color-accent); }
.st-btn--danger { background: var(--color-surface); color: var(--color-danger); }
.st-card .st-btn--danger { background: color-mix(in srgb, var(--color-danger) 10%, var(--color-surface)); }
.st-btn--confirm { background: var(--color-danger); color: var(--color-on-danger); }
.st-card .st-btn--secondary { background: var(--color-surface-2); }
.st-btn--link { background: transparent; color: var(--color-accent); padding: 0 var(--space-3); }
.st-card__head > .st-btn--link:last-child { margin-right: calc(-1 * var(--space-3)); }
.st-btn:hover, .st-btn.is-hover { box-shadow: inset 0 0 0 100px color-mix(in srgb, currentColor 8%, transparent); }
.st-btn:active, .st-btn.is-pressed { transform: scale(0.97); box-shadow: inset 0 0 0 100px color-mix(in srgb, currentColor 14%, transparent); }
.st-btn:disabled, .st-btn[aria-disabled="true"] { opacity: var(--opacity-disabled); cursor: not-allowed; transform: none; box-shadow: none; }
.st-iconbtn { width: var(--size-touch); height: var(--size-touch); border-radius: var(--radius-full); border: none; padding: 0; background: var(--color-surface); color: var(--color-text); display: inline-flex; align-items: center; justify-content: center; cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-standard); }
.st-iconbtn--tonal { background: var(--color-surface-2); }
.st-iconbtn:active, .st-iconbtn.is-pressed { transform: scale(0.94); }

/* Barra di navigazione (telefono) */
.st-nav { height: var(--nav-height); border-radius: var(--radius-full); background: var(--color-surface); box-shadow: var(--shadow-2); display: flex; align-items: center; padding: 0 var(--space-2); }
.st-nav__item { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 3px; text-decoration: none; color: var(--color-text-muted); }
.st-nav__item[aria-current="page"] { color: var(--color-accent); font-weight: 800; }
.st-fab { width: var(--size-fab); height: var(--size-fab); margin: -26px var(--space-2) 0; border-radius: var(--radius-full); border: 4px solid var(--color-bg); background: var(--color-primary); color: var(--color-on-primary);
  display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-fab); cursor: pointer; flex-shrink: 0; padding: 0; }

/* Barra laterale (PC) */
.st-side { width: var(--size-sidebar); background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-3); display: flex; flex-direction: column; gap: var(--space-4); box-shadow: var(--shadow-2); }
.st-side__brand { display: flex; align-items: center; gap: var(--space-2); padding: 0 var(--space-2); font-size: var(--text-lg); font-weight: 800; letter-spacing: var(--tracking-tight); }
.st-side__links { display: flex; flex-direction: column; gap: var(--space-1); }
.st-side__link { height: var(--size-touch); padding: 0 var(--space-3); border-radius: var(--radius-md); display: flex; align-items: center; gap: var(--space-3); text-decoration: none; color: var(--color-text); }
.st-side__link > span { flex: 1; }
.st-side__link:hover, .st-side__link.is-hover { background: var(--color-surface-2); }
.st-side__link[aria-current="page"] { background: var(--color-accent-soft); color: var(--color-accent); }
.st-side__status { padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); background: var(--color-bg); display: flex; align-items: center; gap: var(--space-2); color: var(--color-income); text-decoration: none; }
.st-side__status.is-off { color: var(--color-text-muted); }
.st-side__status > span { display: flex; flex-direction: column; color: var(--color-text); font-size: var(--text-sm); line-height: var(--leading-compact); }
.st-side__status small { font-size: var(--text-xs); font-weight: 500; color: var(--color-text-muted); }

/* Logo: riquadro color-primary col simbolo color-on-primary (in scuro: lilla col simbolo scuro) */
.st-logo { display: block; flex-shrink: 0; }
.st-logo__tile { fill: var(--color-primary); }
.st-logo__glyph { color: var(--color-on-primary); }
.st-wordmark { display: inline-flex; align-items: center; gap: var(--space-2); font-weight: 800; letter-spacing: var(--tracking-tight); color: var(--color-text); }

/* Azione rapida */
.st-quick { border: none; background: transparent; padding: 0; flex: 0 1 calc(var(--size-cat-l) + var(--space-7)); font-size: var(--text-sm); font-weight: 600; display: inline-flex; flex-direction: column; align-items: center; gap: var(--space-2); color: var(--color-text); cursor: pointer; }
.st-quick__circle { width: var(--size-cat-l); height: var(--size-cat-l); border-radius: var(--radius-full); background: var(--color-accent-soft); color: var(--color-accent); display: flex; align-items: center; justify-content: center;
  transition: transform var(--duration-fast) var(--ease-standard); }
.st-quick:active .st-quick__circle, .st-quick.is-pressed .st-quick__circle { transform: scale(0.94); }

/* Icona di categoria (.cat-icon dell'app): tinta al cat-tint con icona colorata (chiaro), più piena con icona cat-icon-dark (scuro) */
[data-theme="dark"] { --cat-tint: @DARK_TINT@; }
.st-cat { --cat: var(--swatch-s1); width: var(--size-cat); height: var(--size-cat); border-radius: var(--radius-full); display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: color-mix(in srgb, var(--cat) var(--cat-tint), transparent); color: var(--cat); font-weight: 800; font-size: var(--text-lg); line-height: 1; }
[data-theme="dark"] .st-cat { color: var(--cat-icon-dark); }
.st-cat--s { width: var(--size-cat-s); height: var(--size-cat-s); font-size: var(--text-sm); }
.st-cat--l { width: var(--size-cat-l); height: var(--size-cat-l); }
.st-cat--neutral, [data-theme="dark"] .st-cat--neutral { background: var(--color-accent-soft); color: var(--color-accent); }
.st-cat--s1 { --cat: var(--swatch-s1); } .st-cat--s2 { --cat: var(--swatch-s2); } .st-cat--s3 { --cat: var(--swatch-s3); } .st-cat--s4 { --cat: var(--swatch-s4); }
.st-cat--s5 { --cat: var(--swatch-s5); } .st-cat--s6 { --cat: var(--swatch-s6); } .st-cat--s7 { --cat: var(--swatch-s7); } .st-cat--s8 { --cat: var(--swatch-s8); }

/* Scelta dell'icona (IconPicker) */
.st-iconpick { display: flex; flex-direction: column; gap: var(--space-2); }
.st-iconpick__current { display: flex; align-items: center; gap: var(--space-3); }
.st-iconpick__what { flex: 1; min-width: 0; color: var(--color-text-muted); font-size: var(--text-sm); }
.st-iconpick__group { margin: var(--space-2) 0 0; font-size: var(--text-xs); font-weight: 800; letter-spacing: var(--tracking-caps); text-transform: uppercase; color: var(--color-text-muted); }
.st-iconpick__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--size-touch), 1fr)); gap: var(--space-2); }
.st-iconpick__opt { justify-self: center; display: grid; place-items: center; width: calc(var(--size-cat) + var(--space-2)); height: calc(var(--size-cat) + var(--space-2)); padding: 0; border: 0; border-radius: var(--radius-full); background: none; cursor: pointer; }
.st-iconpick__opt[aria-checked="true"] { box-shadow: 0 0 0 var(--focus-width) var(--color-text); }
.st-iconpick__opt:hover:not([aria-checked="true"]), .st-iconpick__opt.is-hover:not([aria-checked="true"]) { box-shadow: 0 0 0 var(--focus-width) var(--color-border); }

/* Riga di movimento */
.st-mrow { display: flex; align-items: center; gap: var(--space-3); min-height: var(--size-row); padding: var(--space-2) 0; }
.st-mrow__text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: var(--space-hair); }
.st-mrow__sub { color: var(--color-text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.st-mrow__end { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; white-space: nowrap; }
.st-mrow__amount.is-income { color: var(--color-income); }
.st-mrow--pc { padding: var(--space-2) var(--space-3); margin: 0 calc(-1 * var(--space-3)); border-radius: var(--radius-md); }
.st-mrow--pc:hover, .st-mrow--pc.is-hover { background: var(--color-surface-2); }
.st-day { display: flex; justify-content: space-between; color: var(--color-text-muted); margin-top: var(--space-3); }
.st-badge { height: 22px; padding: 0 var(--space-2); border-radius: var(--radius-full); background: var(--color-surface-2); color: var(--color-text-muted); display: inline-flex; align-items: center; gap: var(--space-1); align-self: flex-start; }
.st-badge--accent { background: var(--color-accent-soft); color: var(--color-accent); }

/* Scheda e riquadro */
.st-card { --st-ground: var(--color-surface); background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-3); }
.st-card__head { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2); }
.st-card--soft { --st-ground: var(--color-accent-soft); background: var(--color-accent-soft); }
/* Riquadro dell'importo principale (.balance-box dell'app) */
.st-balance { display: flex; flex-direction: column; align-items: flex-start; gap: var(--space-1); padding: var(--space-5); border-radius: var(--radius-lg); background: var(--color-primary); color: var(--color-on-primary); }
[data-theme="dark"] .st-balance { background: var(--color-accent-soft); color: var(--color-text); }
.st-balance__label { font-size: var(--text-md); font-weight: 600; }
.st-balance__amount { max-width: 100%; font-size: var(--amount-l); font-weight: 800; letter-spacing: var(--tracking-tighter); line-height: var(--leading-tight); overflow-wrap: anywhere; white-space: nowrap; }
.st-balance__pill { margin-top: var(--space-1); padding: var(--space-1) var(--space-3); border-radius: var(--radius-full); background: color-mix(in srgb, currentColor 16%, transparent); font-size: var(--text-sm); font-weight: 700; }
.st-top { display: flex; flex-direction: column; gap: var(--space-4); }
.st-top__quick { display: flex; justify-content: center; gap: var(--space-2); }
.st-top--wide { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: var(--space-5); }

/* Elenco voce/valore (.facts dell'app): voce sopra il valore sul telefono, affiancati da 600 px */
.st-facts { display: grid; grid-template-columns: minmax(0, 1fr); margin: 0; font-size: var(--text-sm); line-height: var(--leading-compact); }
.st-facts dt { color: var(--color-text-muted); }
.st-facts dd { margin: 0 0 var(--space-3); font-size: var(--text-md); overflow-wrap: anywhere; }
.st-facts dd:last-child { margin-bottom: 0; }
.st-facts--wide { grid-template-columns: minmax(0, 2fr) minmax(0, 3fr); gap: var(--space-2) var(--space-4); }
.st-facts--wide dd { margin: 0; font-size: var(--text-sm); text-align: right; }
.st-tile { flex: 1; min-width: 0; --st-ground: var(--color-surface); background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4); display: flex; align-items: center; gap: var(--space-3); }
.st-tile__icon { width: 32px; height: 32px; border-radius: var(--radius-full); display: flex; align-items: center; justify-content: center; }
.st-tile__icon--in { color: var(--color-income); background: color-mix(in srgb, var(--color-income) 16%, transparent); }
.st-tile__icon--out { color: var(--color-expense-icon); background: color-mix(in srgb, var(--color-expense-icon) 16%, transparent); }

/* Campo */
.st-field { display: flex; flex-direction: column; gap: var(--space-2); }
.st-field__label { color: var(--color-text-muted); }
.st-input { height: var(--size-field); border-radius: var(--radius-md); background: var(--color-surface); display: flex; align-items: center; gap: var(--space-2); padding: 0 var(--space-4); color: var(--color-text-muted); }
.st-input input, .st-input select { flex: 1; min-width: 0; border: none; outline: none; background: transparent; color: var(--color-text); appearance: none; }
.st-input:focus-within, .st-input.is-focus { box-shadow: 0 0 0 var(--focus-width) var(--color-focus); outline: none; }
.st-input.is-error { box-shadow: 0 0 0 var(--focus-width) var(--color-danger); }
.st-input.is-disabled { opacity: var(--opacity-disabled); }
.st-card .st-input { background: var(--color-bg); }
.st-field__help { color: var(--color-text-muted); }
.st-field__error { color: var(--color-danger); display: flex; gap: var(--space-1); align-items: flex-start; }
.st-input--search { height: 48px; border-radius: var(--radius-full); }
.st-amount { display: flex; align-items: baseline; justify-content: center; gap: var(--space-1); }
.st-amount input { width: 5.2ch; border: none; outline: none; background: transparent; text-align: right; color: var(--color-text); }
.st-amount__cur { color: var(--color-text-muted); font-size: 34px; font-weight: 800; }

/* Segmentato */
.st-seg { display: flex; gap: var(--space-1); padding: var(--space-1); background: var(--color-surface-2); border-radius: var(--radius-full); }
.st-seg__opt { flex: 1; height: var(--size-btn-s); border: none; border-radius: var(--radius-full); background: transparent; color: var(--color-text-muted); cursor: pointer; padding: 0 var(--space-3);
  transition: background-color var(--duration-base) var(--ease-standard); }
.st-seg__opt { font-weight: 700; }
.st-seg__opt[aria-checked="true"], .st-seg__opt[aria-pressed="true"] { background: var(--color-primary); color: var(--color-on-primary); font-weight: 800; }

/* Chip */
.st-chip { height: var(--size-btn-s); padding: 0 var(--space-3); border: none; border-radius: var(--radius-full); background: var(--color-surface); color: var(--color-text); display: inline-flex; align-items: center; gap: 6px; cursor: pointer; white-space: nowrap; }
.st-chip--tonal { background: var(--color-surface-2); }
.st-chip[aria-pressed="true"] { background: var(--color-accent-soft); color: var(--color-accent); }

/* Interruttore, casella, scelta */
.st-switch { width: 52px; height: 32px; border-radius: var(--radius-full); border: none; padding: 3px; background: var(--color-text-muted); display: inline-flex; align-items: center; cursor: pointer; flex-shrink: 0;
  transition: background-color var(--duration-base) var(--ease-standard); }
.st-switch__knob { width: 26px; height: 26px; border-radius: var(--radius-full); background: var(--color-surface); box-shadow: var(--shadow-1); display: flex; align-items: center; justify-content: center; color: var(--color-primary);
  transition: transform var(--duration-base) var(--ease-standard); }
.st-switch__knob svg { opacity: 0; }
.st-switch[aria-checked="true"] { background: var(--color-primary); }
.st-switch[aria-checked="true"] .st-switch__knob { transform: translateX(20px); background: var(--color-on-primary); }
.st-switch[aria-checked="true"] .st-switch__knob svg { opacity: 1; }
.st-check { display: inline-flex; align-items: center; gap: var(--space-3); cursor: pointer; position: relative; }
.st-check input, .st-option input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.st-check__box { width: 24px; height: 24px; border-radius: var(--radius-xs); border: 2px solid var(--color-text-muted); display: flex; align-items: center; justify-content: center; color: transparent; flex-shrink: 0; }
.st-check input:checked + .st-check__box { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary); }
.st-check input:focus-visible + .st-check__box { outline: var(--focus-width) solid var(--color-focus); outline-offset: var(--focus-offset); }
.st-option { position: relative; display: flex; gap: var(--space-3); align-items: flex-start; padding: var(--space-4); border-radius: var(--radius-lg); background: var(--color-surface); cursor: pointer; }
.st-option:has(input:checked) { box-shadow: inset 0 0 0 2px var(--color-primary); }
.st-option:has(input:focus-visible) { outline: var(--focus-width) solid var(--color-focus); outline-offset: var(--focus-offset); }
.st-option__dot { width: 24px; height: 24px; border-radius: var(--radius-full); border: 2px solid var(--color-text-muted); flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.st-option:has(input:checked) .st-option__dot { border-color: var(--color-primary); }
.st-option:has(input:checked) .st-option__dot::after { content: ""; width: 12px; height: 12px; border-radius: var(--radius-full); background: var(--color-primary); }

/* Avanzamento: budget, obiettivi */
.st-bar { height: 8px; border-radius: var(--radius-full); background: var(--chart-track); overflow: hidden; display: block; }
.st-bar__fill { display: block; height: 100%; border-radius: inherit; background: var(--color-primary); }
.st-bar__fill.is-warning { background: var(--status-warning); }
.st-bar__fill.is-critical { background: var(--status-critical); }
.st-budget { display: flex; flex-direction: column; gap: var(--space-2); }
.st-budget__head { display: flex; justify-content: space-between; align-items: baseline; gap: var(--space-2); }
.st-budget__state { display: flex; align-items: center; gap: var(--space-1); color: var(--color-text-muted); }
.st-budget__state .ok { color: var(--color-income); }
.st-budget__state .over { color: var(--color-danger); }
.st-ring { position: relative; width: 60px; height: 60px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.st-ring svg { position: absolute; inset: 0; transform: rotate(-90deg); }
.st-ring .track { stroke: var(--chart-track); }
.st-ring .fill { stroke: var(--cat, var(--color-primary)); }

/* Avvisi */
.st-toast { background: var(--toast-bg); color: var(--toast-text); border-radius: var(--radius-md); min-height: var(--size-field); padding: var(--space-2) var(--space-2) var(--space-2) var(--space-4); display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); box-shadow: var(--shadow-2); font-size: var(--text-sm); font-weight: 600; max-width: 480px; }
.st-toast__action { height: var(--size-btn-s); padding: 0 var(--space-3); border: none; border-radius: var(--radius-full); background: transparent; color: var(--toast-action); font-size: var(--text-sm); font-weight: 800; cursor: pointer; }
.st-banner { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); background: var(--color-accent-soft); color: var(--color-text); font-size: var(--text-sm); font-weight: 500; }
.st-banner > span { overflow-wrap: anywhere; }
.st-banner--update { border: 1px solid var(--color-border); }
.st-banner--error { background: color-mix(in srgb, var(--color-danger) 12%, var(--color-bg)); }
.st-errorbox { padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); background: color-mix(in srgb, var(--color-danger) 12%, var(--color-bg)); color: var(--color-text); font-size: var(--text-sm); font-weight: 600; }

/* Pannello, finestra, conferma */
.st-layer { position: relative; overflow: hidden; border-radius: var(--radius-lg); background: var(--color-bg); }
.st-backdrop { position: absolute; inset: 0; background: var(--color-backdrop); }
.st-sheet { position: relative; background: var(--color-bg); border-radius: var(--radius-xl) var(--radius-xl) 0 0; padding: var(--space-3) var(--space-5) var(--space-5); box-shadow: var(--shadow-3); display: flex; flex-direction: column; gap: var(--space-4); }
.st-sheet__grip { align-self: center; width: 40px; height: 4px; border-radius: var(--radius-full); background: var(--color-border); }
.st-dialog { position: relative; width: 100%; max-width: var(--content-max); background: var(--color-bg); border-radius: var(--radius-xl); padding: var(--space-5) var(--space-6) var(--space-6); box-shadow: var(--shadow-3); display: flex; flex-direction: column; gap: var(--space-4); }
.st-dialog__head { display: flex; align-items: center; gap: var(--space-3); }
.st-dialog__head h2 { flex: 1; }
.st-dialog__foot { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-3); padding-top: var(--space-3); border-top: 1px solid var(--color-border); }
.st-danger-icon { width: 64px; height: 64px; border-radius: var(--radius-full); background: color-mix(in srgb, var(--color-danger) 14%, transparent); color: var(--color-danger); display: flex; align-items: center; justify-content: center; align-self: center; }

/* Tasto */
.st-kbd { min-width: 24px; height: 24px; padding: 0 6px; border-radius: var(--radius-xs); background: var(--color-surface-2); color: var(--color-text-muted); border: 1px solid var(--color-border); display: inline-flex; align-items: center; justify-content: center; font-family: inherit; }
.st-kbd--on-primary { background: color-mix(in srgb, var(--color-on-primary) 18%, transparent); color: var(--color-on-primary); border-color: transparent; }

/* Grafico a colonne */
.st-chart { display: flex; flex-direction: column; gap: var(--space-3); }
.st-chart__legend { display: flex; flex-wrap: wrap; gap: var(--space-4); color: var(--color-text-muted); }
.st-chart__legend span { display: inline-flex; align-items: center; gap: 6px; }
.st-chart__key { width: 10px; height: 10px; border-radius: var(--radius-2xs); }
.st-chart__plot { display: flex; gap: var(--space-1); align-items: flex-end; border-bottom: 1px solid var(--chart-grid); }
.st-chart__month { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; color: var(--color-text-muted); font-size: var(--text-2xs); }
.st-chart__bars { display: flex; align-items: flex-end; gap: 3px; height: 100px; }
.st-chart__bar { width: 12px; border-radius: var(--radius-2xs) var(--radius-2xs) 0 0; }
.st-in { background: var(--chart-income); } .st-out { background: var(--chart-expense); }

/* Stato vuoto */
.st-empty { background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-7) var(--space-5); display: flex; flex-direction: column; align-items: center; gap: var(--space-2); text-align: center; }
.st-empty__icon { width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--color-accent-soft); color: var(--color-accent); display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-1); }
.st-empty p { color: var(--color-text-muted); max-width: 32ch; }

/* Tastierino degli importi (Keypad dell'app): 4 colonne, operazioni in tenue, «Fatto» in color-primary */
.st-keypad { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--space-2); padding: var(--space-3) var(--space-5); background: var(--color-bg); border-top: 1px solid var(--color-border); user-select: none; }
.st-keypad--floating { border-top: none; border-radius: var(--radius-xl) var(--radius-xl) 0 0; box-shadow: var(--shadow-3); }
.st-key { display: grid; place-items: center; height: var(--size-key); padding: 0; border: 0; border-radius: var(--radius-md); background: var(--color-surface); color: var(--color-text); font-size: var(--text-xl); font-weight: 700; cursor: pointer;
  transition: background-color var(--duration-fast) var(--ease-standard); }
.st-key:active, .st-key.is-pressed { background: var(--color-surface-2); }
.st-key--op { background: var(--color-accent-soft); color: var(--color-accent); }
.st-key--done { background: var(--color-primary); color: var(--color-on-primary); font-size: var(--text-md); font-weight: 800; }
.st-key--off { visibility: hidden; }

@media (prefers-reduced-motion: reduce) {
  .st *, .st *::before, .st *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
}
'''

# ================================================================ componenti: (nome, gruppo, altezza, readme, anteprima)
COMP = []
def comp(name, group, height, readme, body):
    COMP.append((name, group, height, readme, body))

def card_txt(t): return f'<span class="etichetta st-caption">{t}</span>'

# --- Pulsante
comp('Pulsante', 'Azioni', 470, f'''Il comando a pillola: principale, secondario, tenue, di pericolo o come link.

## Quando usarlo
- **Principale** (`st-btn--primary`): l'azione che chiude il compito, una sola per schermata o pannello (Salva spesa, Continua).
- **Secondario** (`st-btn--secondary` su color-bg, `st-btn--tonal` dentro una scheda): alternative (Salva e aggiungine un'altra, Salta).
- **Tenue** (`st-btn--soft`): azioni utili ma non urgenti dentro i contenuti (Esporta CSV, Aggiungi una spesa).
- **Pericolo** (`st-btn--danger`): «Elimina» scritto in color-danger; dentro una scheda diventa una pillola rosata (color-danger al 10% sulla superficie), così si vede che è un pulsante e resta allineato al testo. Pieno (`st-btn--confirm`, color-danger con color-on-danger) solo nella conferma di una cancellazione, mai come primo pulsante di una schermata.
- **Link** (`st-btn--link`): azioni di poco peso (Lo faccio dopo, Ordina, Imposta budget). A fine riga di un'intestazione è allineato al bordo il testo, non la pillola invisibile intorno.
- Dentro una scheda i pulsanti secondari passano a color-surface-2.

## Struttura
`<button type="button" class="st-btn st-btn--primary pulsante">` con un'icona Lucide facoltativa a sinistra (18 px) e il testo. Grande: `st-btn--l` con `pulsante-l`, a tutta larghezza in fondo a un pannello. Piccolo: `st-btn--s` (`size-btn-s`, testo `text-sm`), dentro righe, schede e avvisi. Nell'app: `.btn`, `.btn-primary`, `.btn-soft`, `.btn-ghost`, `.btn-danger` (`.confirm` per il pieno), `.btn-small`, `.btn-large` in `base.css`.

## Stati
Passaggio del puntatore: velo del colore del testo all'8%. Premuto: scala 0,97 e velo al 14% per `duration-fast`. Focus da tastiera: anello `focus-width` in `color-focus` staccato di `focus-offset`. Disattivato: `opacity-disabled`, nessun velo, `cursor: not-allowed`; spiega accanto perché non si può.

## Testi
Verbo all'infinito o all'imperativo con l'oggetto: «Salva spesa», «Registra», «Esporta CSV». Mai «OK» o «Conferma» da soli.
''', f'''<div class="st st-stage st-stage--col" style="gap: var(--space-4)">
<div class="st-line">
<button type="button" class="st-btn st-btn--primary pulsante">{ic('u-check', 18, 2.2)}Salva spesa</button>
<button type="button" class="st-btn st-btn--secondary pulsante">Salva e aggiungine un’altra</button>
<button type="button" class="st-btn st-btn--soft pulsante">{ic('u-download', 18, 2.2)}Esporta CSV</button>
<button type="button" class="st-btn st-btn--danger pulsante">{ic('u-trash', 18, 2.2)}Elimina</button>
<button type="button" class="st-btn st-btn--link pulsante">Lo faccio dopo</button></div>
<div class="st-line"><section class="st-card" style="width: 340px"><div class="st-card__head"><h2 class="titolo-3">Carta Bancomat</h2><button type="button" class="st-btn st-btn--link st-btn--s pulsante">Modifica</button></div>
<div class="st-line"><button type="button" class="st-btn st-btn--secondary pulsante">Archivia</button><button type="button" class="st-btn st-btn--danger pulsante">Elimina</button></div></section>
<span class="st-stack">{card_txt('Conferma')}<button type="button" class="st-btn st-btn--confirm pulsante">{ic('u-trash', 18, 2.2)}Elimina</button></span></div>
<div class="st-line">
<span class="st-stack">{card_txt('Passaggio')}<button type="button" class="st-btn st-btn--primary pulsante is-hover">Registra</button></span>
<span class="st-stack">{card_txt('Premuto')}<button type="button" class="st-btn st-btn--primary pulsante is-pressed">Registra</button></span>
<span class="st-stack">{card_txt('Focus')}<button type="button" class="st-btn st-btn--primary pulsante is-focus">Registra</button></span>
<span class="st-stack">{card_txt('Disattivato')}<button type="button" class="st-btn st-btn--primary pulsante" disabled>Registra</button></span>
<span class="st-stack">{card_txt('Piccolo')}<button type="button" class="st-btn st-btn--s st-btn--primary pulsante">{ic('u-check', 16, 2.2)}Registra</button></span></div>
<div style="max-width: 350px"><button type="button" class="st-btn st-btn--l st-btn--primary pulsante-l">Registra la prima spesa</button></div></div>''')

# --- PulsanteIcona
comp('PulsanteIcona', 'Azioni', 140, '''Un'icona dentro un cerchio di 44 px, per comandi che tutti riconoscono (Indietro, Cerca, Chiudi, Altre azioni).

## Struttura
`<button type="button" class="st-iconbtn" aria-label="Indietro">` con un'icona Lucide da 20 px. `aria-label` è obbligatorio: dice cosa fa, non come è disegnato. Su PC aggiungi la scorciatoia nell'etichetta («Chiudi (Esc)»). Su color-surface usa `st-iconbtn--tonal`.

## Da evitare
Icone senza un significato universale: in quel caso usa un Pulsante con il testo.
''', f'''<div class="st st-stage">
<button type="button" class="st-iconbtn" aria-label="Indietro">{ic('u-chevL')}</button>
<button type="button" class="st-iconbtn" aria-label="Cerca">{ic('u-search')}</button>
<button type="button" class="st-iconbtn" aria-label="Chiudi">{ic('u-x')}</button>
<button type="button" class="st-iconbtn" aria-label="Altre azioni">{ic('u-more')}</button>
<button type="button" class="st-iconbtn is-focus" aria-label="Calendario del mese">{ic('u-cal')}</button>
<span class="st-card" style="flex-direction: row; padding: var(--space-3)"><button type="button" class="st-iconbtn st-iconbtn--tonal" aria-label="Modifica">{ic('u-pen')}</button><button type="button" class="st-iconbtn st-iconbtn--tonal" aria-label="Elimina">{ic('u-trash')}</button></span></div>''')

# --- AzioneRapida
comp('AzioneRapida', 'Azioni', 150, '''Un cerchio tenue con etichetta sotto, per le azioni più frequenti accanto al RiquadroImporto.

## Quando usarla
In fila da tre, con il riquadro dell'importo: Spesa, Entrata, Trasferisci in Movimenti (i Preferiti restano nella loro barra). Sul telefono le azioni stanno sotto il riquadro, centrate; da 600 px in su accanto al riquadro, a destra.

## Struttura
`<button class="st-quick" aria-label="Nuova spesa">` con dentro `st-quick__circle` (`size-cat-l`, color-accent-soft, icona in color-accent a 22 px) e il testo in `text-sm`, peso 600. Icone: `arrow-up-right` (Spesa), `arrow-down-left` (Entrata), `arrow-left-right` (Trasferisci).

## Stati
Premuto: il cerchio scala a 0,94. Focus: anello sul pulsante intero.
''', f'''<div class="st st-stage" style="justify-content: center">
<div class="st-top__quick" style="width: 350px">
<button type="button" class="st-quick" aria-label="Nuova spesa"><span class="st-quick__circle">{ai('arrow-up-right', 22)}</span>Spesa</button>
<button type="button" class="st-quick" aria-label="Nuova entrata"><span class="st-quick__circle">{ai('arrow-down-left', 22)}</span>Entrata</button>
<button type="button" class="st-quick is-pressed" aria-label="Nuovo trasferimento"><span class="st-quick__circle">{ai('arrow-left-right', 22)}</span>Trasferisci</button></div></div>''')

# --- BarraNavigazione
nav_items = [('u-list', 'Movimenti', True), ('u-wallet', 'Conti', False), None, ('u-chart', 'Analisi', False), ('u-more', 'Altro', False)]
nav = ''.join('<button type="button" class="st-fab" aria-label="Nuovo movimento">' + ic('u-plus', 26, 2.4) + '</button>' if it is None else
              f'<a href="#" class="st-nav__item nav"{" aria-current=\"page\"" if it[2] else ""}>{ic(it[0], 22, 2.1 if it[2] else 1.8)}{it[1]}</a>' for it in nav_items)
comp('BarraNavigazione', 'Navigazione', 170, '''La barra flottante del telefono: quattro sezioni e il pulsante + al centro.

## Struttura
`<nav aria-label="Sezioni" class="st-nav">` a `space-3` dai bordi e `space-4` dal fondo, alta `nav-height`, con `shadow-2`. Voci: `<a class="st-nav__item nav">` con icona da 22 px; la sezione corrente ha `aria-current="page"` (color-accent, peso 800, tratto 2,2). Al centro `st-fab`: 56 px, color-primary, bordo di 4 px in color-bg, `shadow-fab`, `aria-label="Nuovo movimento"`.

## Regole
- Compare solo nelle quattro sezioni principali. Le schermate aperte da un'altra (dettaglio conto, Cerca, Ricorrenti, Categorie) hanno la freccia indietro e niente barra.
- Il contenuto scorre sotto la barra: lascia libero in fondo `nav-height` + `space-4` + `space-8`.
- Il + ha `data-no-autoauth` nell'app: apre il modulo del movimento senza rinnovare prima l'accesso a Google.
- Da 900 px la sostituisce la BarraLaterale.
''', f'''<div class="st st-stage" style="justify-content: center; padding-top: var(--space-7)"><nav aria-label="Sezioni" class="st-nav" style="width: 366px">{nav}</nav></div>''')

# --- BarraLaterale
side_links = [('list', 'Movimenti', True), ('wallet', 'Conti', False), ('chart-column', 'Analisi', False), ('ellipsis', 'Altro', False), ('search', 'Cerca', False)]
sl = ''.join(f'<a href="#" class="st-side__link corpo-forte{" is-hover" if lab == "Conti" else ""}"{" aria-current=\"page\"" if on else ""}{" aria-keyshortcuts=\"/\" title=\"Scorciatoia: tasto /\"" if lab == "Cerca" else ""}>{ai(i, 22, 2.2 if on else 1.8)}<span>{lab}</span></a>' for i, lab, on in side_links)
comp('BarraLaterale', 'Navigazione', 560, '''La navigazione su PC: logo, «Nuovo movimento», sezioni, Cerca e stato della sincronizzazione.

## Struttura
`<nav aria-label="Sezioni" class="st-side">` largo `size-sidebar`, color-surface, `radius-lg`, `shadow-2`, a tutta altezza (fissa mentre il contenuto scorre). Dentro, dall'alto:
- il marchio: Logo a 36 px e «Statera» in `text-lg`, peso 800, `tracking-tight`;
- il Pulsante principale «Nuovo movimento» con il +, allineato a sinistra;
- le voci `st-side__link` (Movimenti, Conti, Analisi, Altro, poi Cerca), icone da 22 px, la corrente con `aria-current="page"` (color-accent-soft e color-accent);
- in fondo lo stato della sincronizzazione (`st-side__status`, color-bg): icona `cloud-check` in color-income, «Sincronizzato» e «Google Drive, cifrato»; senza sincronizzazione `smartphone` in color-text-muted, «Solo su questo dispositivo». Porta ad Altro.

## Regole
- Niente lettere delle scorciatoie scritte sulle voci: N e / funzionano ancora e sono nel suggerimento al passaggio del puntatore («Scorciatoia: tasto N») e in `aria-keyshortcuts`.
- Compare da 900 px; sotto, la BarraNavigazione flottante.
''', f'''<div class="st st-stage"><nav aria-label="Sezioni" class="st-side" style="min-height: 520px">
<div class="st-side__brand">{APP.logo_svg(36)}<span>Statera</span></div>
<button type="button" class="st-btn st-btn--primary pulsante" aria-keyshortcuts="N" title="Scorciatoia: tasto N" style="justify-content: flex-start; padding: 0 var(--space-4)">{ai('plus', 20, 2.4)}<span style="flex: 1; text-align: left">Nuovo movimento</span></button>
<div class="st-side__links">{sl}</div>
<span style="flex: 1"></span>
<a href="#" class="st-side__status">{ai('cloud-check', 20)}<span><b>Sincronizzato</b><small>Google Drive, cifrato</small></span></a></nav>
<nav aria-label="Sezioni, senza sincronizzazione" class="st-side" style="min-height: 0; align-self: flex-end"><a href="#" class="st-side__status is-off">{ai('smartphone', 20)}<span><b>Solo su questo dispositivo</b><small>Sincronizzazione non attiva</small></span></a></nav></div>''')

# --- IconaCategoria
cats = [('shopping-cart', 's1'), ('utensils', 's2'), ('fuel', 's3'), ('bus', 's4'), ('heart-pulse', 's5'), ('house', 's6'), ('zap', 's7'), ('sprout', 's8')]
cat_row = lambda size, ipx: ''.join(f'<span class="st-cat{size} st-cat--{c}" aria-hidden="true">{ai(n, ipx) if n in APP.icons else ai("tag", ipx)}</span>' for n, c in cats)
comp('IconaCategoria', 'Contenuti', 300, f'''Il cerchio colorato che identifica una categoria o un conto: icona Lucide sulla sua tinta.

## Regole di colore
- Tema chiaro: fondo = tinta (`swatch-s1`…`swatch-s8`) al `cat-tint` ({TL['cat-tint']}), icona nella tinta piena: da {f1(min(cr(V(f'swatch-s{i}'), _mix(V(f'swatch-s{i}'), V('color-surface'), TL['cat-tint'])) for i in range(1, 9)))}:1 a {f1(max(cr(V(f'swatch-s{i}'), _mix(V(f'swatch-s{i}'), V('color-surface'), TL['cat-tint'])) for i in range(1, 9)))}:1 su bianco.
- Tema scuro: fondo = tinta al {DARK_TINT}, icona `cat-icon-dark` (bianca): almeno {f1(min(cr(V('cat-icon-dark', 'dark'), _mix(V(f'swatch-s{i}'), V('color-surface', 'dark'), DARK_TINT)) for i in range(1, 9)))}:1. Provata anche l'icona colorata su cerchio tenue: meno leggibile.
- Senza tinta (trasferimento, conti senza colore): `st-cat--neutral`, color-accent-soft con color-accent.
- Scelta in un elenco di icone: vedi SceltaIcona.

## Struttura
`<span class="st-cat st-cat--s2" aria-hidden="true">` con l'icona a 20 px (`size-cat`, 44 px), 22 px in `st-cat--l` (`size-cat-l`, 52 px), 16 px in `st-cat--s` (`size-cat-s`, 32 px). Nell'app: `.cat-icon` in `base.css` e il componente `CategoryIcon`. Il nome della categoria sta sempre accanto, in testo: il cerchio è decorativo.

## Icona
- Il colore arriva dalla chiave salvata (`s1`…`s8`), l'icona dalla chiave del campo `icon` (vedi Iconografia).
- Campo assente: icona automatica, dall'id delle categorie iniziali e poi **in base al nome** («Palestra» → manubrio, «Farmacia» → pillola); se non si trova, l'iniziale del nome (`text-lg`, peso 800).
- `null` (scelta «Nessuna»): l'iniziale.
''', f'''<div class="st st-stage st-stage--col">
<div class="st-line">{cat_row(' st-cat--l', 22)}</div>
<div class="st-line">{cat_row('', 20)}</div>
<div class="st-line">{cat_row(' st-cat--s', 16)}</div>
<div class="st-line"><span class="st-cat st-cat--s7" aria-hidden="true">O</span><span class="st-cat st-cat--neutral" aria-hidden="true">{ai('arrow-left-right')}</span><span class="st-cat st-cat--s3" aria-hidden="true">{ai('landmark')}</span><span class="st-cat st-cat--s2" aria-hidden="true">{ai('ticket')}</span><span class="st-cat st-cat--s6 st-cat--s" aria-hidden="true">P</span></div></div>''')

# --- RigaMovimento
rows = [('spesa', 's1', 'Conad', 'Spesa alimentare · Bancomat', '−42,30 €', False, None, False),
        ('stipendio', 's6', 'Stipendio ottobre', 'Stipendio · Conto corrente', '+1.850,00 €', True, None, False),
        ('bollette', 's3', 'Bolletta luce e gas', 'Casa › Bollette', '−96,00 €', False, 'non incide', False)]
rr = ''.join(f'<li class="st-mrow"><span class="st-cat st-cat--{s}" aria-hidden="true">{ic(k)}</span><span class="st-mrow__text"><span class="corpo-forte">{d}</span><span class="st-mrow__sub secondario">{sub}</span></span>'
             f'<span class="st-mrow__end"><span class="st-mrow__amount corpo-forte{" is-income" if inc else ""}">{a}</span>{"<span class=\"st-badge badge\">" + ic("u-tag", 12, 2.2) + b + "</span>" if b else ""}</span></li>' for k, s, d, sub, a, inc, b, _ in rows)
comp('RigaMovimento', 'Contenuti', 400, '''Una riga di un elenco di movimenti: icona della categoria, descrizione, categoria · fonte, importo.

## Struttura
`<li class="st-mrow">`: IconaCategoria, poi `st-mrow__text` con la descrizione in `corpo-forte` e la riga «Categoria · Conto o carta» in `secondario`, poi l'importo in `corpo-forte`. Le righe sono raggruppate per giorno sotto un'intestazione `st-day` (giorno a sinistra, saldo del giorno a destra, `secondario`).

## Importi
- Formato italiano con il punto delle migliaia: «1.234,56 €». Il meno è il segno tipografico «−» (U+2212), il più «+» solo per le entrate.
- Uscite in color-text, entrate in color-income con `is-income`. Il colore non è mai l'unico segnale: c'è sempre il segno.
- Nel dettaglio di un conto, sotto l'importo, il saldo dopo il movimento («saldo 6.940,55 €») oppure il Badge «non incide» se il movimento è prima del saldo iniziale.

## PC
Con `st-mrow--pc` la riga ha una colonna per la fonte e, al passaggio del puntatore, fondo color-surface-2 con i pulsanti Modifica ed Elimina.
''', f'''<div class="st st-stage st-stage--col"><div class="st-card" style="max-width: 390px; padding-top: var(--space-2)">
<h3 class="st-day secondario" style="font-weight: 600"><span>Sabato 14 novembre</span><span>−42,30 €</span></h3><ul>{rr}</ul></div>
<div class="st-card" style="max-width: 640px; padding-top: var(--space-2); padding-bottom: var(--space-3)"><ul><li class="st-mrow st-mrow--pc is-hover"><span class="st-cat st-cat--s3" aria-hidden="true">{ic('carburante')}</span><span class="st-mrow__text"><span class="corpo-forte">Q8 via Appia</span><span class="st-mrow__sub secondario">Carburante</span></span><span class="secondario st-muted" style="width: 140px">Bancomat</span><span class="st-line" style="gap: var(--space-1)"><button type="button" class="st-iconbtn" aria-label="Modifica">{ic('u-pen', 18)}</button><button type="button" class="st-iconbtn" aria-label="Elimina">{ic('u-trash', 18)}</button></span><span class="corpo-forte" style="width: 100px; text-align: right">−50,00 €</span></li></ul></div></div>''')

# --- Scheda
comp('Scheda', 'Contenuti', 360, '''Il contenitore di ogni gruppo di contenuti: color-surface, `radius-lg`, interno `space-5`, senza bordo né ombra.

## Varianti
- `st-card`: schede delle sezioni, con il titolo in `titolo-3` a sinistra e un'azione piccola a destra (`st-card__head`).
- `st-card--soft`: color-accent-soft, per ciò che chiede un'azione (Da registrare).
- L'importo principale di una schermata non sta in una scheda: vedi RiquadroImporto.
- `st-tile`: i riquadri Entrate e Uscite, con l'icona nel suo cerchio.

## Regole
Una schermata alterna schede e spazi `space-4`: niente schede dentro schede, niente bordi colorati su un lato.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 330px"><div class="st-card__head"><h2 class="titolo-3">Obiettivi di risparmio</h2><button type="button" class="st-btn st-btn--s st-btn--soft pulsante">{ic('u-plus', 16, 2.2)}Nuovo</button></div><p class="corpo st-muted">Una vacanza, un fondo per gli imprevisti.</p></section>
<div class="st-line" style="width: 330px; flex-wrap: nowrap; gap: var(--space-2)"><div class="st-tile"><span class="st-tile__icon st-tile__icon--in">{ic('u-in', 18, 2.2)}</span><span class="st-stack" style="gap: 0"><span class="secondario st-muted">Entrate</span><span class="corpo-forte" style="font-size: var(--text-lg); font-weight: 800; white-space: nowrap">2.010,00 €</span></span></div><div class="st-tile"><span class="st-tile__icon st-tile__icon--out">{ic('u-out', 18, 2.2)}</span><span class="st-stack" style="gap: 0"><span class="secondario st-muted">Uscite</span><span class="corpo-forte" style="font-size: var(--text-lg); font-weight: 800; white-space: nowrap">684,35 €</span></span></div></div></div>''')

# --- Campo
comp('Campo', 'Moduli', 520, '''Campi dei moduli: testo, importo grande, scelta, ricerca. Etichetta sopra, aiuto o errore sotto.

## Struttura
`<label class="st-field">` con `st-field__label` (`etichetta-campo`), poi `st-input` (alto `size-field`, color-surface, `radius-md`) con l'icona a sinistra e `<input>` in `campo`. L'importo di Nuova spesa è `st-amount` con `importo-xl` e il simbolo € in color-text-muted. La ricerca è `st-input--search`, a pillola.

## Stati
- Focus: anello di `focus-width` in color-focus intorno al campo.
- Errore: anello in color-danger e, sotto, il messaggio con l'icona di avviso: cosa non va e come rimediare («Scrivi un importo maggiore di zero»). L'errore di salvataggio va accanto ai pulsanti.
- Disattivato: `opacity-disabled`, con il motivo scritto.

## Regole
I moduli hanno `novalidate`: la validazione è nostra e i messaggi sono in italiano. Il campo importo accetta calcoli («12,50+3,20») e mostra la tastiera numerica con il pulsante +.
''', f'''<div class="st st-stage st-stage--col" style="max-width: 420px">
<div class="st-amount"><input type="text" value="42,30" readonly aria-label="Importo" class="importo-xl"><span class="st-amount__cur">€</span></div>
<label class="st-field"><span class="st-field__label etichetta-campo">Descrizione</span><span class="st-input is-focus">{ic('u-pen', 18)}<input type="text" value="Conad" readonly class="campo"></span></label>
<label class="st-field"><span class="st-field__label etichetta-campo">Con</span><span class="st-input">{ic('c-carta', 18)}<select class="campo" style="font-weight: 700"><option>Bancomat · Conto corrente</option></select>{ic('u-chevD', 18)}</span></label>
<label class="st-field"><span class="st-field__label etichetta-campo">Saldo di oggi</span><span class="st-input is-error"><input type="text" value="0,00 €" readonly class="campo"></span><span class="st-field__error secondario">{ic('u-alert', 16, 2.2)}Scrivi un importo maggiore di zero.</span></label>
<label class="st-input st-input--search">{ic('u-search', 18)}<span class="st-sr">Cerca</span><input type="text" placeholder="Cerca movimenti" readonly class="campo"><kbd class="st-kbd tasto">/</kbd></label></div>''')

# --- Segmentato
comp('Segmentato', 'Moduli', 170, '''Due o tre scelte che si escludono, dentro una pillola: tipo di movimento, Mese o Anno, Uscite o Entrate.

## Struttura
`<div role="radiogroup" aria-label="…" class="st-seg">` con un `<button role="radio" aria-checked class="st-seg__opt">` per opzione (componente `Segmented` dell'app). L'opzione scelta è color-primary con color-on-primary, peso 800; le altre color-text-muted su color-surface-2, peso 700. Il cambio dura `duration-base`. La scelta del tema è un Segmentato: vedi SceltaTema.

## Regole
Al massimo tre opzioni, con parole brevi («Trasf.» se lo spazio manca). Per più scelte usa i Chip.
''', f'''<div class="st st-stage st-stage--col" style="max-width: 380px">
<div role="radiogroup" aria-label="Tipo di movimento" class="st-seg"><button type="button" role="radio" class="st-seg__opt" aria-checked="true">Uscita</button><button type="button" role="radio" class="st-seg__opt" aria-checked="false">Entrata</button><button type="button" role="radio" class="st-seg__opt" aria-checked="false">Trasferimento</button></div>
<div role="radiogroup" aria-label="Periodo" class="st-seg" style="width: 200px"><button type="button" role="radio" class="st-seg__opt" aria-checked="false">Mese</button><button type="button" role="radio" class="st-seg__opt is-focus" aria-checked="true">Anno</button></div></div>''')

# --- Chip
comp('Chip', 'Moduli', 170, '''Pillole piccole per filtri e scelte rapide: tipo, periodo, conto, categoria, Oggi / Ieri.

## Struttura
`<button class="st-chip secondario" aria-pressed>` alto `size-btn-s`, testo a 13 px peso 700. Attivo: color-accent-soft con color-accent. Un filtro attivo si toglie con la ✕ (`aria-label="Pasti fuori, togli il filtro"`); un menu ha la freccia in giù. Dentro una scheda usa `st-chip--tonal`.

## Regole
Vanno a capo, non scorrono di lato. Il chip scelto si riconosce anche dall'icona (spunta o ✕), non solo dal colore.
''', f'''<div class="st st-stage">
<button type="button" class="st-chip secondario" aria-pressed="true" style="font-weight: 700">{ic('u-check', 15, 2.2)}Uscite</button>
<button type="button" class="st-chip secondario" aria-pressed="true" style="font-weight: 700">Ultimi 3 mesi{ic('u-chevD', 15, 2.2)}</button>
<button type="button" class="st-chip secondario" aria-pressed="true" aria-label="Pasti fuori, togli il filtro" style="font-weight: 700">Pasti fuori{ic('u-x', 14, 2.4)}</button>
<button type="button" class="st-chip secondario" aria-pressed="false" style="font-weight: 700">Tutti i conti{ic('u-chevD', 15, 2.2)}</button>
<button type="button" class="st-chip secondario" aria-pressed="false" style="font-weight: 700">{ic('u-cal', 15, 2.1)}Ieri</button></div>''')

# --- Interruttore
comp('Interruttore', 'Moduli', 330, '''Interruttore, casella di spunta e scelta a schede.

## Interruttore
`<button role="switch" aria-checked class="st-switch">` (52 × 32) con `st-switch__knob`. Acceso: binario color-primary, pomello color-on-primary con la spunta; spento: binario color-text-muted, pomello color-surface. Lo stato si legge anche dalla posizione e dalla spunta. Va a destra di una riga con il nome dell'impostazione (Blocca con PIN).

## Casella
`<label class="st-check">` con `<input type="checkbox">` nascosto e `st-check__box` (24 px, `radius-xs`). Per scelte indipendenti (Salva anche tra i preferiti, i conti della guida).

## Scelta a schede
`<label class="st-option">` con `<input type="radio">`, icona, titolo, spiegazione e il pallino a destra; la scelta ha il bordo interno di 2 px in color-primary. Per decisioni con conseguenze da spiegare (dove tenere i dati).
''', f'''<div class="st st-stage st-stage--col" style="max-width: 420px">
<div class="st-card" style="gap: var(--space-2)"><div class="st-line" style="flex-wrap: nowrap"><span class="corpo-forte" style="flex: 1">Blocca con PIN</span><button type="button" role="switch" aria-checked="true" aria-label="Blocca con PIN" class="st-switch"><span class="st-switch__knob">{ic('u-check', 14, 2.6)}</span></button></div>
<div class="st-line" style="flex-wrap: nowrap"><span class="corpo-forte" style="flex: 1">Sblocca con l’impronta</span><button type="button" role="switch" aria-checked="false" aria-label="Sblocca con l’impronta" class="st-switch"><span class="st-switch__knob">{ic('u-check', 14, 2.6)}</span></button></div>
<label class="st-check corpo"><input type="checkbox" checked><span class="st-check__box">{ic('u-check', 16, 2.8)}</span>Salva anche tra i preferiti</label></div>
<label class="st-option"><input type="radio" name="dove" checked><span class="st-cat st-cat--s3" aria-hidden="true" style="background: var(--color-accent-soft); color: var(--color-accent)">{ic('u-cloud')}</span><span class="st-stack" style="flex: 1; gap: 2px"><span class="corpo-forte">Google Drive, cifrato</span><span class="secondario st-muted">Ritrovi tutto su telefono e PC.</span></span><span class="st-option__dot"></span></label></div>''')

# --- Avanzamento
import math
def ring(pct, s, label):
    r = 27; c = 2 * math.pi * r
    return (f'<span class="st-ring" role="img" aria-label="{label}" style="--cat: var(--swatch-{s})"><svg width="60" height="60" viewBox="0 0 60 60" aria-hidden="true"><circle class="track" cx="30" cy="30" r="{r}" fill="none" stroke-width="6"/>'
            f'<circle class="fill" cx="30" cy="30" r="{r}" fill="none" stroke-width="6" stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{c * (1 - pct / 100):.1f}"/></svg><span class="badge" style="font-size: 13px; font-weight: 800">{pct}%</span></span>')
def budget(name, spent, tot, pct, kind):
    fill = {'ok': '', 'warn': ' is-warning', 'over': ' is-critical'}[kind]
    state = {'ok': f'<span class="ok">{ic("u-check", 14, 2.4)}</span>In regola', 'warn': f'{ic("u-alert", 14, 2.2)}Quasi esaurito', 'over': f'<span class="over">{ic("u-alert", 14, 2.2)}</span>Superato di 12,00 €'}[kind]
    return (f'<li class="st-budget"><span class="st-budget__head corpo"><span class="corpo-forte" style="font-size: 14px">{name}</span><span><span class="corpo-forte" style="font-size: 14px">{spent}</span><span class="st-muted" style="font-size: 14px"> di {tot}</span></span></span>'
            f'<span class="st-bar" aria-hidden="true"><span class="st-bar__fill{fill}" style="width: {min(pct, 100)}%"></span></span><span class="st-budget__state secondario" style="font-size: 12px; font-weight: 600">{state} · {pct}%</span></li>')
comp('Avanzamento', 'Stato e messaggi', 420, '''Barre del budget e anelli degli obiettivi: quanto è stato usato o raggiunto, sempre scritto.

## Budget
`<li class="st-budget">`: nome e «speso di totale» sopra, la barra `st-bar` (8 px, binario chart-track), sotto lo stato con simbolo e percentuale. Tre stati:
- **In regola** (sotto l'80%): barra color-primary, spunta in color-income.
- **Quasi esaurito** (dall'80%): barra status-warning, triangolo di avviso.
- **Superato** (oltre il 100%): barra status-critical piena, triangolo in color-danger e di quanto è stato superato.

## Obiettivo
`st-ring` (60 px, tratto 6) nella tinta dell'obiettivo, con la percentuale scritta al centro e `role="img"` con l'etichetta completa. Accanto: «1.228,15 € di 2.000,00 €», quanto manca e, se c'è una data, quanto mettere da parte al mese.

## Regole
Mai uno stato indicato dal solo colore: parola, simbolo e numero ci sono sempre.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 340px"><h2 class="titolo-3">Budget del mese</h2><ul class="st-stack" style="gap: var(--space-4)">{budget('Spesa alimentare', '168,40 €', '300 €', 56, 'ok')}{budget('Pasti fuori', '72,00 €', '80 €', 90, 'warn')}{budget('Svago', '62,00 €', '50 €', 124, 'over')}</ul></section>
<section class="st-card" style="width: 340px"><h2 class="titolo-3">Obiettivi di risparmio</h2><div class="st-line" style="flex-wrap: nowrap">{ring(61, 's6', 'Vacanza estate: 61% raggiunto')}<span class="st-stack" style="gap: 2px"><span class="corpo-forte">Vacanza estate</span><span class="corpo" style="font-size: 14px"><b>1.228,15 €</b><span class="st-muted"> di 2.000,00 €</span></span><span class="secondario st-muted">Circa 110 € al mese fino a giugno 2027</span></span></div></section></div>''')

# --- Avviso
comp('Avviso', 'Stato e messaggi', 470, '''Messaggi all'utente: la conferma a comparsa in basso, l'avviso in cima alla schermata e il riquadro d'errore nei moduli.

## Conferma a comparsa
`<div role="status" class="st-toast">` (componente `Toast`): toast-bg con toast-text (colori invertiti rispetto al tema), alta almeno `size-field`, testo `text-sm` peso 600, una frase al passato e al massimo un'azione (Annulla) in toast-action, peso 800. Sta in basso sopra la barra flottante (su PC a `space-4` dal fondo), larga al massimo 480 px.

## Avviso in cima
`st-banner` sopra il contenuto di ogni schermata, solo quando serve un intervento: testo `text-sm` a sinistra, Pulsante piccolo a destra.
- **Nuova versione** (`st-banner--update`, con bordo color-border): «È disponibile una nuova versione di Statera.» · Aggiorna.
- **Accesso a Google scaduto**: «Sincronizzazione in pausa: l'accesso a Google è scaduto.» · Riconnetti. Compare **solo se il rinnovo automatico non riesce**: il permesso di Google dura un'ora e, senza un server, non si rinnova in sottofondo; l'app lo rinnova al primo tocco su un pulsante o un link (vedi il manuale, Accesso a Google).
- **Bloccata**: «Sincronizzazione bloccata: serve la password di Statera.» · Apri.
- **Errore** (`st-banner--error`, `role="alert"`): «Sincronizzazione non riuscita: …» · Riprova (Pulsante secondario).

## Riquadro d'errore
`st-errorbox` (`.error-box` dell'app): color-danger al 12% sullo sfondo, testo color-text `text-sm` peso 600, accanto ai pulsanti del modulo. Il testo resta color-text: il colore di pericolo sta solo nel fondo.

## Testi
Prima cosa è successo, poi cosa fare, senza colpe e senza punti esclamativi: «Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.»
''', f'''<div class="st st-stage st-stage--col" style="max-width: 440px; gap: var(--space-3)">
<div role="status" class="st-toast"><span>Spesa registrata</span><button type="button" class="st-toast__action">Annulla</button></div>
<div role="status" class="st-banner st-banner--update"><span>È disponibile una nuova versione di Statera.</span><button type="button" class="st-btn st-btn--s st-btn--primary pulsante">Aggiorna</button></div>
<div role="status" class="st-banner"><span>Sincronizzazione in pausa: l'accesso a Google è scaduto.</span><button type="button" class="st-btn st-btn--s st-btn--primary pulsante">Riconnetti</button></div>
<div role="alert" class="st-banner st-banner--error"><span>Sincronizzazione non riuscita: Google Drive non risponde.</span><button type="button" class="st-btn st-btn--s st-btn--secondary pulsante">Riprova</button></div>
<p class="st-errorbox">Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.</p></div>''')

# --- Finestra
comp('Finestra', 'Stato e messaggi', 560, '''I contenitori modali: il pannello che sale dal basso sul telefono, la finestra centrata su PC, la conferma.

## Pannello (telefono)
`st-sheet` sopra `st-backdrop`: color-bg, angoli alti `radius-xl`, maniglia `st-sheet__grip`, `shadow-3`. Sale con `duration-slow` ed `ease-standard`. In alto: Chiudi a sinistra, il Segmentato o il titolo al centro; in fondo il Pulsante grande.

## Finestra (PC)
`st-dialog`, larga al massimo `content-max`, a `space-8` dal bordo alto, contenuto su due colonne. Intestazione con titolo `titolo-2` e Chiudi con il Tasto Esc; in fondo `st-dialog__foot` con le azioni a destra e il Tasto Invio sul pulsante principale.

## Conferma
Per ciò che non si annulla: icona di pericolo (`st-danger-icon`), domanda come titolo («Eliminare questa spesa?»), che cosa si elimina, una frase sulle conseguenze, poi Elimina (Pulsante di pericolo pieno, `st-btn--confirm`) e Annulla. `role="alertdialog"`.

## Regole
Usa `<dialog>` aperto con `showModal()`: il focus resta dentro, Esc chiude, il focus torna al comando che l'ha aperta. La schermata di blocco sta sopra tutte le altre finestre.
''', f'''<div class="st st-stage" style="align-items: flex-end; padding-bottom: 0">
<div class="st-layer" style="width: 360px; height: 500px; border-radius: var(--radius-lg) var(--radius-lg) 0 0"><div class="st-backdrop"></div>
<div role="alertdialog" aria-modal="true" aria-label="Eliminare questa spesa?" class="st-sheet" style="position: absolute; left: 0; right: 0; bottom: 0; text-align: center">
<span class="st-sheet__grip" aria-hidden="true"></span><span class="st-danger-icon" aria-hidden="true">{ic('u-trash', 28)}</span>
<h2 class="titolo-2">Eliminare questa spesa?</h2>
<div class="st-card" style="flex-direction: row; align-items: center; padding: var(--space-3) var(--space-4); text-align: left"><span class="st-cat st-cat--s1" aria-hidden="true">{ic('spesa')}</span><span class="st-mrow__text"><span class="corpo-forte">Conad</span><span class="secondario st-muted">Sabato 14 novembre</span></span><span class="corpo-forte">−42,30 €</span></div>
<p class="corpo st-muted">Sparisce anche dagli altri dispositivi collegati.</p>
<div class="st-stack"><button type="button" class="st-btn st-btn--l st-btn--confirm pulsante-l">{ic('u-trash', 20, 2.2)}Elimina</button><button type="button" class="st-btn st-btn--l st-btn--secondary pulsante-l" style="background: var(--color-surface)">Annulla</button></div></div></div></div>''')

# --- Tasto
comp('Tasto', 'Azioni', 150, '''Un tasto della tastiera, per mostrare le scorciatoie su PC accanto ai comandi.

## Struttura
`<kbd class="st-kbd tasto">`: color-surface-2, bordo color-border, `radius-xs`. Su un pulsante principale: `st-kbd--on-primary`.

## Scorciatoie
N nuovo movimento · / cerca · ← → mese precedente e successivo · ? elenco delle scorciatoie · Esc chiude · Invio salva. Non si attivano mentre si scrive in un campo.
''', f'''<div class="st st-stage"><span class="st-line corpo st-muted" style="gap: 6px"><kbd class="st-kbd tasto">N</kbd>nuovo <kbd class="st-kbd tasto">/</kbd>cerca <kbd class="st-kbd tasto">←</kbd><kbd class="st-kbd tasto">→</kbd>mese <kbd class="st-kbd tasto">?</kbd>tutte</span>
<button type="button" class="st-btn st-btn--primary pulsante" style="padding-right: var(--space-3)">Salva spesa<kbd class="st-kbd st-kbd--on-primary tasto">Invio</kbd></button></div>''')

# --- Grafico
months = [('Giu', 2010, 1420), ('Lug', 2010, 1610), ('Ago', 2240, 1980), ('Set', 2010, 1240), ('Ott', 2050, 1380), ('Nov', 2010, 684)]
bars = ''.join(f'<div class="st-chart__month secondario" style="font-size: 12px"><div class="st-chart__bars"><span class="st-chart__bar st-in" style="height: {round(i / 2240 * 100)}px"></span><span class="st-chart__bar st-out" style="height: {round(o / 2240 * 100)}px"></span></div>{m}</div>' for m, i, o in months)
comp('Grafico', 'Dati', 260, '''Colonne di entrate e uscite per mese, con la legenda sempre visibile.

## Regole
- Entrate in chart-income, uscite in chart-expense: blu e arancio si distinguono anche per chi non vede rosso e verde, e differiscono in luminosità.
- Legenda scritta sopra il grafico; il mese in corso è segnato «in corso».
- `role="img"` con un'etichetta che riassume il grafico, e accanto la vista a tabella («Vedi come tabella») con gli stessi numeri.
- Su PC: griglia con chart-grid e valori sull'asse; al passaggio del puntatore, il riepilogo del mese.
''', f'''<div class="st st-stage st-stage--col"><section class="st-card" style="max-width: 390px"><h2 class="titolo-3">Ultimi 6 mesi</h2>
<div class="st-chart" role="img" aria-label="Entrate e uscite degli ultimi 6 mesi"><div class="st-chart__legend secondario"><span><span class="st-chart__key st-in"></span>Entrate</span><span><span class="st-chart__key st-out"></span>Uscite</span><span>novembre in corso</span></div><div class="st-chart__plot">{bars}</div></div></section></div>''')

# --- StatoVuoto
comp('StatoVuoto', 'Stato e messaggi', 300, '''Quello che si vede quando non c'è ancora niente: cosa manca e come rimediare, con un solo pulsante.

## Struttura
`st-empty` dentro la scheda che sarebbe piena: icona Lucide in un cerchio color-accent-soft da 64 px, titolo in `titolo-3`, una frase in `corpo` color-text-muted, un Pulsante tenue.

## Testi
Titolo che descrive lo stato («Ancora nessun movimento a novembre», «Nessun risultato per «palestra»»), frase con il prossimo passo. Niente illustrazioni né battute.
''', f'''<div class="st st-stage st-stage--col"><div class="st-empty" style="max-width: 360px"><span class="st-empty__icon" aria-hidden="true">{ic('x-receipt', 28, 1.9)}</span><h2 class="titolo-3">Ancora nessun movimento a novembre</h2><p class="corpo">Tocca + per la prima spesa. Le spese di tutti i giorni puoi salvarle tra i preferiti.</p><button type="button" class="st-btn st-btn--s st-btn--soft pulsante" style="font-size: 13px; margin-top: var(--space-2)">{ic('u-plus', 16, 2.2)}Aggiungi una spesa</button></div></div>''')

# --- Tastierino
def keypad(integer=False, floating=False, pressed='5'):
    k = lambda d: f'<button type="button" class="st-key{" is-pressed" if d == pressed else ""}">{d}</button>'
    off = ' st-key--off' if integer else ''
    dis = ' disabled' if integer else ''
    ops = [f'<button type="button" class="st-key st-key--op" aria-label="Cancella">{ai("delete", 22)}</button>',
           f'<button type="button" class="st-key st-key--op{off}" aria-label="Più"{dis}>{ai("plus", 22)}</button>',
           f'<button type="button" class="st-key st-key--op{off}" aria-label="Meno"{dis}>{ai("minus", 22)}</button>']
    rows = ''.join(''.join(k(d) for d in row) + ops[r] for r, row in enumerate(['123', '456', '789']))
    rows += (f'<button type="button" class="st-key{off}" aria-label="Virgola"{dis}>,</button>{k("0")}'
             f'<button type="button" class="st-key st-key--op{off}" aria-label="Calcola"{dis}>=</button><button type="button" class="st-key st-key--done">Fatto</button>')
    return f'<div class="st-keypad{" st-keypad--floating" if floating else ""}" role="group" aria-label="Tastierino">{rows}</div>'
comp('Tastierino', 'Moduli', 560, '''Il tastierino degli importi: su telefono sostituisce la tastiera del sistema nei campi di importo e di numero di buoni.

## Struttura
`<div class="st-keypad" role="group" aria-label="Tastierino">` (componente `Keypad` dell'app) con 4 colonne a passo `space-2`:
- righe 1–3: cifre, poi in quarta colonna **Cancella** (`delete`), **+** e **−** per i calcoli;
- riga 4: **virgola**, **0**, **=** per il risultato e **Fatto** in color-primary con color-on-primary.

Tasti alti `size-key`, `radius-md`; cifre in `tastierino` (`text-xl`, peso 700) su color-surface, premute color-surface-2; operazioni (Cancella, +, −, =) in color-accent-soft con color-accent; «Fatto» in `text-md` peso 800. Tutti con `aria-label` dove il segno non basta.

## Dove sta
- Dentro un pannello (Finestra): sopra i pulsanti, con il bordo alto color-border e lo sfondo color-bg.
- Fuori da un pannello: in fondo alla pagina (`st-keypad--floating`), con gli angoli alti `radius-xl` e `shadow-3`.

## Comportamento
- I tasti non prendono il focus: il cursore resta nel campo. Al tocco il contenuto del campo è selezionato, così la prima cifra lo sostituisce.
- «12,50+3,20» e poi = scrive il risultato; Fatto chiude il tastierino.
- Numeri interi (buoni pasto): virgola, +, − e = restano al loro posto ma invisibili e disattivati, così le cifre non si spostano.
- Su PC si usa la tastiera vera: il tastierino non compare.
''', f'''<div class="st st-stage" style="align-items: flex-end">
<div class="st-stack" style="width: 360px">{card_txt('Importo, dentro il pannello')}{keypad()}</div>
<div class="st-stack" style="width: 360px">{card_txt('Numero di buoni, in fondo alla pagina')}{keypad(integer=True, floating=True, pressed=None)}</div></div>''')

# --- RiquadroImporto
def balance(label, amount, pill=None, wide=False, quick=False):
    b = f'<section class="st-balance" aria-label="{label}"><span class="st-balance__label">{label}</span><span class="st-balance__amount">{amount}</span>{f"<span class=\"st-balance__pill\">{pill}</span>" if pill else ""}</section>'
    if not quick: return b
    q = ''.join(f'<button type="button" class="st-quick" aria-label="{al}"><span class="st-quick__circle">{ai(i, 22)}</span>{t}</button>' for i, t, al in
                [('arrow-up-right', 'Spesa', 'Nuova spesa'), ('arrow-down-left', 'Entrata', 'Nuova entrata'), ('arrow-left-right', 'Trasferisci', 'Nuovo trasferimento')])
    return f'<div class="st-top{" st-top--wide" if wide else ""}">{b}<div class="st-top__quick">{q}</div></div>'
comp('RiquadroImporto', 'Contenuti', 560, '''Il riquadro dell'importo principale di una schermata: saldo del mese (Movimenti), patrimonio (Conti), risparmio (Analisi).

## Struttura
`<section class="st-balance" aria-label="Saldo del mese">` (`.balance-box` in `base.css`): etichetta sopra (`text-md`, peso 600), importo (`amount-l`, peso 800, `tracking-tighter`, `leading-tight`), pillola facoltativa sotto (`st-balance__pill`, `text-sm` peso 700, il colore del testo al 16%): numero di conti attivi e archiviati, percentuale delle entrate risparmiata.

## Colori
- Tema chiaro: color-primary con le cifre in color-on-primary.
- Tema scuro: color-accent-soft con color-text, per non abbagliare.
- Le cifre restano chiare anche quando l'importo è negativo: il segno «−» basta, niente rosso. Il saldo positivo ha il «+».

## Con le azioni rapide
Sul telefono le AzioneRapida stanno sotto il riquadro, centrate, a `space-4`; da 600 px in su accanto, a destra (`st-top--wide`, griglia con `space-5`). Sotto il blocco `space-5`, poi i riquadri Entrate e Uscite.

## Regole
Un solo riquadro per schermata, allineato a sinistra, mai in una Scheda.
''', f'''<div class="st st-stage st-stage--col" style="max-width: 640px">
{card_txt('Movimenti, telefono')}<div style="max-width: 360px">{balance('Saldo del mese', '+1.325,65 €', quick=True)}</div>
{card_txt('Movimenti, da 600 px')}{balance('Saldo del mese', '−84,20 €', wide=True, quick=True)}
<div class="st-line" style="align-items: flex-start"><div style="width: 300px">{balance('Patrimonio', '8.412,90 €', '3 conti attivi · 1 archiviato')}</div><div style="width: 300px">{balance('Risparmio', '1.325,65 €', '66% delle entrate')}</div></div></div>''')

# --- ElencoVoci
facts = lambda wide: (f'<dl class="st-facts{" st-facts--wide" if wide else ""}"><dt>Account Google</dt><dd>mario.rossi@example.com</dd><dt>Stato</dt><dd>Sincronizzato</dd>'
                      '<dt>Ultima sincronizzazione</dt><dd>sabato 14 novembre, 18:42</dd><dt>Dove sono salvati</dt><dd>Su questo dispositivo e, cifrati, sul tuo Google Drive</dd></dl>')
comp('ElencoVoci', 'Contenuti', 470, '''Elenco di voci e valori dentro una scheda: I tuoi dati, Informazioni, Sincronizzazione.

## Struttura
`<dl class="st-facts">` (`.facts` in `base.css`) con coppie `<dt>` (voce, color-text-muted, `text-sm`) e `<dd>` (valore). `leading-compact`.
- **Telefono**: la voce sta sopra il valore (valore in `text-md`, `space-3` sotto), così nessuno dei due va a capo a metà: prima «Dove sono / salvati» e l'indirizzo email spezzato.
- **Da 600 px** (`st-facts--wide`): affiancati su due colonne (2:3), valore a destra in `text-sm`, `space-2` tra le righe e `space-4` tra le colonne.

## Regole
Valori lunghi (email, percorsi) vanno a capo dove serve (`overflow-wrap: anywhere`), mai fuori dalla scheda. Un numero di versione usa le cifre tabulari.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 340px"><h2 class="titolo-3">Sincronizzazione</h2>{facts(False)}</section>
<section class="st-card" style="width: 520px"><h2 class="titolo-3">Sincronizzazione · PC</h2>{facts(True)}</section></div>''')

# --- SceltaIcona
def iconpick(color, current, auto, open_groups):
    prev = (f'<span class="st-cat st-cat--l st-cat--{color}" aria-hidden="true">{ai(APP.cat_icons[current], 22) if current else "B"}</span>')
    what = (APP.cat_labels[current] + ('<small> · in base al nome</small>' if auto else '')) if current else 'Nessuna, si vede l’iniziale'
    btn = 'Chiudi' if open_groups else ('Cambia' if current else 'Scegli')
    h = (f'<fieldset class="st-iconpick" style="border: 0; margin: 0; padding: 0"><legend class="etichetta-campo st-muted" style="padding: 0; margin-bottom: var(--space-1)">Icona</legend>'
         f'<div class="st-iconpick__current">{prev}<span class="st-iconpick__what">{what}</span><button type="button" class="st-btn st-btn--s st-btn--soft pulsante" aria-expanded="{"true" if open_groups else "false"}">{btn}</button></div>')
    if open_groups:
        h += '<div role="radiogroup" aria-label="Icona" class="st-iconpick" style="margin-top: var(--space-3)"><div class="st-iconpick__grid">'
        h += f'<button type="button" role="radio" class="st-iconpick__opt" aria-checked="{"false" if current else "true"}" aria-label="Nessuna icona (iniziale)"><span class="st-cat st-cat--{color}" aria-hidden="true">B</span></button></div>'
        for g in APP.cat_groups[:open_groups]:
            h += f'<p class="st-iconpick__group">{g["label"]}</p><div class="st-iconpick__grid" role="group" aria-label="{g["label"]}">'
            h += ''.join(f'<button type="button" role="radio" class="st-iconpick__opt{" is-hover" if k == "pizza" else ""}" aria-checked="{"true" if k == current else "false"}" aria-label="{APP.cat_labels[k]}" title="{APP.cat_labels[k]}"><span class="st-cat st-cat--{color}" aria-hidden="true">{ai(APP.cat_icons[k])}</span></button>' for k in g['keys'])
            h += '</div>'
        h += '</div>'
    return h + '</fieldset>'
GROUPS_LINE = '; '.join(f'**{g["label"]}** ({len(g["keys"])})' for g in APP.cat_groups)
comp('SceltaIcona', 'Moduli', 760, f'''La scelta dell'icona nel modulo della categoria: anteprima nel colore scelto e, su richiesta, la griglia delle icone per gruppi.

## Struttura
`<fieldset>` con la legenda «Icona» (componente `IconPicker` dell'app):
- **Anteprima**: IconaCategoria grande nella tinta della categoria, il nome dell'icona in italiano (`text-sm`, color-text-muted) e un Pulsante piccolo tenue: «Scegli», «Cambia» o «Chiudi» (`aria-expanded`).
- Finché non la si sceglie, l'icona è automatica e l'anteprima dice «· in base al nome»: segue il nome mentre lo si scrive.
- **Griglia** (`role="radiogroup"`): prima «Nessuna» (l'iniziale), poi i gruppi {GROUPS_LINE}, ognuno col titolo in maiuscolo (`text-xs`, peso 800, `tracking-caps`). Celle da `size-touch` a riempimento automatico; ogni icona è un `role="radio"` con `aria-label` e suggerimento col nome in italiano, letto dagli screen reader.

## Stati
Scelta: anello di `focus-width` in color-text intorno alla cella (la forma cambia, non solo il colore). Passaggio del puntatore: anello in color-border.

## Dati
Si salva solo la chiave (`caffe`, `treno`…), mai il disegno; «Nessuna» salva `null`. Niente migrazione: il campo viaggia col record.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 340px">{iconpick('s2', 'pasti', True, 0)}</section>
<section class="st-card" style="width: 380px">{iconpick('s2', 'caffe', False, 2)}</section></div>''')

# --- SceltaTema
theme_opts = lambda on: ''.join(f'<button type="button" role="radio" class="st-seg__opt" aria-checked="{"true" if v == on else "false"}">{t}</button>' for v, t in [('auto', 'Automatico'), ('light', 'Chiaro'), ('dark', 'Scuro')])
comp('SceltaTema', 'Moduli', 210, '''La scelta del tema in Altro → Aspetto: Automatico, Chiaro o Scuro, per dispositivo.

## Struttura
Scheda «Aspetto» con una frase in color-text-muted e un Segmentato a tre opzioni (`role="radiogroup"`, `aria-label="Tema"`): **Automatico** (come il telefono o il PC), **Chiaro**, **Scuro**.

## Comportamento
- La scelta vale solo per il dispositivo (`statera.tema` nella memoria del browser) e non si sincronizza.
- Si applica prima che la pagina compaia (`public/tema.js`), così non c'è il lampo del tema sbagliato; il tema scuro è `data-theme="dark"` sulla radice, mai una media query nei componenti.
- Il colore della barra del sistema segue lo sfondo dell'app.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 360px"><h2 class="titolo-3">Aspetto</h2><p class="corpo st-muted" style="font-size: var(--text-sm)">Colori chiari o scuri. «Automatico» segue l’impostazione del telefono o del PC. La scelta vale per questo dispositivo.</p><div role="radiogroup" aria-label="Tema" class="st-seg">{theme_opts('auto')}</div></section>
<section class="st-card" style="width: 360px"><h2 class="titolo-3">Aspetto</h2><div role="radiogroup" aria-label="Tema" class="st-seg">{theme_opts('dark')}</div></section></div>''')

# --- Logo
comp('Logo', 'Marchio', 300, f'''Il logo di Statera: la bilancia a tratto bianca nel riquadro indaco arrotondato. Disegno originale dell'app, non un'icona Lucide.

## Struttura
`<svg viewBox="0 0 {APP.logo_size} {APP.logo_size}">` (componente `Logo` dell'app, dati in `src/lib/logo.ts`): un `<rect rx="{APP.logo_radius}">` in color-primary e il simbolo in color-on-primary. Due disegni: **grande** da 48 px in su, **piccolo** fino a 32 px (tratti più spessi, un tirante per piatto, piatti più grandi), scelto da solo in base alla misura.

## Colori
- Tema chiaro: riquadro indaco con simbolo bianco ({ratio('color-on-primary', 'color-primary')}:1).
- Tema scuro: riquadro lilla con simbolo scuro ({ratio('color-on-primary', 'color-primary', 'dark')}:1). Le icone installate (home, barra delle applicazioni) restano sempre indaco col simbolo bianco.

## Uso
Nella barra laterale a 36 px accanto a «Statera», nella schermata di recupero, nel marchio. Sempre `aria-hidden`: il nome è scritto accanto. Regole complete nel manuale, sezione Marchio.
''', f'''<div class="st st-stage" style="gap: var(--space-6)">
<span class="st-stack" style="align-items: center">{APP.logo_svg(96)}<span class="secondario st-muted">96 · grande</span></span>
<span class="st-stack" style="align-items: center">{APP.logo_svg(48)}<span class="secondario st-muted">48 · grande</span></span>
<span class="st-stack" style="align-items: center">{APP.logo_svg(36)}<span class="secondario st-muted">36 · grande</span></span>
<span class="st-stack" style="align-items: center">{APP.logo_svg(32)}<span class="secondario st-muted">32 · piccolo</span></span>
<span class="st-stack" style="align-items: center">{APP.logo_svg(24)}<span class="secondario st-muted">24 · piccolo</span></span>
<span class="st-stack" style="align-items: center">{APP.logo_svg(16)}<span class="secondario st-muted">16 · piccolo</span></span>
<span class="st-wordmark" style="font-size: 40px; gap: var(--space-3)">{APP.logo_svg(56)}<span>Statera</span></span></div>''')

# ================================================================ copertina
COVER = '''<!-- @dsCard height=288 -->
<div class="st" style="position: relative; width: 960px; height: 288px; overflow: hidden; background: var(--color-bg)">
<style>
.cv-primary { fill: var(--color-primary); } .cv-soft { fill: var(--color-accent-soft); } .cv-ink { fill: var(--color-text); }
.cv-warm { fill: var(--swatch-s2); } .cv-cut { fill: var(--color-bg); }
.cv-name { position: absolute; left: 48px; bottom: 64px; margin: 0; font-family: var(--font-sans); font-weight: 800; font-size: 100px; line-height: 0.92; letter-spacing: -0.03em; color: var(--color-text); }
.cv-tag { position: absolute; left: 50px; bottom: 36px; margin: 0; font-family: var(--font-sans); font-size: 14px; font-weight: 500; color: var(--color-text-muted); max-width: 440px; }
</style>
<svg width="960" height="288" viewBox="0 0 960 288" aria-hidden="true" style="position: absolute; inset: 0">
<!-- blocchi: color-primary pilastro 176×328 (raggio metà del lato corto), color-accent-soft pillola 296×120, color-text disco r 56, swatch-s2 disco r 28 -->
<!-- disposizione: un pilastro alto che esce dall'alto, satelliti a destra che escono dal bordo destro, tutto a destra di x = 480 -->
<!-- motivo: dischi (riga «raggi grandi, cerchi e pillole»): l'app è fatta di cerchi, le icone delle categorie, le azioni rapide, i biglietti dei buoni pasto; 16 dischi r 8 a passo space-7, ritagliati nel colore di fondo -->
<!-- scale: passo space-7 (32 px), spazio space-6 (24 px) tra i blocchi, pillole con raggio pari a metà del lato corto -->
<rect class="cv-primary" x="512" y="-40" width="176" height="328" rx="88"/>
<rect class="cv-soft" x="712" y="32" width="296" height="120" rx="60"/>
<circle class="cv-ink" cx="792" cy="232" r="56"/>
<circle class="cv-warm" cx="904" cy="216" r="28"/>
'''
for row in range(4):
    for colx in range(4):
        COVER += f'<circle class="cv-cut" cx="{552 + colx * 32}" cy="{56 + row * 32}" r="8"/>\n'
COVER += '''</svg>
<span style="position: absolute; left: 48px; top: 40px">''' + APP.logo_svg(72) + '''</span>
<p class="cv-name">Statera</p>
<p class="cv-tag">Entrate e spese, chiare. Sul tuo dispositivo.</p>
</div>
'''

# ================================================================ testi del manuale
labels = dict((k, lab) for k, c, lab in icone.USCITE + icone.ENTRATE)
labels['regali'] = 'Regali, Regali ricevuti'; labels['altro'] = 'Altro (uscite ed entrate)'
TABLE_ICONS = ''.join(f'| `{k}` | {lab} | `{APP.cat_icons[k]}` |\n' for k, lab in labels.items())
FREE = [k for g in APP.cat_groups for k in g['keys'] if k not in labels]
FREE_LINE = ' · '.join(f'`{k}` ({APP.cat_icons[k]})' for k in FREE)
GROUPS_TXT = ', '.join(f'{g["label"]}' for g in APP.cat_groups)
ACCOUNTS = [('conto_corrente', 'landmark'), ('contanti', 'banknote'), ('buoni_pasto', 'ticket'), ('altro', 'piggy-bank')]
CAT_MIN = min(cr(V(f'swatch-s{i}'), _mix(V(f'swatch-s{i}'), V('color-surface'), TL['cat-tint'])) for i in range(1, 9))
CAT_MAX = max(cr(V(f'swatch-s{i}'), _mix(V(f'swatch-s{i}'), V('color-surface'), TL['cat-tint'])) for i in range(1, 9))

README = f'''Statera è l'app personale per registrare entrate e spese, su telefono Android e PC Windows. Lo stile è «Vivace»: l'importo principale grande in un riquadro indaco, azioni in cerchi, categorie riconoscibili dal colore e dall'icona, angoli molto arrotondati. La palette è «Indaco morbido»: un indaco calmo, che non stanca la vista, con tinte vivaci per le categorie.

Il riferimento è l'app pubblicata (versione {APP.version}): token, icone, logo e carattere di questo sistema sono letti dal codice (`src/styles/tokens.css`, `src/lib/icons.ts`, `src/lib/logo.ts`, `icona/`), con gli stessi nomi.

## Principi
- **Il numero prima di tutto.** Ogni schermata ha un importo protagonista nel RiquadroImporto (saldo del mese, patrimonio, risparmio) o in uno stile `importo-*`; il resto gli fa spazio.
- **Il colore non basta mai.** Stati, budget, entrate e uscite hanno sempre anche una parola, un simbolo o un segno.
- **Calma.** Un solo colore forte (color-primary) per schermata: l'azione principale o il riquadro dell'importo. Le tinte delle categorie stanno su cerchi tenui.
- **Tutto in locale, detto chiaramente.** Dove si parla di dati, si dice dove stanno: «sul dispositivo», «cifrato su Google Drive».

## Testi
- Italiano, del «tu», frasi brevi. Maiuscola solo a inizio frase e nei nomi. Nessuna emoji, nessun punto esclamativo.
- Pulsanti col verbo e l'oggetto: «Salva spesa», «Registra», «Esporta CSV», «Collega Google Drive». Domande dirette nei campi: «Quanto hai speso?».
- Errori in due tempi: cosa è successo, cosa fare. «Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.»
- Stati vuoti che indicano il prossimo passo: «Ancora nessun movimento a novembre. Tocca + per la prima spesa.»
- Date: «sabato 14 novembre», «14/11/2026» nei campi. Virgolette «basse», apostrofo tipografico «’».
- Separatore tra informazioni: « · » (Carburante · Bancomat); gerarchia delle categorie: « › » (Casa › Bollette).

## Importi e segno meno
- Formato italiano, sempre col punto delle migliaia e la virgola: «1.234,56 €». Tra cifra e € lo spazio normale (non separabile): uno spazio più stretto faceva sembrare il simbolo attaccato.
- Negli importi il **vero segno meno «−» (U+2212)**, largo come il «+», nelle righe dei movimenti come nei totali e nei riquadri: «−42,30 €», mai il trattino «-42,30 €». Nell'app lo mette solo `formatEuro` (`src/lib/format.ts`); nessun componente lo scrive a mano.
- Nei campi e nel CSV resta il trattino, che è quello che si scrive e che leggono i fogli di calcolo.
- Entrate col «+» e color-income; uscite col «−» e color-expense (il colore del testo, mai rosso). Il saldo positivo del mese ha il «+».

## Accesso a Google
- Il permesso di Google dura un'ora e, senza un server, non si rinnova in sottofondo. L'app lo **rinnova da sola al primo tocco** su un pulsante o un link dopo la scadenza: di solito non si vede niente, al massimo la finestrella di Google che si apre e si chiude.
- L'Avviso «Sincronizzazione in pausa: l'accesso a Google è scaduto» con Riconnetti compare **solo se il rinnovo automatico non riesce**. I dati intanto restano al sicuro sul dispositivo.
- I comandi che aprono il modulo del movimento (il +, Nuovo movimento, le azioni rapide) non fanno partire il rinnovo (`data-no-autoauth`): chi registra una spesa non deve aspettare Google.

## Colore
- Sfondo color-bg, contenuti in schede color-surface; dentro una scheda, i comandi secondari sono color-surface-2 e i campi color-bg. Bordi color-border solo come linee sottili, mai intorno alle schede.
- Testo color-text; seconde righe, date e didascalie color-text-muted. Entrambi superano 4,5:1 su color-bg, color-surface e color-surface-2 in tutti e due i temi.
- color-primary con color-on-primary per un solo elemento forte per schermata (pulsante +, Salva, «Fatto», segmento attivo) e per il RiquadroImporto. Per link, icone d'accento e voci attive: color-accent; per i fondi tenui: color-accent-soft.
- Uscite in color-expense (= color-text), entrate in color-income. color-income non va su color-accent-soft in tema chiaro.
- Grafici: chart-income (blu) e chart-expense (arancio), mai rosso e verde; legenda sempre visibile.
- Stati: status-warning per «quasi esaurito» e i promemoria, status-critical / color-danger per «superato», errori e cancellazioni. Sempre con simbolo e parola. color-danger non si usa per gli importi in uscita.
- **Tinte delle categorie** `swatch-s1`…`swatch-s8`: vivaci, vicine alla saturazione massima alla stessa luminosità (calcolate in OKLCH). I dati salvano solo la chiave (`s1`…`s8`), quindi un cambio di tinte non tocca i dati. Nel cerchio: tinta al `cat-tint` ({TL['cat-tint']}) con icona colorata in chiaro ({f1(CAT_MIN)}:1–{f1(CAT_MAX)}:1), al {DARK_TINT} con icona `cat-icon-dark` bianca in scuro (vedi IconaCategoria).
- **Riquadro dell'importo principale**: color-primary con cifre color-on-primary in chiaro, color-accent-soft con color-text in scuro; cifre chiare anche quando l'importo è negativo.
- **Tema a scelta** (SceltaTema): Automatico, Chiaro o Scuro, per dispositivo. Stessi ruoli con i valori scuri; gli avvisi a comparsa invertono i colori (toast-bg, toast-text, toast-action).

## Tipografia
- Un solo carattere: Plus Jakarta Sans (licenza OFL), incluso nel pacchetto dell'app, mai caricato da internet. Peso variabile 200–800; si usano 400, 500, 600, 700, 800. `font-num` è lo stesso carattere, con le cifre tabulari.
- Cifre tabulari ovunque (`font-variant-numeric: tabular-nums`), così le colonne di importi si allineano. Crenatura del carattere attiva, dimensioni ottiche automatiche.
- Scala: `text-2xs` 11 · `text-xs` 12 · `text-sm` 13 · `text-md` 15 · `text-input` 16 · `text-lg` 17 · `text-xl` 22 · `text-2xl` 26 px; importi `amount-s` 20 · `amount-m` 34 · `amount-l` 46 · `amount-xl` 56 px. Gli stili di testo (`importo-*`, `titolo-*`, `corpo`, `secondario`…) sono fatti con questi token.
- **Interlinea**: `leading-tight` {TL['leading-tight']} per titoli e importi grandi, `leading-snug` {TL['leading-snug']} per i titoli, `leading-compact` {TL['leading-compact']} per le seconde righe che vanno a capo, `leading-normal` {TL['leading-normal']} per il testo corrente.
- **Spaziatura delle lettere**: titoli `tracking-tight` (−0,02 em), importi grandi `tracking-tighter` (−0,03 em), etichette in maiuscolo `tracking-caps` (+0,06 em), chiave di recupero `tracking-code` (+0,04 em), cifre nascoste del PIN `tracking-pin` (+0,4 em).
- **A capo**: titoli bilanciati (`text-wrap: balance`), paragrafi senza una parola sola sull'ultima riga (`text-wrap: pretty`). Righe dei movimenti: categoria e conto su una riga, con i puntini se non ci stanno.
- Importi: `importo-xl` mentre scrivi, `importo-l` nel RiquadroImporto, `importo-m` per il saldo di un conto, `importo-s` per i totali.
- Titoli: `titolo-1` per le quattro sezioni, `titolo-2` per le schermate secondarie e le finestre, `titolo-3` per le schede.
- Testo: `corpo` per le frasi, `corpo-forte` per il titolo delle righe, `campo` dentro i campi (16 px), `secondario` per le seconde righe, `pulsante` e `pulsante-l` sui pulsanti, `tastierino` sui tasti del Tastierino.
- Etichette: `etichetta-campo` sopra i campi, `etichetta` per i titoli di gruppo (in maiuscolo con `text-transform`), `nav` nella barra, `badge` e `tasto`.

## Spazi, forme e ombre
- Griglia di 4 px: `space-1` (4) … `space-8` (48), più il mezzo passo `space-hair` (2 px) per le distanze minime tra due righe. Nessuna misura scritta a mano nei componenti.
- **Ritmo verticale**: `space-4` tra le schede, `space-6` sopra i titoli di sezione in maiuscolo, `space-5` sotto il blocco del saldo con le azioni rapide. Margine laterale del telefono `space-5`, interno delle schede `space-5` (su PC, da 900 px, 20 × 24 px), tra le colonne su PC `space-6`.
- **Dimensioni fisse**: riga di elenco `size-row` (56 px), campo `size-field` (52), area di tocco minima `size-touch` (44), tasto del tastierino `size-key` (52), numeri dei passi `size-step` (28), icona della schermata di blocco `size-hero-icon` (72), barra flottante `nav-height` (66), barra laterale `size-sidebar` (248).
- Raggi: `radius-lg` per schede e riquadri, `radius-md` per campi, tasti e righe evidenziate, `radius-xl` per pannelli e finestre, `radius-full` per pulsanti, chip, cerchi e barra flottante, `radius-xs` per tasti e caselle, `radius-2xs` per le barre dei grafici.
- Ombre solo per ciò che galleggia: `shadow-2` per barra flottante, barra laterale e avvisi; `shadow-3` per pannelli, finestre e tastierino fuori da un pannello; `shadow-fab` per il +; `shadow-1` per il pomello dell'interruttore. Le schede non hanno ombra.

## Schemi ricorrenti
- **RiquadroImporto** per l'importo principale, con le AzioneRapida sotto (telefono) o accanto (da 600 px).
- **ElencoVoci** per voci e valori: voce sopra il valore sul telefono, affiancati da 600 px.
- **Pulsanti-collegamento a fine riga** (Ordina, + Carta, Imposta budget, Tabella): allineato al bordo della scheda è il testo, non la pillola.
- **«Elimina» dentro una scheda**: pillola rosata (Pulsante di pericolo).
- **Analisi**: importi delle categorie allineati al nome; nei confronti con la media la riga di dettaglio parte dal nome, non dall'icona.

## Impaginazione
- **Telefono**: barra flottante con il + al centro (BarraNavigazione) nelle quattro sezioni Movimenti, Conti, Analisi, Altro. Le schermate aperte da un'altra hanno la freccia indietro in alto e niente barra. I moduli salgono dal basso in un pannello (Finestra), col Tastierino degli importi sopra i pulsanti.
- **PC (da 900 px)**: BarraLaterale larga `size-sidebar` al posto della barra flottante, col Logo in cima; contenuto largo al massimo `content-max`; i moduli si aprono in una finestra centrata. Le scorciatoie (N nuovo movimento, / cerca, frecce per il mese, Esc chiude) sono nel suggerimento dei comandi, non scritte sulle voci.

## Stati dei comandi
- Passaggio del puntatore (solo PC): velo del colore del testo all'8%, o color-surface-2 per righe e voci.
- Premuto: scala 0,97 (cerchi 0,94) e velo al 14%, per `duration-fast`; i tasti del tastierino passano a color-surface-2.
- Focus da tastiera: anello pieno di `focus-width` in color-focus, staccato di `focus-offset`; sui campi l'anello è intorno al campo. Mai togliere il focus visibile.
- Disattivato: `opacity-disabled`, senza ombre né movimento, con il motivo scritto vicino.
- Errore: anello in color-danger sul campo e riquadro d'errore (Avviso) accanto ai pulsanti.

## Movimento
- `duration-fast` (120 ms) per pressioni, tasti e colori, `duration-base` (200 ms) per interruttori, segmentato e avvisi, `duration-slow` (280 ms) per pannelli e finestre. Entrate con `ease-standard`, uscite con `ease-exit`.
- Il movimento accompagna, non decora: niente rimbalzi, niente animazioni in attesa.
- Con «riduci animazioni» attivo nel sistema, nessuno spostamento: transizioni e animazioni ridotte a 0,01 ms, scorrimento senza animazione.

## Iconografia
- **Lucide** (licenza ISC), versione 1.73: tratto 2 px su griglia 24, estremità arrotondate. 20 px nell'interfaccia, 22 px nella barra e nel tastierino, 16 px in chip e pulsanti piccoli.
- Nell'app le icone sono copiate nel codice (`src/lib/icons.ts`, solo quelle usate, generato da `scripts/icone.mjs`), mai caricate da internet né lette dai dati come disegno: i dati salvano solo una chiave. Le icone si colorano col colore del testo (`currentColor`); quelle in questo sistema, viste come immagine, sono nere.
- Il logo non è un'icona Lucide: è un disegno originale dell'app (vedi Marchio e il gruppo Logo negli asset).
- Ogni categoria ha un campo facoltativo `icon` con una chiave. Senza chiave l'icona è automatica: id delle categorie iniziali, poi il nome («Palestra» → manubrio), infine l'iniziale. `null` = «Nessuna», si vede l'iniziale.

| Chiave | Categoria iniziale | Icona Lucide |
|---|---|---|
{TABLE_ICONS}
- Conti, per tipo: {', '.join(f'`{t}` → `{n}`' for t, n in ACCOUNTS)}; carte → `credit-card`.
- Scelta libera nel modulo della categoria (SceltaIcona), in cinque gruppi ({GROUPS_TXT}): {FREE_LINE}.
- Icone dell'interfaccia: gruppo Interfaccia negli asset.

## Marchio
**Bilancia a tratto** (scelta il 14/11/2026, nell'app dalla versione 0.29.0): una bilancia a due piatti disegnata da zero, con colonna, base, pomello, braccio, tiranti e piatti pieni. Simbolo bianco su riquadro indaco color-primary ({ratio('color-on-primary', 'color-primary')}:1).

**Due disegni**, sulla stessa griglia di 100 unità:
- **grande**, da 48 px in su: tutti i dettagli, due tiranti per piatto;
- **piccolo**, fino a 32 px: tratti più spessi, un solo tirante per piatto e piatti più grandi, per restare leggibile a 16 px (favicon, schede del browser).

**Proporzioni**
- Riquadro arrotondato con raggio {APP.logo_radius} su {APP.logo_size} (circa {f1(APP.logo_radius / APP.logo_size * 100)}% del lato).
- Nel riquadro il lato lungo del simbolo occupa il **60%** (disegno grande) o il **68%** (disegno piccolo, che ha bisogno di più pixel), centrato.
- Versioni piene (maskable, icona adattiva di Android, monochrome): tutto il simbolo sta dentro il cerchio della **zona sicura del 66%** del lato, così nessuna maschera del launcher (tonda, squircle, goccia) lo taglia.

**Colori**
- Icona dell'app (home di Android, barra delle applicazioni e menu Start di Windows, favicon): sempre riquadro indaco con simbolo bianco; la monochrome è solo la forma, colorata dal tema di Android.
- Logo dentro l'app: colori dai token. In tema chiaro indaco col simbolo bianco ({ratio('color-on-primary', 'color-primary')}:1); in tema scuro **riquadro lilla col simbolo scuro** ({ratio('color-on-primary', 'color-primary', 'dark')}:1).
- Barra del sistema e schermata d'avvio restano lo sfondo dell'app (color-bg), non l'indaco.

**Marchio con la scritta**: Logo e «Statera» in Plus Jakarta Sans 800, `tracking-tight`, color-text, a `space-2` dal riquadro (36 px di logo con `text-lg` nella barra laterale). Il nome si scrive sempre con la sola iniziale maiuscola.

**Usi corretti**
- Il disegno arriva solo dai file generati (`scripts/icona-app.mjs` nell'app; `simbolo.svg` e `simbolo-piccolo.svg` negli asset), mai ridisegnato.
- Disegno piccolo fino a 32 px, grande da 48 px; a 36–40 px si usa il grande.
- Simbolo da solo (senza riquadro) solo nella monochrome e nelle versioni adattive; altrove sempre nel riquadro.

**Da evitare**
- Allungare, ruotare o inclinare la bilancia (un braccio inclinato sembra uno squilibrio: per questo è stata scartata la «Bilancia in movimento»).
- Altri colori del riquadro oltre a indaco e lilla, sfumature, ombre, contorni.
- Usare la bilancia di Lucide (`scale`) o un altro simbolo al posto del logo.
- Mettere il simbolo piccolo sopra i 32 px o il grande sotto i 48 px.
- Avvicinare testo o bordi al simbolo oltre la zona sicura nelle versioni piene.

## Licenze
Plus Jakarta Sans (SIL Open Font License 1.1) e Lucide (ISC) sono inclusi nell'app e citati in Altro › Informazioni (`public/licenze.html`); i testi completi sono nella sezione Licenze.
'''

LIC = f'''# Licenze

Il carattere e le icone sono inclusi nell'app; queste licenze vanno riportate nelle note dell'app (Altro › Informazioni).

## Plus Jakarta Sans

Distribuito come @fontsource-variable/plus-jakarta-sans 5.3.0 (solo il sottoinsieme latino, pesi 200–800); copia in `src/assets/fonts/` dell'app.

```
{open(APP.font_license).read().strip()}
```

## Lucide

lucide-static {icone.SET['lucide']['versione']}.

```
{open(os.path.join(LUCIDE, 'LICENSE')).read().strip()}
```
'''

# ================================================================ tokens.css (come lo compila la pagina)
def tokens_css():
    """tokens.css nella forma che la pagina del design system compila da tokens.json: la pagina lo riscrive
    al primo salvataggio, ma finché nessuno salva le anteprime leggono questo file."""
    def cval(v, th):
        if isinstance(v, dict): v = v.get(th, v['light'])
        m = re.fullmatch(r'\{(.+)\}', v)
        return f'var(--{m[1]})' if m else (v.lower() if v.startswith('#') else v)
    note = lambda u: ' /* ' + u.replace('*/', '') + ' */' if u else ''
    fams = [FAM['color'], FAM['shadow']]
    out = ['/* Statera — generated from tokens.json */', ':root, [data-theme="light"] {']
    out += [f'  --{x["name"]}: {cval(x["value"], "light")};{note(x["usage"])}' for f in fams for x in f]
    out += ['}', '[data-theme="dark"] {']
    out += [f'  --{x["name"]}: {cval(x["value"], "dark")};' for f in fams for x in f]
    out += ['}', ':root {']
    out += [f'  --{x["name"]}: {x["value"]};{note(x["usage"])}' for k in ('spacing', 'radius', 'testo', 'dimensioni', 'stati', 'animazione') for x in FAM[k]]
    out += [f'  --font-{k}: {v};' for k, v in TYPE['families'].items()]
    styles = [st_ for g in TYPE['groups'] for st_ in g['styles']]
    out += [f'  --text-{x["name"]}: {x["fontWeight"]} {x["fontSize"]}/{x["lineHeight"]} var(--font-sans);{note(x["usage"])}' for x in styles]
    out += ['}']
    for x in styles:
        out += [f'.{x["name"]} {{', '  font-family: var(--font-sans);', f'  font-size: {x["fontSize"]};', f'  line-height: {x["lineHeight"]};',
                f'  font-weight: {x["fontWeight"]};', f'  letter-spacing: {x.get("letterSpacing", "0")};', '}']
    for f in TYPE['fonts']:
        out += ['@font-face {', f'  font-family: "{f["family"]}";', f'  src: url("{f["file"]}") format("woff2");', f'  font-weight: {f["weight"]};',
                f'  font-style: {f["style"]};', '  font-display: swap;', '}']
    return '\n'.join(out) + '\n'

# ================================================================ scrittura
def main():
    if os.path.exists(OUTDIR): shutil.rmtree(OUTDIR)
    w('README.md', README)
    w('Licenze.md', LIC)
    w('tokens.json', json.dumps(TOKENS, ensure_ascii=False, indent=1))
    w('tokens.css', tokens_css())
    w('components/bundle.css', CSS.replace('@DARK_TINT@', DARK_TINT))
    for name, group, height, readme, body in COMP:
        w(f'components/{name}/README.md', f'# {name}\n\n{readme}')
        w(f'components/{name}/preview.html', f'<!-- @dsCard group="{group}" height={height} -->\n{body}\n')
    w('components/Cover/preview.html', COVER)
    os.makedirs(os.path.join(P, 'fonts'), exist_ok=True)
    shutil.copy(APP.font, os.path.join(P, 'fonts', 'plus-jakarta-sans-latin-wght-normal.woff2'))
    # asset: originali di Lucide (nominati con la chiave) e, a parte, il logo dell'app
    groups = {'Logo': [], 'Categorie': [(APP.cat_icons[k], f'{k}.svg') for k in labels],
              'Conti': [(n, f'{t}.svg') for t, n in ACCOUNTS] + [('credit-card', 'carta.svg')],
              'Interfaccia': [(icone.SET['lucide']['icone'][k]['nome'], f'{icone.SET["lucide"]["icone"][k]["nome"]}.svg') for k in icone.UI + ['u-chevL', 'u-chevR', 'u-chevD']]
                             + [(n, f'{n}.svg') for n in ('delete', 'minus', 'smartphone')]}
    readmes = {'Logo': f'Logo di Statera, bilancia a tratto: disegno originale dell\'app, non Lucide. Generato da `scripts/icona-app.mjs` (app {APP.version}). `simbolo.svg` (grande, da 48 px) e `simbolo-piccolo.svg` (fino a 32 px): il simbolo da solo, in indaco #535AA6. `icona.svg`: riquadro arrotondato indaco col simbolo bianco (icona «any»). `maskable.svg`: piena fino agli angoli, simbolo nella zona sicura del 66%. Regole d\'uso nel manuale, sezione Marchio.',
               'Categorie': 'Icone delle categorie iniziali (Lucide, ISC). Il nome del file è la chiave salvata nel campo `icon` della categoria; nell\'app si colorano con la tinta della categoria (`currentColor`), qui sono nere.',
               'Conti': 'Icone dei conti, scelte dal tipo di conto (il nome del file è il tipo) e della carta. Inchiostro nero qui, `currentColor` nell\'app.',
               'Interfaccia': 'Icone dell\'interfaccia (Lucide, ISC), col nome Lucide. Inchiostro nero qui, `currentColor` nell\'app: prendono il colore del testo o di color-accent.'}
    plan = {}
    for g, items in groups.items():
        d = os.path.join(OUTDIR, 'asset', g); os.makedirs(d, exist_ok=True)
        w(f'assets/{g}/README.md', f'# {g}\n\n{readmes[g]}\n')
        for lucide_name, fname in items:
            shutil.copy(os.path.join(LUCIDE, 'icons', lucide_name + '.svg'), os.path.join(d, fname))
        plan[g] = [f for _, f in items]
    logo = {'simbolo.svg': APP.simbolo, 'simbolo-piccolo.svg': APP.simbolo_piccolo,
            'icona.svg': open(APP.p('public/icons/icon.svg')).read().strip(), 'maskable.svg': open(APP.p('public/icons/maskable.svg')).read().strip()}
    for fname, svg in logo.items():
        open(os.path.join(OUTDIR, 'asset', 'Logo', fname), 'w').write(svg + '\n')
    plan['Logo'] = list(logo)
    json.dump(plan, open(os.path.join(OUTDIR, 'piano-asset.json'), 'w'), indent=1)
    n = sum(len(v) for v in plan.values())
    print(f'app {APP.version} · componenti', len(COMP), '· asset', n, '· colori', len(C), '· stili', sum(len(g['styles']) for g in TYPE['groups']),
          '· token', sum(len(v) for v in FAM.values()))

if __name__ == '__main__':
    main()
