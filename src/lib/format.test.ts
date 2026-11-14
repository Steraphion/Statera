import { describe, expect, it } from 'vitest'
import { centsToInput, parseEuro } from './format'

describe('parseEuro', () => {
  it.each([
    ['12', 1200],
    ['12,5', 1250],
    ['12,50', 1250],
    ['0,07', 7],
    ['1.234,56', 123456],
    ['1234.56', 123456],
    ['1.234', 123400],
    ['€ 8', 800],
    ['-3,20', -320],
  ])('%s → %i', (input, cents) => {
    expect(parseEuro(input)).toBe(cents)
  })

  it.each(['', 'abc', '12,345', '1,2,3', '--5'])('rifiuta %s', (input) => {
    expect(parseEuro(input)).toBeNull()
  })
})

describe('centsToInput', () => {
  it('formatta per la modifica', () => {
    expect(centsToInput(123456)).toBe('1234,56')
    expect(centsToInput(5)).toBe('0,05')
    expect(centsToInput(-320)).toBe('-3,20')
  })

  it('andata e ritorno', () => {
    for (const c of [0, 1, 99, 100, 123456, -4321]) expect(parseEuro(centsToInput(c))).toBe(c)
  })
})

describe('formatEuro', () => {
  it('punto delle migliaia, spazio unificatore e vero segno meno', async () => {
    const { formatEuro } = await import('./format')
    expect(formatEuro(123456)).toBe('1.234,56 €')
    expect(formatEuro(-12000)).toBe('−120,00 €')
    expect(parseEuro(formatEuro(-12000))).toBe(-12000)
  })
})
