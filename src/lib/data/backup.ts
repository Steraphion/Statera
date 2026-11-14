import { db, type StateraDB } from './db'
import { ensureSeeded } from './repo'
import type { Account, Card, Category, Goal, Meta, Recurring, Template, Transaction } from './types'
import { TABLES, type Snapshot } from '../sync/merge'
import { openWithPassword, sealWithPassword, type PasswordSealed } from '../sync/crypto'

/**
 * Backup manuale: un file JSON con TUTTI i dati del dispositivo
 * (compresi i record cancellati, che servono alla sincronizzazione).
 * Il file può essere protetto da password (consigliato): in quel caso è un
 * "involucro" cifrato AES-256-GCM con chiave derivata dalla password (PBKDF2).
 */

export const BACKUP_FORMAT = 'statera-backup'
export const BACKUP_SCHEMA = 1

export interface BackupFile {
  format: typeof BACKUP_FORMAT
  schema: number
  appVersion: string
  exportedAt: string
  data: {
    accounts: Account[]
    cards: Card[]
    categories: Category[]
    transactions: Transaction[]
    /** Dalla Fase 3 (assente nei backup precedenti). */
    recurring?: Recurring[]
    /** Dalla v0.15 (assenti nei backup precedenti). */
    templates?: Template[]
    goals?: Goal[]
    meta: Meta[]
  }
}

export interface BackupSummary {
  exportedAt: string
  accounts: number
  cards: number
  categories: number
  transactions: number
}

/** Chiavi tecniche del dispositivo che non viaggiano con il backup. */
const LOCAL_META = new Set(['ultimoBackup', 'sync', 'syncKey'])

export async function buildBackup(appVersion: string, d: StateraDB = db): Promise<BackupFile> {
  const rows = await Promise.all(TABLES.map((t) => d.table(t).toArray()))
  const meta = await d.meta.toArray()
  return {
    format: BACKUP_FORMAT,
    schema: BACKUP_SCHEMA,
    appVersion,
    exportedAt: new Date().toISOString(),
    data: {
      ...(Object.fromEntries(TABLES.map((t, i) => [t, rows[i]])) as unknown as Snapshot),
      meta: meta.filter((m) => !LOCAL_META.has(m.key)),
    },
  }
}

export async function markBackupDone(d: StateraDB = db) {
  await d.meta.put({ key: 'ultimoBackup', value: Date.now() })
}

export async function lastBackupAt(d: StateraDB = db): Promise<number | null> {
  return ((await d.meta.get('ultimoBackup'))?.value as number | undefined) ?? null
}

function isRecordList(v: unknown): v is { id: string }[] {
  return Array.isArray(v) && v.every((r) => r && typeof r === 'object' && typeof (r as { id: unknown }).id === 'string')
}

export const ENCRYPTED_FORMAT = 'statera-backup-cifrato'

/** File di backup protetto da password: solo la data di esportazione è in chiaro. */
export interface EncryptedBackupFile {
  format: typeof ENCRYPTED_FORMAT
  exportedAt: string
  sealed: PasswordSealed
}

export async function encryptBackup(file: BackupFile, password: string): Promise<EncryptedBackupFile> {
  return { format: ENCRYPTED_FORMAT, exportedAt: file.exportedAt, sealed: await sealWithPassword(password, file) }
}

/** Legge un file scelto dall'utente: backup in chiaro oppure protetto da password. */
export function readBackupFile(text: string): { encrypted: EncryptedBackupFile } | { plain: BackupFile } {
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    throw new Error('Il file non è un backup di Statera (formato non leggibile)')
  }
  const e = raw as Partial<EncryptedBackupFile>
  if (e?.format === ENCRYPTED_FORMAT) {
    if (!e.sealed?.data || !e.sealed.salt) throw new Error('Il backup è incompleto o danneggiato')
    return { encrypted: e as EncryptedBackupFile }
  }
  return { plain: validateBackup(raw) }
}

/** Apre un backup protetto: password sbagliata → errore chiaro. */
export async function decryptBackup(file: EncryptedBackupFile, password: string): Promise<BackupFile> {
  return validateBackup(await openWithPassword<unknown>(password, file.sealed))
}

/** Legge e controlla un file di backup in chiaro. Lancia un errore comprensibile se non è valido. */
export function parseBackup(text: string): BackupFile {
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    throw new Error('Il file non è un backup di Statera (formato non leggibile)')
  }
  return validateBackup(raw)
}

function validateBackup(raw: unknown): BackupFile {
  const b = raw as Partial<BackupFile>
  if (!b || b.format !== BACKUP_FORMAT) throw new Error('Il file non è un backup di Statera')
  if (typeof b.schema !== 'number' || b.schema > BACKUP_SCHEMA) {
    throw new Error("Il backup è stato creato da una versione più recente di Statera: aggiorna l'app e riprova")
  }
  const data = b.data
  if (
    !data ||
    !isRecordList(data.accounts) ||
    !isRecordList(data.cards) ||
    !isRecordList(data.categories) ||
    !isRecordList(data.transactions) ||
    !Array.isArray(data.meta)
  ) {
    throw new Error('Il backup è incompleto o danneggiato')
  }
  return b as BackupFile
}

export function summarize(b: BackupFile): BackupSummary {
  const alive = (rows: { deletedAt: number | null }[]) => rows.filter((r) => r.deletedAt === null).length
  return {
    exportedAt: b.exportedAt,
    accounts: alive(b.data.accounts),
    cards: alive(b.data.cards),
    categories: alive(b.data.categories),
    transactions: alive(b.data.transactions),
  }
}

/** Sostituisce TUTTI i dati del dispositivo con quelli del backup. */
export async function restoreBackup(backup: BackupFile, d: StateraDB = db) {
  // Copia "pulita" (solo dati), qualunque sia l'origine dell'oggetto
  const b: BackupFile = JSON.parse(JSON.stringify(backup))
  await d.transaction('rw', [...TABLES.map((t) => d.table(t)), d.meta], async () => {
    const keep = (await d.meta.toArray()).filter((m) => LOCAL_META.has(m.key))
    await Promise.all([...TABLES.map((t) => d.table(t).clear()), d.meta.clear()])
    for (const t of TABLES) await d.table(t).bulkAdd(((b.data as unknown as Record<string, unknown[]>)[t] ?? []) as object[])
    await d.meta.bulkPut([...b.data.meta.filter((m) => !LOCAL_META.has(m.key)), ...keep])
    // Un backup ha sempre già le sue categorie: non ricaricare quelle iniziali
    await d.meta.put({ key: 'seeded', value: { restoredAt: Date.now() } })
  })
}

/**
 * Cancella tutto e riporta l'app allo stato iniziale (con le categorie di base).
 * Scollega anche questo dispositivo dalla sincronizzazione: i dati su Drive restano.
 */
export async function wipeAll(d: StateraDB = db) {
  await d.transaction('rw', [...TABLES.map((t) => d.table(t)), d.meta], async () => {
    await Promise.all([...TABLES.map((t) => d.table(t).clear()), d.meta.clear()])
  })
  await ensureSeeded(d)
}

export function backupFileName(date = new Date(), encrypted = false): string {
  const p = (n: number) => String(n).padStart(2, '0')
  const day = `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}`
  return encrypted ? `statera-backup-protetto-${day}.json` : `statera-backup-${day}.json`
}
