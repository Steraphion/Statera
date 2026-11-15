/**
 * Navigazione minima basata sull'hash dell'indirizzo (#/movimenti, #/conto/<id>...).
 * Funziona offline e su GitHub Pages senza configurazioni del server.
 */

import type { IconName } from './icons'

export type NavId = 'movimenti' | 'conti' | 'analisi' | 'altro'
export type RouteId = NavId | 'categorie' | 'conto' | 'cerca' | 'ricorrenti'

export const ROUTES: { id: NavId; label: string; icon: IconName }[] = [
  { id: 'movimenti', label: 'Movimenti', icon: 'list' },
  { id: 'conti', label: 'Conti', icon: 'wallet' },
  { id: 'analisi', label: 'Analisi', icon: 'chart-column' },
  { id: 'altro', label: 'Altro', icon: 'ellipsis' },
]

/** Schermate secondarie e la voce di menu a cui appartengono. */
const SUBROUTES: Record<string, NavId> = { categorie: 'altro', conto: 'conti', cerca: 'movimenti', ricorrenti: 'altro' }

const DEFAULT_ROUTE: RouteId = 'movimenti'

/** Su PC sono una schermata sola: elenco dei conti e dettaglio del conto scelto. */
const PANE_ROUTES = new Set<RouteId>(['conti', 'conto'])

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
      const before = this.#route.id
      this.#route = parse(location.hash)
      // Su PC, passando da un conto all'altro accanto all'elenco, la pagina resta dov'era
      const sameScreen = PANE_ROUTES.has(before) && PANE_ROUTES.has(this.#route.id) && matchMedia('(min-width: 900px)').matches
      if (!sameScreen) window.scrollTo(0, 0)
    })
  }

  go(id: RouteId, param?: string) {
    location.hash = param ? `/${id}/${encodeURIComponent(param)}` : `/${id}`
  }
}

export const router = new Router()
