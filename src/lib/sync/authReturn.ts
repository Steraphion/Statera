import { takeAuthResult, type AuthResult } from './google'

/**
 * Risposta di Google arrivata col ritorno all'app dopo `startRedirect`. Si legge una volta sola
 * all'avvio, prima che il router guardi l'indirizzo: per questo `main.ts` importa questo modulo
 * prima di `App.svelte`. La consuma `sync` (rinnovo) o la scheda di attivazione (primo collegamento).
 */
export const authReturn: { result: AuthResult | null } = { result: takeAuthResult() }
