import { db } from './data/db'
import { ensureSeeded } from './data/repo'
import { errorMessage, withTimeout } from './data/util'

/**
 * Avvio dell'app e rete di sicurezza.
 * - L'interfaccia si mostra subito; il database si prepara in parallelo.
 * - Se il database non si apre entro pochi secondi, si mostra una schermata
 *   di recupero con le istruzioni invece di uno schermo vuoto.
 * - Gli errori imprevisti vengono mostrati in un avviso, non ignorati.
 */
class Startup {
  state = $state<'loading' | 'ready' | 'failed'>('loading')
  failure = $state('')
  /** Ultimo errore imprevisto (per l'avviso in basso). */
  lastError = $state('')

  async run() {
    this.state = 'loading'
    try {
      await withTimeout(
        db.open().then(() => ensureSeeded()),
        8000,
        'Il database dell\'app non risponde',
      )
      this.state = 'ready'
      // La sincronizzazione parte dopo: un suo problema non deve bloccare l'app
      void import('./sync/sync.svelte').then(({ sync }) => sync.init()).catch((e) => this.report(e))
    } catch (e) {
      this.failure = errorMessage(e)
      this.state = 'failed'
    }
  }

  installHandlers() {
    window.addEventListener('error', (e) => this.report(e.error ?? e.message))
    window.addEventListener('unhandledrejection', (e) => this.report(e.reason))
    // Una versione più nuova dell'app (in un'altra finestra) cambia il database: ricarica
    db.on('versionchange', () => {
      db.close()
      location.reload()
    })
  }

  report(e: unknown) {
    const msg = errorMessage(e)
    // Errori innocui di rete/estensioni non interessano all'utente
    if (!msg || /ResizeObserver|Script error/i.test(msg)) return
    console.error(e)
    this.lastError = msg
  }
}

export const startup = new Startup()
