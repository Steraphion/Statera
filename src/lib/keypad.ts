/*
 * Tastierino dell'app per gli importi (solo su telefono). Logica pura, testata:
 * dato il testo del campo, la selezione e il tasto, restituisce il nuovo testo e la posizione del cursore.
 */
import { centsToInput, evalAmount, isExpression } from './format'

export type KeypadMode = 'decimal' | 'integer'
export type Key = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | ',' | '+' | '-' | 'back' | '='

export interface Edit {
  value: string
  caret: number
}

const OPS = /[+\-*/×x÷:]/i

/** Il numero (tra due operatori) in cui cade la posizione `at`. */
function segmentAround(text: string, at: number): string {
  let a = at
  while (a > 0 && !OPS.test(text[a - 1])) a--
  let b = at
  while (b < text.length && !OPS.test(text[b])) b++
  return text.slice(a, b)
}

export function applyKey(value: string, start: number, end: number, key: Key, mode: KeypadMode = 'decimal'): Edit {
  const s = Math.max(0, Math.min(start, value.length))
  const e = Math.max(s, Math.min(end, value.length))
  const before = value.slice(0, s)
  const after = value.slice(e)
  const insert = (t: string): Edit => ({ value: before + t + after, caret: s + t.length })

  if (key === 'back') {
    if (s !== e) return { value: before + after, caret: s }
    if (s === 0) return { value, caret: 0 }
    return { value: value.slice(0, s - 1) + after, caret: s - 1 }
  }

  if (mode === 'integer') {
    if (!/^\d$/.test(key)) return { value, caret: e }
    if ((before + after).replace(/\D/g, '').length >= 4) return { value, caret: e }
    return insert(key)
  }

  if (key === '=') {
    if (!isExpression(value)) return { value, caret: value.length }
    const c = evalAmount(value)
    if (c === null || c < 0) return { value, caret: value.length }
    const t = centsToInput(c)
    return { value: t, caret: t.length }
  }

  if (key === '+' || key === '-') {
    const prev = before.slice(-1)
    // In testa solo il meno (es. saldo iniziale negativo)
    if (!before) return key === '-' && !after.startsWith('-') ? insert('-') : { value, caret: e }
    if (OPS.test(prev)) return { value: before.slice(0, -1) + key + after, caret: s }
    if (prev === ',') return { value: before.slice(0, -1) + key + after, caret: s }
    return insert(key)
  }

  const seg = segmentAround(before + after, s)
  if (key === ',') {
    if (seg.includes(',')) return { value, caret: e }
    const prev = before.slice(-1)
    return insert(!prev || OPS.test(prev) ? '0,' : ',')
  }

  // Cifra: al massimo due decimali, sette cifre intere e niente zeri inutili in testa
  const left = segmentAround(before, s)
  const comma = seg.indexOf(',')
  if (comma >= 0 && left.includes(',') && seg.length - comma - 1 >= 2) return { value, caret: e }
  if (seg === '0' && left === '0') return { value: before.slice(0, -1) + key + after, caret: s }
  if (!left.includes(',') && (comma >= 0 ? seg.slice(0, comma) : seg).replace(/\D/g, '').length >= 7) return { value, caret: e }
  return insert(key)
}
