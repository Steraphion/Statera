import type { Action } from 'svelte/action'
import { applyKey, type Key, type KeypadMode } from './keypad'

/*
 * Tastierino degli importi su telefono: al posto della tastiera del sistema compare il componente
 * Keypad (dentro il pannello aperto, o in fondo alla pagina). Su PC e con il mouse i campi restano normali.
 * Si attiva su un campo con `use:amountKeys` (decimali) o `use:amountKeys={'integer'}` (numero di buoni).
 */
export const HAS_KEYPAD =
  typeof matchMedia === 'function' && matchMedia('(pointer: coarse) and (hover: none)').matches

class KeypadState {
  target = $state<HTMLInputElement | null>(null)
  mode = $state<KeypadMode>('decimal')

  press(key: Key) {
    const t = this.target
    if (!t) return
    const len = t.value.length
    const r = applyKey(t.value, t.selectionStart ?? len, t.selectionEnd ?? len, key, this.mode)
    if (r.value !== t.value) {
      t.value = r.value
      // Come se l'utente avesse scritto: aggiorna i valori collegati con bind:value
      t.dispatchEvent(new Event('input', { bubbles: true }))
    }
    try {
      t.setSelectionRange(r.caret, r.caret)
    } catch {
      // alcuni tipi di campo non hanno il cursore
    }
  }

  /** "Fatto": chiude il tastierino e lascia il campo. */
  done() {
    const t = this.target
    this.target = null
    t?.blur()
  }
}

export const keypad = new KeypadState()

/*
 * Toccando fuori dal campo, il campo perde il focus a metà del tocco (prima del "click"). Se il
 * tastierino sparisse subito, il pannello cambierebbe forma sotto il dito e il tocco andrebbe a vuoto
 * o su un'altra voce: quindi si chiude dopo il click che segue, o comunque entro poco.
 */
function afterTap(fn: () => void) {
  let done = false
  const run = () => {
    if (done) return
    done = true
    document.removeEventListener('click', onClick, true)
    clearTimeout(timer)
    fn()
  }
  const onClick = () => setTimeout(run, 0)
  document.addEventListener('click', onClick, true)
  const timer = setTimeout(run, 400)
}

export const amountKeys: Action<HTMLInputElement, KeypadMode | undefined> = (node, initial) => {
  if (!HAS_KEYPAD) return
  let mode: KeypadMode = initial ?? 'decimal'
  node.inputMode = 'none'
  node.setAttribute('data-keypad', mode)

  // Focus e blur possono arrivare mentre Svelte aggiorna la pagina (es. un campo che sparisce):
  // lo stato del tastierino si cambia subito dopo, mai durante l'aggiornamento.
  function open() {
    queueMicrotask(() => {
      if (document.activeElement !== node || !node.isConnected) return
      keypad.mode = mode
      keypad.target = node
    })
    requestAnimationFrame(() => node.scrollIntoView({ block: 'nearest' }))
  }
  function release() {
    afterTap(() => {
      if (keypad.target === node && document.activeElement !== node) keypad.target = null
    })
  }
  function onFocus() {
    open()
    // Come in una calcolatrice: il contenuto è selezionato, la prima cifra lo sostituisce.
    // Dopo il tocco (che sposta il cursore), quindi al fotogramma successivo.
    requestAnimationFrame(() => {
      if (document.activeElement === node) node.select()
    })
  }
  function onClick() {
    if (document.activeElement === node && keypad.target !== node) open()
  }
  function onBlur(e: FocusEvent) {
    const to = e.relatedTarget as Element | null
    if (to?.closest('.keypad')) return
    release()
  }

  node.addEventListener('focus', onFocus)
  node.addEventListener('click', onClick)
  node.addEventListener('blur', onBlur)
  if (document.activeElement === node) onFocus()

  return {
    update(m) {
      mode = m ?? 'decimal'
      node.setAttribute('data-keypad', mode)
      if (keypad.target === node) queueMicrotask(() => (keypad.mode = mode))
    },
    destroy() {
      node.removeEventListener('focus', onFocus)
      node.removeEventListener('click', onClick)
      node.removeEventListener('blur', onBlur)
      release()
    },
  }
}
