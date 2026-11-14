import { db, type StateraDB } from './db'
import { checkMovement, createMovement, type MovementInput } from './transactions'
import type { Template, Transaction } from './types'
import { baseFields } from './util'

/**
 * Movimenti preferiti: modelli registrabili con un tocco dalla schermata Movimenti.
 * Si sincronizzano come gli altri dati (tabella `templates`).
 */

export const MAX_TEMPLATES = 12

/** Il preferito ha un importo? Altrimenti al tocco si apre il modulo per scriverlo. */
export function hasAmount(t: Pick<Template, 'parts'>): boolean {
  return t.parts.every((p) => p.amount > 0 || (p.vouchers ?? 0) > 0)
}

function cleanName(name: string): string {
  return name.replace(/\s+/g, ' ').trim()
}

/** Nome proposto: la descrizione, o la categoria. */
export function suggestedName(input: Pick<MovementInput, 'description'>, categoryName = ''): string {
  return cleanName(input.description) || categoryName || 'Preferito'
}

export async function createTemplate(name: string, input: MovementInput, d: StateraDB = db): Promise<Template> {
  const n = cleanName(name)
  if (!n) throw new Error('Dai un nome al preferito')
  if (n.length > 30) throw new Error('Nome troppo lungo (massimo 30 caratteri)')
  // Con l'importo il modello deve essere un movimento valido; senza, almeno fonte e categoria
  if (input.parts.every((p) => p.amount > 0 || (p.vouchers ?? 0) > 0)) await checkMovement(input, d)
  else if (input.type !== 'trasferimento' && !input.categoryId) throw new Error('Scegli una categoria')
  const alive = (await d.templates.toArray()).filter((t) => t.deletedAt === null)
  if (alive.length >= MAX_TEMPLATES) throw new Error(`Puoi avere al massimo ${MAX_TEMPLATES} preferiti`)
  const t: Template = {
    ...baseFields(),
    name: n,
    type: input.type,
    parts: input.parts.map((p) => ({ source: p.source, amount: p.amount, vouchers: p.vouchers })),
    categoryId: input.type === 'trasferimento' ? null : input.categoryId,
    toAccountId: input.type === 'trasferimento' ? input.toAccountId : null,
    description: input.description.trim(),
    order: Math.max(0, ...alive.map((x) => x.order)) + 1,
  }
  await d.templates.add(t)
  return t
}

export async function renameTemplate(id: string, name: string, d: StateraDB = db) {
  const n = cleanName(name)
  if (!n) throw new Error('Dai un nome al preferito')
  if (n.length > 30) throw new Error('Nome troppo lungo (massimo 30 caratteri)')
  await d.templates.update(id, { name: n, updatedAt: Date.now() })
}

export async function deleteTemplate(id: string, d: StateraDB = db) {
  const now = Date.now()
  await d.templates.update(id, { deletedAt: now, updatedAt: now })
}

/** Sposta un preferito di una posizione (-1 = prima, +1 = dopo). */
export async function moveTemplate(id: string, delta: -1 | 1, d: StateraDB = db) {
  await d.transaction('rw', d.templates, async () => {
    const list = (await d.templates.toArray()).filter((t) => t.deletedAt === null).sort(byOrder)
    const i = list.findIndex((t) => t.id === id)
    const j = i + delta
    if (i < 0 || j < 0 || j >= list.length) return
    ;[list[i], list[j]] = [list[j], list[i]]
    const now = Date.now()
    for (let k = 0; k < list.length; k++) {
      if (list[k].order !== k + 1) await d.templates.update(list[k].id, { order: k + 1, updatedAt: now })
    }
  })
}

export function byOrder(a: Template, b: Template): number {
  return a.order - b.order || a.name.localeCompare(b.name, 'it')
}

export function toMovementInput(t: Template, date: string): MovementInput {
  return {
    type: t.type,
    date,
    parts: t.parts.map((p) => ({ ...p })),
    categoryId: t.categoryId,
    toAccountId: t.toAccountId,
    description: t.description,
    notes: '',
  }
}

/** Registra il preferito con la data indicata. */
export async function registerTemplate(t: Template, date: string, d: StateraDB = db): Promise<Transaction> {
  return createMovement(toMovementInput(t, date), d)
}
