/**
 * Movimento (design system: Movimento). Le animazioni stanno nei fogli di stile, scritte coi token
 * (`--duration-*`, `--ease-*`): così valgono la CSP (niente stili inline) e la regola di base.css che,
 * con «riduci animazioni», porta durate e animazioni a 0,01 ms.
 *
 * Qui c'è solo ciò che serve a Svelte per le uscite: un elemento che sta per sparire riceve
 * `data-leaving` (il suo CSS avvia l'animazione d'uscita) e resta nella pagina per la durata del token.
 * Le transizioni di Svelte non passano dalla regola di base.css, quindi la durata si azzera qui
 * quando il sistema chiede di ridurre le animazioni.
 *
 * Uso: `<div in:enter out:leave>` oppure `out:leave={{ duration: '--duration-slow' }}`.
 *
 * Righe degli elenchi: si aprono e si chiudono solo quelle che l'utente ha appena salvato, eliminato o
 * ripristinato (`markChanged(id)`), con `in:enterIf={id} out:leaveIf={id}` e la classe `.fold` di
 * base.css. Così un elenco che cambia mese, o che si riempie all'apertura, non si anima.
 */

export type DurationToken = '--duration-fast' | '--duration-base' | '--duration-slow'

/** "280ms" → 280, "0.2s" → 200; qualunque altro valore → 0. */
export function parseDuration(value: string): number {
  const m = /^\s*(-?\d*\.?\d+)\s*(ms|s)\s*$/i.exec(value)
  if (!m) return 0
  const n = Number(m[1]) * (m[2].toLowerCase() === 's' ? 1000 : 1)
  return Number.isFinite(n) && n > 0 ? n : 0
}

/** Durata da usare per un'uscita: quella del token, o nessuna con «riduci animazioni». */
export function exitDuration(tokenValue: string, reduced: boolean): number {
  return reduced ? 0 : parseDuration(tokenValue)
}

export function prefersReducedMotion(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** Durata in millisecondi di un token, letta dal foglio di stile attivo. */
export function tokenDuration(name: DurationToken, el: Element = document.documentElement): number {
  return exitDuration(getComputedStyle(el).getPropertyValue(name), prefersReducedMotion())
}

/** Entrata: l'animazione è nel CSS dell'elemento; qui si annulla un'uscita interrotta (riapertura). */
export function enter(node: Element) {
  node.removeAttribute('data-leaving')
  return { duration: 0 }
}

const armed = new WeakSet<Element>()

/** Uscita: avvia l'animazione `[data-leaving]` del CSS e tiene l'elemento per la durata del token. */
export function leave(node: Element, { duration = '--duration-base' }: { duration?: DurationToken } = {}) {
  node.setAttribute('data-leaving', '')
  // Svelte chiama leave() solo alla prima uscita: se l'elemento torna prima di sparire (enter toglie
  // data-leaving) e poi esce di nuovo, riusa la stessa durata senza richiamarla. L'evento outrostart
  // arriva a ogni uscita e rimette l'attributo.
  if (!armed.has(node)) {
    armed.add(node)
    node.addEventListener('outrostart', () => node.setAttribute('data-leaving', ''))
  }
  return { duration: tokenDuration(duration, node) }
}

// ---------- Righe appena cambiate ----------

/** Per quanto tempo una modifica fatta dall'utente fa animare la sua riga (millisecondi). */
export const RECENT_MS = 2000

const recent = new Map<string, number>()

/** Da chiamare appena prima di salvare, eliminare o ripristinare un movimento dall'interfaccia. */
export function markChanged(id: string, now = Date.now()) {
  recent.set(id, now)
}

/**
 * Vero se uno degli id è stato cambiato da poco; l'id viene consumato, così la stessa modifica
 * anima una riga una volta sola (non di nuovo cambiando mese e tornando).
 */
export function takeChanged(ids: string | readonly string[], now = Date.now()): boolean {
  let hit = false
  for (const id of typeof ids === 'string' ? [ids] : ids) {
    const at = recent.get(id)
    if (at === undefined) continue
    recent.delete(id)
    if (now - at < RECENT_MS) hit = true
  }
  return hit
}

/** Entrata di una riga appena salvata o ripristinata: `data-entering` avvia l'animazione `.fold`. */
export function enterIf(node: Element, ids: string | readonly string[]) {
  node.removeAttribute('data-leaving')
  if (takeChanged(ids)) {
    node.setAttribute('data-entering', '')
    node.addEventListener('animationend', () => node.removeAttribute('data-entering'), { once: true })
  }
  return { duration: 0 }
}

/** Uscita di una riga appena eliminata; le altre spariscono subito (es. cambiando mese). */
export function leaveIf(node: Element, ids: string | readonly string[]) {
  if (!takeChanged(ids)) return { duration: 0 }
  node.removeAttribute('data-entering')
  return leave(node)
}
