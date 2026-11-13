import { describe, expect, it } from 'vitest'
import { emptySnapshot, hasUserData, merge, unifyForFirstLink, type Snapshot } from './merge'
import type { Account, Card, Category, Transaction } from '../data/types'
import { seedId } from '../data/repo'

const acc = (id: string, name: string, updatedAt = 1, over: Partial<Account> = {}): Account => ({
  id, name, type: 'conto_corrente', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null,
  color: 's1', order: 1, archived: false, createdAt: 1, updatedAt, deletedAt: null, ...over,
})
const cat = (id: string, name: string, parentId: string | null = null, kind: 'uscita' | 'entrata' = 'uscita'): Category => ({
  id, name, kind, parentId, color: 's1', order: 1, archived: false, createdAt: 1, updatedAt: 1, deletedAt: null,
})
const card = (id: string, name: string, accountId: string): Card => ({
  id, name, accountId, order: 1, archived: false, createdAt: 1, updatedAt: 1, deletedAt: null,
})
const tx = (id: string, over: Partial<Transaction> = {}): Transaction => ({
  id, type: 'uscita', date: '2026-11-02', categoryId: null, description: '', notes: '', toAccountId: null,
  parts: [], accountIds: [], createdAt: 1, updatedAt: 1, deletedAt: null, ...over,
})
const snap = (s: Partial<Snapshot>): Snapshot => ({ ...emptySnapshot(), ...s })

describe('merge', () => {
  it('vince la modifica più recente, in entrambe le direzioni', () => {
    const local = snap({ accounts: [acc('a', 'Locale nuovo', 5), acc('b', 'B vecchio', 1)] })
    const remote = snap({ accounts: [acc('a', 'Remoto vecchio', 3), acc('b', 'B nuovo', 9)] })
    const r = merge(local, remote)
    expect(r.merged.accounts.map((a) => a.name).sort()).toEqual(['B nuovo', 'Locale nuovo'])
    expect(r.toLocal.accounts.map((a) => a.name)).toEqual(['B nuovo'])
    expect(r.remoteChanged).toBe(true)
  })

  it('record solo da una parte: unione', () => {
    const r = merge(snap({ transactions: [tx('l')] }), snap({ transactions: [tx('r')] }))
    expect(r.merged.transactions.map((t) => t.id).sort()).toEqual(['l', 'r'])
    expect(r.toLocal.transactions.map((t) => t.id)).toEqual(['r'])
    expect(r.remoteChanged).toBe(true)
  })

  it('cancellazione più recente si propaga', () => {
    const r = merge(snap({ transactions: [tx('x', { updatedAt: 1 })] }), snap({ transactions: [tx('x', { updatedAt: 2, deletedAt: 2 })] }))
    expect(r.toLocal.transactions[0].deletedAt).toBe(2)
    expect(r.remoteChanged).toBe(false)
  })

  it('niente da fare se uguali', () => {
    const s = snap({ accounts: [acc('a', 'A')] })
    const r = merge(s, structuredClone(s))
    expect(r.remoteChanged).toBe(false)
    expect(r.toLocal.accounts).toHaveLength(0)
  })

  it('merge ripetuto è stabile (idempotente)', () => {
    const local = snap({ accounts: [acc('a', 'A', 5)], transactions: [tx('t1')] })
    const remote = snap({ accounts: [acc('a', 'A0', 3)], transactions: [tx('t2')] })
    const first = merge(local, remote).merged
    const second = merge(first, first)
    expect(second.remoteChanged).toBe(false)
  })
})

describe('primo collegamento', () => {
  it('unifica conti, carte e categorie con lo stesso nome e ricollega i movimenti', () => {
    const remote = snap({
      accounts: [acc('R-conto', 'Conto principale')],
      cards: [card('R-bm', 'Bancomat', 'R-conto')],
      categories: [cat('R-casa', 'Casa'), cat('R-boll', 'Bollette', 'R-casa'), cat('R-stip', 'Stipendio', null, 'entrata')],
    })
    const local = snap({
      accounts: [acc('L-conto', 'conto  principale '), acc('L-altro', 'Risparmi')],
      cards: [card('L-bm', 'Bancomat', 'L-conto')],
      categories: [cat('L-casa', 'Casa'), cat('L-boll', 'Bollette', 'L-casa'), cat('L-luce', 'Luce', 'L-casa')],
      transactions: [
        tx('t1', { categoryId: 'L-boll', parts: [{ accountId: 'L-conto', cardId: 'L-bm', amount: 100, vouchers: null, voucherValue: null }], accountIds: ['L-conto'] }),
        tx('t2', { type: 'trasferimento', parts: [{ accountId: 'L-conto', cardId: null, amount: 5, vouchers: null, voucherValue: null }], toAccountId: 'L-altro', accountIds: ['L-conto', 'L-altro'] }),
      ],
    })
    const u = unifyForFirstLink(local, remote)
    expect(u.accounts.map((a) => a.id)).toEqual(['L-altro'])
    expect(u.cards).toHaveLength(0)
    expect(u.categories.map((c) => [c.id, c.parentId])).toEqual([['L-luce', 'R-casa']])
    expect(u.transactions[0]).toMatchObject({ categoryId: 'R-boll', accountIds: ['R-conto'] })
    expect(u.transactions[0].parts[0]).toMatchObject({ accountId: 'R-conto', cardId: 'R-bm' })
    expect(u.transactions[1].accountIds.sort()).toEqual(['L-altro', 'R-conto'])

    const m = merge(u, remote).merged
    expect(m.accounts.map((a) => a.name).sort()).toEqual(['Conto principale', 'Risparmi'])
    expect(m.categories).toHaveLength(4)
  })

  it('le categorie iniziali hanno lo stesso id su ogni dispositivo', () => {
    expect(seedId('uscita', 'Spesa alimentare')).toBe('seed-uscita-spesa-alimentare')
    expect(seedId('uscita', 'Casa', 'Affitto/mutuo')).toBe('seed-uscita-casa-affitto-mutuo')
  })

  it('dati utente presenti?', () => {
    expect(hasUserData(snap({ categories: [cat('c', 'Casa')] }))).toBe(false)
    expect(hasUserData(snap({ accounts: [acc('a', 'A')] }))).toBe(true)
  })
})
