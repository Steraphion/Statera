import { describe, expect, it } from 'vitest'
import * as an from './analytics'
import type { Account, Category, Transaction } from './types'

const base = { createdAt: 1, updatedAt: 1, deletedAt: null }
const cat = (id: string, name: string, parentId: string | null = null): Category => ({ ...base, id, name, kind: 'uscita', parentId, color: 's1', order: 1, archived: false })
const cats = [cat('spesa', 'Spesa'), cat('svago', 'Svago'), cat('casa', 'Casa'), cat('bollette', 'Bollette', 'casa')]
let n = 0
const tx = (date: string, categoryId: string, amount: number, type: Transaction['type'] = 'uscita', accountId = 'a'): Transaction => ({
  ...base, id: `t${n++}`, type, date, categoryId, description: '', notes: '',
  parts: [{ accountId, cardId: null, amount, vouchers: null, voucherValue: null }], toAccountId: null, accountIds: [accountId],
})

describe('confronto con la media dei 3 mesi prima', () => {
  const rows = [
    ...['2026-08', '2026-09', '2026-10'].flatMap((m) => [tx(`${m}-05`, 'spesa', 30000), tx(`${m}-10`, 'svago', 5000), tx(`${m}-12`, 'bollette', 10000)]),
    tx('2026-11-05', 'spesa', 31000), // +3%: non conta
    tx('2026-11-06', 'svago', 12000), // +140%
    tx('2026-11-07', 'bollette', 4000), // -60%, sotto-categoria di Casa
  ]
  it('solo differenze di almeno 10 € e 20%, ordinate', () => {
    const c = an.categoryChanges(rows, '2026-11', 'uscita', cats)
    expect(c.map((x) => [x.category.id, x.diff])).toEqual([['svago', 7000], ['casa', -6000]])
    expect(c[0].ratio).toBeCloseTo(1.4)
  })
  it('senza mesi precedenti nessun confronto', () => {
    expect(an.categoryChanges([tx('2026-11-01', 'spesa', 5000)], '2026-11', 'uscita', cats)).toEqual([])
  })
})

describe('ritmo del mese', () => {
  const rows = [tx('2026-11-01', 'spesa', 3000), tx('2026-11-10', 'spesa', 7000), tx('2026-11-20', 'spesa', 9999), tx('2026-11-03', 'spesa', 5000, 'entrata')]
  it('mese in corso: media al giorno e stima di fine mese', () => {
    const p = an.monthPace(rows, '2026-11', '2026-11-10')!
    expect(p.spent).toBe(10000)
    expect(p.perDay).toBe(1000)
    expect(p.projected).toBe(30000)
  })
  it('primi due giorni: nessuna stima; mese passato: media su tutto il mese; futuro: niente', () => {
    expect(an.monthPace(rows, '2026-11', '2026-11-02')!.projected).toBeNull()
    const past = an.monthPace(rows, '2026-11', '2026-12-15')!
    expect(past.spent).toBe(19999)
    expect(past.perDay).toBe(Math.round(19999 / 30))
    expect(past.projected).toBeNull()
    expect(an.monthPace(rows, '2026-12', '2026-11-15')).toBeNull()
  })
})

describe('patrimonio nel tempo', () => {
  const acc = (id: string, initialBalance: number, initialDate: string, over: Partial<Account> = {}): Account => ({
    ...base, id, name: id, type: 'conto_corrente', initialBalance, initialDate, voucherValue: null, initialVouchers: null, color: 's1', order: 1, archived: false, ...over,
  })
  it('a fine di ogni mese, solo conti già iniziati; mese in corso fino a oggi', () => {
    const accounts = [acc('a', 100000, '2026-09-01'), acc('b', 50000, '2026-10-15'), acc('x', 999, '2026-01-01', { deletedAt: 5 })]
    const rows = [tx('2026-09-20', 'spesa', 20000), tx('2026-10-31', 'spesa', 10000, 'uscita', 'b'), tx('2026-11-20', 'spesa', 5000)]
    const s = an.netWorthSeries(accounts, rows, '2026-11', '2026-11-14', 4)
    expect(s).toEqual([
      { month: '2026-08', value: null },
      { month: '2026-09', value: 80000 },
      { month: '2026-10', value: 120000 },
      { month: '2026-11', value: 120000 },
    ])
  })
})

describe('riepilogo del mese', () => {
  it('totali, confronto e categoria principale', () => {
    const rows = [tx('2026-10-02', 'spesa', 20000), tx('2026-10-03', 'bollette', 8000), tx('2026-10-04', 'spesa', 150000, 'entrata'), tx('2026-09-02', 'spesa', 25000)]
    const r = an.monthRecap(rows, '2026-10', cats)
    expect([r.income, r.expense, r.net, r.previousExpense, r.count]).toEqual([150000, 28000, 122000, 25000, 3])
    expect(r.top?.category.id).toBe('spesa')
  })
})
