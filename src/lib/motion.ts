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

/** Uscita: avvia l'animazione `[data-leaving]` del CSS e tiene l'elemento per la durata del token. */
export function leave(node: Element, { duration = '--duration-base' }: { duration?: DurationToken } = {}) {
  node.setAttribute('data-leaving', '')
  return { duration: tokenDuration(duration, node) }
}
