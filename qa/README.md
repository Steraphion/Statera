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
- `calendario-obiettivi.py` — Fase 5.3 con orologio fisso: calendario del mese (giorno scelto, movimenti del
  giorno, entrate segnate anche a parole, tinta per il giorno più caro, cambio mese) e obiettivi di risparmio (a
  mano con aggiunte, collegati al saldo di un conto, quanto al mese, eliminazione). Uso come `collaudo.py`.
- `importa.py` — Fase 5.4: import da CSV di un estratto conto (colonne riconosciute, tipo dal segno, categoria
  "Altro", riga con problema, doppioni saltati reimportando) e di un file esportato da Statera (categoria,
  sottocategoria, note, etichette; trasferimenti esclusi). Uso come `collaudo.py`.
- `icone.py` — v0.25: icona delle categorie (predefinita per le categorie iniziali, scelta nel modulo con
  anteprima, "Nessuna" mostra l'iniziale, salvata come chiave e solo se cambiata, visibile nell'elenco e nella
  scelta della categoria, conservata dopo il riavvio), su Android chiaro e PC scuro. Uso come `collaudo.py`.
- `tema-tastierino.py` — v0.26: scelta del tema in Altro → Aspetto (automatico, chiaro, scuro, conservata dopo il
  riavvio, colore della barra di sistema) e tastierino degli importi su telefono (cifre, virgola, somme, "=",
  cancella, "Fatto", Salva visibile, buoni solo cifre, tastierino in fondo alla pagina in Cerca; su PC tastiera
  normale). Uso come `collaudo.py`.
- `icona.py` — v0.29: logo e icone (bilancia a tratto). Manifest con icone any 16–512, maskable 192/512 e monochrome
  della dimensione dichiarata; any con angoli trasparenti, maskable piena, monochrome trasparente fuori dal simbolo;
  scorciatoie a 96 px; favicon ICO (16, 32, 48) e SVG; icona Apple 180 px; tutto nella cache per l'uso senza rete;
  logo nella barra laterale (indaco in chiaro, lilla col simbolo scuro in scuro), nascosto su telefono.
  Uso come `collaudo.py`.
- `movimento.py` — v0.30: movimento di pannelli e finestre su Android (sale dal basso) e PC (finestra centrata).
  Durate e curve uguali ai token (`--duration-slow`/`--ease-standard` in entrata, `--duration-base`/`--ease-exit` in
  uscita, anche per lo sfondo scurito), finestra ancora aperta e inattiva durante l'uscita, apertura da tastiera con
  focus nel pannello, Tab che non esce, chiusura con Esc (anche doppio), «Chiudi» e tocco sullo sfondo, focus che torna
  a «Nuovo movimento», riapertura durante l'uscita, blocco che arriva mentre un pannello si chiude (resta sopra, col
  focus sul PIN). Poi con «riduci animazioni»: durate a 0,01 ms (sfondo compreso), pannello subito al suo posto, Esc che
  chiude senza attesa. Le animazioni si osservano rallentate (CDP `Animation.setPlaybackRate`).
  Dalla v0.30.1: sul telefono il pannello sale senza tornare indietro (posizione fotogramma per fotogramma, finestra
  che non scorre) per quasi tutto `--duration-slow`; cambio di schermata con un anno di movimenti e processore
  rallentato 6 volte: la schermata compare intera (importo e posizione del riquadro principale non cambiano dopo la
  comparsa), in dissolvenza tra le sezioni, con spostamento verso il dettaglio conto e al ritorno; il modulo aperto
  sopra Movimenti non la nasconde; con «riduci animazioni» comparsa a 0,01 ms.
  Dalla v0.30.2: avviso a comparsa (da un preferito) che entra salendo ed esce in dissolvenza coi token, «Annulla» che
  lo sostituisce senza sovrapporne due; pannello e avviso riaperti mentre escono, poi richiusi, rifanno l'uscita;
  tastierino nel pannello che si apre in altezza e si chiude con «Fatto» in `--ease-exit`; in Cerca sale dal basso e
  resta fermo passando da «Importo da» a «Importo a».
  Dalla v0.31.1 su PC il conto si apre accanto all'elenco: si controlla che la schermata non si nasconda e che il
  dettaglio compaia in dissolvenza (`pane-in`) invece dello spostamento.
  Dalla v0.30.3: un movimento salvato apre la sua riga (o il giorno intero, se nuovo), uno eliminato la chiude in
  `--ease-exit` e «Annulla» la riapre ripristinando il dato; una descrizione lunga non allarga la riga; cambiando mese
  nessuna riga si anima; la barra del budget scorre al nuovo valore in `--duration-slow`. Uso come `collaudo.py`.
- `pc.py` — v0.31: schermate PC con orologio fisso (14/11/2026) e dati di esempio (un anno di movimenti, due budget,
  due preferiti, una bolletta da confermare). A 900, 1024, 1280 e 1440 px, in chiaro e in scuro: testo da 16 px
  (radice 17 px), barra laterale stretta sotto i 1200 px, contenuti larghi al massimo `--content-max-wide`, niente
  scorrimento orizzontale. Movimenti con la colonna di destra (da registrare, preferiti che vanno a capo, budget del
  mese, suggerimento delle scorciatoie), larga quanto il token o meno se l'elenco resterebbe sotto `--size-main-min`.
  Colonne regolabili: separatore con limiti dai token, trascinamento (anche oltre il massimo), scelta salvata e
  ritrovata dopo il riavvio, frecce (con Maiuscole), Inizio, Invio e doppio clic per la larghezza iniziale, frecce che
  non cambiano mese, finestra ristretta che non toglie spazio all'elenco. Barra laterale da stringere da 1200 px in su
  (in `--duration-base`, salvata, voci ancora trovabili per nome). Sul telefono nessuna di queste cose e lo stesso
  ordine di prima. Dalla v0.31.1, Conti: elenco e dettaglio affiancati (primo conto scelto, saldo di oggi,
  movimenti del mese in tabella col saldo dopo ognuno e il saldo a inizio mese), frecce ← → per il mese e ↑ ↓ per il
  conto senza riempire la cronologia, clic su un altro conto con indirizzo `#/conto/…`, schermata che non si
  nasconde né torna in cima e dettaglio in dissolvenza in `--duration-base`, Indietro, riga della tabella che apre il
  movimento, elenco regolabile col dettaglio mai sotto `--size-detail-min`, colonna del saldo nascosta quando il
  dettaglio è stretto (960 px). Sul telefono il conto si apre ancora nella sua schermata. Dalla v0.31.2, finestra del
  movimento: larga `--size-window-wide` e su due colonne da 900 px (importo, conto, data e descrizione a sinistra,
  categoria a destra con l'elenco più lungo; per i trasferimenti data a sinistra e altre scelte a destra), suggerimenti
  nella colonna di sinistra con frecce e Invio (che non salva), Invio sulla categoria che salva, Invio nelle note che va
  a capo e Ctrl+Invio che salva, Esc; a 800 px finestra `--size-window` a una colonna; sul telefono modulo in colonna.
  Uso come `collaudo.py`.
