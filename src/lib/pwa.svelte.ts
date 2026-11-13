import { registerSW } from 'virtual:pwa-register'

/**
 * Aggiornamenti dell'app.
 * Un'app installata su Android resta aperta in background anche per giorni:
 * per questo controlliamo se esiste una nuova versione ogni volta che l'app
 * torna in primo piano (e comunque ogni ora). Quando è pronta mostriamo un
 * avviso: l'aggiornamento parte solo quando l'utente lo conferma, così non
 * si perde un movimento a metà inserimento.
 */
class PwaState {
  updateReady = $state(false)
  updating = $state(false)

  start() {
    if (!('serviceWorker' in navigator)) return
    registerSW({
      immediate: true,
      onNeedRefresh: () => {
        this.updateReady = true
      },
      onRegisteredSW: (_url, registration) => {
        if (!registration) return
        const check = () => {
          if (navigator.onLine) registration.update().catch(() => {})
        }
        document.addEventListener('visibilitychange', () => {
          if (document.visibilityState === 'visible') check()
        })
        setInterval(check, 60 * 60 * 1000)
      },
    })
  }

  /**
   * Applica l'aggiornamento: attiva la nuova versione e ricarica.
   * Funziona sia se la pagina è già gestita dal service worker sia se non lo è
   * (es. primo avvio dopo l'installazione): in ogni caso si ricarica entro 3 secondi.
   */
  async update() {
    this.updating = true
    try {
      const reg = await navigator.serviceWorker.getRegistration()
      const waiting = reg?.waiting
      if (waiting) {
        const activated = new Promise<void>((resolve) => {
          navigator.serviceWorker.addEventListener('controllerchange', () => resolve(), { once: true })
          waiting.addEventListener('statechange', () => {
            if (waiting.state === 'activated') resolve()
          })
        })
        waiting.postMessage({ type: 'SKIP_WAITING' })
        await Promise.race([activated, new Promise((r) => setTimeout(r, 3000))])
      }
    } finally {
      location.reload()
    }
  }
}

export const pwa = new PwaState()
