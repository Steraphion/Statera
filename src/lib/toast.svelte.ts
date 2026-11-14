/** Avviso breve in basso (es. "Caffè registrato · Annulla"). Uno alla volta. */
interface ToastState {
  id: number
  text: string
  action?: { label: string; run: () => unknown }
}

class Toasts {
  current = $state<ToastState | null>(null)
  #timer: ReturnType<typeof setTimeout> | undefined
  #n = 0

  show(text: string, action?: ToastState['action'], ms = 6000) {
    clearTimeout(this.#timer)
    const id = ++this.#n
    this.current = { id, text, action }
    this.#timer = setTimeout(() => {
      if (this.current?.id === id) this.current = null
    }, ms)
  }

  close() {
    clearTimeout(this.#timer)
    this.current = null
  }
}

export const toast = new Toasts()
