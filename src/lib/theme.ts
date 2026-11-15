/** Tema scelto: automatico (come il sistema), chiaro o scuro. Logica pura, testata. */
export type ThemePref = 'auto' | 'light' | 'dark'
export type Theme = 'light' | 'dark'

export const THEME_KEY = 'statera.tema'

export function parseThemePref(v: string | null | undefined): ThemePref {
  return v === 'light' || v === 'dark' ? v : 'auto'
}

export function resolveTheme(pref: ThemePref, systemDark: boolean): Theme {
  return pref === 'auto' ? (systemDark ? 'dark' : 'light') : pref
}

/** Palette di colori (Altro → Aspetto → Colori). Ognuna ha valori chiari e scuri in tokens.css. */
export const PALETTES = [
  { id: 'indaco', name: 'Indaco morbido' },
  { id: 'zafferano', name: 'Blu, oliva e zafferano' },
  { id: 'petrolio', name: 'Petrolio' },
  { id: 'ciclamino', name: 'Ciclamino' },
  { id: 'ottone', name: 'Ardesia e ottone' },
  { id: 'lime', name: 'Notte e lime' },
] as const

export type PaletteId = (typeof PALETTES)[number]['id']
export const DEFAULT_PALETTE: PaletteId = 'indaco'
export const PALETTE_KEY = 'statera.colori'

export function parsePalette(v: string | null | undefined): PaletteId {
  return PALETTES.some((p) => p.id === v) ? (v as PaletteId) : DEFAULT_PALETTE
}
