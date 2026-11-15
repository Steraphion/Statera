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

describe('palette', () => {
  it('valori sconosciuti = Indaco morbido', async () => {
    const { parsePalette, PALETTES } = await import('./theme')
    expect(parsePalette('petrolio')).toBe('petrolio')
    expect(parsePalette(null)).toBe('indaco')
    expect(parsePalette('arcobaleno')).toBe('indaco')
    expect(PALETTES[0].id).toBe('indaco')
  })

  it('ogni palette ha i colori chiari e scuri in tokens.css, e tema.js la conosce', async () => {
    const { readFileSync } = await import('node:fs')
    const { PALETTES } = await import('./theme')
    const css = readFileSync(new URL('../styles/tokens.css', import.meta.url), 'utf8')
    const js = readFileSync(new URL('../../public/tema.js', import.meta.url), 'utf8')
    for (const { id } of PALETTES) {
      expect(css, id).toContain(`[data-palette='${id}']`)
      expect(css, id).toContain(`:root[data-theme='dark'] [data-palette='${id}']`)
      expect(js, id).toMatch(new RegExp(`[(|]${id}[|)]`))
    }
  })
})
