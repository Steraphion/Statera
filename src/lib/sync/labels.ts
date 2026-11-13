import type { SyncStatus } from './sync.svelte'

export function statusLabel(s: SyncStatus): string {
  switch (s) {
    case 'off':
      return 'Non attiva'
    case 'idle':
      return 'Sincronizzato'
    case 'syncing':
      return 'Sincronizzazione in corso…'
    case 'needs-auth':
      return 'In pausa: riconnettiti a Google'
    case 'locked':
      return 'Bloccata: serve la password'
    case 'offline':
      return 'In attesa di connessione'
    case 'error':
      return 'Errore'
  }
}
