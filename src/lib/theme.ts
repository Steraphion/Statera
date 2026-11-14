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
