import { describe, expect, it } from 'vitest'
import { accountBalance, netWorth } from './balances'
import type { Account, Transaction, TransactionPart } from './types'

const base = { createdAt: 0, updatedAt: 0, deletedAt: null }

function account(over: Partial<Account>): Account {
  return {
    ...base, id: 'a', name: 'Conto', type: 'conto_corrente', initialBalance: 0, initialDate: '2026-01-01',
    voucherValue: null, initialVouchers: null, color: 's1', order: 1, archived: false, ...over,
  }
}

function part(accountId: string, amount: number, vouchers: number | null = null): TransactionPart {
  return { accountId, cardId: null, amount, vouchers, voucherValue: vouchers ? amount / vouchers : null }
}

function tx(over: Partial<Transaction>): Transaction {
  return {
    ...base, id: Math.random().toString(), type: 'uscita', date: '2026-02-01', categoryId: null,
    description: '', notes: '', parts: [], toAccountId: null, accountIds: [], ...over,
  }
}

describe('accountBalance', () => {
  const conto = account({ id: 'cc', initialBalance: 100000 })
  const contanti = account({ id: 'cash', type: 'contanti', initialBalance: 2000 })
  const buoni = account({ id: 'bp', type: 'buoni_pasto', voucherValue: 800, initialVouchers: 5, initialBalance: 4000 })

  const txs = [
    tx({ type: 'entrata', parts: [part('cc', 150000)] }),
    tx({ type: 'uscita', parts: [part('cc', 2550)] }),
    tx({ type: 'trasferimento', parts: [part('cc', 5000)], toAccountId: 'cash' }),
    // pagamento misto: 3 buoni + 7,40 € con il conto
    tx({ type: 'uscita', parts: [part('bp', 2400, 3), part('cc', 740)] }),
    tx({ type: 'entrata', parts: [part('bp', 16000, 20)] }),
    // ignorati: cancellato e precedente alla data iniziale
    tx({ type: 'uscita', parts: [part('cc', 99999)], deletedAt: 1 }),
    tx({ type: 'uscita', date: '2025-12-31', parts: [part('cc', 99999)] }),
  ]

  it('conto corrente', () => {
    expect(accountBalance(conto, txs).amount).toBe(100000 + 150000 - 2550 - 5000 - 740)
  })

  it('contanti riceve il trasferimento', () => {
    expect(accountBalance(contanti, txs).amount).toBe(7000)
  })

  it('buoni pasto: numero e valore', () => {
    expect(accountBalance(buoni, txs)).toEqual({ amount: 4000 - 2400 + 16000, vouchers: 5 - 3 + 20 })
  })

  it('patrimonio esclude gli archiviati', () => {
    const archived = account({ id: 'old', initialBalance: 50000, archived: true })
    expect(netWorth([conto, contanti, buoni, archived], txs)).toBe(
      accountBalance(conto, txs).amount + 7000 + accountBalance(buoni, txs).amount,
    )
  })
})
