/**
 * Profili: ogni account Google ha il proprio database sul dispositivo,
 * così più persone possono usare Statera sullo stesso telefono/PC
 * senza mai mescolare i dati.
 */

export interface Profile {
  /** Nome del database locale. */
  db: string
  /** Account Google collegato ('' se non ancora collegato). */
  email: string
  name: string
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
    return Array.isArray(list) ? list : []
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
