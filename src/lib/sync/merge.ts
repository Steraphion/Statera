import type { Account, Base, Card, Category, Goal, Recurring, Template, Transaction } from '../data/types'
import { normalize } from '../data/transactions'

/** Tutti i dati sincronizzati. */
export interface Snapshot {
  accounts: Account[]
  cards: Card[]
  categories: Category[]
  transactions: Transaction[]
  /** Dalla Fase 3; può mancare nei file creati da versioni precedenti. */
  recurring: Recurring[]
  /** Dalla v0.15 (Fase 4); può mancare. */
  templates: Template[]
  /** Dalla v0.15 (Fase 5); può mancare. */
  goals: Goal[]
}

/** Tabelle sincronizzate (e salvate nei backup). */
export const TABLES = ['accounts', 'cards', 'categories', 'transactions', 'recurring', 'templates', 'goals'] as const
export type TableName = (typeof TABLES)[number]

export function emptySnapshot(): Snapshot {
  return { accounts: [], cards: [], categories: [], transactions: [], recurring: [], templates: [], goals: [] }
}

/** Solo le tabelle sincronizzate (es. dai dati di un backup, senza `meta`). */
export function snapshotOf(data: Partial<Record<string, unknown>>): Snapshot {
  const out = emptySnapshot() as unknown as Record<string, unknown>
  for (const t of TABLES) if (Array.isArray(data[t])) out[t] = data[t]
  return out as unknown as Snapshot
}

export interface MergeResult {
  merged: Snapshot
  /** Record da scrivere sul dispositivo (più recenti su Drive o nuovi). */
  toLocal: Snapshot
  /** Il dispositivo ha qualcosa che Drive non ha: va caricato. */
  remoteChanged: boolean
}

/**
 * Unione record per record: vince la modifica più recente (updatedAt).
 * Le cancellazioni sono record con deletedAt: si propagano come le modifiche.
 * A parità, vince il dispositivo.
 */
export function merge(local: Snapshot, remote: Snapshot): MergeResult {
  const merged = emptySnapshot()
  const toLocal = emptySnapshot()
  let remoteChanged = false

  for (const t of TABLES) {
    const L = new Map<string, Base>((local[t] ?? []).map((r) => [r.id, r]))
    const R = new Map<string, Base>((remote[t] ?? []).map((r) => [r.id, r]))
    const out: Base[] = []
    for (const [id, l] of L) {
      const r = R.get(id)
      if (!r) {
        out.push(l)
        remoteChanged = true
      } else if (r.updatedAt > l.updatedAt) {
        out.push(r)
        ;(toLocal[t] as Base[]).push(r)
      } else {
        out.push(l)
        if (l.updatedAt > r.updatedAt) remoteChanged = true
      }
    }
    for (const [id, r] of R) {
      if (L.has(id)) continue
      out.push(r)
      ;(toLocal[t] as Base[]).push(r)
    }
    ;(merged[t] as Base[]) = out
  }
  // Tabelle aggiunte da versioni più recenti dell'app: si conservano così come sono
  for (const k of Object.keys(remote)) {
    if (!(TABLES as readonly string[]).includes(k)) (merged as unknown as Record<string, unknown>)[k] = (remote as unknown as Record<string, unknown>)[k]
  }
  return { merged, toLocal, remoteChanged }
}

/**
 * Primo collegamento di un dispositivo che ha già dei dati a un Drive che ne ha altri:
 * conti, carte e categorie con lo stesso nome (e tipo) vengono considerati la stessa cosa,
 * così non compaiono doppioni (es. le categorie iniziali create su entrambi i dispositivi).
 * I movimenti del dispositivo vengono ricollegati ai conti/categorie di Drive.
 */
export function unifyForFirstLink(local: Snapshot, remote: Snapshot): Snapshot {
  const alive = <T extends Base>(rows: T[]) => rows.filter((r) => r.deletedAt === null)
  const key = (s: string) => normalize(s).replace(/\s+/g, ' ').trim()

  // Conti: stesso tipo e nome
  const remoteAcc = new Map(alive(remote.accounts).map((a) => [`${a.type}|${key(a.name)}`, a.id]))
  const accMap = new Map<string, string>()
  for (const a of alive(local.accounts)) {
    const r = remoteAcc.get(`${a.type}|${key(a.name)}`)
    if (r && r !== a.id) accMap.set(a.id, r)
  }

  // Carte: stesso conto (dopo l'unificazione) e nome
  const remoteCard = new Map(alive(remote.cards).map((c) => [`${c.accountId}|${key(c.name)}`, c.id]))
  const cardMap = new Map<string, string>()
  for (const c of alive(local.cards)) {
    const r = remoteCard.get(`${accMap.get(c.accountId) ?? c.accountId}|${key(c.name)}`)
    if (r && r !== c.id) cardMap.set(c.id, r)
  }

  // Categorie: stesso tipo, stessa categoria principale (per nome) e stesso nome
  const path = (c: Category, all: Category[]) => {
    const parent = c.parentId ? all.find((p) => p.id === c.parentId) : null
    return `${c.kind}|${parent ? key(parent.name) : ''}|${key(c.name)}`
  }
  const rCats = alive(remote.categories)
  const remoteCat = new Map(rCats.map((c) => [path(c, rCats), c.id]))
  const lCats = alive(local.categories)
  const catMap = new Map<string, string>()
  for (const c of lCats) {
    const r = remoteCat.get(path(c, lCats))
    if (r && r !== c.id) catMap.set(c.id, r)
  }

  const now = Date.now()
  /** Ricorrenti e preferiti: fonti, categoria e conto di destinazione ricollegati. */
  function remapModel<T extends Recurring | Template>(r: T): T {
    const remapSource = (src: string) => {
      const [k, id] = src.split(':')
      const to = k === 'c' ? cardMap.get(id) : accMap.get(id)
      return to ? `${k}:${to}` : src
    }
    const parts = r.parts.map((p) => ({ ...p, source: remapSource(p.source) }))
    const categoryId = r.categoryId ? (catMap.get(r.categoryId) ?? r.categoryId) : null
    const toAccountId = r.toAccountId ? (accMap.get(r.toAccountId) ?? r.toAccountId) : null
    const changed =
      categoryId !== r.categoryId || toAccountId !== r.toAccountId || parts.some((p, i) => p.source !== r.parts[i].source)
    return changed ? { ...r, parts, categoryId, toAccountId, updatedAt: now } : r
  }
  const remapCategory = (c: Category): Category =>
    c.parentId && catMap.has(c.parentId) ? { ...c, parentId: catMap.get(c.parentId)!, updatedAt: now } : c

  return {
    accounts: local.accounts.filter((a) => !accMap.has(a.id)),
    cards: local.cards
      .filter((c) => !cardMap.has(c.id))
      .map((c) => (accMap.has(c.accountId) ? { ...c, accountId: accMap.get(c.accountId)!, updatedAt: now } : c)),
    categories: local.categories.filter((c) => !catMap.has(c.id)).map(remapCategory),
    recurring: (local.recurring ?? []).map(remapModel),
    templates: (local.templates ?? []).map(remapModel),
    goals: (local.goals ?? []).map((g) =>
      g.accountId && accMap.has(g.accountId) ? { ...g, accountId: accMap.get(g.accountId)!, updatedAt: now } : g,
    ),
    transactions: local.transactions.map((t) => {
      const changed =
        (t.categoryId && catMap.has(t.categoryId)) ||
        (t.toAccountId && accMap.has(t.toAccountId)) ||
        t.parts.some((p) => accMap.has(p.accountId) || (p.cardId && cardMap.has(p.cardId)))
      if (!changed) return t
      const parts = t.parts.map((p) => ({
        ...p,
        accountId: accMap.get(p.accountId) ?? p.accountId,
        cardId: p.cardId ? (cardMap.get(p.cardId) ?? p.cardId) : null,
      }))
      const toAccountId = t.toAccountId ? (accMap.get(t.toAccountId) ?? t.toAccountId) : null
      return {
        ...t,
        categoryId: t.categoryId ? (catMap.get(t.categoryId) ?? t.categoryId) : null,
        toAccountId,
        parts,
        accountIds: [...new Set([...parts.map((p) => p.accountId), ...(toAccountId ? [toAccountId] : [])])],
        updatedAt: now,
      }
    }),
  }
}

/** Il dispositivo ha dati inseriti dall'utente (non solo le categorie iniziali)? */
export function hasUserData(s: Snapshot): boolean {
  return s.accounts.some((a) => a.deletedAt === null) || s.transactions.some((t) => t.deletedAt === null)
}
