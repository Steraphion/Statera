import { db, type StateraDB } from './db'
import type { Account, Card, Category, Transaction, TransactionPart, TransactionType } from './types'
import { baseFields } from './util'

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

export async function createMovement(input: MovementInput, d: StateraDB = db): Promise<Transaction> {
  const data = await validate(input, d)
  const t: Transaction = { ...baseFields(), ...data }
  await d.transaction('rw', d.transactions, d.meta, async () => {
    await d.transactions.add(t)
    await rememberSource(input.type, input.parts[0].source, d)
  })
  return t
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
