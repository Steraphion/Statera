import { db, type StateraDB } from './db'
import { accountBalance } from './balances'
import type { Account, Goal, SwatchKey, Transaction } from './types'
import { baseFields } from './util'

/**
 * Obiettivi di risparmio. Il progresso è il saldo di un conto dedicato (es. "Risparmi")
 * oppure un importo accantonato segnato a mano.
 */

export interface GoalInput {
  name: string
  target: number
  accountId: string | null
  saved: number
  dueDate: string | null
  color: SwatchKey
}

async function clean(input: GoalInput, d: StateraDB): Promise<GoalInput> {
  const name = input.name.replace(/\s+/g, ' ').trim()
  if (!name) throw new Error("Dai un nome all'obiettivo")
  if (name.length > 40) throw new Error('Nome troppo lungo (massimo 40 caratteri)')
  if (!Number.isInteger(input.target) || input.target <= 0) throw new Error("Indica l'importo da raggiungere")
  if (input.dueDate !== null && !/^\d{4}-\d{2}-\d{2}$/.test(input.dueDate)) throw new Error('Data non valida')
  let accountId: string | null = null
  if (input.accountId) {
    const a = await d.accounts.get(input.accountId)
    if (!a || a.deletedAt !== null) throw new Error('Conto non trovato')
    if (a.type === 'buoni_pasto') throw new Error('Scegli un conto, non i buoni pasto')
    accountId = a.id
  }
  const saved = accountId ? 0 : input.saved
  if (!Number.isInteger(saved) || saved < 0) throw new Error("L'importo accantonato non può essere negativo")
  return { name, target: input.target, accountId, saved, dueDate: input.dueDate || null, color: input.color }
}

export async function createGoal(input: GoalInput, d: StateraDB = db): Promise<Goal> {
  const g: Goal = { ...baseFields(), ...(await clean(input, d)), archived: false }
  await d.goals.add(g)
  return g
}

export async function updateGoal(id: string, input: GoalInput, d: StateraDB = db) {
  await d.goals.update(id, { ...(await clean(input, d)), updatedAt: Date.now() })
}

export async function deleteGoal(id: string, d: StateraDB = db) {
  const now = Date.now()
  await d.goals.update(id, { deletedAt: now, updatedAt: now })
}

/** Aggiunge (o toglie, se negativo) all'accantonato di un obiettivo senza conto dedicato. */
export async function addToGoal(id: string, cents: number, d: StateraDB = db) {
  if (!Number.isInteger(cents) || cents === 0) throw new Error('Inserisci un importo (es. 50 oppure -20)')
  await d.transaction('rw', d.goals, async () => {
    const g = await d.goals.get(id)
    if (!g || g.deletedAt !== null) throw new Error('Obiettivo non trovato')
    if (g.accountId) throw new Error('Questo obiettivo segue il saldo di un conto')
    const saved = g.saved + cents
    if (saved < 0) throw new Error("Non puoi togliere più di quanto hai accantonato")
    await d.goals.update(id, { saved, updatedAt: Date.now() })
  })
}

export interface GoalProgress {
  current: number
  /** 0–1 (oltre 1 se superato). */
  ratio: number
  remaining: number
  reached: boolean
  /** Mesi interi che restano fino alla scadenza (almeno 1), o null. */
  monthsLeft: number | null
  /** Quanto mettere da parte al mese per arrivarci in tempo, o null. */
  perMonth: number | null
  overdue: boolean
}

export function goalProgress(g: Goal, accounts: Account[], transactions: Transaction[], todayStr: string): GoalProgress {
  const acc = g.accountId ? accounts.find((a) => a.id === g.accountId) : undefined
  const current = acc ? accountBalance(acc, transactions).amount : g.saved
  const remaining = Math.max(0, g.target - current)
  const reached = current >= g.target
  let monthsLeft: number | null = null
  let perMonth: number | null = null
  let overdue = false
  if (g.dueDate && !reached) {
    const [ty, tm] = todayStr.split('-').map(Number)
    const [dy, dm] = g.dueDate.split('-').map(Number)
    const months = (dy - ty) * 12 + (dm - tm)
    overdue = g.dueDate < todayStr
    monthsLeft = overdue ? null : Math.max(1, months)
    perMonth = monthsLeft ? Math.ceil(remaining / monthsLeft) : null
  }
  return { current, ratio: g.target ? current / g.target : 0, remaining, reached, monthsLeft, perMonth, overdue }
}
