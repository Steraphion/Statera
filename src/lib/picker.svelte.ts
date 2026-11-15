import type { Action } from 'svelte/action'
import { HAS_KEYPAD } from './keypad.svelte'

/*
 * Scelte del telefono nello stile dell'app: su telefono gli elenchi a tendina (<select>) e le date
 * (<input type="date">) non aprono il pannello di Android ma PickerSheet (in App.svelte). Il campo
 * vero resta al suo posto e riceve il valore scelto con gli eventi input e change, quindi bind:value,
 * onchange e i collaudi continuano a funzionare. Su PC e con il mouse nulla cambia.
 * Si attiva con `use:picker` sul <select> o sull'<input type="date">.
 */
export type PickerField = HTMLSelectElement | HTMLInputElement

class PickerState {
  field = $state<PickerField | null>(null)
  title = $state('')

  open(el: PickerField) {
    if (this.field || el.disabled) return
    this.title = fieldLabel(el)
    this.field = el
  }

  close() {
    this.field = null
  }

  /** Scrive il valore nel campo vero, come se l'utente l'avesse scelto lì. */
  choose(value: string) {
    const el = this.field
    this.field = null
    if (!el || el.value === value) return
    el.value = value
    el.dispatchEvent(new Event('input', { bubbles: true }))
    el.dispatchEvent(new Event('change', { bubbles: true }))
  }
}

export const picker = new PickerState()

/** Nome del campo per il titolo del pannello: aria-label, oppure il testo della sua etichetta. */
export function fieldLabel(el: PickerField): string {
  const aria = el.getAttribute('aria-label')
  if (aria) return aria
  const label = el.labels?.[0]
  if (label) {
    const copy = label.cloneNode(true) as HTMLElement
    copy.querySelectorAll('select, input, option, .hint, small').forEach((n) => n.remove())
    const text = copy.textContent?.replace(/\s+/g, ' ').trim()
    if (text) return text
  }
  return el instanceof HTMLSelectElement ? 'Scegli' : 'Data'
}

/** Spostamento oltre il quale un tocco è uno scorrimento della pagina, non una scelta. */
const MOVE = 10

export const pickerAction: Action<PickerField> = (node) => {
  if (!HAS_KEYPAD) return
  node.setAttribute('data-picker', '')
  const host: HTMLElement = node
  let x = 0
  let y = 0
  let moved = false

  const onTouchStart = (e: TouchEvent) => {
    x = e.touches[0].clientX
    y = e.touches[0].clientY
    moved = false
  }
  const onTouchMove = (e: TouchEvent) => {
    const t = e.touches[0]
    if (Math.hypot(t.clientX - x, t.clientY - y) > MOVE) moved = true
  }
  // Annullando la fine del tocco Android non apre il suo pannello (né il clic che lo aprirebbe)
  const onTouchEnd = (e: TouchEvent) => {
    if (moved || !e.cancelable) return
    e.preventDefault()
    picker.open(node)
  }
  // Mouse o penna su un telefono, e i collaudi: niente pannello del sistema, si apre il nostro al clic
  const onMouseDown = (e: MouseEvent) => e.preventDefault()
  const onClick = (e: MouseEvent) => {
    e.preventDefault()
    picker.open(node)
  }
  // Tastiera collegata al telefono o lettore di schermo: Invio, spazio, Alt+↓ aprono la scelta
  const onKey = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ' || (e.altKey && e.key === 'ArrowDown') || e.key === 'F4') {
      e.preventDefault()
      picker.open(node)
    }
  }

  host.addEventListener('touchstart', onTouchStart, { passive: true })
  host.addEventListener('touchmove', onTouchMove, { passive: true })
  host.addEventListener('touchend', onTouchEnd, { passive: false })
  host.addEventListener('mousedown', onMouseDown)
  host.addEventListener('click', onClick)
  host.addEventListener('keydown', onKey)
  return {
    destroy() {
      host.removeEventListener('touchstart', onTouchStart)
      host.removeEventListener('touchmove', onTouchMove)
      host.removeEventListener('touchend', onTouchEnd)
      host.removeEventListener('mousedown', onMouseDown)
      host.removeEventListener('click', onClick)
      host.removeEventListener('keydown', onKey)
      if (picker.field === node) picker.close()
    },
  }
}
