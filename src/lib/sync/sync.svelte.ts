import { liveQuery } from 'dexie'
import { db } from '../data/db'
import { today } from '../data/util'
import { processRecurring } from '../data/recurring'
import { upsertProfile } from '../profiles'
import * as core from './core'
import * as cr from './crypto'
import { AuthExpiredError, Drive, OfflineError, requestToken, revokeToken, type DriveFile, type Token } from './google'
import { hasUserData, TABLES } from './merge'

/**
 * Stato della sincronizzazione per l'interfaccia, e quando sincronizzare:
 * all'avvio, quando l'app torna in primo piano, quando torna la rete,
 * pochi secondi dopo ogni modifica e ogni 5 minuti mentre l'app è aperta.
 */

export type SyncStatus =
  | 'off' // non attiva su questo dispositivo
  | 'locked' // collegata, ma serve la password
  | 'needs-auth' // serve riconnettersi a Google (permesso scaduto)
  | 'idle' // tutto a posto
  | 'syncing'
  | 'offline'
  | 'error'

export interface SyncMeta {
  email: string
  name: string
  linkedAt: number
  lastSyncAt: number | null
  lastBackupDay: string | null
}

/** Esito del primo passo dell'attivazione (dopo l'accesso a Google). */
export interface Connection {
  email: string
  name: string
  /** Su Drive esiste già una configurazione di Statera (altro dispositivo). */
  existing: boolean
  /** Questo dispositivo ha già dati inseriti dall'utente. */
  localHasData: boolean
}

const TOKEN_KEY = () => `statera.token.${db.name}`

interface Pending {
  token: Token
  email: string
  name: string
  files: DriveFile[]
  keys: cr.KeysFile | null
}

class SyncEngine {
  status = $state<SyncStatus>('off')
  meta = $state<SyncMeta | null>(null)
  error = $state('')
  /** Ultimo esito, per mostrarlo all'utente. */
  lastResult = $state<{ pulled: number; pushed: boolean } | null>(null)

  #key: CryptoKey | null = null
  #token: Token | null = null
  #pending: Pending | null = null
  #running = false
  #again = false
  #timer: ReturnType<typeof setTimeout> | null = null
  #watching = false
  #lastStamp = 0

  // ---------- avvio ----------

  async init() {
    const meta = (await db.meta.get('sync'))?.value as SyncMeta | undefined
    this.meta = meta ?? null
    this.#key = ((await db.meta.get('syncKey'))?.value as CryptoKey | undefined) ?? null
    this.#token = this.#loadToken()
    if (!meta) {
      this.status = 'off'
      return
    }
    this.#watch()
    if (!this.#key) this.status = 'locked'
    else this.syncSoon(0)
  }

  // ---------- permesso Google ----------

  #loadToken(): Token | null {
    try {
      const t = JSON.parse(localStorage.getItem(TOKEN_KEY()) ?? 'null') as Token | null
      return t && t.expiresAt > Date.now() ? t : null
    } catch {
      return null
    }
  }

  #saveToken(t: Token | null) {
    this.#token = t
    try {
      if (t) localStorage.setItem(TOKEN_KEY(), JSON.stringify(t))
      else localStorage.removeItem(TOKEN_KEY())
    } catch {
      /* non importa */
    }
  }

  #validToken(): Token | null {
    if (this.#token && this.#token.expiresAt > Date.now()) return this.#token
    return null
  }

  /** Riconnessione a Google dopo la scadenza del permesso (va chiamata da un tocco). */
  async reconnect() {
    this.error = ''
    try {
      const t = await requestToken({ silent: true, hint: this.meta?.email })
      // Controllo che sia lo stesso account
      const user = await new Drive(t.value).user()
      if (user?.email && this.meta?.email && user.email !== this.meta.email) {
        throw new Error(`Hai scelto ${user.email}, ma questo profilo è collegato a ${this.meta.email}`)
      }
      this.#saveToken(t)
      await this.syncNow()
    } catch (e) {
      this.error = msg(e)
    }
  }

  // ---------- attivazione ----------

  /** Passo 1: accesso a Google e controllo di cosa c'è su Drive (va chiamata da un tocco). */
  async connect(): Promise<Connection> {
    const token = await requestToken({ silent: false })
    const drive = new Drive(token.value)
    const user = (await drive.user()) ?? { email: '', name: '' }
    const files = await drive.list()
    const keys = await core.readKeys(drive, files)
    this.#pending = { token, ...user, files, keys }
    return {
      email: user.email,
      name: user.name,
      existing: !!keys,
      localHasData: hasUserData(await core.readLocal(db)),
    }
  }

  /** Passo 2 (primo dispositivo): crea le chiavi con password e chiave di recupero, poi carica i dati. */
  async createNew(password: string, recoveryKey: string) {
    const p = this.#need()
    const { keys, dataKey } = await cr.createKeys(password, recoveryKey)
    const drive = new Drive(p.token.value)
    await core.writeKeys(drive, p.files, keys)
    await this.#link(p, dataKey)
    await this.#run(() => core.syncOnce(db, drive, dataKey))
  }

  /** Passo 2 (altro dispositivo): sblocca con la password o la chiave di recupero. */
  async joinExisting(
    secret: { password?: string; recoveryKey?: string; newPassword?: string },
    mode: 'merge' | 'replace',
  ) {
    const p = this.#need()
    if (!p.keys) throw new Error('Configurazione su Drive non trovata')
    const drive = new Drive(p.token.value)
    let keys = p.keys
    let dataKey: CryptoKey
    if (secret.recoveryKey) {
      dataKey = await cr.unlockWithRecovery(keys, secret.recoveryKey)
      if (secret.newPassword) {
        keys = await cr.changePassword(keys, { recoveryKey: secret.recoveryKey }, secret.newPassword)
        await core.writeKeys(drive, p.files, keys)
      }
    } else {
      dataKey = await cr.unlockWithPassword(keys, secret.password ?? '')
    }
    await this.#link(p, dataKey)
    await this.#run(() => core.firstLink(db, drive, dataKey, mode))
  }

  /** Dispositivo collegato ma "bloccato" (chiave assente): sblocco con la password. */
  async unlock(secret: { password?: string; recoveryKey?: string }) {
    const token = this.#validToken() ?? (await requestToken({ silent: true, hint: this.meta?.email }))
    this.#saveToken(token)
    const drive = new Drive(token.value)
    const keys = await core.readKeys(drive, await drive.list())
    if (!keys) throw new Error('Configurazione su Drive non trovata')
    const dataKey = secret.recoveryKey
      ? await cr.unlockWithRecovery(keys, secret.recoveryKey)
      : await cr.unlockWithPassword(keys, secret.password ?? '')
    this.#key = dataKey
    await db.meta.put({ key: 'syncKey', value: dataKey })
    await this.syncNow()
  }

  #need() {
    if (!this.#pending) throw new Error('Accedi prima con Google')
    return this.#pending
  }

  async #link(p: Pending, dataKey: CryptoKey) {
    const meta: SyncMeta = { email: p.email, name: p.name, linkedAt: Date.now(), lastSyncAt: null, lastBackupDay: null }
    await db.meta.bulkPut([
      { key: 'sync', value: meta },
      { key: 'syncKey', value: dataKey },
    ])
    this.meta = meta
    this.#key = dataKey
    this.#saveToken(p.token)
    this.#pending = null
    upsertProfile({ db: db.name, email: p.email, name: p.name })
    this.#watch()
  }

  /** Dopo "Elimina tutti i dati": il dispositivo non è più collegato (Drive non viene toccato). */
  forget() {
    this.#saveToken(null)
    this.meta = null
    this.#key = null
    this.status = 'off'
    this.error = ''
  }

  /** Scollega questo dispositivo: i dati restano qui e su Drive. */
  async disconnect() {
    const t = this.#validToken()
    if (t) await revokeToken(t.value)
    this.#saveToken(null)
    await db.meta.bulkDelete(['sync', 'syncKey'])
    this.meta = null
    this.#key = null
    this.status = 'off'
    this.error = ''
  }

  // ---------- sincronizzazione ----------

  /** Programma una sincronizzazione fra `delay` ms (le richieste ravvicinate si uniscono). */
  syncSoon(delay = 3000) {
    if (!this.meta) return
    if (this.#timer) clearTimeout(this.#timer)
    this.#timer = setTimeout(() => {
      this.#timer = null
      void this.syncNow()
    }, delay)
  }

  async syncNow() {
    if (!this.meta) return
    if (!this.#key) {
      this.status = 'locked'
      return
    }
    const token = this.#validToken()
    if (!token) {
      this.status = 'needs-auth'
      return
    }
    const key = this.#key
    await this.#run(() => core.syncOnce(db, new Drive(token.value), key))
  }

  async #run(job: () => Promise<core.SyncResult>) {
    if (this.#running) {
      this.#again = true
      return
    }
    if (typeof navigator !== 'undefined' && navigator.onLine === false) {
      this.status = 'offline'
      return
    }
    this.#running = true
    this.status = 'syncing'
    this.error = ''
    try {
      const r = await job()
      this.lastResult = { pulled: r.pulled, pushed: r.pushed }
      const t = this.#validToken()
      const day = today()
      if (t && this.#key && this.meta?.lastBackupDay !== day) {
        await core.dailyBackup(new Drive(t.value), this.#key, r.merged, r.files, day)
        await this.#updateMeta({ lastBackupDay: day })
      }
      await this.#updateMeta({ lastSyncAt: Date.now() })
      // Ora che i dati sono allineati, si registrano i movimenti ricorrenti scaduti
      // (se ne nascono, verranno caricati alla prossima sincronizzazione, tra pochi secondi)
      this.#lastStamp = await this.#localStamp()
      this.status = 'idle'
      if ((await processRecurring(today())) > 0) this.syncSoon(1000)
    } catch (e) {
      if (e instanceof AuthExpiredError) {
        this.#saveToken(null)
        this.status = 'needs-auth'
      } else if (e instanceof OfflineError) {
        this.status = 'offline'
      } else {
        this.status = 'error'
        this.error = msg(e)
      }
    } finally {
      this.#running = false
      if (this.#again) {
        this.#again = false
        this.syncSoon(500)
      }
    }
  }

  async #updateMeta(patch: Partial<SyncMeta>) {
    if (!this.meta) return
    const next = { ...this.meta, ...patch }
    await db.meta.put({ key: 'sync', value: next })
    this.meta = next
  }

  /** "Impronta" dei dati locali: l'orario della modifica più recente. */
  async #localStamp(): Promise<number> {
    const last = await Promise.all(
      TABLES.map((t) =>
        db.table(t).orderBy('updatedAt').last(),
      ),
    )
    return Math.max(0, ...last.map((r) => (r as { updatedAt?: number } | undefined)?.updatedAt ?? 0))
  }

  #watch() {
    if (this.#watching || typeof window === 'undefined') return
    this.#watching = true
    // Modifiche fatte sul dispositivo → sincronizza dopo qualche secondo
    liveQuery(() => this.#localStamp()).subscribe({
      next: (stamp) => {
        if (this.meta && stamp > this.#lastStamp && this.status !== 'syncing') this.syncSoon(4000)
      },
    })
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') this.syncSoon(500)
    })
    window.addEventListener('online', () => this.syncSoon(500))
    setInterval(() => {
      if (document.visibilityState === 'visible') this.syncSoon(0)
    }, 5 * 60 * 1000)
  }

  // ---------- gestione ----------

  async #drive(): Promise<Drive> {
    const t = this.#validToken()
    if (!t) {
      this.status = 'needs-auth'
      throw new Error('Riconnettiti a Google per continuare')
    }
    return new Drive(t.value)
  }

  async changePassword(current: { password?: string; recoveryKey?: string }, newPassword: string) {
    const drive = await this.#drive()
    const files = await drive.list()
    const keys = await core.readKeys(drive, files)
    if (!keys) throw new Error('Configurazione su Drive non trovata')
    await core.writeKeys(drive, files, await cr.changePassword(keys, current, newPassword))
  }

  async backups(): Promise<DriveFile[]> {
    const drive = await this.#drive()
    return core.listBackups(await drive.list())
  }

  /** Ripristino da un file esportato quando la sincronizzazione è attiva: vale per tutti i dispositivi. */
  async restoreSnapshot(snap: import('./merge').Snapshot) {
    const drive = await this.#drive()
    if (!this.#key) throw new Error('Sincronizzazione bloccata: inserisci la password')
    await core.restoreSnapshot(db, drive, this.#key, snap)
    await this.#updateMeta({ lastSyncAt: Date.now() })
  }

  async restore(backupId: string) {
    const drive = await this.#drive()
    if (!this.#key) throw new Error('Sincronizzazione bloccata: inserisci la password')
    await core.restoreFromBackup(db, drive, this.#key, backupId)
    await this.#updateMeta({ lastSyncAt: Date.now() })
  }
}

function msg(e: unknown): string {
  if (e instanceof cr.WrongSecretError) return e.message
  return e instanceof Error ? e.message : String(e)
}

export const sync = new SyncEngine()
