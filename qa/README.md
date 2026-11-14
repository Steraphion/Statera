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
- `inserimento.py` — Fase 4.1: calcoli nel campo importo e pulsante +, suggerimenti dalla descrizione (categoria,
  fonte e importo dell'ultima volta, frecce e Invio su PC), scorciatoie dell'icona (`#/movimenti/nuova-uscita`),
  ricerca per importo, icone delle scorciatoie nel manifest. Uso come `collaudo.py`.
- `preferiti.py` — Fase 4.2: preferito dal modulo (con e senza importo), un tocco registra con avviso "Annulla",
  preferito senza importo apre il modulo compilato, gestione (rinomina, ordine, eliminazione), riavvio.
  Il passaggio del database dalla versione 2 alla 3 (v0.14.0 → v0.15.0, dati intatti) è stato verificato con lo
  schema di `aggiornamento.py`. Uso come `collaudo.py`.
- `guida-saldo.py` — Fase 4.3: guida al primo avvio (tre passi, non nascondibile senza conti, sparisce a fine),
  budget con "circa X € al giorno" (solo mese in corso), Allinea saldo con anteprima, rettifica e caso "già
  giusto". Uso come `collaudo.py`.
- `blocco.py` — Fase 4.4: blocco con PIN e impronta (autenticatore virtuale WebAuthn di Chrome): attivazione con
  controllo dei PIN prevedibili, blocco/sblocco, impronta all'avvio ma non dopo "Blocca ora", tempi di blocco,
  copertura dei pannelli aperti ed Esc, inserimento a metà conservato, cambio PIN, attese dopo 5 errori, PIN
  dimenticato (eliminazione dei dati del dispositivo), disattivazione. Uso come `collaudo.py`.
- `approfondimenti.py` — Fase 5.1 con orologio fisso e un anno di dati di esempio: riepilogo del mese precedente
  nei primi 7 giorni (e poi non più), ritmo di spesa e stima di fine mese, confronto con la media dei 3 mesi
  prima, patrimonio nel tempo (grafico e tabella). Uso come `collaudo.py`.
- `etichette.py` — Fase 5.2: ripartizione su più categorie (riga che prende il resto, categoria principale,
  analisi, CSV una riga per categoria, ritorno a una sola categoria, somma sbagliata) ed etichette (chip, scheda
  in Analisi, filtro in Cerca). Uso come `collaudo.py`.
