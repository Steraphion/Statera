import type { Account, Card, Transaction } from './types'

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

    for (const p of t.parts) {
      if (p.accountId !== account.id) continue
      const sign = t.type === 'entrata' ? 1 : -1
      amount += sign * p.amount
      if (vouchers !== null) vouchers += sign * (p.vouchers ?? 0)
    }

    if (t.type === 'trasferimento' && t.toAccountId === account.id) {
      const total = t.parts.reduce((s, p) => s + p.amount, 0)
      amount += total
      if (vouchers !== null) vouchers += t.parts.reduce((s, p) => s + (p.vouchers ?? 0), 0)
    }
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
export function cardEligible(account: Account): boolean {
  return account.type === 'conto_corrente' || account.type === 'altro'
}

export function cardsOf(account: Account, cards: Card[]): Card[] {
  return cards.filter((c) => c.accountId === account.id && c.deletedAt === null)
}
