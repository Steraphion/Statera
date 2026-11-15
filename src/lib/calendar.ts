/*
 * Calendario della scelta della data (pannello dell'app al posto di quello del telefono).
 * Logica pura, testata: date come testo 'AAAA-MM-GG', settimana da lunedì, nomi italiani.
 */
export const WEEKDAYS = ['L', 'M', 'M', 'G', 'V', 'S', 'D'] as const
export const WEEKDAY_NAMES = ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì', 'sabato', 'domenica'] as const
export const MONTHS = [
  'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
  'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre',
] as const

export interface YM {
  year: number
  /** 0 = gennaio */
  month: number
}

const pad = (n: number) => String(n).padStart(2, '0')

export function iso(year: number, month: number, day: number): string {
  return `${year}-${pad(month + 1)}-${pad(day)}`
}

/** Mese di una data 'AAAA-MM-GG' (o null se non valida). */
export function ymOf(date: string | null | undefined): YM | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date ?? '')
  if (!m) return null
  const month = Number(m[2]) - 1
  if (month < 0 || month > 11) return null
  return { year: Number(m[1]), month }
}

export function addMonths(ym: YM, n: number): YM {
  const t = ym.year * 12 + ym.month + n
  return { year: Math.floor(t / 12), month: ((t % 12) + 12) % 12 }
}

export function daysInMonth(ym: YM): number {
  return new Date(ym.year, ym.month + 1, 0).getDate()
}

/** Celle del mese, settimane da lunedì: null per i giorni vuoti prima del primo del mese. */
export function monthCells(ym: YM): (string | null)[] {
  const first = (new Date(ym.year, ym.month, 1).getDay() + 6) % 7
  const cells: (string | null)[] = Array(first).fill(null)
  for (let d = 1; d <= daysInMonth(ym); d++) cells.push(iso(ym.year, ym.month, d))
  return cells
}

/** La data è dentro i limiti del campo (min e max facoltativi, come negli attributi HTML). */
export function inRange(date: string, min?: string | null, max?: string | null): boolean {
  return (!min || date >= min) && (!max || date <= max)
}

/** Il mese ha almeno un giorno sceglibile. */
export function monthInRange(ym: YM, min?: string | null, max?: string | null): boolean {
  return inRange(iso(ym.year, ym.month, daysInMonth(ym)), min, null) && inRange(iso(ym.year, ym.month, 1), null, max)
}

/** "novembre 2026" */
export function monthLabel(ym: YM): string {
  return `${MONTHS[ym.month]} ${ym.year}`
}

/** "domenica 15 novembre 2026", per gli screen reader e il titolo del pannello. */
export function longDate(date: string): string {
  const ym = ymOf(date)
  if (!ym) return ''
  const day = Number(date.slice(8, 10))
  const wd = (new Date(ym.year, ym.month, day).getDay() + 6) % 7
  return `${WEEKDAY_NAMES[wd]} ${day} ${MONTHS[ym.month]} ${ym.year}`
}
