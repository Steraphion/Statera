import { describe, expect, it } from 'vitest'
import { parseThemePref, resolveTheme } from './theme'

describe('tema', () => {
  it('scelta salvata: valori sconosciuti = automatico', () => {
    expect(parseThemePref('light')).toBe('light')
    expect(parseThemePref('dark')).toBe('dark')
    expect(parseThemePref(null)).toBe('auto')
    expect(parseThemePref('viola')).toBe('auto')
  })
  it('automatico segue il sistema, chiaro e scuro no', () => {
    expect(resolveTheme('auto', true)).toBe('dark')
    expect(resolveTheme('auto', false)).toBe('light')
    expect(resolveTheme('light', true)).toBe('light')
    expect(resolveTheme('dark', false)).toBe('dark')
  })
})
