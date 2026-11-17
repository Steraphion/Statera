import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import { accountGroups, cardEligible, cardsOf } from './balances'
import { sourceOptions } from './transactions'
import type { AccountType } from './types'

let d: StateraDB
let n = 0
const acc = (name: string, type: AccountType, initialBalance = 0) =>
  repo.createAccount({ name, type, initialBalance, initialDate: '2026-11-01', voucherValue: type === 'buoni_pasto' ? 800 : null, initialVouchers: type === 'buoni_pasto' ? 5 : null, color: 's1' }, d)

beforeEach(async () => {
  d = new StateraDB(`gruppi-${++n}`)
  await d.open()
})

describe('conti divisi per tipo', () => {
  it('gruppi nell\'ordine fissato, solo quelli non vuoti, con il totale', async () => {
    await acc('Contanti', 'contanti', 5000)
    await acc('Prepagata viaggi', 'carta_prepagata', 20000)
    await acc('Conto principale', 'conto_corrente', 150000)
    await acc('Conto secondario', 'conto_corrente', 30000)
    await acc('Ricaricabile', 'carta_prepagata', 1000)
    const accounts = (await d.accounts.toArray()).sort((a, b) => a.order - b.order)
    const g = accountGroups(accounts, [])
    expect(g.map((x) => [x.label, x.accounts.map((a) => a.name), x.total])).toEqual([
      ['Conti correnti', ['Conto principale', 'Conto secondario'], 180000],
      ['Carte prepagate', ['Prepagata viaggi', 'Ricaricabile'], 21000],
      ['Contanti', ['Contanti'], 5000],
    ])
  })

  it('le prepagate non hanno carte collegate; conti correnti e altri sì', async () => {
    const p = await acc('Prepagata', 'carta_prepagata')
    const c = await acc('Conto', 'conto_corrente')
    expect(cardEligible(p)).toBe(false)
    expect(cardEligible(c)).toBe(true)
    await expect(repo.createAccountWithCard({ ...p, name: 'Altra prepagata' }, 'Carta', d)).rejects.toThrow('solo a un conto corrente')
  })

  it('conto corrente e carta creati insieme; la carta compare come modo di pagare quel conto', async () => {
    const a = await repo.createAccountWithCard(
      { name: 'Conto principale', type: 'conto_corrente', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's2' },
      '  Carta  del conto ',
      d,
    )
    const cards = cardsOf(a, await d.cards.toArray())
    expect(cards.map((c) => c.name)).toEqual(['Carta del conto'])
    const opts = sourceOptions([a], cards)
    expect(opts.map((o) => o.label)).toEqual(['Conto principale', 'Carta del conto (Conto principale)'])
    // senza nome della carta: solo il conto
    const b = await repo.createAccountWithCard({ ...a, name: 'Senza carta' }, ' ', d)
    expect(cardsOf(b, await d.cards.toArray())).toEqual([])
  })

  it('"Ordina" sposta il conto solo dentro il suo gruppo', async () => {
    const c1 = await acc('Conto A', 'conto_corrente')
    await acc('Prepagata', 'carta_prepagata')
    const c2 = await acc('Conto B', 'conto_corrente')
    await repo.moveAccount(c2.id, -1, d)
    let list = (await d.accounts.toArray()).sort((a, b) => a.order - b.order).map((a) => a.name)
    expect(list.filter((x) => x.startsWith('Conto'))).toEqual(['Conto B', 'Conto A'])
    // già primo del gruppo: non si muove (anche se nell'ordine generale c'è un conto prima)
    await repo.moveAccount(c2.id, -1, d)
    list = (await d.accounts.toArray()).sort((a, b) => a.order - b.order).map((a) => a.name)
    expect(list.filter((x) => x.startsWith('Conto'))).toEqual(['Conto B', 'Conto A'])
    await repo.moveAccount(c1.id, 1, d)
    expect((await d.accounts.toArray()).sort((a, b) => a.order - b.order).filter((a) => a.type === 'conto_corrente').map((a) => a.name)).toEqual(['Conto B', 'Conto A'])
  })

  it('da "Altro" a "Carta prepagata": saldo e carte già collegate restano', async () => {
    const a = await repo.createAccountWithCard({ name: 'Ricaricabile', type: 'altro', initialBalance: 4000, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's3' }, 'Carta', d)
    await repo.updateAccount(a.id, { name: 'Ricaricabile', type: 'carta_prepagata', initialBalance: 4000, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's3' }, d)
    const after = (await d.accounts.get(a.id))!
    expect(after.type).toBe('carta_prepagata')
    expect(after.initialBalance).toBe(4000)
    expect(cardsOf(after, await d.cards.toArray())).toHaveLength(1)
  })
})
