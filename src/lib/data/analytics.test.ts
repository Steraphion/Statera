import { describe, expect, it } from 'vitest'
import * as an from './analytics'
import type { Category, Transaction } from './types'

const cat = (id: string, name: string, parentId: string | null = null, kind: 'uscita' | 'entrata' = 'uscita', monthlyBudget: number | null = null): Category => ({
  id, name, kind, parentId, color: 's1', order: 1, archived: false, createdAt: 1, updatedAt: 1, deletedAt: null, monthlyBudget,
})
let n = 0
const tx = (date: string, type: Transaction['type'], amount: number, categoryId: string | null, parts = 1): Transaction => ({
  id: `t${++n}`, type, date, categoryId, description: '', notes: '', toAccountId: null, accountIds: ['a'],
  parts: Array.from({ length: parts }, () => ({ accountId: 'a', cardId: null, amount: amount / parts, vouchers: null, voucherValue: null })),
  createdAt: 1, updatedAt: 1, deletedAt: null,
})

const cats = [cat('casa', 'Casa', null, 'uscita', 50000), cat('boll', 'Bollette', 'casa'), cat('spesa', 'Spesa', null, 'uscita', 10000), cat('stip', 'Stipendio', null, 'entrata')]
const rows = [
  tx('2026-11-02', 'uscita', 30000, 'casa'),
  tx('2026-11-03', 'uscita', 8000, 'boll'),
  tx('2026-11-04', 'uscita', 12000, 'spesa', 2), // pagamento misto: conta per intero
  tx('2026-11-05', 'entrata', 150000, 'stip'),
  tx('2026-11-06', 'trasferimento', 5000, null),
  tx('2026-10-10', 'uscita', 4000, 'spesa'),
  tx('2025-12-31', 'uscita', 999, 'spesa'),
]

describe('analisi', () => {
  it('per categoria con sottocategorie, quote e ordine', () => {
    const g = an.byCategory(an.periodRows(rows, { kind: 'mese', month: '2026-11' }), 'uscita', cats)
    expect(g.map((x) => [x.category.id, x.total])).toEqual([['casa', 38000], ['spesa', 12000]])
    expect(g[0].share).toBeCloseTo(0.76)
    expect(g[0].children.map((c) => [c.category.id, c.total, c.direct])).toEqual([['casa', 30000, true], ['boll', 8000, false]])
    expect(g[1].children).toEqual([])
  })

  it('periodo anno e intervallo date', () => {
    expect(an.periodRows(rows, { kind: 'anno', year: '2026' })).toHaveLength(6)
    expect(an.periodRange({ kind: 'mese', month: '2026-02' })).toEqual({ from: '2026-02-01', to: '2026-02-28' })
    expect(an.periodRange({ kind: 'anno', year: '2026' })).toEqual({ from: '2026-01-01', to: '2026-12-31' })
  })

  it('serie mensile: 12 mesi, trasferimenti esclusi', () => {
    const s = an.monthlySeries(rows, '2026-11')
    expect(s).toHaveLength(12)
    expect(s[0].month).toBe('2025-12')
    expect(s[11]).toEqual({ month: '2026-11', income: 150000, expense: 50000, net: 100000 })
    expect(s[10]).toMatchObject({ month: '2026-10', expense: 4000 })
    expect(s[0].expense).toBe(999)
  })

  it('budget: stati ok / attenzione / superato', () => {
    const b = an.budgetStatus(rows, '2026-11', cats)
    expect(b.map((x) => [x.category.id, x.spent, x.state])).toEqual([['spesa', 12000, 'superato'], ['casa', 38000, 'ok']])
    const b2 = an.budgetStatus(rows, '2026-11', [cat('casa', 'Casa', null, 'uscita', 45000), cats[1]])
    expect(b2[0].state).toBe('attenzione')
    expect(an.budgetStatus(rows, '2026-11', [cat('x', 'X')])).toEqual([])
  })

  it('tacche dell\'asse pulite', () => {
    expect(an.niceTicks(173000)).toEqual([0, 50000, 100000, 150000, 200000])
    expect(an.niceTicks(0)).toEqual([0])
  })
})
