#!/usr/bin/env python3
"""Design system «Statera» (tipo Design System di claude.ai): token, carattere, componenti, icone.
I nomi dei token sono quelli di src/styles/tokens.css dell'app, così il passaggio al codice è diretto.
Uso: design_system.py <cartella di uscita> <cartella del pacchetto lucide-static> <file woff2 di Plus Jakarta Sans> <LICENSE del font>
Scrive <uscita>/project/… e <uscita>/icone/<gruppo>/<file>.svg (da caricare come asset)."""
import json, os, shutil, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palettes import cr
from altre import L, K, SW
import icone
from icone import seticon

OUTDIR, LUCIDE, FONT, FONT_LIC = sys.argv[1:5]
P = os.path.join(OUTDIR, 'project')
def w(rel, text):
    path = os.path.join(P, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text)

def ic(key, size=20, sw=2):
    return seticon('lucide', key, size, sw=sw)

def ratio(a, b):
    return f'{cr(a, b):.1f}'.replace('.', ',')

# ================================================================ token
C = []  # (nome, chiaro, scuro, uso)
def col(name, light, dark, usage):
    C.append({'name': name, 'value': {'light': light, 'dark': dark} if dark is not None else light, 'usage': usage})

col('color-bg', L['bg'], K['bg'], 'Sfondo di ogni schermata, dei pannelli che salgono dal basso e delle finestre su PC.')
col('color-surface', L['surf'], K['surf'], 'Schede, campi, barra di navigazione, barra laterale e pulsanti secondari appoggiati su color-bg.')
col('color-surface-2', L['surf2'], K['surf2'], 'Secondo livello su color-surface: pulsanti e tasti dentro una scheda, riga al passaggio del puntatore su PC, segmentato.')
col('color-border', L['border'], K['border'], 'Linee sottili: separatori tratteggiati, righe delle tabelle su PC, maniglia dei pannelli. Mai per contornare le schede.')
col('color-text', L['text'], K['text'], f'Testo e importi in uscita su color-bg, color-surface, color-surface-2 e color-accent-soft ({ratio(L["text"], L["bg"])}:1 chiaro, {ratio(K["text"], K["bg"])}:1 scuro su color-bg).')
col('color-text-muted', L['muted'], K['muted'], f'Testo secondario (categoria · conto, date, didascalie) su color-bg, color-surface e color-surface-2: minimo {ratio(L["muted"], L["surf2"])}:1 in chiaro, {ratio(K["muted"], K["surf2"])}:1 in scuro. Anche interruttore spento e bordo delle caselle.')
col('color-primary', L['primary'], K['primary'], 'Il colore di Statera, come riempimento: pulsante +, pulsante principale, segmento attivo, interruttore acceso, casella spuntata, riquadro «hai risparmiato» in tema chiaro. Sopra va color-on-primary.')
col('color-on-primary', L['onp'], K['onp'], f'Testo e icone su color-primary ({ratio(L["onp"], L["primary"])}:1 chiaro, {ratio(K["onp"], K["primary"])}:1 scuro).')
col('color-accent', L['accent'], K['accent'], f'Testo e icone d\'accento: link, icone delle azioni rapide, voce attiva della barra, pulsante tenue. Su color-surface ({ratio(L["accent"], L["surf"])}:1 / {ratio(K["accent"], K["surf"])}:1), color-bg e color-accent-soft ({ratio(L["accent"], L["accentSoft"])}:1 / {ratio(K["accent"], K["accentSoft"])}:1).')
col('color-accent-soft', L['accentSoft'], K['accentSoft'], 'Fondo tenue: cerchi delle azioni rapide, chip attivi, parola trovata in Cerca, sezione «Da registrare», voce attiva della barra laterale, riquadro «hai risparmiato» in tema scuro.')
col('color-income', L['income'], K['income'], f'Solo le entrate: importi positivi e icona del riquadro Entrate, su color-surface e color-bg ({ratio(L["income"], L["surf"])}:1 / {ratio(K["income"], K["surf"])}:1). Non su color-accent-soft in chiaro ({ratio(L["income"], L["accentSoft"])}:1).')
col('color-expense-icon', L['outIcon'], K['outIcon'], 'Solo l\'icona del riquadro Uscite (grafica, almeno 3:1). Gli importi in uscita restano color-text.')
col('status-warning', L['warn'], K['warn'], f'Attenzione: barra del budget quasi esaurito (da 80%) e fondo dei promemoria, sempre con simbolo e testo. È grafica, non testo: in chiaro arriva a {ratio(L["warn"], L["surf"])}:1 su bianco.')
col('color-danger', L['danger'], K['danger'], f'Pericolo, solo per ciò che cancella o è fallito: Elimina, Elimina tutti i dati, salvataggio non riuscito, troppi tentativi del PIN. Testo su color-surface ({ratio(L["danger"], L["surf"])}:1 / {ratio(K["danger"], K["surf"])}:1) e color-bg.')
col('color-on-danger', L['onDanger'], K['onDanger'], f'Testo e icone sul pulsante di pericolo ({ratio(L["onDanger"], L["danger"])}:1 / {ratio(K["onDanger"], K["danger"])}:1).')
col('status-critical', '{color-danger}', None, 'Budget superato (oltre 100%): barra e simbolo, sempre con la parola «Superato».')
col('color-focus', '{color-primary}', None, 'Anello del focus da tastiera: 2 px pieni, staccato di 2 px. Almeno 3:1 su color-bg, color-surface e color-accent-soft in entrambi i temi.')
col('color-backdrop', 'rgba(20, 22, 40, 0.5)', 'rgba(0, 0, 0, 0.6)', 'Velo sotto i pannelli e le finestre.')
col('toast-bg', L['toast'], K['toast'], 'Fondo degli avvisi a comparsa: colori invertiti rispetto al tema.')
col('toast-text', L['onToast'], K['onToast'], f'Testo degli avvisi a comparsa su toast-bg ({ratio(L["onToast"], L["toast"])}:1 / {ratio(K["onToast"], K["toast"])}:1).')
col('toast-action', L['toastAction'], K['toastAction'], f'Azione dell\'avviso (Annulla, Aggiorna) su toast-bg ({ratio(L["toastAction"], L["toast"])}:1 / {ratio(K["toastAction"], K["toast"])}:1).')
col('chart-income', L['chIn'], K['chIn'], 'Grafici: entrate. Coppia blu/arancio scelta per chi non distingue rosso e verde; legenda sempre visibile.')
col('chart-expense', L['chOut'], K['chOut'], 'Grafici: uscite, e barre delle categorie in Analisi.')
col('chart-worth', '{color-primary}', None, 'Grafici: andamento del patrimonio (una sola serie).')
col('chart-track', '{color-surface-2}', None, 'Binario delle barre di budget, obiettivi e categorie.')
col('chart-grid', '{color-border}', None, 'Linee della griglia e asse dei grafici.')
NAMES_SW = ['verde', 'terracotta', 'blu', 'nocciola', 'viola', 'petrolio', 'rosa', 'oliva']
for i, (k, v) in enumerate(SW.items()):
    col(f'swatch-{k}', v, None, f'Tinta {k} ({NAMES_SW[i]}) di conti, categorie e obiettivi: i dati salvano solo «{k}». Uguale nei due temi; per l\'icona di categoria vedi IconaCategoria.')

FAMILY = '"Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
def st(name, size, lh, weight, sample, usage, ls=None):
    d = {'name': name, 'fontSize': f'{size}px', 'lineHeight': f'{lh}px', 'fontWeight': weight, 'sample': sample, 'usage': usage}
    if ls: d['letterSpacing'] = ls
    return d
TYPE = {
 'fonts': [{'family': 'Plus Jakarta Sans', 'file': 'fonts/plus-jakarta-sans-latin-wght-normal.woff2', 'weight': '200 800', 'style': 'normal'}],
 'families': {'sans': FAMILY},
 'groups': [
  {'name': 'Importi', 'family': 'sans', 'styles': [
    st('importo-xl', 56, 64, 800, '42,30 €', 'Importo mentre lo scrivi in Nuova spesa.', '-0.03em'),
    st('importo-l', 46, 52, 800, '+1.325,65 €', 'Saldo del mese in Movimenti; i centesimi a 28 px.', '-0.03em'),
    st('importo-m', 34, 40, 800, '8.412,90 €', 'Patrimonio, saldo di un conto, numero di buoni.', '-0.03em'),
    st('importo-s', 20, 26, 800, '2.010,00 €', 'Riquadri Entrate e Uscite, totali di Cerca.', '-0.02em'),
    st('tasto-pin', 28, 32, 700, '7', 'Cifre del tastierino del PIN.')]},
  {'name': 'Titoli', 'family': 'sans', 'styles': [
    st('titolo-1', 26, 32, 800, 'Analisi', 'Titolo delle sezioni principali (Movimenti, Conti, Analisi, Altro).', '-0.02em'),
    st('titolo-2', 22, 28, 800, 'Conto corrente', 'Schermate aperte da un\'altra, finestre e pannelli.', '-0.02em'),
    st('titolo-3', 17, 24, 800, 'Budget del mese', 'Titolo di una scheda.')]},
  {'name': 'Testo', 'family': 'sans', 'styles': [
    st('corpo', 15, 22, 400, 'Gli automatici si registrano da soli.', 'Spiegazioni e messaggi.'),
    st('corpo-forte', 15, 20, 700, 'Q8 via Appia', 'Titolo di una riga, importo in un elenco.'),
    st('campo', 16, 22, 500, 'Conad', 'Testo dentro i campi: 16 px perché il telefono non ingrandisca la pagina.'),
    st('secondario', 13, 18, 500, 'Carburante · Bancomat', 'Seconda riga, date, didascalie, in color-text-muted.'),
    st('pulsante', 15, 20, 800, 'Salva spesa', 'Etichetta dei pulsanti normali e piccoli (questi a 13 px).'),
    st('pulsante-l', 17, 24, 800, 'Registra la prima spesa', 'Pulsante grande in fondo a un pannello.')]},
  {'name': 'Etichette', 'family': 'sans', 'styles': [
    st('etichetta-campo', 13, 18, 700, 'Descrizione', 'Nome sopra un campo, in color-text-muted.'),
    st('etichetta', 11, 14, 800, 'USCITE', 'Titolo di un gruppo, scritto in maiuscolo con text-transform.', '0.06em'),
    st('nav', 11, 14, 600, 'Movimenti', 'Voci della barra di navigazione (attiva: peso 700).'),
    st('badge', 11, 14, 700, 'non incide', 'Etichette piccole nelle righe (Automatico, non incide).'),
    st('tasto', 12, 16, 700, 'Esc', 'Tasti delle scorciatoie.')]},
 ]}
SPACE = [('space-1', '4px', 'Tra icona e testo piccoli; spessore interno del segmentato.'),
         ('space-2', '8px', 'Tra chip e tra pulsanti vicini; tra etichetta e campo.'),
         ('space-3', '12px', 'Tra icona e testi di una riga; tra le righe di un modulo.'),
         ('space-4', '16px', 'Tra le schede di una schermata; margine della barra flottante.'),
         ('space-5', '20px', 'Margine laterale delle schermate del telefono; interno delle schede.'),
         ('space-6', '24px', 'Interno delle finestre su PC; tra colonne su PC.'),
         ('space-7', '32px', 'Sopra un titolo di gruppo; stati vuoti.'),
         ('space-8', '48px', 'Distanza della finestra dal bordo alto su PC.')]
RADIUS = [('radius-xs', '8px', 'Tasti delle scorciatoie, caselle di spunta.'),
          ('radius-sm', '12px', 'Icone dell\'interfaccia su fondo, elementi piccoli.'),
          ('radius-md', '16px', 'Campi, riga evidenziata, voci della barra laterale, avvisi.'),
          ('radius-lg', '24px', 'Schede, barra laterale, riquadri.'),
          ('radius-xl', '32px', 'Pannelli dal basso (solo gli angoli alti) e finestre su PC.'),
          ('radius-full', '999px', 'Pulsanti, chip, segmentato, barra flottante, cerchi.')]
SHADOW = [('shadow-1', '0 1px 3px rgba(23, 25, 40, 0.18)', '0 1px 3px rgba(0, 0, 0, 0.5)', 'Pomello dell\'interruttore.'),
          ('shadow-2', '0 6px 24px rgba(23, 25, 40, 0.10)', '0 6px 24px rgba(0, 0, 0, 0.45)', 'Barra flottante, barra laterale, avvisi, suggerimenti.'),
          ('shadow-3', '0 24px 64px rgba(23, 25, 40, 0.28)', '0 24px 64px rgba(0, 0, 0, 0.6)', 'Pannelli e finestre sopra il velo.'),
          ('shadow-fab', '0 8px 20px rgba(83, 90, 166, 0.35)', '0 8px 20px rgba(0, 0, 0, 0.5)', 'Pulsante + della barra.')]
SIZES = [('size-touch', '44px', 'Area di tocco minima di ogni comando; pulsanti normali e pulsanti icona.'),
         ('size-field', '52px', 'Altezza dei campi.'),
         ('size-btn-l', '58px', 'Pulsante grande in fondo a un pannello.'),
         ('size-btn-s', '36px', 'Pulsante piccolo e chip (l\'area di tocco resta 44 px con il margine).'),
         ('size-cat-s', '32px', 'Icona di categoria piccola: sottocategorie, preferiti, tabelle su PC.'),
         ('size-cat', '44px', 'Icona di categoria nelle righe.'),
         ('size-cat-l', '52px', 'Icona di categoria nella griglia di Nuova spesa; azioni rapide.'),
         ('size-fab', '56px', 'Pulsante + al centro della barra.'),
         ('size-nav', '66px', 'Altezza della barra flottante del telefono.'),
         ('size-sidebar', '232px', 'Larghezza della barra laterale su PC.'),
         ('size-icon', '20px', 'Icone dell\'interfaccia; 22 px nella barra, 16 px nei chip.'),
         ('content-max', '760px', 'Larghezza massima delle finestre su PC e del testo lungo.')]
STATES = [('opacity-disabled', '0.45', 'Comandi disattivati: opacità, niente ombra né movimento.'),
          ('focus-width', '2px', 'Spessore dell\'anello del focus.'),
          ('focus-offset', '2px', 'Distanza dell\'anello dal comando.')]
MOTION = [('duration-fast', '120ms', 'Pressione di un pulsante, cambio di colore.'),
          ('duration-base', '200ms', 'Interruttore, segmentato, avvisi che compaiono.'),
          ('duration-slow', '280ms', 'Pannello che sale dal basso, finestra che si apre.'),
          ('ease-standard', 'cubic-bezier(0.2, 0, 0, 1)', 'Ingressi e cambi di stato.'),
          ('ease-exit', 'cubic-bezier(0.3, 0, 0.8, 0.15)', 'Uscite: pannelli che si chiudono, avvisi che spariscono.')]
lst = lambda rows: {'tokens': [{'name': n, 'value': v, 'usage': u} for n, v, u in rows]}
TOKENS = {'name': 'Statera', 'version': 1,
          'color': {'themes': [{'id': 'light', 'name': 'Chiaro'}, {'id': 'dark', 'name': 'Scuro'}], 'tokens': C},
          'type': TYPE, 'spacing': lst(SPACE), 'radius': lst(RADIUS),
          'shadow': {'tokens': [{'name': n, 'value': {'light': a, 'dark': b}, 'usage': u} for n, a, b, u in SHADOW]},
          'dimensioni': lst(SIZES), 'stati': lst(STATES), 'animazione': lst(MOTION)}

# ================================================================ foglio dei componenti
CSS = r'''/* Statera — componenti di riferimento. Tutti i valori vengono da tokens.css (tokens.json):
   qui ci sono solo struttura e stati. Prefisso st-. */
.st { font-family: var(--font-sans); color: var(--color-text); font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; --st-ground: var(--color-bg); }
.st *, .st *::before, .st *::after { box-sizing: border-box; }
.st button, .st input, .st select { font: inherit; color: inherit; margin: 0; }
.st h1, .st h2, .st h3, .st p { margin: 0; }
.st ul { list-style: none; margin: 0; padding: 0; }
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
.st-btn--s { height: var(--size-btn-s); padding: 0 var(--space-3); }
.st-btn--primary { background: var(--color-primary); color: var(--color-on-primary); }
.st-btn--secondary { background: var(--color-surface); color: var(--color-text); }
.st-btn--tonal { background: var(--color-surface-2); color: var(--color-text); }
.st-btn--soft { background: var(--color-accent-soft); color: var(--color-accent); }
.st-btn--danger { background: var(--color-danger); color: var(--color-on-danger); }
.st-btn--link { background: transparent; color: var(--color-accent); padding: 0 var(--space-2); }
.st-btn:hover, .st-btn.is-hover { box-shadow: inset 0 0 0 100px color-mix(in srgb, currentColor 8%, transparent); }
.st-btn:active, .st-btn.is-pressed { transform: scale(0.97); box-shadow: inset 0 0 0 100px color-mix(in srgb, currentColor 14%, transparent); }
.st-btn:disabled, .st-btn[aria-disabled="true"] { opacity: var(--opacity-disabled); cursor: not-allowed; transform: none; box-shadow: none; }
.st-iconbtn { width: var(--size-touch); height: var(--size-touch); border-radius: var(--radius-full); border: none; padding: 0; background: var(--color-surface); color: var(--color-text); display: inline-flex; align-items: center; justify-content: center; cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-standard); }
.st-iconbtn--tonal { background: var(--color-surface-2); }
.st-iconbtn:active, .st-iconbtn.is-pressed { transform: scale(0.94); }

/* Barra di navigazione (telefono) */
.st-nav { height: var(--size-nav); border-radius: var(--radius-full); background: var(--color-surface); box-shadow: var(--shadow-2); display: flex; align-items: center; padding: 0 var(--space-2); }
.st-nav__item { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 3px; text-decoration: none; color: var(--color-text-muted); }
.st-nav__item[aria-current="page"] { color: var(--color-accent); font-weight: 700; }
.st-fab { width: var(--size-fab); height: var(--size-fab); margin-top: -26px; border-radius: var(--radius-full); border: 4px solid var(--color-bg); background: var(--color-primary); color: var(--color-on-primary);
  display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-fab); cursor: pointer; flex-shrink: 0; padding: 0; }

/* Barra laterale (PC) */
.st-side { width: var(--size-sidebar); background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-3); display: flex; flex-direction: column; gap: var(--space-4); box-shadow: var(--shadow-2); }
.st-side__brand { display: flex; align-items: center; gap: var(--space-2); padding: 0 var(--space-2); }
.st-side__mark { width: 36px; height: 36px; border-radius: var(--radius-full); background: var(--color-primary); color: var(--color-on-primary); display: flex; align-items: center; justify-content: center; }
.st-side__links { display: flex; flex-direction: column; gap: var(--space-1); }
.st-side__link { height: var(--size-touch); padding: 0 var(--space-3); border-radius: var(--radius-md); display: flex; align-items: center; gap: var(--space-3); text-decoration: none; color: var(--color-text); }
.st-side__link > span { flex: 1; }
.st-side__link:hover, .st-side__link.is-hover { background: var(--color-surface-2); }
.st-side__link[aria-current="page"] { background: var(--color-accent-soft); color: var(--color-accent); }
.st-side__status { padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); background: var(--color-bg); display: flex; align-items: center; gap: var(--space-2); }
.st-side__status svg { color: var(--color-income); }

/* Azione rapida */
.st-quick { border: none; background: transparent; padding: 0; min-width: 72px; display: inline-flex; flex-direction: column; align-items: center; gap: var(--space-2); color: var(--color-text); cursor: pointer; }
.st-quick__circle { width: var(--size-cat-l); height: var(--size-cat-l); border-radius: var(--radius-full); background: var(--color-accent-soft); color: var(--color-accent); display: flex; align-items: center; justify-content: center;
  transition: transform var(--duration-fast) var(--ease-standard); }
.st-quick:active .st-quick__circle, .st-quick.is-pressed .st-quick__circle { transform: scale(0.94); }

/* Icona di categoria: tinta al 15% con icona colorata (chiaro), al 30% con icona bianca (scuro) */
.st-cat { --cat: var(--swatch-s1); width: var(--size-cat); height: var(--size-cat); border-radius: var(--radius-full); display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: color-mix(in srgb, var(--cat) 15%, transparent); color: var(--cat); }
[data-theme="dark"] .st-cat { background: color-mix(in srgb, var(--cat) 30%, transparent); color: #FFFFFF; }
.st-cat--s { width: var(--size-cat-s); height: var(--size-cat-s); }
.st-cat--l { width: var(--size-cat-l); height: var(--size-cat-l); }
.st-cat__letter { font-size: 18px; font-weight: 800; line-height: 1; }
.st-cat--s .st-cat__letter { font-size: 14px; }
.st-cat--s1 { --cat: var(--swatch-s1); } .st-cat--s2 { --cat: var(--swatch-s2); } .st-cat--s3 { --cat: var(--swatch-s3); } .st-cat--s4 { --cat: var(--swatch-s4); }
.st-cat--s5 { --cat: var(--swatch-s5); } .st-cat--s6 { --cat: var(--swatch-s6); } .st-cat--s7 { --cat: var(--swatch-s7); } .st-cat--s8 { --cat: var(--swatch-s8); }
.st-catpick { border: none; background: transparent; padding: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; color: var(--color-text); cursor: pointer; text-align: center; }
.st-catpick[aria-pressed="true"] .st-cat { background: var(--cat); color: #FFFFFF; box-shadow: 0 0 0 3px var(--st-ground), 0 0 0 5px var(--cat); }
.st-catpick[aria-pressed="true"] { font-weight: 800; }
.st-catgrid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: var(--space-3); column-gap: var(--space-1); }

/* Riga di movimento */
.st-mrow { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) 0; }
.st-mrow__text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.st-mrow__sub { color: var(--color-text-muted); }
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
.st-hero { background: var(--color-primary); color: var(--color-on-primary); border-radius: var(--radius-lg); padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-2); }
[data-theme="dark"] .st-hero { background: var(--color-accent-soft); color: var(--color-text); }
.st-hero__pill { height: 30px; padding: 0 var(--space-3); border-radius: var(--radius-full); background: color-mix(in srgb, currentColor 16%, transparent); display: inline-flex; align-items: center; }
.st-tile { flex: 1; min-width: 0; background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4); display: flex; align-items: center; gap: var(--space-3); }
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
.st-seg__opt[aria-pressed="true"] { background: var(--color-primary); color: var(--color-on-primary); }

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
.st-toast { background: var(--toast-bg); color: var(--toast-text); border-radius: var(--radius-md); min-height: 52px; padding: 0 var(--space-2) 0 var(--space-4); display: flex; align-items: center; gap: var(--space-3); box-shadow: var(--shadow-2); }
.st-toast__text { flex: 1; }
.st-toast__action { height: var(--size-touch); padding: 0 var(--space-3); border: none; border-radius: var(--radius-full); background: transparent; color: var(--toast-action); cursor: pointer; }
.st-banner { border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); display: flex; gap: var(--space-3); align-items: flex-start; background: var(--color-accent-soft); color: var(--color-text); }
.st-banner__icon { color: var(--color-accent); margin-top: 1px; }
.st-banner__body { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.st-banner--ok { background: color-mix(in srgb, var(--color-income) 14%, var(--color-bg)); }
.st-banner--ok .st-banner__icon { color: var(--color-income); }
.st-banner--warning { background: color-mix(in srgb, var(--status-warning) 20%, var(--color-bg)); }
.st-banner--warning .st-banner__icon { color: var(--color-text); }
.st-banner--danger { background: color-mix(in srgb, var(--color-danger) 12%, var(--color-bg)); }
.st-banner--danger .st-banner__icon { color: var(--color-danger); }

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
.st-chart__key { width: 10px; height: 10px; border-radius: 2px; }
.st-chart__plot { display: flex; gap: var(--space-1); align-items: flex-end; border-bottom: 1px solid var(--chart-grid); }
.st-chart__month { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; color: var(--color-text-muted); }
.st-chart__bars { display: flex; align-items: flex-end; gap: 3px; height: 100px; }
.st-chart__bar { width: 12px; border-radius: 6px 6px 0 0; }
.st-in { background: var(--chart-income); } .st-out { background: var(--chart-expense); }

/* Stato vuoto */
.st-empty { background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-7) var(--space-5); display: flex; flex-direction: column; align-items: center; gap: var(--space-2); text-align: center; }
.st-empty__icon { width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--color-accent-soft); color: var(--color-accent); display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-1); }
.st-empty p { color: var(--color-text-muted); max-width: 32ch; }

/* Tastierino del PIN */
.st-pin { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-4) var(--space-5); width: 290px; }
.st-pin__key { width: 76px; height: 76px; justify-self: center; border-radius: var(--radius-full); border: none; padding: 0; background: var(--color-surface); color: var(--color-text); display: flex; align-items: center; justify-content: center; cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-standard); }
.st-pin__key:active, .st-pin__key.is-pressed { transform: scale(0.94); background: var(--color-surface-2); }
.st-pin__key--soft { background: var(--color-accent-soft); color: var(--color-accent); }
.st-pin__key--ghost { background: transparent; }
.st-pin__dots { display: flex; gap: 14px; align-items: center; justify-content: center; height: 40px; }
.st-pin__dot { width: 14px; height: 14px; border-radius: var(--radius-full); background: var(--color-text); }
.st-pin__caret { width: 2px; height: 22px; border-radius: 1px; background: var(--color-primary); }

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
comp('Pulsante', 'Azioni', 340, f'''Il comando a pillola: principale, secondario, tenue, di pericolo o come link.

## Quando usarlo
- **Principale** (`st-btn--primary`): l'azione che chiude il compito, una sola per schermata o pannello (Salva spesa, Continua).
- **Secondario** (`st-btn--secondary` su color-bg, `st-btn--tonal` dentro una scheda): alternative (Salva e aggiungine un'altra, Salta).
- **Tenue** (`st-btn--soft`): azioni utili ma non urgenti dentro i contenuti (Esporta CSV, Aggiungi una spesa).
- **Pericolo** (`st-btn--danger`): solo per confermare una cancellazione, mai come primo pulsante di una schermata.
- **Link** (`st-btn--link`): azioni di poco peso (Ho dimenticato il PIN, Lo faccio dopo).

## Struttura
`<button type="button" class="st-btn st-btn--primary pulsante">` con un'icona Lucide facoltativa a sinistra (18 px) e il testo. Grande: `st-btn--l` con `pulsante-l`, a tutta larghezza in fondo a un pannello. Piccolo: `st-btn--s`, testo a 13 px, solo dentro righe e schede.

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
<div class="st-line">
<span class="st-stack">{card_txt('Passaggio')}<button type="button" class="st-btn st-btn--primary pulsante is-hover">Registra</button></span>
<span class="st-stack">{card_txt('Premuto')}<button type="button" class="st-btn st-btn--primary pulsante is-pressed">Registra</button></span>
<span class="st-stack">{card_txt('Focus')}<button type="button" class="st-btn st-btn--primary pulsante is-focus">Registra</button></span>
<span class="st-stack">{card_txt('Disattivato')}<button type="button" class="st-btn st-btn--primary pulsante" disabled>Registra</button></span>
<span class="st-stack">{card_txt('Piccolo')}<button type="button" class="st-btn st-btn--s st-btn--primary pulsante" style="font-size: 13px">{ic('u-check', 16, 2.2)}Registra</button></span></div>
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
comp('AzioneRapida', 'Azioni', 150, '''Un cerchio tenue con etichetta sotto, per le quattro azioni più frequenti sotto il saldo.

## Quando usarla
Solo in fila da quattro, sotto un importo grande: Spesa, Entrata, Trasferisci, Preferiti in Movimenti; Spesa, Entrata, Trasferisci, Allinea saldo nel dettaglio di un conto.

## Struttura
`<button class="st-quick secondario">` con dentro `st-quick__circle` (52 px, color-accent-soft, icona in color-accent a 22 px) e il testo. Peso 600.

## Stati
Premuto: il cerchio scala a 0,94. Focus: anello sul pulsante intero.
''', f'''<div class="st st-stage" style="justify-content: center">
<div style="display: flex; width: 350px">
<button type="button" class="st-quick secondario" style="flex: 1; font-weight: 600"><span class="st-quick__circle">{ic('u-out', 22, 2.1)}</span>Spesa</button>
<button type="button" class="st-quick secondario" style="flex: 1; font-weight: 600"><span class="st-quick__circle">{ic('u-in', 22, 2.1)}</span>Entrata</button>
<button type="button" class="st-quick secondario" style="flex: 1; font-weight: 600"><span class="st-quick__circle">{ic('u-swap', 22, 2.1)}</span>Trasferisci</button>
<button type="button" class="st-quick secondario is-pressed" style="flex: 1; font-weight: 600"><span class="st-quick__circle">{ic('u-star', 22, 2.1)}</span>Preferiti</button></div></div>''')

# --- BarraNavigazione
nav_items = [('u-list', 'Movimenti', True), ('u-wallet', 'Conti', False), None, ('u-chart', 'Analisi', False), ('u-more', 'Altro', False)]
nav = ''.join('<button type="button" class="st-fab" aria-label="Nuovo movimento">' + ic('u-plus', 26, 2.4) + '</button>' if it is None else
              f'<a href="#" class="st-nav__item nav"{" aria-current=\"page\"" if it[2] else ""}>{ic(it[0], 22, 2.1 if it[2] else 1.8)}{it[1]}</a>' for it in nav_items)
comp('BarraNavigazione', 'Navigazione', 170, '''La barra flottante del telefono: quattro sezioni e il pulsante + al centro.

## Struttura
`<nav aria-label="Sezioni" class="st-nav">` a `space-3` dai bordi e `space-4` dal fondo, alta `size-nav`, con `shadow-2`. Voci: `<a class="st-nav__item nav">` con icona da 22 px; la sezione corrente ha `aria-current="page"` (color-accent, peso 700, tratto 2,1). Al centro `st-fab`: 56 px, color-primary, bordo di 4 px in color-bg, `shadow-fab`, `aria-label="Nuovo movimento"`.

## Regole
- Compare solo nelle quattro sezioni principali. Le schermate aperte da un'altra (dettaglio conto, Cerca, Ricorrenti, Categorie) hanno la freccia indietro e niente barra.
- Il contenuto scorre sotto la barra: lascia 96 px liberi in fondo.
- Su PC la sostituisce la BarraLaterale.
''', f'''<div class="st st-stage" style="justify-content: center; padding-top: var(--space-7)"><nav aria-label="Sezioni" class="st-nav" style="width: 366px">{nav}</nav></div>''')

# --- BarraLaterale
side_links = [('u-list', 'Movimenti', None, True), ('u-wallet', 'Conti', None, False), ('u-chart', 'Analisi', None, False), ('u-search', 'Cerca', '/', False), ('u-more', 'Altro', None, False)]
sl = ''.join(f'<a href="#" class="st-side__link corpo-forte{" is-hover" if lab == "Conti" else ""}"{" aria-current=\"page\"" if on else ""}>{ic(i, 20, 2.1 if on else 1.8)}<span>{lab}</span>{"<kbd class=\"st-kbd tasto\">" + k + "</kbd>" if k else ""}</a>' for i, lab, k, on in side_links)
comp('BarraLaterale', 'Navigazione', 600, '''La navigazione su PC: marchio, «Nuovo movimento», sezioni, stato della sincronizzazione e profilo.

## Struttura
`<aside class="st-side">` largo `size-sidebar`, color-surface, `radius-lg`, `shadow-2`, a tutta altezza. Dentro, dall'alto: il marchio (segnaposto: bilancia `scale` in un cerchio color-primary, poi «Statera» in `titolo-3`); il Pulsante principale «Nuovo movimento» con il Tasto `N`; `<nav aria-label="Sezioni">` con le voci `st-side__link` (la corrente con `aria-current="page"`); in fondo lo stato della sincronizzazione (`st-side__status`) e il profilo.

## Regole
- Le scorciatoie si scrivono accanto alla voce (Cerca `/`), non solo nell'elenco.
- Sotto i 760 px la barra va in cima e le voci si dispongono su due colonne.
''', f'''<div class="st st-stage"><aside class="st-side" style="min-height: 540px">
<div class="st-side__brand"><span class="st-side__mark" aria-hidden="true">{ic('rettifica', 20, 2.1)}</span><span class="titolo-3">Statera</span></div>
<button type="button" class="st-btn st-btn--primary pulsante" style="justify-content: flex-start; padding: 0 var(--space-3) 0 var(--space-4)">{ic('u-plus', 20, 2.4)}<span style="flex: 1; text-align: left">Nuovo movimento</span><kbd class="st-kbd st-kbd--on-primary tasto">N</kbd></button>
<nav aria-label="Sezioni" class="st-side__links">{sl}</nav>
<span style="flex: 1"></span>
<div class="st-side__status">{ic('u-cloud', 20)}<span class="st-stack" style="gap: 0"><span class="secondario" style="font-weight: 800">Sincronizzato</span><span class="secondario st-muted">2 minuti fa</span></span></div>
<a href="#" style="display: flex; align-items: center; gap: var(--space-2); padding: 0 var(--space-2); color: var(--color-text); text-decoration: none"><span aria-hidden="true" class="st-cat st-cat--s st-cat--s3" style="background: var(--color-accent-soft); color: var(--color-accent)"><span class="st-cat__letter">L</span></span><span class="st-stack" style="gap: 0; flex: 1"><span class="corpo-forte" style="font-size: 14px">Livio</span><span class="secondario st-muted">Profilo personale</span></span>{ic('u-chevD', 18)}</a></aside></div>''')

# --- IconaCategoria
cats = [('spesa', 's1', 'Spesa alimentare', False), ('pasti', 's2', 'Pasti fuori', True), ('carburante', 's3', 'Carburante', False), ('mezzi', 's4', 'Mezzi pubblici', False),
        ('casa', 's7', 'Casa', False), ('salute', 's6', 'Salute', False), ('svago', 's5', 'Svago', False), (None, 's8', 'Orto', False)]
cg = ''.join(f'<button type="button" class="st-catpick secondario" aria-pressed="{"true" if on else "false"}" style="font-size: 11px"><span class="st-cat st-cat--l st-cat--{s}" aria-hidden="true">{ic(k, 22) if k else "<span class=\"st-cat__letter\">" + lab[0] + "</span>"}</span>{lab}</button>' for k, s, lab, on in cats)
comp('IconaCategoria', 'Contenuti', 300, '''Il cerchio colorato che identifica una categoria o un conto: icona Lucide sulla sua tinta.

## Regole di colore
- Tema chiaro: fondo = tinta (`swatch-s1`…`swatch-s8`) al 15%, icona nella tinta piena.
- Tema scuro: fondo = tinta al 30%, icona bianca.
- Selezionata (griglia di Nuova spesa, scelta dell'icona): fondo pieno nella tinta, icona bianca, doppio anello (3 px del colore di fondo, poi 2 px della tinta). L'anello cambia anche la forma, quindi la scelta si vede anche senza colore.

## Struttura
`<span class="st-cat st-cat--s2" aria-hidden="true">` con l'icona a 20 px (44 px), 22 px in `st-cat--l` (52 px), 16 px in `st-cat--s` (32 px). Il nome della categoria sta sempre accanto o sotto, in testo: il cerchio è decorativo. Senza icona, o con una chiave sconosciuta: l'iniziale del nome (`st-cat__letter`). Nella griglia, ogni voce è `<button class="st-catpick" aria-pressed>`.

## Dati
Il colore arriva dalla chiave salvata (`s1`…`s8`), l'icona dalla chiave del campo `icon` (vedi Iconografia).
''', f'''<div class="st st-stage st-stage--col"><div class="st-card" style="max-width: 360px"><div class="st-catgrid">{cg}</div></div>
<div class="st-line"><span class="st-cat st-cat--s st-cat--s7" aria-hidden="true">{ic('bollette', 16)}</span><span class="st-cat st-cat--s3" aria-hidden="true">{ic('c-corrente')}</span><span class="st-cat st-cat--s2" aria-hidden="true">{ic('buoni')}</span><span class="st-cat st-cat--s1" aria-hidden="true"><span class="st-cat__letter">S</span></span></div></div>''')

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
- `st-hero`: il riquadro del risparmio in Analisi. color-primary con color-on-primary in chiaro; in scuro color-accent-soft con color-text, per non abbagliare.
- `st-tile`: i riquadri Entrate e Uscite, con l'icona nel suo cerchio.

## Regole
Una schermata alterna schede e spazi `space-4`: niente schede dentro schede, niente bordi colorati su un lato.
''', f'''<div class="st st-stage" style="align-items: flex-start">
<section class="st-card" style="width: 330px"><div class="st-card__head"><h2 class="titolo-3">Obiettivi di risparmio</h2><button type="button" class="st-btn st-btn--s st-btn--soft pulsante" style="font-size: 13px">{ic('u-plus', 16, 2.2)}Nuovo</button></div><p class="corpo st-muted">Una vacanza, un fondo per gli imprevisti.</p></section>
<section class="st-hero" style="width: 330px"><span class="corpo-forte" style="font-weight: 600">A novembre hai risparmiato</span><span class="importo-m">1.325,65 €</span><span class="st-line" style="gap: var(--space-2)"><span class="st-hero__pill badge" style="font-size: 13px">66% delle entrate</span></span></section>
<div class="st-line" style="width: 330px; flex-wrap: nowrap; gap: var(--space-2)"><div class="st-tile"><span class="st-tile__icon st-tile__icon--in">{ic('u-in', 18, 2.2)}</span><span class="st-stack" style="gap: 0"><span class="secondario st-muted">Entrate</span><span class="importo-s" style="font-size: 16px">2.010,00 €</span></span></div><div class="st-tile"><span class="st-tile__icon st-tile__icon--out">{ic('u-out', 18, 2.2)}</span><span class="st-stack" style="gap: 0"><span class="secondario st-muted">Uscite</span><span class="importo-s" style="font-size: 16px">684,35 €</span></span></div></div></div>''')

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
`<div role="group" aria-label="…" class="st-seg">` con un `<button class="st-seg__opt pulsante" aria-pressed>` per opzione. L'opzione scelta è color-primary con color-on-primary; le altre color-text-muted su color-surface-2. Il cambio dura `duration-base`.

## Regole
Al massimo tre opzioni, con parole brevi («Trasf.» se lo spazio manca). Per più scelte usa i Chip.
''', f'''<div class="st st-stage st-stage--col" style="max-width: 380px">
<div role="group" aria-label="Tipo di movimento" class="st-seg"><button type="button" class="st-seg__opt pulsante" aria-pressed="true">Uscita</button><button type="button" class="st-seg__opt pulsante" aria-pressed="false">Entrata</button><button type="button" class="st-seg__opt pulsante" aria-pressed="false">Trasferimento</button></div>
<div role="group" aria-label="Periodo" class="st-seg" style="width: 200px"><button type="button" class="st-seg__opt pulsante" aria-pressed="false">Mese</button><button type="button" class="st-seg__opt pulsante is-focus" aria-pressed="true">Anno</button></div></div>''')

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
def banner(kind, icn, title, sub, action=''):
    return (f'<div role="{"alert" if kind == "danger" else "status"}" class="st-banner st-banner--{kind}"><span class="st-banner__icon">{ic(icn, 20, 2.2)}</span><span class="st-banner__body"><span class="corpo-forte" style="font-size: 14px; font-weight: 800">{title}</span>'
            f'<span class="secondario">{sub}</span>{action}</span></div>')
comp('Avviso', 'Stato e messaggi', 560, '''Messaggi all'utente: conferme a comparsa in basso e riquadri dentro le schermate.

## Conferma a comparsa
`<div role="status" class="st-toast">`: toast-bg con toast-text (colori invertiti rispetto al tema), icona, una frase al passato e una sola azione in toast-action (Annulla, Aggiorna). Compare in basso sopra la barra per 5 secondi, entra con `duration-base` ed esce con `ease-exit`; con un'azione resta finché non la si usa o non si tocca altrove.

## Riquadro
`st-banner` con icona, titolo in grassetto e una frase su cosa fare:
- informazione (color-accent-soft): sincronizzazione sospesa, sei offline;
- `st-banner--ok`: operazione riuscita che va letta (backup ripristinato);
- `st-banner--warning`: budget superato, backup vecchio; icona color-text;
- `st-banner--danger` con `role="alert"`: salvataggio non riuscito, troppi tentativi del PIN.

## Testi
Prima cosa è successo, poi cosa fare, senza colpe e senza punti esclamativi: «Accesso a Google scaduto. I dati sono al sicuro qui: ricollegati per riprendere la sincronizzazione.»
''', f'''<div class="st st-stage st-stage--col" style="max-width: 420px; gap: var(--space-3)">
<div role="status" class="st-toast">{ic('u-check', 18, 2.2)}<span class="st-toast__text corpo" style="font-weight: 600">Pranzo con buono registrato</span><button type="button" class="st-toast__action pulsante">Annulla</button></div>
{banner('info', 'u-cloud', 'Accesso a Google scaduto', 'I dati sono al sicuro qui. Ricollegati per riprendere la sincronizzazione.', '<span style="display: flex; margin-top: var(--space-2)"><button type="button" class="st-btn st-btn--s st-btn--primary pulsante" style="font-size: 13px">Riconnetti</button></span>')}
{banner('ok', 'u-check', 'Backup ripristinato', 'I dati sono tornati al 12 novembre, su tutti i dispositivi.')}
{banner('warning', 'u-alert', 'Pasti fuori: budget superato', '92,00 € di 80,00 € · 12,00 € oltre il previsto')}
{banner('danger', 'u-alert', 'Spesa non salvata', 'Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.')}</div>''')

# --- Finestra
comp('Finestra', 'Stato e messaggi', 560, '''I contenitori modali: il pannello che sale dal basso sul telefono, la finestra centrata su PC, la conferma.

## Pannello (telefono)
`st-sheet` sopra `st-backdrop`: color-bg, angoli alti `radius-xl`, maniglia `st-sheet__grip`, `shadow-3`. Sale con `duration-slow` ed `ease-standard`. In alto: Chiudi a sinistra, il Segmentato o il titolo al centro; in fondo il Pulsante grande.

## Finestra (PC)
`st-dialog`, larga al massimo `content-max`, a `space-8` dal bordo alto, contenuto su due colonne. Intestazione con titolo `titolo-2` e Chiudi con il Tasto Esc; in fondo `st-dialog__foot` con le azioni a destra e il Tasto Invio sul pulsante principale.

## Conferma
Per ciò che non si annulla: icona di pericolo (`st-danger-icon`), domanda come titolo («Eliminare questa spesa?»), che cosa si elimina, una frase sulle conseguenze, poi Elimina (Pulsante di pericolo) e Annulla. `role="alertdialog"`.

## Regole
Usa `<dialog>` aperto con `showModal()`: il focus resta dentro, Esc chiude, il focus torna al comando che l'ha aperta. La schermata di blocco sta sopra tutte le altre finestre.
''', f'''<div class="st st-stage" style="align-items: flex-end; padding-bottom: 0">
<div class="st-layer" style="width: 360px; height: 500px; border-radius: var(--radius-lg) var(--radius-lg) 0 0"><div class="st-backdrop"></div>
<div role="alertdialog" aria-modal="true" aria-label="Eliminare questa spesa?" class="st-sheet" style="position: absolute; left: 0; right: 0; bottom: 0; text-align: center">
<span class="st-sheet__grip" aria-hidden="true"></span><span class="st-danger-icon" aria-hidden="true">{ic('u-trash', 28)}</span>
<h2 class="titolo-2">Eliminare questa spesa?</h2>
<div class="st-card" style="flex-direction: row; align-items: center; padding: var(--space-3) var(--space-4); text-align: left"><span class="st-cat st-cat--s1" aria-hidden="true">{ic('spesa')}</span><span class="st-mrow__text"><span class="corpo-forte">Conad</span><span class="secondario st-muted">Sabato 14 novembre</span></span><span class="corpo-forte">−42,30 €</span></div>
<p class="corpo st-muted">Sparisce anche dagli altri dispositivi collegati.</p>
<div class="st-stack"><button type="button" class="st-btn st-btn--l st-btn--danger pulsante-l">{ic('u-trash', 20, 2.2)}Elimina</button><button type="button" class="st-btn st-btn--l st-btn--secondary pulsante-l" style="background: var(--color-surface)">Annulla</button></div></div></div></div>''')

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
keys = ''.join(f'<button type="button" class="st-pin__key tasto-pin{" is-pressed" if k == "5" else ""}">{k}</button>' for k in '123456789')
keys += f'<button type="button" class="st-pin__key st-pin__key--soft" aria-label="Sblocca con l’impronta">{ic("u-finger", 30, 1.9)}</button><button type="button" class="st-pin__key tasto-pin">0</button><button type="button" class="st-pin__key st-pin__key--ghost" aria-label="Cancella l’ultima cifra">{seticon("lucide", "u-x", 26, sw=1.9)}</button>'
comp('Tastierino', 'Moduli', 520, '''Il tastierino della schermata di blocco: cifre grandi, impronta e cancella.

## Struttura
`st-pin__dots` mostra un pallino per ogni cifra già scritta e il cursore: non ci sono caselle vuote, così non si capisce quanto è lungo il PIN (da 4 a 8 cifre). Sotto, `st-pin` con i tasti da 76 px in `tasto-pin`; in basso a sinistra l'impronta (`st-pin__key--soft`, `aria-label`), in basso a destra Cancella.

## Regole
Dopo 5 errori compare l'Avviso di pericolo «Troppi tentativi» con l'attesa. Sotto il tastierino, il link «Ho dimenticato il PIN».
''', f'''<div class="st st-stage st-stage--col" style="align-items: center"><div role="status" aria-label="3 cifre inserite" class="st-pin__dots"><span class="st-pin__dot"></span><span class="st-pin__dot"></span><span class="st-pin__dot"></span><span class="st-pin__caret" aria-hidden="true"></span></div><div class="st-pin">{keys}</div></div>''')

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
<p class="cv-name">Statera</p>
<p class="cv-tag">Entrate e spese, chiare. Sul tuo dispositivo.</p>
</div>
'''

# ================================================================ testi del manuale
TABLE_ICONS = ''
labels = dict((k, lab) for k, c, lab in icone.USCITE + icone.ENTRATE)
labels['regali'] = 'Regali, Regali ricevuti'; labels['altro'] = 'Altro (uscite ed entrate)'
for k, lab in labels.items():
    TABLE_ICONS += f'| `{k}` | {lab} | `{icone.SET["lucide"]["icone"][k]["nome"]}` |\n'
EXTRA = {'x-coffee': 'caffe', 'x-pizza': 'pizza', 'x-wine': 'vino', 'x-beer': 'birra', 'x-icecream': 'gelato', 'x-croissant': 'colazione', 'x-sofa': 'arredamento',
         'x-baby': 'bambini', 'x-paw': 'animali', 'x-plant': 'giardino', 'x-washing': 'elettrodomestici', 'x-wifi': 'internet', 'x-phone': 'telefono', 'x-tv': 'tv',
         'x-bike': 'bici', 'x-train': 'treno', 'x-taxi': 'taxi', 'x-parking': 'parcheggio', 'x-ship': 'traghetto', 'x-pill': 'farmaci', 'x-stetho': 'medico',
         'x-scissors': 'parrucchiere', 'x-sparkles': 'bellezza', 'x-glasses': 'ottico', 'x-music': 'musica', 'x-film': 'cinema', 'x-book': 'libri', 'x-game': 'videogiochi',
         'x-camera': 'foto', 'x-party': 'feste', 'x-graduation': 'studio', 'x-laptop': 'computer', 'x-coins': 'monete', 'x-percent': 'tasse', 'x-receipt': 'scontrino',
         'x-trend': 'investimenti', 'x-umbrella': 'assicurazioni', 'x-heart': 'cuore', 'x-globe': 'mondo', 'x-tent': 'campeggio', 'x-hotel': 'alloggio', 'x-dog': 'cane',
         'x-handheart': 'donazioni'}
EXTRA_LINE = ' · '.join(f'`{v}` ({icone.SET["lucide"]["icone"][k]["nome"]})' for k, v in EXTRA.items())
ACCOUNTS = [('conto_corrente', 'c-corrente'), ('contanti', 'c-contanti'), ('buoni_pasto', 'buoni'), ('altro', 'c-risparmi')]

README = f'''Statera è l'app personale per registrare entrate e spese, su telefono Android e PC Windows. Lo stile è «Vivace»: saldo grande al centro, azioni in cerchi, categorie riconoscibili dal colore e dall'icona, angoli molto arrotondati. La palette è «Indaco morbido»: un indaco calmo, che non stanca la vista nell'uso di tutti i giorni.

## Principi
- **Il numero prima di tutto.** Ogni schermata ha un importo protagonista (saldo del mese, patrimonio, importo che stai scrivendo) in uno stile `importo-*`; il resto gli fa spazio.
- **Il colore non basta mai.** Stati, budget, entrate e uscite hanno sempre anche una parola, un simbolo o un segno.
- **Calma.** Un solo colore forte (color-primary) per schermata, usato per l'azione principale. Le tinte delle categorie sono tenui e non competono.
- **Tutto in locale, detto chiaramente.** Dove si parla di dati, si dice dove stanno: «sul dispositivo», «cifrato su Google Drive».

## Testi
- Italiano, del «tu», frasi brevi. Maiuscola solo a inizio frase e nei nomi. Nessuna emoji, nessun punto esclamativo.
- Pulsanti col verbo e l'oggetto: «Salva spesa», «Registra», «Esporta CSV», «Collega Google Drive». Domande dirette nei campi: «Quanto hai speso?».
- Errori in due tempi: cosa è successo, cosa fare. «Il salvataggio non è riuscito entro 10 secondi. Riprova: i dati del modulo sono ancora qui.»
- Stati vuoti che indicano il prossimo passo: «Ancora nessun movimento a novembre. Tocca + per la prima spesa.»
- Importi: «1.234,56 €», sempre col punto delle migliaia e la virgola; uscite col segno meno tipografico «−» (U+2212), entrate col «+». Date: «sabato 14 novembre», «14/11/2026» nei campi. Virgolette «basse», apostrofo tipografico «’».
- Separatore tra informazioni: « · » (Carburante · Bancomat); gerarchia delle categorie: « › » (Casa › Bollette).

## Colore
- Sfondo color-bg, contenuti in schede color-surface; dentro una scheda, i comandi secondari sono color-surface-2. Bordi color-border solo come linee sottili, mai intorno alle schede.
- Testo color-text; seconde righe, date e didascalie color-text-muted. Entrambi superano 4,5:1 su color-bg, color-surface e color-surface-2 in tutti e due i temi.
- color-primary con color-on-primary per un solo comando forte per schermata (pulsante +, Salva, segmento attivo). Per link, icone d'accento e voci attive: color-accent; per i fondi tenui: color-accent-soft.
- Uscite in color-text, entrate in color-income. color-income non va su color-accent-soft in tema chiaro.
- Grafici: chart-income (blu) e chart-expense (arancio), mai rosso e verde; legenda sempre visibile.
- Stati: status-warning per «quasi esaurito» e i promemoria, status-critical / color-danger per «superato», errori e cancellazioni. Sempre con simbolo e parola. color-danger non si usa per gli importi in uscita.
- Conti e categorie hanno una tinta tra swatch-s1 e swatch-s8; i dati salvano solo la chiave (`s1`…`s8`). Come si usa nel cerchio: IconaCategoria.
- Tema scuro: stessi ruoli con i valori scuri. Il riquadro «hai risparmiato» passa da color-primary pieno a color-accent-soft, per non abbagliare. Gli avvisi a comparsa invertono i colori (toast-bg, toast-text, toast-action).

## Tipografia
- Un solo carattere: Plus Jakarta Sans (licenza OFL), incluso nel pacchetto dell'app, mai caricato da internet. Peso variabile 200–800; si usano 400, 500, 600, 700, 800.
- Cifre sempre tabulari (`font-variant-numeric: tabular-nums`), così gli importi si allineano.
- Importi: `importo-xl` mentre scrivi, `importo-l` per il saldo del mese (centesimi più piccoli, a 28 px), `importo-m` per patrimonio e saldi dei conti, `importo-s` per i riquadri e i totali.
- Titoli: `titolo-1` per le quattro sezioni, `titolo-2` per le schermate secondarie e le finestre, `titolo-3` per le schede.
- Testo: `corpo` per le frasi, `corpo-forte` per il titolo delle righe, `campo` dentro i campi (16 px), `secondario` per le seconde righe, `pulsante` e `pulsante-l` sui pulsanti.
- Etichette: `etichetta-campo` sopra i campi, `etichetta` per i titoli di gruppo (in maiuscolo con `text-transform`), `nav` nella barra, `badge` e `tasto`.

## Spazi, forme e ombre
- Griglia di 4 px: space-1 (4) … space-8 (48). Margine laterale del telefono space-5, tra le schede space-4, interno delle schede space-5, su PC tra le colonne space-6.
- Raggi: radius-lg per schede e riquadri, radius-md per campi e righe evidenziate, radius-xl per pannelli e finestre, radius-full per pulsanti, chip, cerchi e barra flottante, radius-xs per tasti e caselle.
- Ombre solo per ciò che galleggia: shadow-2 per barra flottante, barra laterale e avvisi; shadow-3 per pannelli e finestre; shadow-fab per il +; shadow-1 per il pomello dell'interruttore. Le schede non hanno ombra.
- Aree di tocco di almeno size-touch (44 px). Campi alti size-field, pulsante grande size-btn-l.

## Impaginazione
- **Telefono (390 px)**: barra flottante con il + al centro (BarraNavigazione) nelle quattro sezioni Movimenti, Conti, Analisi, Altro. Le schermate aperte da un'altra hanno la freccia indietro in alto e niente barra. I moduli salgono dal basso in un pannello (Finestra).
- **PC (da 1024 px)**: BarraLaterale larga size-sidebar al posto della barra flottante; contenuto su una o due colonne (elenco a sinistra, riepiloghi o dettaglio a destra); i moduli si aprono in una finestra centrata larga al massimo content-max, su due colonne. Le scorciatoie sono scritte accanto ai comandi con il Tasto.

## Stati dei comandi
- Passaggio del puntatore (solo PC): velo del colore del testo all'8%, o color-surface-2 per righe e voci.
- Premuto: scala 0,97 (cerchi 0,94) e velo al 14%, per duration-fast.
- Focus da tastiera: anello pieno di focus-width in color-focus, staccato di focus-offset; sui campi l'anello è intorno al campo. Mai togliere il focus visibile.
- Disattivato: opacity-disabled, senza ombre né movimento, con il motivo scritto vicino.
- Errore: anello e messaggio in color-danger con l'icona di avviso.

## Movimento
- duration-fast (120 ms) per pressioni e colori, duration-base (200 ms) per interruttori, segmentato e avvisi, duration-slow (280 ms) per pannelli e finestre. Entrate con ease-standard, uscite con ease-exit.
- Il movimento accompagna, non decora: niente rimbalzi, niente animazioni in attesa.
- Con «riduci animazioni» attivo nel sistema, nessuno spostamento: solo cambi di colore e dissolvenze brevi.

## Iconografia
- **Lucide** (licenza ISC), versione 1.73: tratto 2 px su griglia 24, estremità arrotondate. 20 px nell'interfaccia, 22 px nella barra, 16 px in chip e pulsanti piccoli.
- Nell'app le icone sono copiate nel codice (solo quelle usate), mai caricate da internet né lette dai dati come disegno: i dati salvano solo una chiave. Le icone si colorano col colore del testo (`currentColor`); quelle in questo sistema, viste come immagine, sono nere.
- Ogni categoria ha un campo facoltativo `icon` con una chiave. Senza chiave, o con una sconosciuta, il cerchio mostra l'iniziale del nome. Le categorie iniziali prendono l'icona dal loro id fisso.

| Chiave | Categoria iniziale | Icona Lucide |
|---|---|---|
{TABLE_ICONS}
- Conti, per tipo: {', '.join(f'`{t}` → `{icone.SET["lucide"]["icone"][k]["nome"]}`' for t, k in ACCOUNTS)}; carte → `credit-card`.
- Scelta libera nel modulo della categoria, in cinque gruppi (Suggerite, Casa, Trasporti e viaggi, Salute e tempo libero, Soldi e lavoro), con ricerca: {EXTRA_LINE}.
- Icone dell'interfaccia: gruppo Interfaccia negli asset.

## Marchio
Il logo non c'è ancora. Fino ad allora il nome si scrive «Statera» in Plus Jakarta Sans 800, e come segno si usa la bilancia di Lucide (`scale`) in un cerchio color-primary con l'icona in color-on-primary.
'''

LIC = f'''# Licenze

Il carattere e le icone sono inclusi nell'app; queste licenze vanno riportate nelle note dell'app (Altro › Informazioni).

## Plus Jakarta Sans

Distribuito come @fontsource-variable/plus-jakarta-sans 5.3.0 (solo il sottoinsieme latino, pesi 200–800).

```
{open(FONT_LIC).read().strip()}
```

## Lucide

lucide-static {icone.SET['lucide']['versione']}.

```
{open(os.path.join(LUCIDE, 'LICENSE')).read().strip()}
```
'''

# ================================================================ scrittura
def main():
    if os.path.exists(OUTDIR): shutil.rmtree(OUTDIR)
    w('README.md', README)
    w('Licenze.md', LIC)
    w('tokens.json', json.dumps(TOKENS, ensure_ascii=False, indent=1))
    w('components/bundle.css', CSS)
    for name, group, height, readme, body in COMP:
        w(f'components/{name}/README.md', f'# {name}\n\n{readme}')
        w(f'components/{name}/preview.html', f'<!-- @dsCard group="{group}" height={height} -->\n{body}\n')
    w('components/Cover/preview.html', COVER)
    os.makedirs(os.path.join(P, 'fonts'), exist_ok=True)
    shutil.copy(FONT, os.path.join(P, 'fonts', 'plus-jakarta-sans-latin-wght-normal.woff2'))
    # icone da caricare: originali di Lucide, nominate con la chiave
    groups = {'Categorie': [(k, f'{k}.svg') for k in labels],
              'Conti': [(k, f'{t}.svg') for t, k in ACCOUNTS] + [('c-carta', 'carta.svg')],
              'Interfaccia': [(k, f'{icone.SET["lucide"]["icone"][k]["nome"]}.svg') for k in icone.UI + ['u-chevL', 'u-chevR', 'u-chevD']]}
    readmes = {'Categorie': 'Icone delle categorie iniziali (Lucide, ISC). Il nome del file è la chiave salvata nel campo `icon` della categoria; nell\'app si colorano con la tinta della categoria (`currentColor`), qui sono nere.',
               'Conti': 'Icone dei conti, scelte dal tipo di conto (il nome del file è il tipo) e della carta. Inchiostro nero qui, `currentColor` nell\'app.',
               'Interfaccia': 'Icone dell\'interfaccia (Lucide, ISC), col nome Lucide. Inchiostro nero qui, `currentColor` nell\'app: prendono il colore del testo o di color-accent.'}
    plan = {}
    for g, items in groups.items():
        os.makedirs(os.path.join(OUTDIR, 'icone', g), exist_ok=True)
        w(f'assets/{g}/README.md', f'# {g}\n\n{readmes[g]}\n')
        for k, fname in items:
            src = os.path.join(LUCIDE, 'icons', icone.SET['lucide']['icone'][k]['nome'] + '.svg')
            shutil.copy(src, os.path.join(OUTDIR, 'icone', g, fname))
        plan[g] = [f for _, f in items]
    json.dump(plan, open(os.path.join(OUTDIR, 'piano-icone.json'), 'w'), indent=1)
    n = sum(len(v) for v in plan.values())
    print('componenti', len(COMP), '· icone', n, '· colori', len(C), '· stili', sum(len(g['styles']) for g in TYPE['groups']))

if __name__ == '__main__':
    main()
