# Collaudo end-to-end

Prove automatiche nel browser (Chrome + Playwright per Python), con soli dati di esempio.

- `collaudo.py` — percorre tutte le funzioni in emulazione Android (Pixel 7) e PC: conti, carte, movimenti
  (anche pagamento misto), saldi, dettaglio conto, ricerca, categorie, backup/ripristino, 5 ricariche di fila,
  uso senza rete, schermata di recupero con database non apribile.
  Uso: `npm run build && npx vite preview --port 4173` e poi `python3 qa/collaudo.py`.
- `aggiornamento.py` — verifica il passaggio da una versione all'altra (avviso "Aggiorna", dati intatti).
  Richiede due build in cartelle separate servite su `localhost:4174`.
- `sincronizzazione.py` — Fase 2 con Google e Drive **simulati** (nessun account reale): attivazione con password e
  chiave di recupero, secondo dispositivo con unione senza doppioni, modifiche e cancellazioni nei due sensi,
  permesso scaduto e riconnessione, cambio password, terzo dispositivo con chiave di recupero, backup e ripristino,
  profili, scollegamento, uso senza rete. Uso come `collaudo.py`.
- `analisi.py` + `anno-di-esempio.js` — Fase 3: carica un anno di movimenti di esempio e controlla riquadri,
  barre per categoria, colonne mensili (suggerimento al passaggio e vista tabella), budget, passaggio a Cerca.
  Uso come `collaudo.py`.
- `ricorrenti.py` — movimenti ricorrenti: occorrenze automatiche recuperate all'avvio senza doppioni,
  "Da registrare" con conferma e salto, modifica, sospensione, eliminazione. Uso come `collaudo.py`.
- `esportazione.py` — CSV per Excel da Cerca e da Analisi: BOM UTF-8, separatore `;`, importi con la virgola,
  date gg/mm/aaaa, testo con `;` e virgolette, formule neutralizzate, periodo vuoto. Uso come `collaudo.py`.
