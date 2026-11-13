import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'

let d: StateraDB
let n = 0

beforeEach(async () => {
  d = new StateraDB(`test-${++n}`)
  await d.open()
})

describe('primo avvio', () => {
  it('carica le categorie una sola volta', async () => {
    await repo.ensureSeeded(d)
    const first = await d.categories.count()
    expect(first).toBeGreaterThan(10)
    await repo.ensureSeeded(d)
    expect(await d.categories.count()).toBe(first)
    const casa = (await d.categories.toArray()).find((c) => c.name === 'Casa')!
    expect(await d.categories.where('parentId').equals(casa.id).count()).toBe(3)
  })
})

describe('conti', () => {
  it('buoni pasto: saldo iniziale = buoni × valore', async () => {
    const a = await repo.createAccount(
      { name: ' Buoni ', type: 'buoni_pasto', initialBalance: 0, initialDate: '2026-11-01', voucherValue: 800, initialVouchers: 10, color: 's2' },
      d,
    )
    expect(a.name).toBe('Buoni')
    expect(a.initialBalance).toBe(8000)
  })

  it('nome obbligatorio', async () => {
    await expect(
      repo.createAccount({ name: '  ', type: 'contanti', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' }, d),
    ).rejects.toThrow()
  })

  it('eliminare un conto elimina le sue carte', async () => {
    const a = await repo.createAccount({ name: 'Banca', type: 'conto_corrente', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' }, d)
    const c = await repo.createCard({ name: 'Bancomat', accountId: a.id }, d)
    await repo.deleteAccount(a.id, d)
    expect((await d.accounts.get(a.id))!.deletedAt).not.toBeNull()
    expect((await d.cards.get(c.id))!.deletedAt).not.toBeNull()
  })

  it('un conto con movimenti non si elimina', async () => {
    const a = await repo.createAccount({ name: 'Banca', type: 'conto_corrente', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' }, d)
    await d.transactions.add({
      id: 't1', createdAt: 0, updatedAt: 0, deletedAt: null, type: 'uscita', date: '2026-11-02', categoryId: null,
      description: 'Esempio', notes: '', parts: [{ accountId: a.id, cardId: null, amount: 100, vouchers: null, voucherValue: null }],
      toAccountId: null, accountIds: [a.id],
    })
    await expect(repo.deleteAccount(a.id, d)).rejects.toThrow(/archiviarlo/)
  })
})

describe('categorie', () => {
  it('massimo due livelli e stesso tipo', async () => {
    const madre = await repo.createCategory({ name: 'Casa', kind: 'uscita', parentId: null, color: 's1' }, d)
    const figlia = await repo.createCategory({ name: 'Bollette', kind: 'uscita', parentId: madre.id, color: 's1' }, d)
    await expect(repo.createCategory({ name: 'Luce', kind: 'uscita', parentId: figlia.id, color: 's1' }, d)).rejects.toThrow(/due livelli/)
    await expect(repo.createCategory({ name: 'X', kind: 'entrata', parentId: madre.id, color: 's1' }, d)).rejects.toThrow(/stesso tipo/)
  })

  it('archiviare la madre archivia le figlie', async () => {
    const madre = await repo.createCategory({ name: 'Casa', kind: 'uscita', parentId: null, color: 's1' }, d)
    const figlia = await repo.createCategory({ name: 'Bollette', kind: 'uscita', parentId: madre.id, color: 's1' }, d)
    await repo.setCategoryArchived(madre.id, true, d)
    expect((await d.categories.get(figlia.id))!.archived).toBe(true)
  })
})

describe('ordine dei conti', () => {
  it('sposta su e giù', async () => {
    const mk = (name: string) =>
      repo.createAccount({ name, type: 'contanti', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' }, d)
    const a = await mk('A')
    await mk('B')
    const c = await mk('C')
    await repo.moveAccount(c.id, -1, d)
    await repo.moveAccount(a.id, 1, d)
    const names = (await d.accounts.toArray()).sort((x, y) => x.order - y.order).map((x) => x.name)
    expect(names).toEqual(['C', 'A', 'B'])
    await repo.moveAccount(c.id, -1, d) // già primo: nessun cambiamento
    expect((await d.accounts.get(c.id))!.order).toBe(1)
  })
})
