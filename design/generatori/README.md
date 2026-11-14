# Generatori delle tavole di design

Script Python (solo libreria standard) che hanno prodotto le tavole della tela
"Statera — Proposte di stile" su claude.ai
(https://claude.ai/artifact/A273BvJuvrhLBUZbRPSZmx). Contengono solo dati di esempio.
Le decisioni prese sono in `claude/identita-grafica.md` nel Progetto "Statera".

Ogni tavola è un file `.dc.html` (formato del tipo "Design" di claude.ai) da 390×844 px.
I file vengono scritti in `out/project/`, oppure nella cartella indicata dalla variabile `STATERA_CANVAS`.

| File | Contenuto |
|---|---|
| `gen.py` | Base comune: icone, dati finti, `page()`, le tre direzioni A/B/C (pagina "Direzioni") |
| `palettes.py` | Barra di navigazione flottante con il + (`B_nav`), controllo contrasti `cr()`, 5 palette per Vivace |
| `coolors.py` | Le 6 palette da Coolors e `mov()`, cioè Movimenti in stile Vivace con colori parametrici |
| `chosen.py` | Analisi a pagina intera con il budget del mese (`analisi()`) |
| `scelta.py` | **Indaco morbido** (valori in OKLCH, `IND_L`, `IND_D`, `IND_SW`), Nuova spesa sopra la lista (`new()`), scheda colori |
| `scelta2.py` | Pagina "Scelte": rigenera le tavole Zafferano e Indaco morbido partendo dal `canvas.json` della tela |
| `altre.py` | Indaco morbido, telefono: Conti, dettaglio conto, Cerca, Altro, Ricorrenti, Categorie, blocco col PIN, guida al primo avvio, stati vuoti, avvisi, conferma. Ruoli nuovi `warn` e `danger`, icone dell'interfaccia, controllo contrasti `check()` |
| `pc.py` | Indaco morbido, PC (1280 px, tavole fluide): barra laterale, Nuova spesa in finestra, Analisi, Conti con dettaglio, scorciatoie |
| `pagina_altre.py` | Pagina "Altre schermate · Indaco morbido": scrive le tavole `ind-*.dc.html` e le voci da aggiungere a `canvas.json` (`voci-mobile.json`, `voci-pc.json`) |
| `icone.py` | Pagina "Icone delle categorie": Lucide, Tabler e Phosphor a confronto, in contesto, e scelta dell'icona nel modulo della categoria (voci in `voci-icone.json`) |
| `icone_set.json` | Le ~100 icone usate, nei tre set (solo forme geometriche). Licenze in `LICENZE-ICONE.md` |
| `voglio.json`, `risolvi.py`, `estrai.py` | Da quale icona di ogni set viene ogni chiave, e come rigenerare `icone_set.json` dai pacchetti npm (`npm pack lucide-static @tabler/icons @phosphor-icons/core`, poi estrarre e passare le cartelle agli script) |
| `design_system.py` | Design system "Statera" (tipo Design System di claude.ai, https://claude.ai/artifact/HYogYA8sLDbtWMS277c1CF): `tokens.json` e `tokens.css`, `bundle.css` con i componenti `st-*`, anteprime e guide di 24 componenti, manuale, licenze, asset (icone Lucide e logo). **Il riferimento è l'app**: token, icone, logo e carattere si leggono da un checkout del ramo `main` (vedi `app_main.py`), niente valori copiati a mano. Uso: `python3 design_system.py <uscita> <pacchetto lucide-static 1.73.0> <checkout di main>` (es. `npm pack lucide-static@1.73.0` ed estrarlo). Scrive `<uscita>/project/` (da pubblicare nel design system) e `<uscita>/asset/<gruppo>/` (da caricare come asset; `piano-asset.json` li elenca) |
| `app_main.py` | Lettura del ramo `main` per il design system: `src/styles/tokens.css` (tema chiaro e scuro), `src/lib/icons.ts` (icone, chiavi, nomi e gruppi della scelta dell'icona), `src/lib/logo.ts` e `icona/simbolo*.svg` (logo, generati da `scripts/icona-app.mjs`), `src/assets/fonts/` (Plus Jakarta Sans e OFL). Un token nuovo in `tokens.css` senza famiglia ferma il generatore; senza descrizione dà un avviso |
| `prova_design_system.py` | Controllo locale: `python3 prova_design_system.py <uscita>` scrive in `<uscita>/prova/` una pagina per anteprima in chiaro e in scuro, da aprire nel browser (o da fotografare con Chrome senza finestra) |
| `logo_simboli.py`, `logo_tavole.py` | Pagina "Logo e icona" (14/11): i simboli A–G in una griglia di 100 unità (variante piccola fino a 32 px) e le tavole confronto / simbolo e marchio / sui dispositivi. Scelta la **E, bilancia a tratto**: il disegno definitivo è in `scripts/icona-app.mjs` sul ramo `main`. Questi due script usano Pillow e `rsvg-convert` per misurare e rasterizzare; le PNG a 16/32 px vanno caricate come asset della tela (identificativi in `PX`) |

Per le schermate nuove, parti da `scelta.py`: usa `IND_L` / `IND_D` / `IND_SW` con
`gen.page()` e le funzioni di `coolors.py` e `scelta.py`.

Non sono codice dell'app: questo ramo (`design`) non viene pubblicato su GitHub Pages.
