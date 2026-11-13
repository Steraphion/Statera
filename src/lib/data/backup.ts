import { db, type StateraDB } from './db'
import { ensureSeeded } from './repo'
import type { Account, Card, Category, Meta, Transaction } from './types'

/**
 * Backup manuale: un file JSON con TUTTI i dati del dispositivo
 * (compresi i record cancellati, che servono alla sincronizzazione).
 * Il file non è cifrato: la cifratura arriva con la Fase 2.
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
  const [accounts, cards, categories, transactions, meta] = await Promise.all([
    d.accounts.toArray(),
    d.cards.toArray(),
    d.categories.toArray(),
    d.transactions.toArray(),
    d.meta.toArray(),
  ])
  return {
    format: BACKUP_FORMAT,
    schema: BACKUP_SCHEMA,
    appVersion,
    exportedAt: new Date().toISOString(),
    data: { accounts, cards, categories, transactions, meta: meta.filter((m) => !LOCAL_META.has(m.key)) },
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

/** Legge e controlla un file di backup. Lancia un errore comprensibile se non è valido. */
export function parseBackup(text: string): BackupFile {
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    throw new Error('Il file non è un backup di Statera (formato non leggibile)')
  }
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
  await d.transaction('rw', [d.accounts, d.cards, d.categories, d.transactions, d.meta], async () => {
    const keep = (await d.meta.toArray()).filter((m) => LOCAL_META.has(m.key))
    await Promise.all([d.accounts.clear(), d.cards.clear(), d.categories.clear(), d.transactions.clear(), d.meta.clear()])
    await d.accounts.bulkAdd(b.data.accounts)
    await d.cards.bulkAdd(b.data.cards)
    await d.categories.bulkAdd(b.data.categories)
    await d.transactions.bulkAdd(b.data.transactions)
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
  await d.transaction('rw', [d.accounts, d.cards, d.categories, d.transactions, d.meta], async () => {
    await Promise.all([d.accounts.clear(), d.cards.clear(), d.categories.clear(), d.transactions.clear(), d.meta.clear()])
  })
  await ensureSeeded(d)
}

export function backupFileName(date = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0')
  return `statera-backup-${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}.json`
}
