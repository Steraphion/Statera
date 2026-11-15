import { describe, expect, it } from 'vitest'
import * as an from './analytics'
import { accountBalance } from './balances'
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

describe('patrimonio nel tempo: stesso risultato del calcolo conto per conto', () => {
  const acc = (id: string, initialBalance: number, initialDate: string): Account => ({
    ...base, id, name: id, type: 'conto_corrente', initialBalance, initialDate, voucherValue: null, initialVouchers: null, color: 's1', order: 1, archived: false,
  })
  // Generatore pseudo-casuale fisso, così il test è ripetibile
  let seed = 7
  const rnd = (k: number) => ((seed = (seed * 1103515245 + 12345) % 2147483648) % k)
  it('con entrate, uscite, trasferimenti, pagamenti misti, eliminati e movimenti prima del saldo iniziale', () => {
    const accounts = [acc('a', 100000, '2025-03-10'), acc('b', 20000, '2025-08-01'), acc('c', 0, '2026-02-15')]
    const ids = accounts.map((a) => a.id)
    const rows: Transaction[] = []
    for (let i = 0; i < 400; i++) {
      const date = `202${5 + rnd(2)}-${String(1 + rnd(12)).padStart(2, '0')}-${String(1 + rnd(28)).padStart(2, '0')}`
      const kind = rnd(4)
      const t = tx(date, 'spesa', 100 + rnd(9000), kind === 0 ? 'entrata' : kind === 1 ? 'trasferimento' : 'uscita', ids[rnd(3)])
      if (kind === 1) t.toAccountId = ids.find((x) => x !== t.parts[0].accountId)!
      if (kind === 2 && rnd(3) === 0) t.parts.push({ accountId: ids[rnd(3)], cardId: null, amount: 50 + rnd(500), vouchers: null, voucherValue: null })
      if (rnd(10) === 0) t.deletedAt = 99
      rows.push(t)
    }
    const today = '2026-11-14'
    const reference = (end: string) => {
      const e = end > today ? today : end
      const until = rows.filter((t) => t.deletedAt === null && t.date <= e)
      const started = accounts.filter((a) => a.initialDate <= e)
      return started.length ? started.reduce((s, a) => s + accountBalance(a, until).amount, 0) : null
    }
    for (const endMonth of ['2025-06', '2026-02', '2026-11', '2027-01']) {
      const s = an.netWorthSeries(accounts, rows, endMonth, today, 12)
      expect(s.filter((p) => p.value !== null).length).toBeGreaterThan(3)
      for (const p of s) {
        const last = new Date(Number(p.month.slice(0, 4)), Number(p.month.slice(5)), 0).getDate()
        const expected = p.month > today.slice(0, 7) ? null : reference(`${p.month}-${String(last).padStart(2, '0')}`)
        expect([p.month, p.value]).toEqual([p.month, expected])
      }
    }
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
