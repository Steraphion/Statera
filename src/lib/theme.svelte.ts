import {
  DEFAULT_PALETTE,
  PALETTE_KEY,
  parsePalette,
  parseThemePref,
  resolveTheme,
  THEME_KEY,
  type PaletteId,
  type Theme,
  type ThemePref,
} from './theme'

/*
 * Tema e palette dell'app. Le scelte valgono per il dispositivo (tutti i profili) e stanno in
 * localStorage, così public/tema.js le applica prima che la pagina compaia. Sono negli attributi
 * data-theme e data-palette di <html>: tokens.css cambia i colori con :root[data-theme='dark'] e
 * [data-palette='…'].
 */
function read(): ThemePref {
  try {
    return parseThemePref(localStorage.getItem(THEME_KEY))
  } catch {
    return 'auto'
  }
}

function readPalette(): PaletteId {
  try {
    return parsePalette(localStorage.getItem(PALETTE_KEY))
  } catch {
    return DEFAULT_PALETTE
  }
}

const media = typeof matchMedia === 'function' ? matchMedia('(prefers-color-scheme: dark)') : null

class ThemeState {
  pref = $state<ThemePref>(read())
  current = $state<Theme>('light')
  palette = $state<PaletteId>(readPalette())

  start() {
    this.apply()
    media?.addEventListener('change', () => this.apply())
  }

  set(pref: ThemePref) {
    this.pref = pref
    try {
      if (pref === 'auto') localStorage.removeItem(THEME_KEY)
      else localStorage.setItem(THEME_KEY, pref)
    } catch {
      // Archiviazione non disponibile: la scelta vale fino alla chiusura
    }
    this.apply()
  }

  setPalette(id: PaletteId) {
    this.palette = id
    try {
      if (id === DEFAULT_PALETTE) localStorage.removeItem(PALETTE_KEY)
      else localStorage.setItem(PALETTE_KEY, id)
    } catch {
      // Archiviazione non disponibile: la scelta vale fino alla chiusura
    }
    this.apply()
  }

  private apply() {
    this.current = resolveTheme(this.pref, media?.matches ?? false)
    const root = document.documentElement
    root.dataset.theme = this.current
    root.dataset.palette = this.palette
    // Colore della barra di sistema uguale allo sfondo del tema scelto
    const bg = getComputedStyle(root).getPropertyValue('--color-bg').trim()
    if (bg) for (const m of document.querySelectorAll('meta[name="theme-color"]')) m.setAttribute('content', bg)
  }
}

export const theme = new ThemeState()
