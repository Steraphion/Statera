import { db, type StateraDB } from './db'
import { checkMovement, createMovement, type MovementInput } from './transactions'
import type { Frequency, Recurring } from './types'
import { baseFields } from './util'

/**
 * MOVIMENTI RICORRENTI
 * - Le date si calcolano dalla data di inizio: l'occorrenza n° k è inizio + k periodi.
 *   Mensile il 31 → l'ultimo giorno nei mesi più corti (il mese dopo torna al 31).
 * - Ogni occorrenza diventa un movimento con id fisso `rec-<id ripetizione>-<data>`:
 *   due dispositivi che la generano entrambi producono lo STESSO movimento, mai un doppione;
 *   se l'utente lo elimina, non viene ricreato.
 */

const pad = (n: number) => String(n).padStart(2, '0')
const fmt = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

/** Data dell'occorrenza n° k (0 = data di inizio). */
export function occurrence(r: Pick<Recurring, 'startDate' | 'frequency'>, k: number): string {
  const [y, m, d] = r.startDate.split('-').map(Number)
  if (r.frequency === 'settimanale') return fmt(new Date(y, m - 1, d + 7 * k))
  const months = r.frequency === 'mensile' ? k : 12 * k
  const target = new Date(y, m - 1 + months, 1)
  const last = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate()
  return fmt(new Date(target.getFullYear(), target.getMonth(), Math.min(d, last)))
}

/** Prossima data da gestire, o null se la ripetizione è finita. */
export function nextDate(r: Recurring): string | null {
  const date = occurrence(r, r.done)
  return r.endDate && date > r.endDate ? null : date
}

/** Occorrenze scadute (fino a oggi compreso) non ancora gestite. */
export function dueDates(r: Recurring, today: string, max = 60): string[] {
  const out: string[] = []
  if (r.deletedAt !== null || r.paused) return out
  for (let k = r.done; out.length < max; k++) {
    const date = occurrence(r, k)
    if (date > today || (r.endDate && date > r.endDate)) break
    out.push(date)
  }
  return out
}

export function movementId(r: Recurring, date: string): string {
  return `rec-${r.id}-${date}`
}

const WEEKDAY = new Intl.DateTimeFormat('it-IT', { weekday: 'long' })
const DAY_MONTH = new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'long' })

/** "Ogni mese, il giorno 27" ecc. */
export function describeFrequency(r: Pick<Recurring, 'frequency' | 'startDate'>): string {
  const [y, m, d] = r.startDate.split('-').map(Number)
  const date = new Date(y, m - 1, d)
  if (r.frequency === 'settimanale') return `Ogni settimana, di ${WEEKDAY.format(date)}`
  if (r.frequency === 'mensile') return d >= 29 ? `Ogni mese, il ${d} (o l'ultimo giorno)` : `Ogni mese, il giorno ${d}`
  return `Ogni anno, il ${DAY_MONTH.format(date)}`
}

export const FREQUENCY_LABELS: Record<Frequency, string> = {
  settimanale: 'Ogni settimana',
  mensile: 'Ogni mese',
  annuale: 'Ogni anno',
}

/** Il movimento da registrare per una certa data, a partire dal modello. */
export function toMovementInput(r: Recurring, date: string): MovementInput {
  return {
    type: r.type,
    date,
    parts: r.parts.map((p) => ({ ...p })),
    categoryId: r.categoryId,
    toAccountId: r.toAccountId,
    description: r.description,
    notes: r.notes,
  }
}

export interface Schedule {
  frequency: Frequency
  /** Data della prossima occorrenza (in creazione: la prima). */
  date: string
  endDate: string | null
  auto: boolean
}

function template(input: MovementInput) {
  return {
    type: input.type,
    parts: input.parts.map((p) => ({ source: p.source, amount: p.amount, vouchers: p.vouchers })),
    categoryId: input.type === 'trasferimento' ? null : input.categoryId,
    toAccountId: input.type === 'trasferimento' ? input.toAccountId : null,
    description: input.description.trim().slice(0, 80),
    notes: input.notes.trim().slice(0, 500),
  }
}

function checkSchedule(s: Schedule) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s.date)) throw new Error('Data non valida')
  if (s.endDate && s.endDate < s.date) throw new Error('La data di fine è precedente alla prima occorrenza')
}

/**
 * Nuovo movimento ricorrente dal modulo. Se la prima data è oggi o passata,
 * il primo movimento viene registrato subito (l'utente lo sta inserendo adesso).
 */
export async function createRecurring(
  input: MovementInput,
  s: Schedule,
  today: string,
  d: StateraDB = db,
): Promise<Recurring> {
  checkSchedule(s)
  return d.transaction('rw', [d.recurring, d.transactions, d.meta, d.accounts, d.cards, d.categories], async () => {
  const r: Recurring = {
    ...baseFields(),
    ...template(input),
    frequency: s.frequency,
    startDate: s.date,
    endDate: s.endDate,
    done: 0,
    auto: s.auto,
    paused: false,
  }
  // Il movimento deve essere valido (conti, categoria, importi…) prima di salvare il modello
  if (s.date <= today) {
    await createMovement({ ...input, date: s.date }, d, { id: movementId(r, s.date) })
    r.done = 1
  } else {
    await checkMovement({ ...input, date: s.date }, d)
  }
  await d.recurring.add(r)
  return r
  })
}

/**
 * Modifica: aggiorna il modello. Se cambiano frequenza o prossima data, la ripetizione
 * riparte da quella data. I movimenti già registrati non cambiano.
 */
export async function updateRecurring(id: string, input: MovementInput, s: Schedule, d: StateraDB = db) {
  const r = await d.recurring.get(id)
  if (!r || r.deletedAt !== null) throw new Error('Ripetizione non trovata')
  checkSchedule(s)
  await checkMovement({ ...input, date: s.date }, d)
  const scheduleChanged = r.frequency !== s.frequency || nextDate(r) !== s.date
  await d.recurring.update(id, {
    ...template(input),
    frequency: s.frequency,
    endDate: s.endDate,
    auto: s.auto,
    ...(scheduleChanged ? { startDate: s.date, done: 0 } : {}),
    updatedAt: Date.now(),
  })
}

export async function deleteRecurring(id: string, d: StateraDB = db) {
  await d.recurring.update(id, { deletedAt: Date.now(), updatedAt: Date.now() })
}

export async function setRecurringPaused(id: string, paused: boolean, d: StateraDB = db) {
  await d.recurring.update(id, { paused, updatedAt: Date.now() })
}

/** Segna come gestita l'occorrenza di quella data (registrata o saltata). */
async function markHandled(r: Recurring, date: string, d: StateraDB) {
  const fresh = await d.recurring.get(r.id)
  if (!fresh) return
  // Avanza solo se quella data è proprio la prossima: idempotente anche tra dispositivi
  let done = fresh.done
  while (occurrence(fresh, done) <= date) done++
  if (done !== fresh.done) await d.recurring.update(r.id, { done, updatedAt: Date.now() })
}

/**
 * Registra un'occorrenza da confermare (eventualmente con importo, data o altri dati modificati).
 * `occurrenceDate` è la data prevista: identifica l'occorrenza anche se la data del movimento cambia.
 */
export async function confirmOccurrence(r: Recurring, input: MovementInput, occurrenceDate: string, d: StateraDB = db) {
  await createMovement(input, d, { id: movementId(r, occurrenceDate) })
  await markHandled(r, occurrenceDate, d)
}

/**
 * Quando registrare automaticamente: subito se la sincronizzazione non è attiva;
 * se è attiva, dopo ogni sincronizzazione riuscita (così si conosce già ciò che hanno
 * fatto gli altri dispositivi), oppure comunque se non si sincronizza da più di un giorno.
 */
export function shouldProcessLocally(syncLinked: boolean, lastSyncAt: number | null, now = Date.now()): boolean {
  if (!syncLinked) return true
  return lastSyncAt === null || now - lastSyncAt > 24 * 60 * 60 * 1000
}

export async function skipOccurrence(r: Recurring, date: string, d: StateraDB = db) {
  await markHandled(r, date, d)
}

/**
 * Registra le occorrenze automatiche scadute. Restituisce quante ne ha registrate.
 * Va chiamata all'avvio (o dopo la sincronizzazione, se attiva) e quando cambia il giorno.
 */
export async function processRecurring(today: string, d: StateraDB = db): Promise<number> {
  let created = 0
  const list = (await d.recurring.toArray()).filter((r) => r.deletedAt === null && r.auto && !r.paused)
  for (const r of list) {
    for (const date of dueDates(r, today)) {
      try {
        await createMovement(toMovementInput(r, date), d, { id: movementId(r, date), remember: false })
        created++
      } catch (e) {
        // Modello non più valido (es. conto eliminato): si mette in pausa invece di bloccare tutto
        console.error('Ripetizione non valida, messa in pausa', r.id, e)
        await d.recurring.update(r.id, { paused: true, updatedAt: Date.now() })
        break
      }
      await markHandled(r, date, d)
    }
  }
  return created
}

/** Occorrenze da confermare, per l'avviso in Movimenti. */
export async function pendingConfirmations(today: string, d: StateraDB = db): Promise<{ r: Recurring; date: string }[]> {
  const list = (await d.recurring.toArray()).filter((r) => r.deletedAt === null && !r.auto && !r.paused)
  return list.flatMap((r) => dueDates(r, today, 12).map((date) => ({ r, date }))).sort((a, b) => a.date.localeCompare(b.date))
}

/** Importo totale previsto di un modello (i buoni pasto valgono al valore attuale del buono). */
export function recurringTotal(r: Recurring, accounts: Map<string, { voucherValue: number | null }>): number {
  return r.parts.reduce((s, p) => {
    if (p.vouchers) {
      const [, id] = p.source.split(':')
      return s + p.vouchers * (accounts.get(id)?.voucherValue ?? 0)
    }
    return s + p.amount
  }, 0)
}
