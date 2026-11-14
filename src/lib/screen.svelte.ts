/**
 * Comparsa delle schermate (design system: Movimento).
 *
 * Una schermata nuova resta invisibile finché le sue letture iniziali dal database non sono pronte
 * (ogni `live()` e ogni lettura registrata con `screen.track()`), poi compare tutta insieme con la sua
 * animazione. Così non si vedono più gli importi a zero, i valori che arrivano a pezzi e i riquadri
 * che spingono giù il resto. Se una lettura tarda, la schermata compare comunque dopo `MAX_WAIT`.
 *
 * Il CSS è in App.svelte (`.screen[data-reveal]`); con «riduci animazioni» la comparsa è immediata.
 */

import { MAX_WAIT, type RevealKind } from './screen'

export { revealKind } from './screen'

class Screen {
  /** false mentre la schermata aspetta i suoi dati. */
  shown = $state(true)
  kind = $state<RevealKind>('fade')
  #pending = 0
  #round = 0
  #timer: ReturnType<typeof setTimeout> | undefined

  /** Nuova schermata: si nasconde finché le letture iniziali non sono pronte. */
  start(kind: RevealKind) {
    this.kind = kind
    this.shown = false
    this.#pending = 0 // le letture di una schermata lasciata a metà non contano più
    const round = ++this.#round
    clearTimeout(this.#timer)
    this.#timer = setTimeout(() => this.#show(round), MAX_WAIT)
    this.#check(round)
  }

  /** Registra una lettura iniziale; la funzione restituita va chiamata alla prima risposta. */
  track(): () => void {
    if (this.shown) return () => {}
    this.#pending++
    const round = this.#round
    let done = false
    return () => {
      if (done || round !== this.#round) return
      done = true
      this.#pending--
      this.#check(round)
    }
  }

  // Si aspetta un fotogramma: nel frattempo i componenti appena comparsi (es. la guida, che dipende
  // dai conti) possono avviare le loro letture.
  #check(round: number) {
    if (this.#pending > 0 || this.shown) return
    requestAnimationFrame(() => {
      if (this.#pending === 0) this.#show(round)
    })
  }

  #show(round: number) {
    if (round !== this.#round || this.shown) return
    clearTimeout(this.#timer)
    this.#pending = 0
    this.shown = true
  }
}

export const screen = new Screen()
