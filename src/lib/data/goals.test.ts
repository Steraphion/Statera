import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as gl from './goals'
import type { Account } from './types'

let d: StateraDB
let n = 0
let risparmi: Account
const base = { initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1' as const }
const goal = (over: Partial<gl.GoalInput> = {}): gl.GoalInput => ({ name: 'Fondo emergenze', target: 300000, accountId: null, saved: 50000, dueDate: null, color: 's3', ...over })

beforeEach(async () => {
  d = new StateraDB(`goal-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
  risparmi = await repo.createAccount({ ...base, name: 'Risparmi', type: 'altro', initialBalance: 120000 }, d)
})

describe('obiettivi di risparmio', () => {
  it('a mano: aggiungi e togli', async () => {
    const g = await gl.createGoal(goal(), d)
    await gl.addToGoal(g.id, 25000, d)
    await gl.addToGoal(g.id, -5000, d)
    expect((await d.goals.get(g.id))!.saved).toBe(70000)
    await expect(gl.addToGoal(g.id, -999999, d)).rejects.toThrow('togliere')
    await expect(gl.addToGoal(g.id, 0, d)).rejects.toThrow('importo')
  })
  it('con un conto: segue il saldo e non accetta aggiunte a mano', async () => {
    const g = await gl.createGoal(goal({ accountId: risparmi.id, saved: 999 }), d)
    expect(g.saved).toBe(0)
    const p = gl.goalProgress(g, await d.accounts.toArray(), [], '2026-11-14')
    expect(p.current).toBe(120000)
    expect(p.remaining).toBe(180000)
    await expect(gl.addToGoal(g.id, 100, d)).rejects.toThrow('saldo di un conto')
  })
  it('scadenza: quanto al mese, raggiunto, scaduto', async () => {
    const g = await gl.createGoal(goal({ dueDate: '2027-05-31' }), d)
    const p = gl.goalProgress(g, [], [], '2026-11-14')
    expect(p.monthsLeft).toBe(6)
    expect(p.perMonth).toBe(Math.ceil(250000 / 6))
    expect(gl.goalProgress({ ...g, dueDate: '2026-11-30' }, [], [], '2026-11-14').monthsLeft).toBe(1)
    expect(gl.goalProgress({ ...g, dueDate: '2026-10-01' }, [], [], '2026-11-14').overdue).toBe(true)
    const done = gl.goalProgress({ ...g, saved: 300000 }, [], [], '2026-11-14')
    expect(done.reached).toBe(true)
    expect(done.perMonth).toBeNull()
  })
  it('validazioni', async () => {
    await expect(gl.createGoal(goal({ name: ' ' }), d)).rejects.toThrow('nome')
    await expect(gl.createGoal(goal({ target: 0 }), d)).rejects.toThrow('raggiungere')
    await expect(gl.createGoal(goal({ saved: -1 }), d)).rejects.toThrow('negativo')
    const b = await repo.createAccount({ ...base, name: 'Buoni', type: 'buoni_pasto', initialBalance: 0, voucherValue: 800, initialVouchers: 0 }, d)
    await expect(gl.createGoal(goal({ accountId: b.id }), d)).rejects.toThrow('buoni')
  })
})
