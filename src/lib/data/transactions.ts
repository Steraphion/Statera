import { formatEuro, parseEuro } from '../format'
import { db, type StateraDB } from './db'
import type { Account, Card, Category, Transaction, TransactionPart, TransactionType } from './types'
import { baseFields, today } from './util'
import { accountBalance } from './balances'
import { ensureAdjustCategory } from './repo'

/**
 * "Con cosa": la fonte di un movimento può essere un conto oppure una carta.
 * Codificata come stringa per i menu a tendina: 'a:<id conto>' o 'c:<id carta>'.
 */
export type SourceKey = string

export function sourceKey(part: Pick<TransactionPart, 'accountId' | 'cardId'>): SourceKey {
  return part.cardId ? `c:${part.cardId}` : `a:${part.accountId}`
}

/** Una parte del pagamento come la inserisce l'utente. */
export interface PartInput {
  /** Fonte: conto o carta. */
  source: SourceKey
  /** Importo in centesimi (ignorato se la fonte è un conto buoni pasto). */
  amount: number
  /** Solo buoni pasto: numero di buoni. */
  vouchers: number | null
}

export interface MovementInput {
  type: TransactionType
  date: string
  /** Una parte = pagamento normale; più parti = pagamento misto (solo uscite). Trasferimenti: il conto di origine. */
  parts: PartInput[]
  categoryId: string | null
  toAccountId: string | null
  description: string
  notes: string
}

async function buildPart(input: PartInput, d: StateraDB, prev?: Transaction): Promise<TransactionPart> {
  const [kind, id] = input.source.split(':')
  let account: Account | undefined
  let cardId: string | null = null

  if (kind === 'c') {
    const card = await d.cards.get(id)
    if (!card || card.deletedAt !== null) throw new Error('Carta non trovata')
    account = await d.accounts.get(card.accountId)
    cardId = card.id
  } else {
    account = await d.accounts.get(id)
  }
  if (!account || account.deletedAt !== null) throw new Error('Scegli un conto')

  if (account.type === 'buoni_pasto') {
    const n = input.vouchers ?? 0
    if (!Number.isInteger(n) || n <= 0) throw new Error(`Indica quanti buoni (${account.name})`)
    // In modifica si conserva il valore del buono di allora
    const value =
      prev?.parts.find((p) => p.accountId === account.id && p.voucherValue)?.voucherValue ?? account.voucherValue ?? 0
    return { accountId: account.id, cardId: null, amount: n * value, vouchers: n, voucherValue: value }
  }

  if (!Number.isInteger(input.amount) || input.amount <= 0) throw new Error('Inserisci un importo maggiore di zero')
  return { accountId: account.id, cardId, amount: input.amount, vouchers: null, voucherValue: null }
}

async function buildParts(input: MovementInput, d: StateraDB, prev?: Transaction): Promise<TransactionPart[]> {
  if (input.parts.length === 0) throw new Error('Indica con cosa hai pagato')
  if (input.parts.length > 1 && input.type !== 'uscita') throw new Error('Il pagamento misto vale solo per le uscite')
  const parts: TransactionPart[] = []
  for (const p of input.parts) parts.push(await buildPart(p, d, prev))
  const keys = parts.map((p) => p.cardId ?? p.accountId)
  if (new Set(keys).size !== keys.length) throw new Error('La stessa fonte compare due volte nel pagamento')
  return parts
}

async function validate(input: MovementInput, d: StateraDB, prev?: Transaction) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.date)) throw new Error('Data non valida')
  const parts = await buildParts(input, d, prev)

  let categoryId: string | null = null
  let toAccountId: string | null = null

  if (input.type === 'trasferimento') {
    if (!input.toAccountId) throw new Error('Scegli il conto di destinazione')
    if (input.toAccountId === parts[0].accountId) throw new Error('Origine e destinazione devono essere diverse')
    const to = await d.accounts.get(input.toAccountId)
    if (!to || to.deletedAt !== null) throw new Error('Conto di destinazione non trovato')
    if (to.type === 'buoni_pasto' || parts.some((p) => p.vouchers !== null)) {
      throw new Error('I buoni pasto non si trasferiscono tra conti')
    }
    toAccountId = to.id
  } else {
    if (!input.categoryId) throw new Error('Scegli una categoria')
    const cat = await d.categories.get(input.categoryId)
    if (!cat || cat.deletedAt !== null) throw new Error('Categoria non trovata')
    if (cat.kind !== input.type) throw new Error('La categoria non corrisponde al tipo di movimento')
    categoryId = cat.id
  }

  const accountIds = [...new Set([...parts.map((p) => p.accountId), ...(toAccountId ? [toAccountId] : [])])]

  return {
    type: input.type,
    date: input.date,
    parts,
    categoryId,
    toAccountId,
    accountIds,
    description: input.description.trim().slice(0, 80),
    notes: input.notes.trim().slice(0, 500),
  }
}

/** Controlla che un movimento sia valido senza salvarlo (es. per un modello ricorrente). */
export async function checkMovement(input: MovementInput, d: StateraDB = db): Promise<void> {
  await validate(input, d)
}

/**
 * Crea un movimento. Con `id` (movimenti generati da una ripetizione) l'identificativo è fisso:
 * se esiste già (anche eliminato, anche creato da un altro dispositivo) non viene ricreato.
 */
export async function createMovement(
  input: MovementInput,
  d: StateraDB = db,
  opts: { id?: string; remember?: boolean } = {},
): Promise<Transaction> {
  const data = await validate(input, d)
  const t: Transaction = { ...baseFields(), ...(opts.id ? { id: opts.id } : {}), ...data }
  let result = t
  await d.transaction('rw', d.transactions, d.meta, async () => {
    if (opts.id) {
      const existing = await d.transactions.get(opts.id)
      if (existing) {
        result = existing
        return
      }
    }
    await d.transactions.add(t)
    if (opts.remember === false) return
    // Nei pagamenti misti si ricorda la fonte "normale" (carta/conto), non i buoni
    const i = data.parts.length > 1 ? Math.max(0, data.parts.findIndex((p) => p.vouchers === null)) : 0
    await rememberSource(input.type, input.parts[i].source, d)
  })
  return result
}

export async function updateMovement(id: string, input: MovementInput, d: StateraDB = db) {
  const prev = await d.transactions.get(id)
  if (!prev || prev.deletedAt !== null) throw new Error('Movimento non trovato')
  const data = await validate(input, d, prev)
  await d.transactions.update(id, { ...data, updatedAt: Date.now() })
}

export async function deleteMovement(id: string, d: StateraDB = db) {
  await d.transactions.update(id, { deletedAt: Date.now(), updatedAt: Date.now() })
}

// ---------- Ultima fonte usata (per proporla al prossimo inserimento) ----------

type LastSources = Partial<Record<TransactionType, SourceKey>>

async function rememberSource(type: TransactionType, source: SourceKey, d: StateraDB) {
  const prev = ((await d.meta.get('ultimaFonte'))?.value ?? {}) as LastSources
  await d.meta.put({ key: 'ultimaFonte', value: { ...prev, [type]: source } })
}

export async function lastSources(d: StateraDB = db): Promise<LastSources> {
  return ((await d.meta.get('ultimaFonte'))?.value ?? {}) as LastSources
}

// ---------- Letture e riepiloghi ----------

/** Movimenti di un mese ('AAAA-MM'), dal più recente. */
export async function movementsOfMonth(month: string, d: StateraDB = db): Promise<Transaction[]> {
  const rows = await d.transactions.where('date').between(`${month}-01`, `${month}-31`, true, true).toArray()
  return sortMovements(rows.filter((t) => t.deletedAt === null))
}

export function sortMovements(rows: Transaction[]): Transaction[] {
  return [...rows].sort((a, b) => b.date.localeCompare(a.date) || b.createdAt - a.createdAt)
}

export function total(t: Transaction): number {
  return t.parts.reduce((s, p) => s + p.amount, 0)
}

export interface Totals {
  income: number
  expense: number
  net: number
}

/** Totali: i trasferimenti non sono né entrate né uscite. */
export function totals(rows: Transaction[]): Totals {
  let income = 0
  let expense = 0
  for (const t of rows) {
    if (t.deletedAt !== null) continue
    if (t.type === 'entrata') income += total(t)
    else if (t.type === 'uscita') expense += total(t)
  }
  return { income, expense, net: income - expense }
}

export interface DayGroup {
  date: string
  items: Transaction[]
  net: number
}

export function groupByDay(rows: Transaction[]): DayGroup[] {
  const groups: DayGroup[] = []
  for (const t of rows) {
    let g = groups[groups.length - 1]
    if (!g || g.date !== t.date) {
      g = { date: t.date, items: [], net: 0 }
      groups.push(g)
    }
    g.items.push(t)
    if (t.type === 'entrata') g.net += total(t)
    else if (t.type === 'uscita') g.net -= total(t)
  }
  return groups
}

/** Opzioni "Con cosa": conti attivi e, sotto ogni conto corrente, le sue carte. */
export interface SourceOption {
  key: SourceKey
  label: string
  account: Account
  isCard: boolean
}

export function sourceOptions(accounts: Account[], cards: Card[], keep: SourceKey[] = []): SourceOption[] {
  const out: SourceOption[] = []
  for (const a of accounts) {
    if (a.deletedAt !== null) continue
    const aKey = `a:${a.id}`
    if (!a.archived || keep.includes(aKey)) out.push({ key: aKey, label: a.name, account: a, isCard: false })
    for (const c of cards) {
      if (c.accountId !== a.id || c.deletedAt !== null) continue
      const cKey = `c:${c.id}`
      if ((!c.archived && !a.archived) || keep.includes(cKey)) {
        out.push({ key: cKey, label: `${c.name} (${a.name})`, account: a, isCard: true })
      }
    }
  }
  return out
}

/** Nome leggibile della fonte di una parte: la carta se presente, altrimenti il conto. */
export function partLabel(p: TransactionPart, accounts: Map<string, Account>, cards: Map<string, Card>): string {
  if (p.cardId) return cards.get(p.cardId)?.name ?? '—'
  return accounts.get(p.accountId)?.name ?? '—'
}

export function categoryLabel(id: string | null, categories: Map<string, Category>): string {
  if (!id) return ''
  const c = categories.get(id)
  if (!c) return '—'
  const parent = c.parentId ? categories.get(c.parentId) : null
  return parent ? `${parent.name} › ${c.name}` : c.name
}

// ---------- Ricerca ----------

export interface Filters {
  text: string
  /** 'AAAA-MM-GG' o '' */
  from: string
  to: string
  type: TransactionType | ''
  /** Fonte: 'a:<conto>' (tutti i movimenti del conto, carte comprese) o 'c:<carta>', o '' */
  source: SourceKey | ''
  /** Categoria (comprende le sue sottocategorie) o '' */
  categoryId: string
  /** Importo minimo e massimo (testo in euro, es. "50" o "12,50"), o '' */
  min: string
  max: string
}

export const EMPTY_FILTERS: Filters = { text: '', from: '', to: '', type: '', source: '', categoryId: '', min: '', max: '' }

/** Minuscolo e senza accenti: "Caffè" trova "caffe". */
export function normalize(s: string): string {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export function filterMovements(
  rows: Transaction[],
  f: Filters,
  refs: { accountMap: Map<string, Account>; cardMap: Map<string, Card>; categoryMap: Map<string, Category> },
): Transaction[] {
  const words = normalize(f.text).split(/\s+/).filter(Boolean)
  const [srcKind, srcId] = f.source ? f.source.split(':') : ['', '']
  const catIds = new Set<string>()
  if (f.categoryId) {
    catIds.add(f.categoryId)
    for (const c of refs.categoryMap.values()) if (c.parentId === f.categoryId) catIds.add(c.id)
  }

  const min = f.min ? parseEuro(f.min) : null
  const max = f.max ? parseEuro(f.max) : null

  const out = rows.filter((t) => {
    if (t.deletedAt !== null) return false
    if (min !== null || max !== null) {
      const amount = total(t)
      if (min !== null && amount < min) return false
      if (max !== null && amount > max) return false
    }
    if (f.from && t.date < f.from) return false
    if (f.to && t.date > f.to) return false
    if (f.type && t.type !== f.type) return false
    if (srcKind === 'a' && !t.accountIds.includes(srcId)) return false
    if (srcKind === 'c' && !t.parts.some((p) => p.cardId === srcId)) return false
    if (catIds.size && !(t.categoryId && catIds.has(t.categoryId))) return false
    if (words.length) {
      const hay = normalize(
        [
          t.description,
          t.notes,
          categoryLabel(t.categoryId, refs.categoryMap),
          ...t.parts.map((p) => partLabel(p, refs.accountMap, refs.cardMap)),
          t.toAccountId ? (refs.accountMap.get(t.toAccountId)?.name ?? '') : '',
        ].join(' '),
      )
      if (!words.every((w) => hay.includes(w))) return false
    }
    return true
  })
  return sortMovements(out)
}

// ---------- Suggerimenti mentre si scrive la descrizione ----------

export interface Suggestion {
  /** Descrizione come scritta l'ultima volta. */
  description: string
  /** Quante volte è stata usata. */
  count: number
  /** Movimento più recente con questa descrizione: da qui si prendono categoria, fonte e importo. */
  last: Transaction
}

function descKey(s: string): string {
  return normalize(s).trim().replace(/\s+/g, ' ')
}

/**
 * Descrizioni già usate per questo tipo di movimento che corrispondono a quanto scritto:
 * prima quelle che iniziano con il testo, poi quelle con una parola che inizia così;
 * a parità, le più usate e le più recenti.
 */
export function descriptionSuggestions(
  rows: Transaction[],
  type: TransactionType,
  query: string,
  limit = 5,
): Suggestion[] {
  const q = descKey(query)
  if (!q) return []
  const groups = new Map<string, Suggestion>()
  for (const t of rows) {
    if (t.deletedAt !== null || t.type !== type || !t.description.trim()) continue
    const k = descKey(t.description)
    const g = groups.get(k)
    if (!g) groups.set(k, { description: t.description.trim(), count: 1, last: t })
    else {
      g.count++
      if (t.date > g.last.date || (t.date === g.last.date && t.createdAt > g.last.createdAt)) {
        g.last = t
        g.description = t.description.trim()
      }
    }
  }
  const scored: { s: Suggestion; score: number }[] = []
  for (const [k, s] of groups) {
    const score = k.startsWith(q) ? 2 : k.includes(' ' + q) ? 1 : 0
    if (score) scored.push({ s, score })
  }
  scored.sort(
    (a, b) =>
      b.score - a.score ||
      b.s.count - a.s.count ||
      (a.s.last.date < b.s.last.date ? 1 : a.s.last.date > b.s.last.date ? -1 : 0),
  )
  return scored.slice(0, limit).map((x) => x.s)
}

// ---------- Allinea saldo ----------

/**
 * Porta il saldo del conto al valore reale indicato, con un movimento di rettifica
 * (entrata se il saldo reale è più alto, uscita se è più basso) nella categoria "Rettifica saldo".
 * Per i buoni pasto si indica il numero di buoni. Restituisce null se il saldo era già giusto.
 */
export async function alignBalance(
  accountId: string,
  real: { amount?: number; vouchers?: number },
  date: string = today(),
  d: StateraDB = db,
): Promise<Transaction | null> {
  const account = await d.accounts.get(accountId)
  if (!account || account.deletedAt !== null) throw new Error('Conto non trovato')
  if (date < account.initialDate) throw new Error('La data è precedente al saldo iniziale del conto')
  const rows = await d.transactions.where('accountIds').equals(accountId).toArray()
  // Saldo alla fine del giorno indicato
  const current = accountBalance(account, rows.filter((t) => t.date <= date))
  const isVoucher = account.type === 'buoni_pasto'
  let delta: number
  if (isVoucher) {
    if (real.vouchers === undefined || !Number.isInteger(real.vouchers) || real.vouchers < 0) {
      throw new Error('Indica quanti buoni hai')
    }
    delta = real.vouchers - (current.vouchers ?? 0)
  } else {
    if (real.amount === undefined || !Number.isInteger(real.amount)) throw new Error('Inserisci il saldo reale')
    delta = real.amount - current.amount
  }
  if (delta === 0) return null
  const type: TransactionType = delta > 0 ? 'entrata' : 'uscita'
  const cat = await ensureAdjustCategory(type, d)
  const shown = isVoucher ? `${real.vouchers} buoni` : formatEuro(real.amount!)
  return createMovement(
    {
      type,
      date,
      parts: [{ source: `a:${accountId}`, amount: isVoucher ? 0 : Math.abs(delta), vouchers: isVoucher ? Math.abs(delta) : null }],
      categoryId: cat.id,
      toAccountId: null,
      description: 'Allineamento saldo',
      notes: `Saldo reale indicato: ${shown}`,
    },
    d,
    { remember: false },
  )
}
