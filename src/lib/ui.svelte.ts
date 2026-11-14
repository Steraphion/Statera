import { today } from './data/util'
import { EMPTY_FILTERS, type Filters } from './data/transactions'
import { monthOf } from './format'

/** Stato dell'interfaccia che deve sopravvivere al cambio di schermata. */
class UiState {
  /** Mese mostrato in Movimenti, 'AAAA-MM'. */
  month = $state(monthOf(today()))
  /** Periodo mostrato in Analisi. */
  analysis = $state<{ kind: 'mese' | 'anno'; month: string }>({ kind: 'mese', month: monthOf(today()) })
  /** Movimenti come elenco o come calendario del mese. */
  view = $state<'elenco' | 'calendario'>('elenco')
  /** Ricerca in corso. */
  filters = $state<Filters>({ ...EMPTY_FILTERS })
}

export const ui = new UiState()
