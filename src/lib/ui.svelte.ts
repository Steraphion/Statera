import { today } from './data/util'
import { monthOf } from './format'

/** Stato dell'interfaccia che deve sopravvivere al cambio di schermata. */
class UiState {
  /** Mese mostrato in Movimenti, 'AAAA-MM'. */
  month = $state(monthOf(today()))
}

export const ui = new UiState()
