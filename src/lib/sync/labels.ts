import type { SyncStatus } from './sync.svelte'
import { formatWhen } from '../format'

/** Quello che serve per descrivere lo stato della sincronizzazione (dallo stato di `sync`). */
export interface SyncView {
  status: SyncStatus
  lastSyncAt: number | null
  /** Modifiche fatte su questo dispositivo non ancora inviate a Drive. */
  pending: boolean
  /** Il rinnovo automatico del permesso Google non è riuscito. */
  askReconnect: boolean
}

/** Stato in una frase (Altro, scheda Sincronizzazione). */
export function statusLabel(s: SyncStatus, ctx?: Pick<SyncView, 'pending' | 'askReconnect'>): string {
  switch (s) {
    case 'off':
      return 'Non attiva'
    case 'idle':
      return 'Sincronizzato'
    case 'syncing':
      return 'Sincronizzazione in corso…'
    case 'needs-auth':
      if (!ctx || ctx.askReconnect) return 'In pausa: riconnettiti a Google'
      return ctx.pending ? 'Modifiche da inviare: partono al prossimo tocco' : 'In pausa: nessuna modifica da inviare'
    case 'locked':
      return 'Bloccata: serve la password'
    case 'offline':
      return 'In attesa di connessione'
    case 'error':
      return 'Errore'
  }
}

/** "Aggiornato alle 14:32", "Aggiornato ieri alle 9:05"… o "Mai sincronizzato". */
export function updatedText(lastSyncAt: number | null, now: number = Date.now()): string {
  return lastSyncAt ? `Aggiornato ${formatWhen(lastSyncAt, now)}` : 'Mai sincronizzato'
}

export interface SyncLine {
  title: string
  detail: string
  /** Toccando si rinnova il permesso Google e si sincronizza (altrimenti si apre Altro). */
  renew: boolean
  /** Serve un intervento: colore di avviso. */
  warn: boolean
}

/**
 * Stato in breve per la barra laterale (PC) e la riga in cima a Movimenti (telefono).
 * Permesso Google scaduto senza modifiche da inviare: niente finestra di Google, solo
 * "Aggiornato alle … · Sincronizza", che si tocca quando si vogliono i dati degli altri dispositivi.
 */
export function syncLine(v: SyncView, now: number = Date.now()): SyncLine {
  const line = (title: string, detail: string, renew = false, warn = false): SyncLine => ({ title, detail, renew, warn })
  switch (v.status) {
    case 'off':
      return line('Solo su questo dispositivo', 'Sincronizzazione non attiva')
    case 'idle':
      return line('Sincronizzato', updatedText(v.lastSyncAt, now))
    case 'syncing':
      return line('Sincronizzazione…', 'Google Drive, cifrato')
    case 'needs-auth':
      if (v.askReconnect) return line('In pausa', 'Riconnetti a Google', true, true)
      if (v.pending) return line('Modifiche da inviare', 'Sincronizza', true)
      return line(updatedText(v.lastSyncAt, now), 'Sincronizza', true)
    case 'locked':
      return line('Sincronizzazione bloccata', 'Serve la password', false, true)
    case 'offline':
      return line('Senza connessione', v.pending ? 'Modifiche salvate qui' : updatedText(v.lastSyncAt, now))
    case 'error':
      return line('Sincronizzazione non riuscita', 'Dettagli in Altro', false, true)
  }
}
