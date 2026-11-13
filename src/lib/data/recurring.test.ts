import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as rec from './recurring'
import type { MovementInput } from './transactions'
import type { Account, Recurring } from './types'
import * as core from '../sync/core'
import * as cr from '../sync/crypto'

let d: StateraDB
let n = 0
let conto: Account
const base = { initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1' as const }

beforeEach(async () => {
  d = new StateraDB(`rec-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
  conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, d)
})

const r0 = (startDate: string, frequency: Recurring['frequency']) => ({ startDate, frequency })
const input = (over: Partial<MovementInput> = {}): MovementInput => ({
  type: 'entrata', date: '2026-01-27', parts: [{ source: `a:${conto.id}`, amount: 150000, vouchers: null }],
  categoryId: repo.seedId('entrata', 'Stipendio'), toAccountId: null, description: 'Stipendio', notes: '', ...over,
})
const alive = async (db = d) => (await db.transactions.toArray()).filter((t) => t.deletedAt === null)

describe('calendario', () => {
  it('mensile il 31: ultimo giorno nei mesi corti, poi torna al 31', () => {
    const r = r0('2026-01-31', 'mensile')
    expect([0, 1, 2, 3].map((k) => rec.occurrence(r, k))).toEqual(['2026-01-31', '2026-02-28', '2026-03-31', '2026-04-30'])
  })
  it('settimanale e annuale (anche 29 febbraio)', () => {
    expect(rec.occurrence(r0('2026-12-28', 'settimanale'), 1)).toBe('2027-01-04')
    expect(rec.occurrence(r0('2028-02-29', 'annuale'), 1)).toBe('2029-02-28')
    expect(rec.occurrence(r0('2028-02-29', 'annuale'), 4)).toBe('2032-02-29')
  })
  it('descrizione leggibile', () => {
    expect(rec.describeFrequency(r0('2026-11-27', 'mensile'))).toBe('Ogni mese, il giorno 27')
    expect(rec.describeFrequency(r0('2026-11-13', 'settimanale'))).toBe('Ogni settimana, di venerdì')
    expect(rec.describeFrequency(r0('2026-11-27', 'annuale'))).toBe('Ogni anno, il 27 novembre')
  })
})

describe('ripetizioni automatiche', () => {
  it('crea subito la prima, recupera le scadute, nessun doppione rilanciando', async () => {
    const r = await rec.createRecurring(input(), { frequency: 'mensile', date: '2026-08-27', endDate: null, auto: true }, '2026-11-13', d)
    expect(r.done).toBe(1)
    expect(await alive()).toHaveLength(1)
    expect(await rec.processRecurring('2026-11-13', d)).toBe(2) // settembre, ottobre
    expect((await alive()).map((t) => t.date).sort()).toEqual(['2026-08-27', '2026-09-27', '2026-10-27'])
    expect(await rec.processRecurring('2026-11-13', d)).toBe(0)
    expect(await rec.processRecurring('2026-11-27', d)).toBe(1)
    const fresh = (await d.recurring.get(r.id))!
    expect(rec.nextDate(fresh)).toBe('2026-12-27')
  })

  it('data futura: nessun movimento finché non arriva', async () => {
    await rec.createRecurring(input(), { frequency: 'mensile', date: '2026-12-01', endDate: null, auto: true }, '2026-11-13', d)
    expect(await alive()).toHaveLength(0)
    await rec.processRecurring('2026-12-01', d)
    expect(await alive()).toHaveLength(1)
  })

  it('fine, pausa, eliminazione di un movimento generato (non ricreato)', async () => {
    const r = await rec.createRecurring(input(), { frequency: 'settimanale', date: '2026-11-02', endDate: '2026-11-16', auto: true }, '2026-11-02', d)
    await rec.processRecurring('2026-12-31', d)
    expect(await alive()).toHaveLength(3) // 2, 9, 16 novembre
    const gen = (await alive()).find((t) => t.date === '2026-11-09')!
    expect(gen.id).toBe(`rec-${r.id}-2026-11-09`)
    await d.transactions.update(gen.id, { deletedAt: Date.now(), updatedAt: Date.now() })
    await d.recurring.update(r.id, { done: 1 }) // simula un dispositivo "indietro"
    await rec.processRecurring('2026-12-31', d)
    expect((await alive()).map((t) => t.date).sort()).toEqual(['2026-11-02', '2026-11-16'])
    const r2 = await rec.createRecurring(input({ description: 'Altro' }), { frequency: 'mensile', date: '2026-11-01', endDate: null, auto: true }, '2026-11-01', d)
    await rec.setRecurringPaused(r2.id, true, d)
    expect(await rec.processRecurring('2027-03-01', d)).toBe(0)
  })

  it('modello non più valido: messo in pausa, il resto continua', async () => {
    const r = await rec.createRecurring(input(), { frequency: 'mensile', date: '2026-10-01', endDate: null, auto: true }, '2026-10-01', d)
    await d.accounts.update(conto.id, { deletedAt: Date.now() })
    await rec.processRecurring('2026-11-13', d)
    expect((await d.recurring.get(r.id))!.paused).toBe(true)
  })

  it('modello non valido rifiutato alla creazione', async () => {
    await expect(
      rec.createRecurring(input({ categoryId: null }), { frequency: 'mensile', date: '2026-12-01', endDate: null, auto: true }, '2026-11-13', d),
    ).rejects.toThrow(/categoria/)
    expect(await d.recurring.count()).toBe(0)
  })
})

describe('da confermare', () => {
  it('elenco, conferma con importo diverso, salta', async () => {
    const r = await rec.createRecurring(
      input({ type: 'uscita', categoryId: repo.seedId('uscita', 'Casa', 'Bollette'), description: 'Luce', parts: [{ source: `a:${conto.id}`, amount: 6000, vouchers: null }] }),
      { frequency: 'mensile', date: '2026-09-10', endDate: null, auto: false }, '2026-11-13', d,
    )
    expect(await rec.processRecurring('2026-11-13', d)).toBe(0) // non automatiche
    let pend = await rec.pendingConfirmations('2026-11-13', d)
    expect(pend.map((p) => p.date)).toEqual(['2026-10-10', '2026-11-10'])
    const fresh = (await d.recurring.get(r.id))!
    await rec.confirmOccurrence(fresh, { ...rec.toMovementInput(fresh, '2026-10-12'), parts: [{ source: `a:${conto.id}`, amount: 7350, vouchers: null }] }, '2026-10-10', d)
    await rec.skipOccurrence((await d.recurring.get(r.id))!, '2026-11-10', d)
    pend = await rec.pendingConfirmations('2026-11-13', d)
    expect(pend).toHaveLength(0)
    expect((await alive()).map((t) => [t.date, t.parts[0].amount]).sort()).toEqual([['2026-09-10', 6000], ['2026-10-12', 7350]])
    expect(rec.shouldProcessLocally(false, null)).toBe(true)
    expect(rec.shouldProcessLocally(true, Date.now())).toBe(false)
    expect(rec.shouldProcessLocally(true, Date.now() - 2 * 86400000)).toBe(true)
  })

  it('modifica: cambia importo e data, riparte da lì; i movimenti passati restano', async () => {
    const r = await rec.createRecurring(input(), { frequency: 'mensile', date: '2026-10-27', endDate: null, auto: true }, '2026-11-13', d)
    await rec.updateRecurring(r.id, input({ parts: [{ source: `a:${conto.id}`, amount: 160000, vouchers: null }] }), { frequency: 'mensile', date: '2026-11-25', endDate: null, auto: true }, d)
    await rec.processRecurring('2026-12-31', d)
    expect((await alive()).map((t) => [t.date, t.parts[0].amount]).sort()).toEqual([
      ['2026-10-27', 150000], ['2026-11-25', 160000], ['2026-12-25', 160000],
    ])
  })
})

describe('due dispositivi', () => {
  it('generano la stessa occorrenza: dopo la sincronizzazione nessun doppione', async () => {
    class FakeDrive {
      files = new Map<string, { id: string; name: string; content: string }>(); k = 0
      async list() { return [...this.files.values()].map(({ id, name }) => ({ id, name })) }
      async read(id: string) { return this.files.get(id)!.content }
      async create(name: string, content: string) { const id = `f${++this.k}`; this.files.set(id, { id, name, content }); return { id, name } }
      async update(id: string, content: string) { this.files.get(id)!.content = content; return { id, name: this.files.get(id)!.name } }
      async remove(id: string) { this.files.delete(id) }
    }
    const drive = new FakeDrive()
    const key = (await cr.createKeys('password-di-prova', cr.generateRecoveryKey())).dataKey
    await rec.createRecurring(input(), { frequency: 'mensile', date: '2026-10-27', endDate: null, auto: true }, '2026-10-27', d)
    await core.syncOnce(d, drive, key)
    const pc = new StateraDB(`rec-pc-${n}`)
    await pc.open()
    await repo.ensureSeeded(pc)
    await core.firstLink(pc, drive, key, 'merge')
    // entrambi, offline, arrivano al 27 novembre e registrano lo stipendio
    expect(await rec.processRecurring('2026-11-27', d)).toBe(1)
    expect(await rec.processRecurring('2026-11-27', pc)).toBe(1)
    await core.syncOnce(d, drive, key)
    await core.syncOnce(pc, drive, key)
    await core.syncOnce(d, drive, key)
    expect((await alive(d)).map((t) => t.date).sort()).toEqual(['2026-10-27', '2026-11-27'])
    expect((await alive(pc)).map((t) => t.date).sort()).toEqual(['2026-10-27', '2026-11-27'])
  }, 30_000)
})
