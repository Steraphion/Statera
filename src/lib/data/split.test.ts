import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as mv from './transactions'
import * as an from './analytics'
import type { Account } from './types'

let d: StateraDB
let n = 0
let conto: Account
const base = { initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1' as const }
const spesa = () => repo.seedId('uscita', 'Spesa alimentare')
const casa = () => repo.seedId('uscita', 'Casa')
const input = (over: Partial<mv.MovementInput> = {}): mv.MovementInput => ({
  type: 'uscita', date: '2026-11-10', parts: [{ source: `a:${conto.id}`, amount: 10000, vouchers: null }],
  categoryId: spesa(), toAccountId: null, description: 'Supermercato', notes: '', ...over,
})

beforeEach(async () => {
  d = new StateraDB(`split-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
  conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, d)
})

describe('ripartizione su più categorie', () => {
  it('salva le parti e sceglie come principale la più grande', async () => {
    const t = await mv.createMovement(input({ categoryId: spesa(), splits: [{ categoryId: spesa(), amount: 3000 }, { categoryId: casa(), amount: 7000 }] }), d)
    expect(t.splits).toHaveLength(2)
    expect(t.categoryId).toBe(casa())
    const cats = await d.categories.toArray()
    const g = an.byCategory([t], 'uscita', cats)
    expect(g.map((x) => [x.category.name, x.total])).toEqual([['Casa', 7000], ['Spesa alimentare', 3000]])
  })
  it('la somma deve tornare; categorie valide e non ripetute', async () => {
    await expect(mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 3000 }, { categoryId: casa(), amount: 6000 }] }), d)).rejects.toThrow('uguale al totale')
    await expect(mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 5000 }, { categoryId: spesa(), amount: 5000 }] }), d)).rejects.toThrow('due volte')
    await expect(mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 5000 }, { categoryId: repo.seedId('entrata', 'Stipendio'), amount: 5000 }] }), d)).rejects.toThrow('tipo')
    await expect(mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 10000 }, { categoryId: casa(), amount: 0 }] }), d)).rejects.toThrow('importo')
  })
  it('una sola parte = nessuna ripartizione; togliere la ripartizione in modifica', async () => {
    const t = await mv.createMovement(input({ splits: [{ categoryId: casa(), amount: 10000 }] }), d)
    expect(t.splits).toEqual([])
    expect(t.categoryId).toBe(spesa())
    const s = await mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 4000 }, { categoryId: casa(), amount: 6000 }] }), d)
    await mv.updateMovement(s.id, input({ categoryId: spesa() }), d)
    const after = (await d.transactions.get(s.id))!
    expect(after.splits).toEqual([])
    expect(after.categoryId).toBe(spesa())
  })
  it('la ricerca per categoria trova anche le parti', async () => {
    await mv.createMovement(input({ splits: [{ categoryId: spesa(), amount: 3000 }, { categoryId: casa(), amount: 7000 }] }), d)
    const rows = await d.transactions.toArray()
    const cats = await d.categories.toArray()
    const refs = { accountMap: new Map(), cardMap: new Map(), categoryMap: new Map(cats.map((c) => [c.id, c])) }
    expect(mv.filterMovements(rows, { ...mv.EMPTY_FILTERS, categoryId: spesa() }, refs)).toHaveLength(1)
    expect(mv.filterMovements(rows, { ...mv.EMPTY_FILTERS, categoryId: casa() }, refs)).toHaveLength(1)
  })
})

describe('etichette', () => {
  it('pulite, senza doppioni, al massimo 5', async () => {
    const t = await mv.createMovement(input({ tags: [' #Vacanze  estate ', 'vacanze estate', 'Regali', ''] }), d)
    expect(t.tags).toEqual(['Vacanze estate', 'Regali'])
    await expect(mv.createMovement(input({ tags: ['a', 'b', 'c', 'd', 'e', 'f'] }), d)).rejects.toThrow('5 etichette')
  })
  it('filtro, ricerca testuale ed elenco per frequenza', async () => {
    await mv.createMovement(input({ tags: ['Vacanze estate'] }), d)
    await mv.createMovement(input({ tags: ['Vacanze estate', 'Regali'] }), d)
    await mv.createMovement(input({}), d)
    const rows = await d.transactions.toArray()
    const refs = { accountMap: new Map(), cardMap: new Map(), categoryMap: new Map() }
    expect(mv.filterMovements(rows, { ...mv.EMPTY_FILTERS, tag: 'vacanze ESTATE' }, refs)).toHaveLength(2)
    expect(mv.filterMovements(rows, { ...mv.EMPTY_FILTERS, text: 'regali' }, refs)).toHaveLength(1)
    expect(mv.allTags(rows)).toEqual(['Vacanze estate', 'Regali'])
  })
})
