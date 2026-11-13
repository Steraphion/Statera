/**
 * Navigazione minima basata sull'hash dell'indirizzo (#/movimenti, #/conti...).
 * Funziona offline e su GitHub Pages senza configurazioni del server.
 */

export type NavId = 'movimenti' | 'conti' | 'analisi' | 'altro'
export type RouteId = NavId | 'categorie'

export const ROUTES: { id: NavId; label: string; icon: string }[] = [
  { id: 'movimenti', label: 'Movimenti', icon: 'list' },
  { id: 'conti', label: 'Conti', icon: 'wallet' },
  { id: 'analisi', label: 'Analisi', icon: 'chart' },
  { id: 'altro', label: 'Altro', icon: 'more' },
]

/** Schermate secondarie e la voce di menu a cui appartengono. */
const SUBROUTES: Record<string, NavId> = { categorie: 'altro' }

const DEFAULT_ROUTE: RouteId = 'movimenti'

function parse(hash: string): RouteId {
  const id = hash.replace(/^#\/?/, '').split('/')[0]
  if (ROUTES.some((r) => r.id === id) || id in SUBROUTES) return id as RouteId
  return DEFAULT_ROUTE
}

class Router {
  current = $state<RouteId>(parse(location.hash))
  /** Voce del menu da evidenziare. */
  section = $derived<NavId>(SUBROUTES[this.current] ?? (this.current as NavId))

  constructor() {
    window.addEventListener('hashchange', () => {
      this.current = parse(location.hash)
      window.scrollTo(0, 0)
    })
  }

  go(id: RouteId) {
    location.hash = `/${id}`
  }
}

export const router = new Router()
