import { describe, expect, it } from 'vitest'
import { applyKey, type Key } from './keypad'

/** Scrive una sequenza di tasti partendo da un campo vuoto, col cursore sempre in fondo. */
function type(keys: Key[], mode: 'decimal' | 'integer' = 'decimal', start = '') {
  let v = start
  for (const k of keys) v = applyKey(v, v.length, v.length, k, mode).value
  return v
}

describe('tastierino', () => {
  it('cifre e virgola', () => {
    expect(type(['1', '2', ',', '5', '0'])).toBe('12,50')
    expect(type([',', '5'])).toBe('0,5')
    expect(type(['1', ',', ','])).toBe('1,')
  })

  it('al massimo due decimali e niente zeri in testa', () => {
    expect(type(['1', ',', '2', '3', '4'])).toBe('1,23')
    expect(type(['0', '0', '7'])).toBe('7')
    expect(type(['1', '2', '3', '4', '5', '6', '7', '8'])).toBe('1234567')
  })

  it('somme e sottrazioni, con il risultato su "="', () => {
    expect(type(['1', '2', ',', '5', '+', '3', ',', '2'])).toBe('12,5+3,2')
    expect(type(['1', '0', '+', '-', '2'])).toBe('10-2')
    expect(type(['+', '5'])).toBe('5')
    expect(type(['-', '-', '5'])).toBe('-5')
    expect(type(['5', ',', '+'])).toBe('5+')
    expect(type(['1', '2', ',', '5', '+', '3', ',', '2', '='])).toBe('15,70')
    expect(type(['1', '2', '='])).toBe('12')
    expect(type(['2', '-', '5', '='])).toBe('2-5')
    expect(type(['5', '+', '0', ',', '5', ',', '1'])).toBe('5+0,51')
  })

  it('cancella il carattere prima del cursore o la selezione', () => {
    expect(type(['1', '2', 'back'])).toBe('1')
    expect(applyKey('', 0, 0, 'back')).toEqual({ value: '', caret: 0 })
    expect(applyKey('12,50', 0, 5, 'back')).toEqual({ value: '', caret: 0 })
    expect(applyKey('12,50', 2, 2, 'back')).toEqual({ value: '1,50', caret: 1 })
  })

  it('scrive dove si trova il cursore e sostituisce la selezione', () => {
    expect(applyKey('12', 1, 1, '5')).toEqual({ value: '152', caret: 2 })
    expect(applyKey('12,50', 0, 5, '8')).toEqual({ value: '8', caret: 1 })
    expect(applyKey('12,50', 4, 4, '9')).toEqual({ value: '12,50', caret: 4 })
  })

  it('numero di buoni: solo cifre, al massimo quattro', () => {
    expect(type(['1', ',', '+', '2'], 'integer')).toBe('12')
    expect(type(['1', '2', '3', '4', '5'], 'integer')).toBe('1234')
    expect(type(['1', 'back'], 'integer')).toBe('')
  })
})

describe('importo scritto col tastierino', () => {
  it('la virgola senza decimali vale come intero', async () => {
    const { parseEuro, evalAmount } = await import('./format')
    expect(parseEuro('15,')).toBe(1500)
    expect(evalAmount('12,+3,')).toBe(1500)
    expect(parseEuro(',')).toBeNull()
  })
})
