import type { Category, CategoryKind, Transaction } from './types'
import { total } from './transactions'

/**
 * Calcoli per la sezione Analisi. Regole:
 * - i trasferimenti non sono né entrate né uscite;
 * - un pagamento misto conta per intero nella sua categoria;
 * - le spese con buoni pasto sono spese a tutti gli effetti.
 */

export type Period = { kind: 'mese'; month: string } | { kind: 'anno'; year: string }

export function inPeriod(t: Transaction, p: Period): boolean {
  return p.kind === 'mese' ? t.date.startsWith(p.month + '-') : t.date.startsWith(p.year + '-')
}

export function periodRows(rows: Transaction[], p: Period): Transaction[] {
  return rows.filter((t) => t.deletedAt === null && inPeriod(t, p))
}

export function periodRange(p: Period): { from: string; to: string } {
  if (p.kind === 'anno') return { from: `${p.year}-01-01`, to: `${p.year}-12-31` }
  const [y, m] = p.month.split('-').map(Number)
  const last = new Date(y, m, 0).getDate()
  return { from: `${p.month}-01`, to: `${p.month}-${String(last).padStart(2, '0')}` }
}

export interface CategoryTotal {
  category: Category
  total: number
  /** Quota sul totale del tipo (0–1). */
  share: number
  /** Sottocategorie con spesa > 0 (la quota "diretta" sulla principale compare come voce a sé). */
  children: { category: Category; total: number; direct: boolean }[]
}

/** Totali per categoria principale (sottocategorie comprese), dal più grande. */
export function byCategory(rows: Transaction[], kind: CategoryKind, categories: Category[]): CategoryTotal[] {
  const map = new Map(categories.map((c) => [c.id, c]))
  const tops = new Map<string, { total: number; parts: Map<string, number> }>()
  let sum = 0
  for (const t of rows) {
    if (t.deletedAt !== null || t.type !== kind || !t.categoryId) continue
    const c = map.get(t.categoryId)
    if (!c) continue
    const topId = c.parentId ?? c.id
    const amount = total(t)
    sum += amount
    const g = tops.get(topId) ?? { total: 0, parts: new Map() }
    g.total += amount
    g.parts.set(c.id, (g.parts.get(c.id) ?? 0) + amount)
    tops.set(topId, g)
  }
  const out: CategoryTotal[] = []
  for (const [topId, g] of tops) {
    const top = map.get(topId)
    if (!top) continue
    const children = [...g.parts]
      .filter(([id]) => id !== topId || g.parts.size > 1)
      .map(([id, amount]) => ({ category: map.get(id)!, total: amount, direct: id === topId }))
      .sort((a, b) => b.total - a.total)
    out.push({ category: top, total: g.total, share: sum ? g.total / sum : 0, children })
  }
  return out.sort((a, b) => b.total - a.total || a.category.name.localeCompare(b.category.name, 'it'))
}

export interface MonthPoint {
  month: string
  income: number
  expense: number
  net: number
}

/** Ultimi `n` mesi fino a `endMonth` compreso ('AAAA-MM'), dal più vecchio. */
export function monthlySeries(rows: Transaction[], endMonth: string, n = 12): MonthPoint[] {
  const [y, m] = endMonth.split('-').map(Number)
  const months: string[] = []
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(y, m - 1 - i, 1)
    months.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`)
  }
  const idx = new Map(months.map((mo, i) => [mo, i]))
  const pts: MonthPoint[] = months.map((month) => ({ month, income: 0, expense: 0, net: 0 }))
  for (const t of rows) {
    if (t.deletedAt !== null) continue
    const i = idx.get(t.date.slice(0, 7))
    if (i === undefined) continue
    if (t.type === 'entrata') pts[i].income += total(t)
    else if (t.type === 'uscita') pts[i].expense += total(t)
  }
  for (const p of pts) p.net = p.income - p.expense
  return pts
}

export interface BudgetStatus {
  category: Category
  budget: number
  spent: number
  /** spent / budget */
  ratio: number
  state: 'ok' | 'attenzione' | 'superato'
}

/** Avanzamento dei budget mensili nel mese indicato (sottocategorie comprese). */
export function budgetStatus(rows: Transaction[], month: string, categories: Category[]): BudgetStatus[] {
  const withBudget = categories.filter(
    (c) => c.deletedAt === null && !c.archived && c.parentId === null && c.kind === 'uscita' && (c.monthlyBudget ?? 0) > 0,
  )
  if (!withBudget.length) return []
  const totals = new Map(
    byCategory(periodRows(rows, { kind: 'mese', month }), 'uscita', categories).map((g) => [g.category.id, g.total]),
  )
  return withBudget
    .map((c) => {
      const budget = c.monthlyBudget ?? 0
      const spent = totals.get(c.id) ?? 0
      const ratio = spent / budget
      const state: BudgetStatus['state'] = ratio > 1 ? 'superato' : ratio >= 0.8 ? 'attenzione' : 'ok'
      return { category: c, budget, spent, ratio, state }
    })
    .sort((a, b) => b.ratio - a.ratio)
}

/** Valori "puliti" per l'asse: 0 … massimo arrotondato, `count` tacche. */
export function niceTicks(max: number, count = 4): number[] {
  if (max <= 0) return [0]
  const raw = max / count
  const pow = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 2.5, 5, 10].map((k) => k * pow).find((s) => s >= raw)!
  const ticks: number[] = []
  for (let v = 0; v <= max + step * 0.001; v += step) ticks.push(v)
  if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + step)
  return ticks
}

/**
 * Giorni che restano nel mese, oggi compreso: tutto il mese se è futuro, 0 se è passato.
 */
export function daysLeftInMonth(month: string, todayStr: string): number {
  const [y, m] = month.split('-').map(Number)
  const last = new Date(y, m, 0).getDate()
  const current = todayStr.slice(0, 7)
  if (month < current) return 0
  if (month > current) return last
  return last - Number(todayStr.slice(8, 10)) + 1
}

/** Quanto si può spendere al giorno per restare nel budget (centesimi, arrotondato per difetto). */
export function perDay(left: number, days: number): number | null {
  if (left <= 0 || days <= 0) return null
  return Math.floor(left / days)
}
