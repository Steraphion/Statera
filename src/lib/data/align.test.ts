import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as mv from './transactions'
import { accountBalance } from './balances'
import { daysLeftInMonth, perDay } from './analytics'

let d: StateraDB
let n = 0
const base = { initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' as const }

beforeEach(async () => {
  d = new StateraDB(`align-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
})

describe('allinea saldo', () => {
  it('saldo reale più basso: uscita di rettifica; più alto: entrata', async () => {
    const c = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 100000 }, d)
    const m = await mv.alignBalance(c.id, { amount: 98750 }, '2026-11-14', d)
    expect(m!.type).toBe('uscita')
    expect(m!.parts[0].amount).toBe(1250)
    expect(m!.categoryId).toBe(repo.seedId('uscita', 'Rettifica saldo'))
    expect(m!.notes).toContain('987,50')
    const m2 = await mv.alignBalance(c.id, { amount: 100000 }, '2026-11-14', d)
    expect(m2!.type).toBe('entrata')
    expect(m2!.parts[0].amount).toBe(1250)
    const acc = (await d.accounts.get(c.id))!
    expect(accountBalance(acc, await d.transactions.toArray()).amount).toBe(100000)
    // categoria con id fisso, una sola per tipo
    expect((await d.categories.toArray()).filter((x) => x.name === 'Rettifica saldo')).toHaveLength(2)
  })
  it('già giusto: nessun movimento; data prima del saldo iniziale: errore', async () => {
    const c = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 5000 }, d)
    expect(await mv.alignBalance(c.id, { amount: 5000 }, '2026-11-14', d)).toBeNull()
    await expect(mv.alignBalance(c.id, { amount: 1 }, '2026-10-01', d)).rejects.toThrow('saldo iniziale')
  })
  it('conta solo i movimenti fino alla data indicata', async () => {
    const c = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 10000 }, d)
    await mv.createMovement({ type: 'uscita', date: '2026-11-20', parts: [{ source: `a:${c.id}`, amount: 3000, vouchers: null }], categoryId: repo.seedId('uscita', 'Svago'), toAccountId: null, description: '', notes: '' }, d)
    expect(await mv.alignBalance(c.id, { amount: 10000 }, '2026-11-14', d)).toBeNull()
  })
  it('buoni pasto: si allinea il numero di buoni', async () => {
    const b = await repo.createAccount({ ...base, name: 'Buoni', type: 'buoni_pasto', initialBalance: 0, voucherValue: 800, initialVouchers: 10 }, d)
    const m = await mv.alignBalance(b.id, { vouchers: 7 }, '2026-11-14', d)
    expect(m!.type).toBe('uscita')
    expect(m!.parts[0].vouchers).toBe(3)
    expect(m!.parts[0].amount).toBe(2400)
    await expect(mv.alignBalance(b.id, { vouchers: -1 }, '2026-11-14', d)).rejects.toThrow('buoni')
  })
  it('categoria cancellata torna disponibile', async () => {
    const c = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 100 }, d)
    const cat = await repo.ensureAdjustCategory('uscita', d)
    await d.categories.update(cat.id, { deletedAt: 5 })
    await mv.alignBalance(c.id, { amount: 50 }, '2026-11-14', d)
    expect((await d.categories.get(cat.id))!.deletedAt).toBeNull()
  })
})

describe('budget al giorno', () => {
  it('giorni che restano', () => {
    expect(daysLeftInMonth('2026-11', '2026-11-14')).toBe(17)
    expect(daysLeftInMonth('2026-11', '2026-11-30')).toBe(1)
    expect(daysLeftInMonth('2026-10', '2026-11-14')).toBe(0)
    expect(daysLeftInMonth('2026-12', '2026-11-14')).toBe(31)
    expect(daysLeftInMonth('2028-02', '2028-02-01')).toBe(29)
  })
  it('importo al giorno arrotondato per difetto', () => {
    expect(perDay(8400, 12)).toBe(700)
    expect(perDay(1000, 3)).toBe(333)
    expect(perDay(0, 10)).toBeNull()
    expect(perDay(500, 0)).toBeNull()
  })
})
