import type { Account, AccountType, Card, Transaction } from './types'

export interface Balance {
  /** Saldo in centesimi. */
  amount: number
  /** Solo buoni pasto: numero di buoni disponibili. */
  vouchers: number | null
}

/**
 * Calcola il saldo di un conto: saldo iniziale + movimenti dalla data iniziale in poi.
 * - Entrata: aumenta il conto della parte.
 * - Uscita: diminuisce il conto della parte (una carta scala dal suo conto collegato,
 *   che è già indicato in part.accountId).
 * - Trasferimento: diminuisce il conto della parte, aumenta toAccountId.
 */
export function accountBalance(account: Account, transactions: Transaction[]): Balance {
  let amount = account.initialBalance
  let vouchers = account.type === 'buoni_pasto' ? (account.initialVouchers ?? 0) : null
  for (const t of transactions) {
    if (t.deletedAt !== null || t.date < account.initialDate) continue
    const e = effectOn(account.id, t)
    amount += e.amount
    if (vouchers !== null) vouchers += e.vouchers
  }
  return { amount, vouchers }
}

/** Patrimonio: somma dei saldi dei conti attivi (non archiviati, non cancellati). */
export function netWorth(accounts: Account[], transactions: Transaction[]): number {
  return accounts
    .filter((a) => a.deletedAt === null && !a.archived)
    .reduce((sum, a) => sum + accountBalance(a, transactions).amount, 0)
}

/** Conti a cui si può collegare una carta di debito. */
/**
 * Gruppi della schermata Conti, in quest'ordine: i conti correnti (con sotto le loro carte), le carte
 * prepagate (hanno un saldo loro), poi contanti, buoni pasto e altri conti.
 */
export const ACCOUNT_GROUPS: { type: AccountType; label: string }[] = [
  { type: 'conto_corrente', label: 'Conti correnti' },
  { type: 'carta_prepagata', label: 'Carte prepagate' },
  { type: 'contanti', label: 'Contanti' },
  { type: 'buoni_pasto', label: 'Buoni pasto' },
  { type: 'altro', label: 'Altri conti' },
]

export interface AccountGroup {
  type: AccountType
  label: string
  accounts: Account[]
  /** Somma dei saldi del gruppo (centesimi). */
  total: number
}

/** Conti divisi per tipo, solo i gruppi non vuoti; l'ordine dentro il gruppo è quello dei conti passati. */
export function accountGroups(accounts: Account[], transactions: Transaction[]): AccountGroup[] {
  return ACCOUNT_GROUPS.map((g) => {
    const list = accounts.filter((a) => a.type === g.type)
    return { ...g, accounts: list, total: list.reduce((s, a) => s + accountBalance(a, transactions).amount, 0) }
  }).filter((g) => g.accounts.length > 0)
}

/** Si possono collegare carte di debito: conti correnti e "altro" (non le prepagate, che sono già una carta). */
export function cardEligible(account: Account): boolean {
  return account.type === 'conto_corrente' || account.type === 'altro'
}

export function cardsOf(account: Account, cards: Card[]): Card[] {
  return cards.filter((c) => c.accountId === account.id && c.deletedAt === null)
}

/** Effetto con segno di un movimento su un conto (0 se non lo riguarda). */
export function effectOn(accountId: string, t: Transaction): { amount: number; vouchers: number } {
  let amount = 0
  let vouchers = 0
  for (const p of t.parts) {
    if (p.accountId !== accountId) continue
    const sign = t.type === 'entrata' ? 1 : -1
    amount += sign * p.amount
    vouchers += sign * (p.vouchers ?? 0)
  }
  if (t.type === 'trasferimento' && t.toAccountId === accountId) {
    amount += t.parts.reduce((s, p) => s + p.amount, 0)
    vouchers += t.parts.reduce((s, p) => s + (p.vouchers ?? 0), 0)
  }
  return { amount, vouchers }
}

export interface LedgerEntry {
  t: Transaction
  effect: number
  /** Saldo dopo il movimento (uguale al precedente se non incide). */
  balanceAfter: number
  /** false = precedente alla data del saldo iniziale: non incide sul saldo. */
  counted: boolean
}

/** Estratto conto: movimenti del conto dal più recente, con saldo progressivo. */
export function accountLedger(account: Account, transactions: Transaction[]): LedgerEntry[] {
  const rows = transactions
    .filter((t) => t.deletedAt === null && t.accountIds.includes(account.id))
    .sort((a, b) => a.date.localeCompare(b.date) || a.createdAt - b.createdAt)

  let balance = account.initialBalance
  const out: LedgerEntry[] = []
  for (const t of rows) {
    const effect = effectOn(account.id, t).amount
    const counted = t.date >= account.initialDate
    if (counted) balance += effect
    out.push({ t, effect, balanceAfter: balance, counted })
  }
  return out.reverse()
}

/** Un mese dell'estratto conto (dettaglio del conto su PC, un mese alla volta). */
export interface LedgerMonth {
  /** Movimenti del mese, dal più recente. */
  entries: LedgerEntry[]
  /** Entrate e uscite del mese su questo conto (trasferimenti esclusi); uscite negative. */
  income: number
  expense: number
  /** Effetto netto dei trasferimenti (in entrata positivi, in uscita negativi). */
  transfers: number
  /**
   * Da dove parte il saldo: 'inizio' = saldo a inizio mese; 'iniziale' = il mese del saldo iniziale;
   * 'prima' = mese precedente al saldo iniziale (i movimenti non incidono).
   */
  opening: { kind: 'inizio' | 'iniziale'; amount: number } | { kind: 'prima' }
}

/** Estratto conto di un mese 'AAAA-MM', dall'elenco di accountLedger (dal più recente). */
export function ledgerMonth(account: Account, ledger: LedgerEntry[], month: string): LedgerMonth {
  const entries = ledger.filter((e) => e.t.date.startsWith(month))
  let income = 0
  let expense = 0
  let transfers = 0
  for (const e of entries) {
    if (e.t.type === 'trasferimento') transfers += e.effect
    else if (e.effect > 0) income += e.effect
    else expense += e.effect
  }
  const initMonth = account.initialDate.slice(0, 7)
  let opening: LedgerMonth['opening']
  if (month < initMonth) opening = { kind: 'prima' }
  else if (month === initMonth) opening = { kind: 'iniziale', amount: account.initialBalance }
  else {
    // Il primo movimento prima del mese (l'elenco va dal più recente) porta il saldo di fine mese precedente
    const before = ledger.find((e) => e.t.date < `${month}-01`)
    opening = { kind: 'inizio', amount: before && before.counted ? before.balanceAfter : account.initialBalance }
  }
  return { entries, income, expense, transfers, opening }
}
