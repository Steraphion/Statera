import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as mv from './transactions'
import { accountBalance } from './balances'
import type { Account, Card, Category } from './types'

let d: StateraDB
let n = 0
let conto: Account, contanti: Account, buoni: Account, bancomat: Card
let spesa: Category, stipendio: Category

const base = { initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' as const }

beforeEach(async () => {
  d = new StateraDB(`mv-${++n}`)
  await d.open()
  conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 100000 }, d)
  contanti = await repo.createAccount({ ...base, name: 'Contanti', type: 'contanti', initialBalance: 0 }, d)
  buoni = await repo.createAccount({ ...base, name: 'Buoni', type: 'buoni_pasto', initialBalance: 0, voucherValue: 800, initialVouchers: 5 }, d)
  bancomat = await repo.createCard({ name: 'Bancomat', accountId: conto.id }, d)
  spesa = await repo.createCategory({ name: 'Spesa', kind: 'uscita', parentId: null, color: 's1' }, d)
  stipendio = await repo.createCategory({ name: 'Stipendio', kind: 'entrata', parentId: null, color: 's2' }, d)
})

type Over = Partial<mv.MovementInput> & { source?: string; amount?: number; vouchers?: number | null }

function input(over: Over): mv.MovementInput {
  const { source = `a:${conto.id}`, amount = 1000, vouchers = null, ...rest } = over
  return {
    type: 'uscita', date: '2026-11-10', parts: [{ source, amount, vouchers }],
    categoryId: spesa.id, toAccountId: null, description: 'Esempio', notes: '', ...rest,
  }
}

async function balance(a: Account) {
  return accountBalance((await d.accounts.get(a.id))!, await d.transactions.toArray())
}

describe('movimenti', () => {
  it('uscita con carta scala dal conto collegato e ricorda la carta', async () => {
    const t = await mv.createMovement(input({ source: `c:${bancomat.id}`, amount: 2550 }), d)
    expect(t.parts[0]).toMatchObject({ accountId: conto.id, cardId: bancomat.id, amount: 2550 })
    expect(t.accountIds).toEqual([conto.id])
    expect((await balance(conto)).amount).toBe(100000 - 2550)
    expect((await mv.lastSources(d)).uscita).toBe(`c:${bancomat.id}`)
  })

  it('entrata', async () => {
    await mv.createMovement(input({ type: 'entrata', categoryId: stipendio.id, amount: 150000 }), d)
    expect((await balance(conto)).amount).toBe(250000)
  })

  it('trasferimento: prelievo', async () => {
    const t = await mv.createMovement(input({ type: 'trasferimento', categoryId: null, toAccountId: contanti.id, amount: 5000 }), d)
    expect(t.categoryId).toBeNull()
    expect(t.accountIds.sort()).toEqual([conto.id, contanti.id].sort())
    expect((await balance(conto)).amount).toBe(95000)
    expect((await balance(contanti)).amount).toBe(5000)
  })

  it('buoni pasto: importo = numero × valore', async () => {
    const t = await mv.createMovement(input({ source: `a:${buoni.id}`, amount: 0, vouchers: 2 }), d)
    expect(t.parts[0]).toMatchObject({ amount: 1600, vouchers: 2, voucherValue: 800 })
    expect(await balance(buoni)).toEqual({ amount: 4000 - 1600, vouchers: 3 })
  })

  it('in modifica il valore del buono resta quello di allora', async () => {
    const t = await mv.createMovement(input({ source: `a:${buoni.id}`, amount: 0, vouchers: 2 }), d)
    await repo.updateAccount(buoni.id, { ...base, name: 'Buoni', type: 'buoni_pasto', initialBalance: 0, voucherValue: 1000, initialVouchers: 5 }, d)
    await mv.updateMovement(t.id, input({ source: `a:${buoni.id}`, amount: 0, vouchers: 3 }), d)
    expect((await d.transactions.get(t.id))!.parts[0]).toMatchObject({ amount: 2400, vouchers: 3, voucherValue: 800 })
  })

  it.each([
    [{ amount: 0 }, /maggiore di zero/],
    [{ categoryId: null }, /categoria/],
    [{ type: 'entrata' as const }, /non corrisponde/],
    [{ date: '13/11/2026' }, /Data/],
    [{ type: 'trasferimento' as const, toAccountId: null }, /destinazione/],
  ])('rifiuta %o', async (over, err) => {
    await expect(mv.createMovement(input(over), d)).rejects.toThrow(err)
  })

  it('trasferimento verso lo stesso conto o con buoni non ammesso', async () => {
    await expect(mv.createMovement(input({ type: 'trasferimento', toAccountId: conto.id }), d)).rejects.toThrow(/diverse/)
    await expect(mv.createMovement(input({ type: 'trasferimento', toAccountId: buoni.id }), d)).rejects.toThrow(/buoni/)
  })

  it('eliminato: sparisce da saldi e mese', async () => {
    const t = await mv.createMovement(input({}), d)
    await mv.deleteMovement(t.id, d)
    expect((await balance(conto)).amount).toBe(100000)
    expect(await mv.movementsOfMonth('2026-11', d)).toHaveLength(0)
  })

  it('pagamento misto: buoni + carta, un\'unica spesa', async () => {
    const t = await mv.createMovement(
      input({ parts: [{ source: `a:${buoni.id}`, amount: 0, vouchers: 3 }, { source: `c:${bancomat.id}`, amount: 740, vouchers: null }] }),
      d,
    )
    expect(mv.total(t)).toBe(3140)
    expect(t.accountIds.sort()).toEqual([buoni.id, conto.id].sort())
    expect(await balance(buoni)).toEqual({ amount: 4000 - 2400, vouchers: 2 })
    expect((await balance(conto)).amount).toBe(100000 - 740)
    expect(mv.totals([t]).expense).toBe(3140)
  })

  it('pagamento misto: niente fonti doppie, solo per le uscite', async () => {
    const two = [{ source: `a:${conto.id}`, amount: 100, vouchers: null }, { source: `a:${conto.id}`, amount: 200, vouchers: null }]
    await expect(mv.createMovement(input({ parts: two }), d)).rejects.toThrow(/due volte/)
    const mixed = [{ source: `a:${conto.id}`, amount: 100, vouchers: null }, { source: `a:${contanti.id}`, amount: 200, vouchers: null }]
    await expect(mv.createMovement(input({ type: 'entrata', categoryId: stipendio.id, parts: mixed }), d)).rejects.toThrow(/solo per le uscite/)
  })

  it('un conto con movimenti non si elimina, una carta usata nemmeno', async () => {
    await mv.createMovement(input({ source: `c:${bancomat.id}` }), d)
    await expect(repo.deleteAccount(conto.id, d)).rejects.toThrow()
    await expect(repo.deleteCard(bancomat.id, d)).rejects.toThrow()
  })
})

describe('riepiloghi', () => {
  it('mese, totali e giorni', async () => {
    await mv.createMovement(input({ date: '2026-11-03', amount: 1000 }), d)
    await mv.createMovement(input({ date: '2026-11-03', type: 'entrata', categoryId: stipendio.id, amount: 5000 }), d)
    await mv.createMovement(input({ date: '2026-11-20', amount: 700 }), d)
    await mv.createMovement(input({ date: '2026-11-20', type: 'trasferimento', categoryId: null, toAccountId: contanti.id, amount: 2000 }), d)
    await mv.createMovement(input({ date: '2026-10-31', amount: 999 }), d)
    const rows = await mv.movementsOfMonth('2026-11', d)
    expect(rows).toHaveLength(4)
    expect(mv.totals(rows)).toEqual({ income: 5000, expense: 1700, net: 3300 })
    const days = mv.groupByDay(rows)
    expect(days.map((g) => [g.date, g.items.length, g.net])).toEqual([
      ['2026-11-20', 2, -700],
      ['2026-11-03', 2, 4000],
    ])
  })

  it('opzioni "con cosa": carte sotto il loro conto, archiviati esclusi', async () => {
    await repo.setAccountArchived(contanti.id, true, d)
    const opts = mv.sourceOptions(
      (await d.accounts.toArray()).sort((a, b) => a.order - b.order),
      await d.cards.toArray(),
    )
    expect(opts.map((o) => o.label)).toEqual(['Conto', 'Bancomat (Conto)', 'Buoni'])
  })
})
