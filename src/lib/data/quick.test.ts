import { describe, expect, it } from 'vitest'
import { evalAmount, isExpression } from '../format'
import { descriptionSuggestions, filterMovements, EMPTY_FILTERS } from './transactions'
import type { Transaction } from './types'

describe('calcoli nel campo importo', () => {
  it('somme, sottrazioni, moltiplicazioni e divisioni', () => {
    expect(evalAmount('12,50+3,20')).toBe(1570)
    expect(evalAmount('20 - 2,5')).toBe(1750)
    expect(evalAmount('3x1,20')).toBe(360)
    expect(evalAmount('3*1,20+0,50')).toBe(410)
    expect(evalAmount('100/3')).toBe(3333)
    expect(evalAmount('1.234,56+1')).toBe(123556)
    expect(evalAmount('-5+2')).toBe(-300)
  })
  it('senza operatori come prima', () => {
    expect(evalAmount('12,5')).toBe(1250)
    expect(evalAmount('1.234')).toBe(123400)
    expect(evalAmount('')).toBeNull()
  })
  it('testo non valido', () => {
    expect(evalAmount('12++3')).toBeNull()
    expect(evalAmount('5/0')).toBeNull()
    expect(evalAmount('abc')).toBeNull()
    expect(evalAmount('3+')).toBeNull()
  })
  it('riconosce un calcolo', () => {
    expect(isExpression('12,50+3')).toBe(true)
    expect(isExpression('12,50')).toBe(false)
    expect(isExpression('-12')).toBe(false)
  })
})

const base = { createdAt: 1, updatedAt: 1, deletedAt: null }
let n = 0
const tx = (over: Partial<Transaction>): Transaction => ({
  ...base, id: `t${n++}`, type: 'uscita', date: '2026-11-01', categoryId: 'spesa', description: '', notes: '',
  parts: [{ accountId: 'a', cardId: null, amount: 1000, vouchers: null, voucherValue: null }], toAccountId: null, accountIds: ['a'], ...over,
})

describe('suggerimenti dalla descrizione', () => {
  const rows = [
    tx({ description: 'Conad', date: '2026-10-01' }),
    tx({ description: 'conad ', date: '2026-11-03', parts: [{ accountId: 'a', cardId: 'k', amount: 4210, vouchers: null, voucherValue: null }] }),
    tx({ description: 'Bar Centrale', categoryId: 'pasti' }),
    tx({ description: 'Caffè al bar', categoryId: 'pasti' }),
    tx({ description: 'Caffè al bar', categoryId: 'pasti' }),
    tx({ description: 'Caffè al bar', categoryId: 'pasti' }),
    tx({ description: 'Stipendio', type: 'entrata' }),
    tx({ description: 'Coop', deletedAt: 9 }),
  ]
  it('raggruppa, usa la più recente e ordina', () => {
    const s = descriptionSuggestions(rows, 'uscita', 'co')
    expect(s.map((x) => x.description)).toEqual(['conad'])
    expect(s[0].count).toBe(2)
    expect(s[0].last.parts[0].cardId).toBe('k')
  })
  it('prima chi inizia con il testo, poi le parole; senza accenti', () => {
    expect(descriptionSuggestions(rows, 'uscita', 'bar').map((x) => x.description)).toEqual(['Bar Centrale', 'Caffè al bar'])
    expect(descriptionSuggestions(rows, 'uscita', 'caffe').map((x) => x.count)).toEqual([3])
  })
  it('solo lo stesso tipo, niente cancellati, niente con testo vuoto', () => {
    expect(descriptionSuggestions(rows, 'uscita', 'sti')).toEqual([])
    expect(descriptionSuggestions(rows, 'entrata', 'sti')).toHaveLength(1)
    expect(descriptionSuggestions(rows, 'uscita', 'coop')).toEqual([])
    expect(descriptionSuggestions(rows, 'uscita', '  ')).toEqual([])
  })
})

describe('ricerca per importo', () => {
  const refs = { accountMap: new Map(), cardMap: new Map(), categoryMap: new Map() }
  const rows = [tx({ parts: [{ accountId: 'a', cardId: null, amount: 999, vouchers: null, voucherValue: null }] }), tx({}), tx({ parts: [{ accountId: 'a', cardId: null, amount: 5000, vouchers: null, voucherValue: null }] })]
  it('da e a, estremi compresi', () => {
    expect(filterMovements(rows, { ...EMPTY_FILTERS, min: '10' }, refs)).toHaveLength(2)
    expect(filterMovements(rows, { ...EMPTY_FILTERS, max: '10' }, refs)).toHaveLength(2)
    expect(filterMovements(rows, { ...EMPTY_FILTERS, min: '10', max: '49,99' }, refs)).toHaveLength(1)
    expect(filterMovements(rows, { ...EMPTY_FILTERS, min: 'x' }, refs)).toHaveLength(3)
  })
})
