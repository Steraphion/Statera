import { liveQuery } from 'dexie'
import { screen } from '../screen.svelte'

/**
 * Collega una lettura dal database a uno stato reattivo:
 * quando i dati cambiano (anche da un'altra scheda), lo schermo si aggiorna da solo.
 * Va chiamata durante l'inizializzazione di un componente.
 */
export function live<T>(query: () => Promise<T>, initial: T): { readonly value: T; readonly ready: boolean } {
  const state = $state({ value: initial, ready: false })

  $effect(() => {
    // Una schermata appena aperta aspetta questa lettura prima di comparire (src/lib/screen.svelte.ts)
    const loaded = screen.track()
    const sub = liveQuery(query).subscribe({
      next: (v) => {
        state.value = v
        state.ready = true
        loaded()
      },
      error: (e) => {
        loaded()
        console.error('Errore di lettura dati', e)
      },
    })
    return () => sub.unsubscribe()
  })

  return state
}
