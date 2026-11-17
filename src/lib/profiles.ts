/**
 * Profili: ogni account Google ha il proprio database sul dispositivo,
 * così più persone possono usare Statera sullo stesso telefono/PC
 * senza mai mescolare i dati.
 *
 * Ogni database di Statera presente sul dispositivo compare sempre nell'elenco (dalla v0.36.1):
 * prima il profilo iniziale entrava solo collegandolo a Google, e un profilo nuovo creato da un
 * dispositivo non collegato lo nascondeva, come se i dati fossero spariti.
 */

export interface Profile {
  /** Nome del database locale. */
  db: string
  /** Account Google collegato ('' se non ancora collegato). */
  email: string
  name: string
}

/** Contenuto di un profilo, per riconoscerlo nell'elenco. */
export interface ProfileSummary {
  accounts: number
  movements: number
  /** Account Google collegato secondo il database ('' se non collegato). */
  email: string
}

const KEY_LIST = 'statera.profili'
const KEY_ACTIVE = 'statera.profiloAttivo'
export const DEFAULT_DB = 'statera-locale'

function safeGet(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

function safeSet(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    /* archiviazione non disponibile: si continua con il profilo predefinito */
  }
}

export function listProfiles(): Profile[] {
  try {
    const list = JSON.parse(safeGet(KEY_LIST) ?? '[]') as Profile[]
    return Array.isArray(list) ? list.filter((p) => p && typeof p.db === 'string') : []
  } catch {
    return []
  }
}

function saveProfiles(list: Profile[]) {
  safeSet(KEY_LIST, JSON.stringify(list))
}

/** Database da aprire all'avvio. */
export function activeDbName(): string {
  return safeGet(KEY_ACTIVE) || DEFAULT_DB
}

export function upsertProfile(p: Profile) {
  const list = listProfiles().filter((x) => x.db !== p.db)
  list.push(p)
  saveProfiles(list)
}

export function activeProfile(): Profile {
  const db = activeDbName()
  return listProfiles().find((p) => p.db === db) ?? { db, email: '', name: '' }
}

/** Il profilo in uso entra nell'elenco (senza toccare un account già collegato). */
export function ensureListed(db: string) {
  if (!listProfiles().some((p) => p.db === db)) upsertProfile({ db, email: '', name: '' })
}

/** Passa a un altro profilo: l'app si ricarica con il suo database. */
export function switchTo(db: string) {
  safeSet(KEY_ACTIVE, db)
  location.reload()
}

/** Nuovo profilo vuoto per un altro account Google. */
export function createProfile(): string {
  const db = `statera-${crypto.randomUUID().slice(0, 8)}`
  upsertProfile({ db, email: '', name: '' })
  return db
}

export function removeProfile(db: string) {
  saveProfiles(listProfiles().filter((p) => p.db !== db))
}

/** Nome di un database creato da Statera (profilo iniziale o profilo aggiunto). */
export function isStateraDb(name: string): boolean {
  return name === DEFAULT_DB || /^statera-[0-9a-f]{8}$/.test(name)
}

/**
 * Elenco completo: i profili salvati più i database di Statera trovati sul dispositivo e rimasti
 * fuori (`found`), più quello in uso. Ordine: quello in uso, poi gli altri come erano.
 */
export function mergeProfiles(list: Profile[], found: string[], current: string): Profile[] {
  const out = [...list]
  for (const name of [current, ...found]) {
    if (isStateraDb(name) && !out.some((p) => p.db === name)) out.push({ db: name, email: '', name: '' })
  }
  return [...out.filter((p) => p.db === current), ...out.filter((p) => p.db !== current)]
}

/** Database di Statera presenti sul dispositivo; null se il browser non sa elencarli. */
export async function localDatabases(): Promise<string[] | null> {
  try {
    if (typeof indexedDB === 'undefined' || !indexedDB.databases) return null
    return (await indexedDB.databases()).map((d) => d.name ?? '').filter(isStateraDb)
  } catch {
    return null
  }
}

/**
 * Tutti i profili del dispositivo. Quelli trovati e non ancora nell'elenco vi entrano, così non
 * si perdono più. Se il browser non sa elencare i database si aggiunge almeno il profilo iniziale.
 */
export async function allProfiles(current: string): Promise<Profile[]> {
  const found = (await localDatabases()) ?? [DEFAULT_DB]
  const merged = mergeProfiles(listProfiles(), found, current)
  if (merged.length !== listProfiles().length) saveProfiles(merged)
  return merged
}

/** Nomi di tutti i database di Statera sul dispositivo (per «PIN dimenticato»). */
export async function allDbNames(): Promise<string[]> {
  const found = (await localDatabases()) ?? []
  return [...new Set([DEFAULT_DB, ...listProfiles().map((p) => p.db), ...found])]
}

function request<T>(r: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    r.onsuccess = () => resolve(r.result)
    r.onerror = () => reject(r.error)
  })
}

async function countLive(store: IDBObjectStore): Promise<number> {
  const all = (await request(store.getAll())) as { deletedAt?: number | null }[]
  return all.filter((r) => !r?.deletedAt).length
}

/**
 * Quanti conti e movimenti ha un profilo, letto direttamente dal suo database senza crearlo se
 * non esiste (null in quel caso o se non si riesce a leggerlo).
 */
export async function profileSummary(name: string): Promise<ProfileSummary | null> {
  if (typeof indexedDB === 'undefined') return null
  let idb: IDBDatabase
  try {
    idb = await new Promise<IDBDatabase>((resolve, reject) => {
      const r = indexedDB.open(name)
      // Il database non esiste: si annulla la creazione
      r.onupgradeneeded = () => r.transaction?.abort()
      r.onsuccess = () => resolve(r.result)
      r.onerror = () => reject(r.error)
      r.onblocked = () => reject(new Error('bloccato'))
    })
  } catch {
    return null
  }
  try {
    const stores = ['accounts', 'transactions', 'meta'].filter((s) => idb.objectStoreNames.contains(s))
    if (stores.length < 3) return { accounts: 0, movements: 0, email: '' }
    const tx = idb.transaction(stores, 'readonly')
    const [accounts, movements, sync] = await Promise.all([
      countLive(tx.objectStore('accounts')),
      countLive(tx.objectStore('transactions')),
      request(tx.objectStore('meta').get('sync')) as Promise<{ value?: { email?: string } } | undefined>,
    ])
    return { accounts, movements, email: sync?.value?.email ?? '' }
  } catch {
    return null
  } finally {
    idb.close()
  }
}

/** Elimina un profilo vuoto e il suo database. */
export async function deleteProfile(name: string) {
  await new Promise<void>((resolve) => {
    const r = indexedDB.deleteDatabase(name)
    r.onsuccess = r.onerror = r.onblocked = () => resolve()
  })
  removeProfile(name)
}
