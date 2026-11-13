/**
 * Navigazione minima basata sull'hash dell'indirizzo (#/movimenti, #/conto/<id>...).
 * Funziona offline e su GitHub Pages senza configurazioni del server.
 */

export type NavId = 'movimenti' | 'conti' | 'analisi' | 'altro'
export type RouteId = NavId | 'categorie' | 'conto' | 'cerca'

export const ROUTES: { id: NavId; label: string; icon: string }[] = [
  { id: 'movimenti', label: 'Movimenti', icon: 'list' },
  { id: 'conti', label: 'Conti', icon: 'wallet' },
  { id: 'analisi', label: 'Analisi', icon: 'chart' },
  { id: 'altro', label: 'Altro', icon: 'more' },
]

/** Schermate secondarie e la voce di menu a cui appartengono. */
const SUBROUTES: Record<string, NavId> = { categorie: 'altro', conto: 'conti', cerca: 'movimenti' }

const DEFAULT_ROUTE: RouteId = 'movimenti'

function parse(hash: string): { id: RouteId; param: string } {
  const [id = '', param = ''] = hash.replace(/^#\/?/, '').split('/')
  if (ROUTES.some((r) => r.id === id) || id in SUBROUTES) {
    return { id: id as RouteId, param: decodeURIComponent(param) }
  }
  return { id: DEFAULT_ROUTE, param: '' }
}

class Router {
  #route = $state(parse(location.hash))
  current = $derived(this.#route.id)
  /** Parametro della schermata (es. l'id del conto). */
  param = $derived(this.#route.param)
  /** Voce del menu da evidenziare. */
  section = $derived<NavId>(SUBROUTES[this.#route.id] ?? (this.#route.id as NavId))

  constructor() {
    window.addEventListener('hashchange', () => {
      this.#route = parse(location.hash)
      window.scrollTo(0, 0)
    })
  }

  go(id: RouteId, param?: string) {
    location.hash = param ? `/${id}/${encodeURIComponent(param)}` : `/${id}`
  }
}

export const router = new Router()
