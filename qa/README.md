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
