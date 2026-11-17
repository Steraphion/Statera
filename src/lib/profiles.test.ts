import { describe, expect, it } from 'vitest'
import { DEFAULT_DB, isStateraDb, mergeProfiles } from './profiles'

describe('profili', () => {
  it('riconosce i database di Statera', () => {
    expect(isStateraDb(DEFAULT_DB)).toBe(true)
    expect(isStateraDb('statera-1ecead2b')).toBe(true)
    expect(isStateraDb('statera-prova')).toBe(false)
    expect(isStateraDb('altro-db')).toBe(false)
  })

  it('il profilo iniziale nascosto da un profilo nuovo torna nell\'elenco', () => {
    // Situazione della 0.36.0: profilo nuovo in uso, quello iniziale (con i dati) fuori dall'elenco
    const list = [{ db: 'statera-1ecead2b', email: '', name: '' }]
    const out = mergeProfiles(list, ['statera-1ecead2b', 'statera-locale'], 'statera-1ecead2b')
    expect(out.map((p) => p.db)).toEqual(['statera-1ecead2b', 'statera-locale'])
  })

  it('quello in uso per primo, account collegati intatti, niente doppioni né database estranei', () => {
    const list = [
      { db: 'statera-locale', email: 'utente.prova@example.com', name: 'Utente' },
      { db: 'statera-0000aaaa', email: '', name: '' },
    ]
    const out = mergeProfiles(list, ['statera-locale', 'statera-0000aaaa', 'test-1', 'statera-0000bbbb'], 'statera-0000aaaa')
    expect(out.map((p) => p.db)).toEqual(['statera-0000aaaa', 'statera-locale', 'statera-0000bbbb'])
    expect(out[1].email).toBe('utente.prova@example.com')
  })

  it('il profilo in uso c\'è anche se il browser non elenca i database', () => {
    expect(mergeProfiles([], [], 'statera-locale').map((p) => p.db)).toEqual(['statera-locale'])
  })
})
