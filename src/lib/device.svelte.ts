/**
 * Stato del dispositivo: installazione come app e archiviazione persistente.
 */

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

class DeviceState {
  installed = $state(window.matchMedia('(display-mode: standalone)').matches)
  canInstall = $state(false)
  persistent = $state<boolean | null>(null)
  #promptEvent: BeforeInstallPromptEvent | null = null

  constructor() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      this.#promptEvent = e as BeforeInstallPromptEvent
      this.canInstall = true
    })
    window.addEventListener('appinstalled', () => {
      this.installed = true
      this.canInstall = false
    })
    this.#requestPersistence()
  }

  async install() {
    if (!this.#promptEvent) return
    await this.#promptEvent.prompt()
    await this.#promptEvent.userChoice
    this.#promptEvent = null
    this.canInstall = false
  }

  /** Chiede al browser di non cancellare mai i dati locali per liberare spazio. */
  async #requestPersistence() {
    if (!navigator.storage?.persist) return
    this.persistent = (await navigator.storage.persisted()) || (await navigator.storage.persist())
  }
}

export const device = new DeviceState()
