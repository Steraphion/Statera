import { describe, expect, it } from 'vitest'
import { RECENT_MS, exitDuration, markChanged, parseDuration, takeChanged } from './motion'

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

describe('righe appena cambiate', () => {
  it('solo gli id segnati da poco, una volta sola', () => {
    markChanged('a', 1000)
    expect(takeChanged('b', 1100)).toBe(false)
    expect(takeChanged(['b', 'a'], 1100)).toBe(true)
    expect(takeChanged('a', 1200)).toBe(false)
  })

  it('una modifica vecchia non anima più', () => {
    markChanged('c', 1000)
    expect(takeChanged('c', 1000 + RECENT_MS)).toBe(false)
  })
})

describe('pulizia', () => {
  it('una modifica nuova toglie quelle scadute', () => {
    markChanged('vecchio', 1000)
    markChanged('nuovo', 1000 + RECENT_MS)
    expect(takeChanged('vecchio', 1000)).toBe(false)
    expect(takeChanged('nuovo', 1000 + RECENT_MS)).toBe(true)
  })
})
