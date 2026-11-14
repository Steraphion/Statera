import { describe, expect, it } from 'vitest'
import { exitDuration, parseDuration } from './motion'

describe('parseDuration', () => {
  it('legge millisecondi e secondi', () => {
    expect(parseDuration('280ms')).toBe(280)
    expect(parseDuration(' 200ms ')).toBe(200)
    expect(parseDuration('0.12s')).toBe(120)
    expect(parseDuration('.2s')).toBe(200)
    expect(parseDuration('1S')).toBe(1000)
  })

  it('valori assenti o non validi = nessuna attesa', () => {
    expect(parseDuration('')).toBe(0)
    expect(parseDuration('veloce')).toBe(0)
    expect(parseDuration('200')).toBe(0)
    expect(parseDuration('-200ms')).toBe(0)
    expect(parseDuration('var(--duration-base)')).toBe(0)
  })
})

describe('exitDuration', () => {
  it('usa la durata del token', () => {
    expect(exitDuration('200ms', false)).toBe(200)
  })

  it('con «riduci animazioni» non aspetta', () => {
    expect(exitDuration('200ms', true)).toBe(0)
    expect(exitDuration('280ms', true)).toBe(0)
  })
})
