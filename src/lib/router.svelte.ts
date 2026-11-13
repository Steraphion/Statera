/**
 * Navigazione minima basata sull'hash dell'indirizzo (#/movimenti, #/conti...).
 * Funziona offline e su GitHub Pages senza configurazioni del server.
 */

export type RouteId = 'movimenti' | 'conti' | 'analisi' | 'altro'

export const ROUTES: { id: RouteId; label: string; icon: string }[] = [
  { id: 'movimenti', label: 'Movimenti', icon: 'list' },
  { id: 'conti', label: 'Conti', icon: 'wallet' },
  { id: 'analisi', label: 'Analisi', icon: 'chart' },
  { id: 'altro', label: 'Altro', icon: 'more' },
]

const DEFAULT_ROUTE: RouteId = 'movimenti'

function parse(hash: string): RouteId {
  const id = hash.replace(/^#\/?/, '').split('/')[0]
  return ROUTES.some((r) => r.id === id) ? (id as RouteId) : DEFAULT_ROUTE
}

class Router {
  current = $state<RouteId>(parse(location.hash))

  constructor() {
    window.addEventListener('hashchange', () => {
      this.current = parse(location.hash)
    })
  }

  go(id: RouteId) {
    location.hash = `/${id}`
  }
}

export const router = new Router()
