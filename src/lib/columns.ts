/**
 * Colonne regolabili su PC (logica pura, testata): larghezze scelte trascinando un separatore o con la
 * tastiera, salvate per dispositivo in localStorage come il tema. Nessun dato sincronizzato.
 */

export const COLUMNS_KEY = 'statera.colonne'

/** Colonne regolabili: colonna di destra di Movimenti, elenco dei conti accanto al dettaglio. */
export type ColumnId = 'aside' | 'pane'
/** Barra laterale: intera (da 1200 px) o sempre stretta, solo icone. */
export type SidePref = 'intera' | 'stretta'

export interface ColumnPrefs {
  /** Larghezza scelta in px, `null` = quella iniziale del token. */
  widths: Record<ColumnId, number | null>
  side: SidePref
}

export const DEFAULT_PREFS: ColumnPrefs = { widths: { aside: null, pane: null }, side: 'intera' }

/** Passo della tastiera: frecce 16 px, con Maiuscole 64 px. */
export const STEP = 16
export const STEP_LARGE = 64

/** Larghezze fuori da questi limiti non sono state salvate da noi: si ignorano. */
const SANE_MIN = 100
const SANE_MAX = 2000

function sane(v: unknown): number | null {
  return typeof v === 'number' && Number.isFinite(v) && v >= SANE_MIN && v <= SANE_MAX ? Math.round(v) : null
}

/** Legge le preferenze salvate; qualunque valore strano torna a quello iniziale. */
export function parseColumnPrefs(raw: string | null | undefined): ColumnPrefs {
  let o: unknown
  try {
    o = raw ? JSON.parse(raw) : null
  } catch {
    o = null
  }
  const v = (o && typeof o === 'object' ? o : {}) as Record<string, unknown>
  const w = (v.widths && typeof v.widths === 'object' ? v.widths : {}) as Record<string, unknown>
  return {
    widths: { aside: sane(w.aside), pane: sane(w.pane) },
    side: v.side === 'stretta' ? 'stretta' : 'intera',
  }
}

export function serializeColumnPrefs(p: ColumnPrefs): string {
  return JSON.stringify(p)
}

/** Limiti effettivi: il massimo scende se la colonna principale resterebbe troppo stretta. */
export function limits(min: number, max: number, available?: number): { min: number; max: number } {
  const hi = available === undefined ? max : Math.min(max, Math.floor(available))
  return { min, max: Math.max(min, hi) }
}

export function clamp(w: number, min: number, max: number): number {
  return Math.round(Math.min(max, Math.max(min, w)))
}

/**
 * Nuova larghezza mentre si trascina. `grows` dice da che parte si allarga la colonna: 'left' se
 * la colonna sta a destra del separatore (trascinando a sinistra si allarga), 'right' se sta a sinistra.
 */
export function dragWidth(start: number, startX: number, x: number, grows: 'left' | 'right', min: number, max: number) {
  const delta = grows === 'left' ? startX - x : x - startX
  return clamp(start + delta, min, max)
}

/**
 * Tasti del separatore (come un cursore ARIA): le frecce lo spostano nella direzione indicata, quindi
 * allargano o stringono la colonna secondo da che parte sta; Pagina su/giù fanno passi grandi; Inizio e
 * Fine portano al minimo e al massimo. Restituisce `null` per i tasti che non lo riguardano.
 */
export function keyWidth(
  current: number,
  key: string,
  shift: boolean,
  grows: 'left' | 'right',
  min: number,
  max: number,
): number | null {
  const step = shift ? STEP_LARGE : STEP
  const dir = grows === 'left' ? -1 : 1
  switch (key) {
    case 'ArrowRight':
      return clamp(current + dir * step, min, max)
    case 'ArrowLeft':
      return clamp(current - dir * step, min, max)
    case 'PageUp':
      return clamp(current + STEP_LARGE, min, max)
    case 'PageDown':
      return clamp(current - STEP_LARGE, min, max)
    case 'Home':
      return min
    case 'End':
      return max
    default:
      return null
  }
}

/** Valore di un token di misura (es. "320px") in px; `fallback` se manca o non è in px. */
export function pxOf(value: string | null | undefined, fallback: number): number {
  const m = /^\s*(-?\d+(?:\.\d+)?)px\s*$/.exec(value ?? '')
  return m ? Number(m[1]) : fallback
}
