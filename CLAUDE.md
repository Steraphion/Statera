# Statera — regole per lo sviluppo

Le specifiche complete sono nel Progetto claude.ai "Statera" (`claude/specifiche-statera.md`).

- Interfaccia e testi in **italiano**. Formati it-IT.
- Importi sempre **interi in centesimi**; formattazione solo tramite `src/lib/format.ts`.
- **Nessuna risorsa esterna**: niente CDN, font remoti, analytics. Le uniche origini permesse (dalla Fase 2) sono i domini Google per login e Drive, da aggiungere esplicitamente alla CSP in `vite.config.ts`.
- **Aspetto separato dalla logica**: colori, font e misure solo come variabili in `src/styles/tokens.css`; i componenti usano le variabili, mai valori fissi.
- Ogni record dati ha `id`, `createdAt`, `updatedAt`, `deletedAt` (cancellazione logica, serve alla sync).
- Mai dati reali in chat, nei test o nei commit: solo dati di esempio.
- Tutte le modifiche ai dati passano da `src/lib/data/repo.ts` (conti, carte, categorie) e `src/lib/data/transactions.ts` (movimenti); colori salvati come chiave (`s1`…`s8`), mai come valore.
- Prima di pubblicare: `npm run check`, `npm test` e `npm run build` senza errori.
