/** Comparsa delle schermate: parte pura (testata). Lo stato è in screen.svelte.ts. */
import type { RouteId } from './router.svelte'

/** Attesa massima prima di mostrare comunque la schermata (millisecondi). */
export const MAX_WAIT = 500

/** fade: tra le sezioni; forward: verso una schermata secondaria; back: ritorno alla sezione. */
export type RevealKind = 'fade' | 'forward' | 'back'

const SECTIONS: RouteId[] = ['movimenti', 'conti', 'analisi', 'altro']

export function revealKind(from: RouteId | null, to: RouteId, sameScreenNewParam = false): RevealKind {
  if (from === null) return 'fade'
  const fromSub = !SECTIONS.includes(from)
  const toSub = !SECTIONS.includes(to)
  if (toSub && (!fromSub || sameScreenNewParam || from !== to)) return 'forward'
  if (fromSub && !toSub) return 'back'
  return 'fade'
}
