import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as tp from './templates'
import type { MovementInput } from './transactions'
import type { Account } from './types'
import * as core from '../sync/core'
import * as cr from '../sync/crypto'
import { merge, emptySnapshot, unifyForFirstLink } from '../sync/merge'
import type { DriveFile } from '../sync/google'

let d: StateraDB
let n = 0
let conto: Account
const base = { initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1' as const }
const caffe = (over: Partial<MovementInput> = {}): MovementInput => ({
  type: 'uscita', date: '2026-11-14', parts: [{ source: `a:${conto.id}`, amount: 120, vouchers: null }],
  categoryId: repo.seedId('uscita', 'Pasti fuori'), toAccountId: null, description: 'Caffè', notes: 'non copiata', ...over,
})

beforeEach(async () => {
  d = new StateraDB(`tpl-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
  conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, d)
})

describe('preferiti', () => {
  it('crea e registra con un tocco', async () => {
    const t = await tp.createTemplate('  Caffè  ', caffe(), d)
    expect(t.name).toBe('Caffè')
    expect(tp.hasAmount(t)).toBe(true)
    const m = await tp.registerTemplate(t, '2026-11-20', d)
    expect(m.date).toBe('2026-11-20')
    expect(m.parts[0].amount).toBe(120)
    expect(m.description).toBe('Caffè')
    expect(m.notes).toBe('')
  })
  it('senza importo: si salva, ma serve la categoria', async () => {
    const t = await tp.createTemplate('Spesa', caffe({ parts: [{ source: `a:${conto.id}`, amount: 0, vouchers: null }] }), d)
    expect(tp.hasAmount(t)).toBe(false)
    await expect(tp.createTemplate('X', caffe({ parts: [{ source: `a:${conto.id}`, amount: 0, vouchers: null }], categoryId: null }), d)).rejects.toThrow('categoria')
  })
  it('nome obbligatorio e corto; massimo 12', async () => {
    await expect(tp.createTemplate(' ', caffe(), d)).rejects.toThrow('nome')
    await expect(tp.createTemplate('x'.repeat(31), caffe(), d)).rejects.toThrow('lungo')
    for (let i = 0; i < tp.MAX_TEMPLATES; i++) await tp.createTemplate(`P${i}`, caffe(), d)
    await expect(tp.createTemplate('Troppi', caffe(), d)).rejects.toThrow('massimo')
  })
  it('ordine, rinomina, eliminazione logica', async () => {
    const a = await tp.createTemplate('A', caffe(), d)
    const b = await tp.createTemplate('B', caffe(), d)
    await tp.moveTemplate(b.id, -1, d)
    const list = (await d.templates.toArray()).sort(tp.byOrder)
    expect(list.map((t) => t.name)).toEqual(['B', 'A'])
    await tp.renameTemplate(a.id, 'Caffè al bar', d)
    expect((await d.templates.get(a.id))!.name).toBe('Caffè al bar')
    await tp.deleteTemplate(a.id, d)
    expect((await d.templates.get(a.id))!.deletedAt).not.toBeNull()
  })
})

class FakeDrive implements core.DriveLike {
  files = new Map<string, DriveFile & { content: string }>()
  k = 0
  async list() { return [...this.files.values()].map(({ content: _c, ...f }) => f) }
  async read(id: string) { return this.files.get(id)!.content }
  async create(name: string, content: string) { const id = `f${++this.k}`; this.files.set(id, { id, name, content }); return { id, name } }
  async update(id: string, content: string) { const f = this.files.get(id)!; f.content = content; return { id, name: f.name } }
  async remove(id: string) { this.files.delete(id) }
}

describe('preferiti e sincronizzazione', () => {
  it('passano da un dispositivo all\'altro; primo collegamento ricollega il conto', async () => {
    const key = (await cr.createKeys('password-di-prova', cr.generateRecoveryKey())).dataKey
    const drive = new FakeDrive()
    await tp.createTemplate('Caffè', caffe(), d)
    await core.syncOnce(d, drive, key)
    // secondo dispositivo con un proprio "Conto" (stesso nome): al collegamento diventa lo stesso
    const pc = new StateraDB(`tpl-pc-${n}`)
    await pc.open()
    await repo.ensureSeeded(pc)
    const contoPc = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, pc)
    await tp.createTemplate('Pranzo', caffe({ parts: [{ source: `a:${contoPc.id}`, amount: 800, vouchers: null }], description: 'Pranzo' }), pc)
    await core.firstLink(pc, drive, key, 'merge')
    const list = (await pc.templates.toArray()).filter((t) => t.deletedAt === null)
    expect(list.map((t) => t.name).sort()).toEqual(['Caffè', 'Pranzo'])
    expect(list.every((t) => t.parts[0].source === `a:${conto.id}`)).toBe(true)
    await core.syncOnce(d, drive, key)
    expect(await d.templates.count()).toBe(2)
  }, 30_000)

  it('una versione più nuova con tabelle sconosciute non le perde', () => {
    const remote = { ...emptySnapshot(), futura: [{ id: 'x' }] } as never
    const { merged } = merge(emptySnapshot(), remote)
    expect((merged as unknown as Record<string, unknown>).futura).toEqual([{ id: 'x' }])
  })

  it('obiettivi ricollegati al conto unificato', () => {
    const acc = { ...base, id: 'L', name: 'Risparmi', type: 'altro', initialBalance: 0, order: 1, archived: false, createdAt: 1, updatedAt: 1, deletedAt: null }
    const local = { ...emptySnapshot(), accounts: [acc] as never, goals: [{ id: 'g', name: 'Fondo', target: 100, accountId: 'L', saved: 0, dueDate: null, color: 's1', archived: false, createdAt: 1, updatedAt: 1, deletedAt: null }] as never }
    const remote = { ...emptySnapshot(), accounts: [{ ...acc, id: 'R' }] as never }
    const out = unifyForFirstLink(local, remote)
    expect(out.goals[0].accountId).toBe('R')
  })
})
