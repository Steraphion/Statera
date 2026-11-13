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
  #apply: ((reload?: boolean) => Promise<void>) | null = null

  start() {
    if (!('serviceWorker' in navigator)) return
    this.#apply = registerSW({
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

  async update() {
    await this.#apply?.(true)
  }
}

export const pwa = new PwaState()
