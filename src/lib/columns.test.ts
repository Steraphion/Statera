import { describe, expect, it } from 'vitest'
import {
  DEFAULT_PREFS,
  LAYOUT_STEPS,
  STEP,
  atLeast,
  layoutClass,
  STEP_LARGE,
  clamp,
  dragWidth,
  keyWidth,
  limits,
  parseColumnPrefs,
  pxOf,
  serializeColumnPrefs,
} from './columns'

describe('colonne regolabili', () => {
  it('preferenze assenti o rovinate: valori iniziali', () => {
    expect(parseColumnPrefs(null)).toEqual(DEFAULT_PREFS)
    expect(parseColumnPrefs('non è json')).toEqual(DEFAULT_PREFS)
    expect(parseColumnPrefs('[1,2]')).toEqual(DEFAULT_PREFS)
    expect(parseColumnPrefs('{"widths":{"aside":"320"},"side":"boh"}')).toEqual(DEFAULT_PREFS)
  })

  it('larghezze fuori misura o non numeriche si ignorano, le altre si arrotondano', () => {
    const p = parseColumnPrefs(JSON.stringify({ widths: { aside: 333.6, pane: 99999 }, side: 'stretta' }))
    expect(p).toEqual({ widths: { aside: 334, pane: null }, side: 'stretta' })
    expect(parseColumnPrefs('{"widths":{"aside":NaN}}').widths.aside).toBeNull()
    expect(parseColumnPrefs(JSON.stringify({ widths: { aside: -5 } })).widths.aside).toBeNull()
  })

  it('andata e ritorno', () => {
    const p = { widths: { aside: 400, pane: 300 }, side: 'stretta' as const }
    expect(parseColumnPrefs(serializeColumnPrefs(p))).toEqual(p)
  })

  it('il massimo scende se lo spazio non basta, ma non sotto il minimo', () => {
    expect(limits(260, 460)).toEqual({ min: 260, max: 460 })
    expect(limits(260, 460, 380.7)).toEqual({ min: 260, max: 380 })
    expect(limits(260, 460, 100)).toEqual({ min: 260, max: 260 })
  })

  it('trascinare: la colonna a destra si allarga andando a sinistra, quella a sinistra andando a destra', () => {
    expect(dragWidth(320, 500, 450, 'left', 260, 460)).toBe(370)
    expect(dragWidth(320, 500, 450, 'right', 260, 460)).toBe(270)
    expect(dragWidth(320, 500, 100, 'left', 260, 460)).toBe(460)
    expect(dragWidth(320, 500, 900, 'left', 260, 460)).toBe(260)
    expect(clamp(300.4, 260, 460)).toBe(300)
  })

  it('tastiera: frecce nella direzione del separatore, passi grandi, Inizio e Fine', () => {
    // Colonna a destra: freccia a sinistra = più larga
    expect(keyWidth(320, 'ArrowLeft', false, 'left', 260, 460)).toBe(320 + STEP)
    expect(keyWidth(320, 'ArrowRight', false, 'left', 260, 460)).toBe(320 - STEP)
    expect(keyWidth(320, 'ArrowLeft', true, 'left', 260, 460)).toBe(320 + STEP_LARGE)
    // Colonna a sinistra: freccia a destra = più larga
    expect(keyWidth(320, 'ArrowRight', false, 'right', 260, 460)).toBe(320 + STEP)
    expect(keyWidth(320, 'PageUp', false, 'right', 260, 460)).toBe(320 + STEP_LARGE)
    expect(keyWidth(400, 'PageDown', false, 'left', 260, 460)).toBe(400 - STEP_LARGE)
    expect(keyWidth(320, 'PageDown', false, 'left', 260, 460)).toBe(260)
    expect(keyWidth(320, 'Home', false, 'left', 260, 460)).toBe(260)
    expect(keyWidth(320, 'End', false, 'left', 260, 460)).toBe(460)
    expect(keyWidth(450, 'ArrowLeft', true, 'left', 260, 460)).toBe(460)
    expect(keyWidth(320, 'a', false, 'left', 260, 460)).toBeNull()
  })

  it('misure dei token', () => {
    expect(pxOf('320px', 1)).toBe(320)
    expect(pxOf(' 72.5px ', 1)).toBe(72.5)
    expect(pxOf('2rem', 7)).toBe(7)
    expect(pxOf('', 7)).toBe(7)
  })
})

describe('classi di larghezza dell\'area dei contenuti', () => {
  it('soglie 720, 1100, 1440 px', () => {
    expect(layoutClass(0)).toBe('stretta')
    expect(layoutClass(Number.NaN)).toBe('stretta')
    expect(layoutClass(719)).toBe('stretta')
    expect(layoutClass(LAYOUT_STEPS.media)).toBe('media')
    expect(layoutClass(1099.5)).toBe('media')
    expect(layoutClass(1100)).toBe('larga')
    expect(layoutClass(1439)).toBe('larga')
    expect(layoutClass(1440)).toBe('molto')
    expect(layoutClass(2240)).toBe('molto')
  })
  it('schermi tipici (area = finestra meno barra e margini)', () => {
    expect(layoutClass(900 - 144)).toBe('media') // barra stretta
    expect(layoutClass(1280 - 320)).toBe('media')
    expect(layoutClass(1536 - 320)).toBe('larga') // 1920 al 125%
    expect(layoutClass(1920 - 320)).toBe('molto')
  })
  it('una classe comprende quelle più strette', () => {
    expect(atLeast('molto', 'larga')).toBe(true)
    expect(atLeast('larga', 'larga')).toBe(true)
    expect(atLeast('media', 'larga')).toBe(false)
    expect(atLeast('stretta', 'media')).toBe(false)
  })
})
