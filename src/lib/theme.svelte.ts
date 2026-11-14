import { parseThemePref, resolveTheme, THEME_KEY, type Theme, type ThemePref } from './theme'

/*
 * Tema dell'app. La scelta vale per il dispositivo (tutti i profili) e sta in localStorage, così
 * public/tema.js la applica prima che la pagina compaia. Il tema effettivo è nell'attributo
 * data-theme di <html>: tokens.css cambia i colori con :root[data-theme='dark'].
 */
function read(): ThemePref {
  try {
    return parseThemePref(localStorage.getItem(THEME_KEY))
  } catch {
    return 'auto'
  }
}

const media = typeof matchMedia === 'function' ? matchMedia('(prefers-color-scheme: dark)') : null

class ThemeState {
  pref = $state<ThemePref>(read())
  current = $state<Theme>('light')

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

  private apply() {
    this.current = resolveTheme(this.pref, media?.matches ?? false)
    const root = document.documentElement
    root.dataset.theme = this.current
    // Colore della barra di sistema uguale allo sfondo del tema scelto
    const bg = getComputedStyle(root).getPropertyValue('--color-bg').trim()
    if (bg) for (const m of document.querySelectorAll('meta[name="theme-color"]')) m.setAttribute('content', bg)
  }
}

export const theme = new ThemeState()
