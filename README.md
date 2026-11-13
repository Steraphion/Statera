# Statera

Web app personale per registrare entrate e spese. Funziona offline, si installa su smartphone e PC, e non invia dati a nessuno: in futuro solo a Google Drive, cifrati, per sincronizzazione e backup.

## Comandi

| Comando | Cosa fa |
|---|---|
| `npm install` | Installa le dipendenze |
| `npm run dev` | Avvia l'app in locale per lo sviluppo |
| `npm run check` | Controlla errori nel codice |
| `npm test` | Esegue i test automatici (calcoli, regole sui dati) |
| `npm run build` | Crea la versione pubblicabile in `dist/` |

Ogni modifica sul ramo `main` viene pubblicata automaticamente su GitHub Pages.

## Struttura

- `src/styles/tokens.css` — tutto l'aspetto grafico (colori, font, spaziature)
- `src/screens/` — le schermate
- `src/components/` — elementi riutilizzabili
- `src/lib/data/` — modello dati, database locale, regole e calcolo dei saldi
- `src/lib/` — navigazione, formattazione, stato del dispositivo
- `public/icons/` — icone dell'app
