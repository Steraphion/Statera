/**
 * Stato delle colonne regolabili su PC (logica in columns.ts): larghezze scelte e barra laterale, per
 * dispositivo. Tiene anche le fasce di larghezza della finestra che decidono l'impaginazione.
 */
import { COLUMNS_KEY, parseColumnPrefs, serializeColumnPrefs, type ColumnId, type ColumnPrefs, type SidePref } from './columns'

function read(): ColumnPrefs {
  try {
    return parseColumnPrefs(localStorage.getItem(COLUMNS_KEY))
  } catch {
    return parseColumnPrefs(null)
  }
}

function media(q: string, set: (v: boolean) => void): boolean {
  const m = window.matchMedia(q)
  m.addEventListener('change', (e) => set(e.matches))
  return m.matches
}

class Columns {
  #prefs = $state<ColumnPrefs>(read())
  /** PC: barra laterale e colonne affiancate (da 900 px). */
  pc = $state(false)
  /** Abbastanza largo per la barra laterale intera (da 1200 px). */
  wide = $state(false)

  constructor() {
    this.pc = media('(min-width: 900px)', (v) => (this.pc = v))
    this.wide = media('(min-width: 1200px)', (v) => (this.wide = v))
    // Un'altra finestra dell'app cambia le colonne: si segue
    window.addEventListener('storage', (e) => {
      if (e.key === COLUMNS_KEY) this.#prefs = read()
    })
  }

  width(id: ColumnId): number | null {
    return this.#prefs.widths[id]
  }

  get side(): SidePref {
    return this.#prefs.side
  }

  /** Barra laterale stretta in questo momento (per scelta o perché la finestra è sotto i 1200 px). */
  get railNow(): boolean {
    return this.pc && (!this.wide || this.#prefs.side === 'stretta')
  }

  /** Cambia una larghezza; `save: false` mentre si trascina, per non scrivere a ogni movimento. */
  setWidth(id: ColumnId, w: number | null, save = true) {
    this.#prefs = { ...this.#prefs, widths: { ...this.#prefs.widths, [id]: w } }
    if (save) this.save()
  }

  setSide(side: SidePref) {
    this.#prefs = { ...this.#prefs, side }
    this.save()
  }

  save() {
    try {
      localStorage.setItem(COLUMNS_KEY, serializeColumnPrefs(this.#prefs))
    } catch {
      // Archiviazione non disponibile (navigazione privata): vale solo per questa sessione
    }
  }
}

export const columns = new Columns()
