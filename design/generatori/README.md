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

Per le schermate nuove, parti da `scelta.py`: usa `IND_L` / `IND_D` / `IND_SW` con
`gen.page()` e le funzioni di `coolors.py` e `scelta.py`.

Non sono codice dell'app: questo ramo (`design`) non viene pubblicato su GitHub Pages.
