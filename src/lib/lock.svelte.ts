import * as lk from './lock'

/**
 * Stato del blocco dell'app (vale per tutto il dispositivo, tutti i profili).
 * La configurazione sta in localStorage, così il blocco compare prima ancora di aprire il database.
 * Impronta/volto: WebAuthn con l'autenticatore del dispositivo; nessun server, nessun dato esce.
 */

const store: lk.Storage = {
  getItem: (k) => {
    try {
      return localStorage.getItem(k)
    } catch {
      return null
    }
  },
  setItem: (k, v) => {
    try {
      localStorage.setItem(k, v)
    } catch {
      /* archiviazione non disponibile */
    }
  },
  removeItem: (k) => {
    try {
      localStorage.removeItem(k)
    } catch {
      /* archiviazione non disponibile */
    }
  },
}

const b64url = (buf: ArrayBuffer | Uint8Array) =>
  btoa(String.fromCharCode(...new Uint8Array(buf instanceof Uint8Array ? buf : new Uint8Array(buf))))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
const unb64url = (s: string) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), (c) => c.charCodeAt(0))

class AppLock {
  config = $state<lk.LockConfig | null>(lk.readConfig(store))
  /** All'avvio l'app parte bloccata se il blocco è attivo. */
  locked = $state(lk.readConfig(store) !== null)
  bioAvailable = $state(false)
  /** Proporre subito l'impronta? Sì all'avvio e al ritorno nell'app, no dopo "Blocca ora". */
  autoBio = $state(true)
  #hiddenAt: number | null = null
  #started = false

  get enabled() {
    return this.config !== null
  }

  start() {
    if (this.#started || typeof document === 'undefined') return
    this.#started = true
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.#hiddenAt = Date.now()
        // "Subito": si blocca già nascondendo, così l'anteprima delle app recenti non mostra i dati
        if (this.config && this.config.timeout === 0) this.#lock(true)
      } else {
        if (lk.shouldLock(this.config, this.#hiddenAt)) this.#lock(true)
        this.#hiddenAt = null
      }
    })
    // Un'altra finestra cambia il blocco (es. disattivato su un'altra scheda)
    window.addEventListener('storage', (e) => {
      if (e.key === lk.LOCK_KEY) this.config = lk.readConfig(store)
    })
    void this.checkBio()
  }

  async checkBio() {
    try {
      this.bioAvailable =
        typeof PublicKeyCredential !== 'undefined' &&
        (await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable())
    } catch {
      this.bioAvailable = false
    }
  }

  #save(cfg: lk.LockConfig | null) {
    lk.writeConfig(store, cfg)
    this.config = cfg
  }

  /** Attiva il blocco con un nuovo PIN. */
  async enable(pin: string, timeout: number) {
    this.#save(await lk.makeConfig(pin, timeout))
  }

  async #check(pin: string): Promise<lk.Attempt> {
    if (!this.config) throw new Error('Il blocco non è attivo')
    const r = await lk.tryPin(this.config, pin)
    this.#save(r.cfg)
    return r
  }

  #explain(r: lk.Attempt): string {
    if (r.ok) return ''
    if (r.reason === 'wait') return `Troppi tentativi: riprova tra ${lk.formatWait(r.waitMs)}`
    const left = lk.FREE_ATTEMPTS - r.cfg.fails
    if (r.waitMs) return `PIN sbagliato. Troppi tentativi: riprova tra ${lk.formatWait(r.waitMs)}`
    return left > 0 && left < lk.FREE_ATTEMPTS ? `PIN sbagliato (ancora ${left} ${left === 1 ? 'tentativo' : 'tentativi'} prima di un'attesa)` : 'PIN sbagliato'
  }

  /** Sblocca con il PIN. Restituisce un messaggio d'errore o '' se è andata bene. */
  async unlock(pin: string): Promise<string> {
    const r = await this.#check(pin)
    if (r.ok) this.locked = false
    return this.#explain(r)
  }

  /** Verifica il PIN attuale (per cambiarlo o disattivare il blocco); lancia un errore se sbagliato. */
  async #require(pin: string) {
    const r = await this.#check(pin)
    if (!r.ok) throw new Error(this.#explain(r))
  }

  async changePin(oldPin: string, newPin: string) {
    await this.#require(oldPin)
    const next = await lk.makeConfig(newPin, this.config!.timeout)
    this.#save({ ...next, bio: this.config!.bio })
  }

  async disable(pin: string) {
    await this.#require(pin)
    this.#save(null)
    this.locked = false
  }

  setTimeout(timeout: number) {
    if (this.config) this.#save({ ...this.config, timeout })
  }

  #lock(autoBio: boolean) {
    if (this.locked) return
    this.autoBio = autoBio
    this.locked = true
  }

  lockNow() {
    if (this.config) this.#lock(false)
  }

  // ---------- Impronta, volto o blocco schermo del dispositivo (WebAuthn) ----------

  async enableBio(pin: string) {
    await this.#require(pin)
    if (!this.bioAvailable) throw new Error('Questo dispositivo non offre impronta o riconoscimento del volto al browser')
    let cred: PublicKeyCredential | null
    try {
      cred = (await navigator.credentials.create({
        publicKey: {
          challenge: crypto.getRandomValues(new Uint8Array(32)),
          rp: { name: 'Statera', id: location.hostname },
          user: { id: crypto.getRandomValues(new Uint8Array(16)), name: 'Statera', displayName: 'Statera' },
          pubKeyCredParams: [
            { type: 'public-key', alg: -7 },
            { type: 'public-key', alg: -257 },
          ],
          authenticatorSelection: { authenticatorAttachment: 'platform', userVerification: 'required', residentKey: 'discouraged' },
          attestation: 'none',
          timeout: 60_000,
        },
      })) as PublicKeyCredential | null
    } catch (e) {
      throw new Error(e instanceof DOMException && e.name === 'NotAllowedError' ? 'Operazione annullata' : 'Impossibile attivare l\'impronta su questo dispositivo')
    }
    if (!cred) throw new Error('Operazione annullata')
    this.#save({ ...this.config!, bio: { id: b64url(cred.rawId) } })
  }

  disableBio() {
    if (this.config) this.#save({ ...this.config, bio: null })
  }

  /** Sblocco con impronta. Restituisce '' se riuscito, altrimenti un messaggio. */
  async unlockBio(): Promise<string> {
    const bio = this.config?.bio
    if (!bio) return 'Impronta non attiva'
    if (this.config && Date.now() < this.config.waitUntil) {
      return `Troppi tentativi: riprova tra ${lk.formatWait(this.config.waitUntil - Date.now())}`
    }
    try {
      const a = (await navigator.credentials.get({
        publicKey: {
          challenge: crypto.getRandomValues(new Uint8Array(32)),
          rpId: location.hostname,
          allowCredentials: [{ type: 'public-key', id: unb64url(bio.id), transports: ['internal'] }],
          userVerification: 'required',
          timeout: 60_000,
        },
      })) as PublicKeyCredential | null
      if (!a || b64url(a.rawId) !== bio.id) return 'Impronta non riconosciuta'
      const data = new Uint8Array((a.response as AuthenticatorAssertionResponse).authenticatorData)
      // Flag "utente verificato" (bit 2): impronta, volto o PIN del dispositivo
      if (!(data[32] & 0x04)) return 'Verifica non completata'
      this.locked = false
      this.#save({ ...this.config!, fails: 0, waitUntil: 0 })
      return ''
    } catch {
      return 'Impronta non disponibile: usa il PIN'
    }
  }

  /** PIN dimenticato: cancella tutti i dati locali di Statera su questo dispositivo e il blocco. */
  async resetDevice(dbNames: string[]) {
    for (const name of dbNames) {
      await new Promise<void>((resolve) => {
        const r = indexedDB.deleteDatabase(name)
        r.onsuccess = r.onerror = r.onblocked = () => resolve()
      })
    }
    try {
      for (const k of Object.keys(localStorage)) if (k.startsWith('statera.')) localStorage.removeItem(k)
    } catch {
      /* archiviazione non disponibile */
    }
    location.replace(location.pathname)
  }
}

export const lock = new AppLock()
