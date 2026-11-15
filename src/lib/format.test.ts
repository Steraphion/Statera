import { describe, expect, it } from 'vitest'
import { centsToInput, parseEuro, formatDayMonth, formatWhen } from './format'

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

describe('formatDayMonth', () => {
  it('giorno e mese abbreviato, senza anno', () => {
    expect(formatDayMonth('2026-11-14')).toBe('14 nov')
    expect(formatDayMonth('2026-01-02')).toBe('2 gen')
  })
})

describe('formatWhen', () => {
  const now = new Date(2026, 10, 15, 18, 5).getTime()
  it('oggi: solo l\'ora', () => {
    expect(formatWhen(new Date(2026, 10, 15, 14, 32).getTime(), now)).toBe('alle 14:32')
    expect(formatWhen(new Date(2026, 10, 15, 0, 1).getTime(), now)).toBe('alle 00:01')
  })
  it('ieri e giorni precedenti', () => {
    expect(formatWhen(new Date(2026, 10, 14, 23, 59).getTime(), now)).toBe('ieri alle 23:59')
    expect(formatWhen(new Date(2026, 10, 12, 9, 0).getTime(), now)).toBe('il 12 novembre alle 09:00')
    expect(formatWhen(new Date(2025, 11, 31, 20, 15).getTime(), now)).toBe('il 31 dicembre 2025 alle 20:15')
  })
  it('un orario appena nel futuro (orologi un po\' diversi) vale come adesso', () => {
    expect(formatWhen(now + 60_000, now)).toBe('alle 18:06')
  })
})
