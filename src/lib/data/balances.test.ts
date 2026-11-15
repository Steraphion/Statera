import { describe, expect, it } from 'vitest'
import { accountBalance, accountLedger, ledgerMonth, netWorth } from './balances'
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

describe('accountLedger', () => {
  const conto = account({ id: 'cc', initialBalance: 10000, initialDate: '2026-11-05' })
  const txs = [
    tx({ id: 't1', date: '2026-11-01', type: 'entrata', parts: [part('cc', 5000)], accountIds: ['cc'] }),
    tx({ id: 't2', date: '2026-11-06', type: 'uscita', parts: [part('cc', 1000)], accountIds: ['cc'] }),
    tx({ id: 't3', date: '2026-11-07', type: 'trasferimento', parts: [part('x', 2000)], toAccountId: 'cc', accountIds: ['x', 'cc'] }),
    tx({ id: 't4', date: '2026-11-08', type: 'uscita', parts: [part('x', 300)], accountIds: ['x'] }),
  ]

  it('saldo progressivo, dal più recente', () => {
    const l = accountLedger(conto, txs)
    expect(l.map((e) => [e.t.id, e.effect, e.balanceAfter, e.counted])).toEqual([
      ['t3', 2000, 11000, true],
      ['t2', -1000, 9000, true],
      ['t1', 5000, 10000, false],
    ])
    expect(l[0].balanceAfter).toBe(accountBalance(conto, txs).amount)
  })
})

describe('ledgerMonth', () => {
  const conto = account({ id: 'cc', initialBalance: 100000, initialDate: '2026-02-10' })
  const txs = [
    tx({ id: 'vecchio', date: '2026-02-05', parts: [part('cc', 500)], accountIds: ['cc'] }), // prima del saldo iniziale
    tx({ id: 'f1', date: '2026-02-20', type: 'entrata', parts: [part('cc', 20000)], accountIds: ['cc'] }),
    tx({ id: 'm1', date: '2026-03-02', parts: [part('cc', 3000)], accountIds: ['cc'] }),
    tx({ id: 'm2', date: '2026-03-15', type: 'trasferimento', toAccountId: 'cash', parts: [part('cc', 10000)], accountIds: ['cc', 'cash'] }),
    tx({ id: 'm3', date: '2026-03-20', type: 'trasferimento', toAccountId: 'cc', parts: [part('cash', 2500)], accountIds: ['cash', 'cc'] }),
    tx({ id: 'm4', date: '2026-03-25', type: 'entrata', parts: [part('cc', 4000)], accountIds: ['cc'] }),
    tx({ id: 'x', date: '2026-03-26', parts: [part('cc', 999)], accountIds: ['cc'], deletedAt: 5 }),
  ]
  const ledger = accountLedger(conto, txs)

  it('mese del saldo iniziale: parte dal saldo iniziale, i movimenti di prima non incidono ma contano nei totali', () => {
    const m = ledgerMonth(conto, ledger, '2026-02')
    expect(m.entries.map((e) => e.t.id)).toEqual(['f1', 'vecchio'])
    expect(m.opening).toEqual({ kind: 'iniziale', amount: 100000 })
    expect(m.income).toBe(20000)
    expect(m.expense).toBe(-500)
    expect(m.entries.find((e) => e.t.id === 'vecchio')?.counted).toBe(false)
  })

  it('mese successivo: saldo a inizio mese, entrate, uscite e trasferimenti nei due sensi', () => {
    const m = ledgerMonth(conto, ledger, '2026-03')
    expect(m.entries.map((e) => e.t.id)).toEqual(['m4', 'm3', 'm2', 'm1'])
    expect(m.opening).toEqual({ kind: 'inizio', amount: 120000 })
    expect(m.income).toBe(4000)
    expect(m.expense).toBe(-3000)
    expect(m.transfers).toBe(-10000 + 2500)
    expect(m.entries[0].balanceAfter).toBe(120000 - 3000 - 10000 + 2500 + 4000)
  })

  it('mese senza movimenti dopo altri mesi: parte dal saldo raggiunto', () => {
    const m = ledgerMonth(conto, ledger, '2026-05')
    expect(m.entries).toEqual([])
    expect(m.opening).toEqual({ kind: 'inizio', amount: 113500 })
  })

  it('mese prima del saldo iniziale', () => {
    expect(ledgerMonth(conto, ledger, '2026-01').opening).toEqual({ kind: 'prima' })
  })

  it('conto senza movimenti: saldo iniziale', () => {
    const vuoto = account({ id: 'v', initialBalance: 700, initialDate: '2026-01-01' })
    expect(ledgerMonth(vuoto, [], '2026-04').opening).toEqual({ kind: 'inizio', amount: 700 })
  })
})
