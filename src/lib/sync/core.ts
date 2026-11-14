import type { StateraDB } from '../data/db'
import type { Base } from '../data/types'
import * as cr from './crypto'
import type { DriveFile } from './google'
import { emptySnapshot, hasUserData, merge, TABLES, unifyForFirstLink, type Snapshot } from './merge'

/**
 * Nucleo della sincronizzazione, indipendente dall'interfaccia e da Google:
 * lavora con qualunque oggetto "DriveLike" (il vero Google Drive o uno finto nei test).
 */

export interface DriveLike {
  list(): Promise<DriveFile[]>
  read(id: string): Promise<string>
  create(name: string, content: string): Promise<DriveFile>
  update(id: string, content: string): Promise<DriveFile>
  remove(id: string): Promise<void>
}

export const DATA_FILE = 'statera-data.json'
export const KEYS_FILE = 'statera-keys.json'
export const BACKUP_PREFIX = 'statera-backup-'
export const KEEP_BACKUPS = 30

interface Payload {
  schema: 1
  savedAt: string
  data: Snapshot
}

// ---------- dati locali ----------

export async function readLocal(d: StateraDB): Promise<Snapshot> {
  const rows = await Promise.all(TABLES.map((t) => d.table(t).toArray()))
  return Object.fromEntries(TABLES.map((t, i) => [t, rows[i]])) as unknown as Snapshot
}

/**
 * Scrive i record arrivati da Drive, ma solo se nel frattempo (durante la
 * sincronizzazione) l'utente non li ha modificati di nuovo sul dispositivo.
 */
export async function applyToLocal(d: StateraDB, incoming: Snapshot): Promise<number> {
  let written = 0
  await d.transaction('rw', TABLES.map((t) => d.table(t)), async () => {
    for (const t of TABLES) {
      const rows = (incoming[t] ?? []) as Base[]
      if (!rows.length) continue
      const table = d.table<Base, string>(t)
      const current = await table.bulkGet(rows.map((r) => r.id))
      const fresh = rows.filter((r, i) => !current[i] || current[i]!.updatedAt < r.updatedAt)
      if (fresh.length) await table.bulkPut(fresh)
      written += fresh.length
    }
  })
  return written
}

/** Sostituisce tutti i dati del dispositivo (conti, carte, categorie, movimenti). */
export async function replaceLocal(d: StateraDB, snap: Snapshot) {
  const clean: Snapshot = { ...emptySnapshot(), ...JSON.parse(JSON.stringify(snap)) }
  await d.transaction('rw', TABLES.map((t) => d.table(t)), async () => {
    await Promise.all(TABLES.map((t) => d.table(t).clear()))
    for (const t of TABLES) await d.table(t).bulkAdd(clean[t] as Base[])
  })
}

// ---------- dati su Drive ----------

export function findFile(files: DriveFile[], name: string): DriveFile | undefined {
  return files.find((f) => f.name === name)
}

export async function readRemote(drive: DriveLike, key: CryptoKey, file: DriveFile | undefined): Promise<Snapshot | null> {
  if (!file) return null
  const p = await cr.open<Payload>(key, await drive.read(file.id))
  return { ...emptySnapshot(), ...p.data }
}

async function sealSnapshot(key: CryptoKey, snap: Snapshot): Promise<string> {
  const payload: Payload = { schema: 1, savedAt: new Date().toISOString(), data: snap }
  return cr.seal(key, payload)
}

export async function writeRemote(drive: DriveLike, key: CryptoKey, snap: Snapshot, file: DriveFile | undefined) {
  const content = await sealSnapshot(key, snap)
  return file ? drive.update(file.id, content) : drive.create(DATA_FILE, content)
}

export async function readKeys(drive: DriveLike, files: DriveFile[]): Promise<cr.KeysFile | null> {
  const f = findFile(files, KEYS_FILE)
  return f ? cr.parseKeysFile(await drive.read(f.id)) : null
}

export async function writeKeys(drive: DriveLike, files: DriveFile[], keys: cr.KeysFile) {
  const f = findFile(files, KEYS_FILE)
  const content = JSON.stringify(keys)
  return f ? drive.update(f.id, content) : drive.create(KEYS_FILE, content)
}

// ---------- sincronizzazione ----------

export interface SyncResult {
  /** Record arrivati da Drive e scritti sul dispositivo. */
  pulled: number
  /** Il file su Drive è stato aggiornato. */
  pushed: boolean
  merged: Snapshot
  files: DriveFile[]
}

/** Un giro completo: scarica, unisce, scrive sul dispositivo e (se serve) su Drive. */
export async function syncOnce(d: StateraDB, drive: DriveLike, key: CryptoKey): Promise<SyncResult> {
  const files = await drive.list()
  const dataFile = findFile(files, DATA_FILE)
  const remote = (await readRemote(drive, key, dataFile)) ?? emptySnapshot()
  const local = await readLocal(d)
  const { merged, toLocal, remoteChanged } = merge(local, remote)
  const pulled = await applyToLocal(d, toLocal)
  let pushed = false
  if (remoteChanged || !dataFile) {
    await writeRemote(drive, key, merged, dataFile)
    pushed = true
  }
  return { pulled, pushed, merged, files }
}

/**
 * Primo collegamento di questo dispositivo a un Drive che ha già dei dati.
 * - 'replace': il dispositivo prende i dati di Drive (quelli locali si perdono).
 * - 'merge': unione; conti, carte e categorie con lo stesso nome diventano una cosa sola.
 * Se il dispositivo non ha dati inseriti dall'utente, si prendono semplicemente quelli di Drive.
 */
export async function firstLink(
  d: StateraDB,
  drive: DriveLike,
  key: CryptoKey,
  mode: 'merge' | 'replace',
): Promise<SyncResult> {
  const files = await drive.list()
  const remote = await readRemote(drive, key, findFile(files, DATA_FILE))
  if (remote) {
    const local = await readLocal(d)
    if (mode === 'replace' || !hasUserData(local)) await replaceLocal(d, remote)
    else await replaceLocal(d, unifyForFirstLink(local, remote))
  }
  return syncOnce(d, drive, key)
}

// ---------- backup giornalieri su Drive ----------

export function backupName(day: string): string {
  return `${BACKUP_PREFIX}${day}.json`
}

export function listBackups(files: DriveFile[]): DriveFile[] {
  return files.filter((f) => f.name.startsWith(BACKUP_PREFIX)).sort((a, b) => b.name.localeCompare(a.name))
}

/** Salva (o aggiorna) il backup del giorno e tiene solo gli ultimi 30. */
export async function dailyBackup(drive: DriveLike, key: CryptoKey, snap: Snapshot, files: DriveFile[], day: string) {
  const name = backupName(day)
  const content = await sealSnapshot(key, snap)
  const existing = findFile(files, name)
  if (existing) await drive.update(existing.id, content)
  else await drive.create(name, content)
  const all = listBackups(await drive.list())
  for (const old of all.slice(KEEP_BACKUPS)) await drive.remove(old.id)
}

/** Ripristina un backup di Drive: diventa la versione di tutti i dispositivi. */
export async function restoreFromBackup(d: StateraDB, drive: DriveLike, key: CryptoKey, backupId: string) {
  const p = await cr.open<Payload>(key, await drive.read(backupId))
  await restoreSnapshot(d, drive, key, { ...emptySnapshot(), ...p.data })
}

/**
 * Riporta tutti i dispositivi allo stato di `snap` (backup di Drive o file esportato):
 * ciò che c'è ora e non è nel backup viene marcato come eliminato con un orario più
 * recente, e i record del backup diventano "nuovi", così l'unione non li annulla.
 */
export async function restoreSnapshot(d: StateraDB, drive: DriveLike, key: CryptoKey, snap: Snapshot) {
  const now = Date.now()
  const current = await readLocal(d)
  const files = await drive.list()
  const remote = (await readRemote(drive, key, findFile(files, DATA_FILE))) ?? emptySnapshot()
  const restored = emptySnapshot()
  for (const t of TABLES) {
    const keep = new Set(((snap[t] ?? []) as Base[]).map((r) => r.id))
    const gone = new Map<string, Base>()
    for (const r of [...((current[t] ?? []) as Base[]), ...((remote[t] ?? []) as Base[])]) {
      if (!keep.has(r.id)) gone.set(r.id, { ...r, deletedAt: r.deletedAt ?? now, updatedAt: now })
    }
    ;(restored[t] as Base[]) = [...((snap[t] ?? []) as Base[]).map((r) => ({ ...r, updatedAt: now })), ...gone.values()]
  }
  await replaceLocal(d, restored)
  await writeRemote(drive, key, restored, findFile(files, DATA_FILE))
}
