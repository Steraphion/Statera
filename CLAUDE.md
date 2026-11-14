# Statera — regole per lo sviluppo

Le specifiche complete sono nel Progetto claude.ai "Statera" (`claude/specifiche-statera.md`).

- Interfaccia e testi in **italiano**. Formati it-IT.
- Importi sempre **interi in centesimi**; formattazione solo tramite `src/lib/format.ts`.
- **Nessuna risorsa esterna**: niente CDN, font remoti, analytics. Uniche origini permesse: `accounts.google.com/gsi` (accesso) e `www.googleapis.com` (Drive), dichiarate nella CSP in `vite.config.ts`.
- **Aspetto separato dalla logica**: colori, font e misure solo come variabili in `src/styles/tokens.css`; i componenti usano le variabili, mai valori fissi.
- Ogni record dati ha `id`, `createdAt`, `updatedAt`, `deletedAt` (cancellazione logica, serve alla sync).
- Mai dati reali in chat, nei test o nei commit: solo dati di esempio.
- Tutte le modifiche ai dati passano da `src/lib/data/repo.ts` (conti, carte, categorie, budget), `src/lib/data/transactions.ts` (movimenti) `src/lib/data/recurring.ts` (ricorrenti: i movimenti generati hanno id fisso `rec-<id>-<data>`, così due dispositivi non creano doppioni) e `src/lib/data/templates.ts` (preferiti); colori salvati come chiave (`s1`…`s8`), mai come valore.
- Prima di pubblicare: `npm run check`, `npm test` e `npm run build` senza errori; per modifiche all'interfaccia anche il collaudo in `qa/`.
- Moduli: `novalidate` (validazione solo nostra), errori mostrati nel pannello accanto ai pulsanti, ogni salvataggio con `withTimeout`.
- Sincronizzazione (`src/lib/sync/`): `core.ts` è la logica pura (testata con Drive finto), `sync.svelte.ts` lo stato e i momenti, `google.ts` l'accesso e le API Drive. Non cambiare il formato dei file su Drive (`statera-data.json`, `statera-keys.json`, `statera-backup-*.json`) senza una migrazione.
- Esportazione CSV solo tramite `src/lib/data/csv.ts` (formato Excel italiano, testo protetto dalle formule).
- Tabelle sincronizzate: elenco unico `TABLES` in `src/lib/sync/merge.ts` (sync, backup e unione le usano tutte). Una tabella nuova = nuova versione del database in `db.ts` + `TABLES` + `Snapshot` + ricollegamento in `unifyForFirstLink` se ha riferimenti a conti, carte o categorie.
