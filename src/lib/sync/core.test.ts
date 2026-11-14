import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from '../data/db'
import * as repo from '../data/repo'
import * as mv from '../data/transactions'
import * as cr from './crypto'
import * as core from './core'
import type { DriveFile } from './google'
import { accountBalance } from '../data/balances'

/** Google Drive finto, in memoria, condiviso tra i "dispositivi". */
class FakeDrive implements core.DriveLike {
  files = new Map<string, DriveFile & { content: string }>()
  n = 0
  async list() { return [...this.files.values()].map(({ content: _c, ...f }) => f) }
  async read(id: string) { const f = this.files.get(id); if (!f) throw new Error('404'); return f.content }
  async create(name: string, content: string) { const id = `f${++this.n}`; this.files.set(id, { id, name, content }); return { id, name } }
  async update(id: string, content: string) { const f = this.files.get(id)!; f.content = content; return { id, name: f.name } }
  async remove(id: string) { this.files.delete(id) }
  byName(name: string) { return [...this.files.values()].find((f) => f.name === name) }
}

let n = 0
async function device() {
  const d = new StateraDB(`dev-${++n}`)
  await d.open()
  await repo.ensureSeeded(d)
  return d
}
const base = { initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' as const }
async function spend(d: StateraDB, accountId: string, amount: number, description: string, date = '2026-11-05') {
  return mv.createMovement(
    { type: 'uscita', date, parts: [{ source: `a:${accountId}`, amount, vouchers: null }], categoryId: repo.seedId('uscita', 'Svago'), toAccountId: null, description, notes: '' },
    d,
  )
}

let drive: FakeDrive
let key: CryptoKey

beforeEach(async () => {
  drive = new FakeDrive()
  key = (await cr.createKeys('password-di-prova', cr.generateRecoveryKey())).dataKey
}, 30_000)

describe('sincronizzazione tra due dispositivi', () => {
  it('telefono e PC si allineano, nei due sensi, senza doppioni di categorie', async () => {
    const tel = await device()
    const conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 100000 }, tel)
    await spend(tel, conto.id, 1000, 'Cinema')
    const r1 = await core.syncOnce(tel, drive, key)
    expect(r1.pushed).toBe(true)
    expect(drive.byName(core.DATA_FILE)!.content).not.toContain('Cinema') // cifrato

    const pc = await device()
    await core.firstLink(pc, drive, key, 'merge')
    expect(await pc.accounts.count()).toBe(1)
    expect(await pc.categories.count()).toBe(await tel.categories.count()) // nessun doppione

    await spend(pc, conto.id, 2500, 'Pizza')
    await core.syncOnce(pc, drive, key)
    const r2 = await core.syncOnce(tel, drive, key)
    expect(r2.pulled).toBe(1)
    const a = (await tel.accounts.get(conto.id))!
    expect(accountBalance(a, await tel.transactions.toArray()).amount).toBe(100000 - 1000 - 2500)

    // modifica e cancellazione si propagano
    const pizza = (await tel.transactions.toArray()).find((t) => t.description === 'Pizza')!
    await mv.deleteMovement(pizza.id, tel)
    await core.syncOnce(tel, drive, key)
    await core.syncOnce(pc, drive, key)
    expect((await pc.transactions.get(pizza.id))!.deletedAt).not.toBeNull()

    // a regime: niente da caricare
    const r3 = await core.syncOnce(pc, drive, key)
    expect(r3.pushed).toBe(false)
    expect(r3.pulled).toBe(0)
  }, 30_000)

  it('modifiche contemporanee allo stesso movimento: vince la più recente', async () => {
    const tel = await device()
    const conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, tel)
    const t = await spend(tel, conto.id, 100, 'Originale')
    await core.syncOnce(tel, drive, key)
    const pc = await device()
    await core.firstLink(pc, drive, key, 'merge')

    const input = (desc: string): mv.MovementInput => ({
      type: 'uscita', date: '2026-11-05', parts: [{ source: `a:${conto.id}`, amount: 100, vouchers: null }],
      categoryId: repo.seedId('uscita', 'Svago'), toAccountId: null, description: desc, notes: '',
    })
    await mv.updateMovement(t.id, input('Dal telefono'), tel)
    await new Promise((r) => setTimeout(r, 5))
    await mv.updateMovement(t.id, input('Dal PC, dopo'), pc)
    await core.syncOnce(tel, drive, key)
    await core.syncOnce(pc, drive, key)
    await core.syncOnce(tel, drive, key)
    expect((await tel.transactions.get(t.id))!.description).toBe('Dal PC, dopo')
    expect((await pc.transactions.get(t.id))!.description).toBe('Dal PC, dopo')
  }, 30_000)

  it('primo collegamento con dati già presenti su entrambi: unione o sostituzione', async () => {
    const tel = await device()
    const c1 = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, tel)
    await spend(tel, c1.id, 100, 'Dal telefono')
    await core.syncOnce(tel, drive, key)

    // PC con dati propri e categorie create con id casuali (come nelle versioni precedenti)
    const pc = new StateraDB(`dev-${++n}`)
    await pc.open()
    const casa = await repo.createCategory({ name: 'Svago', kind: 'uscita', parentId: null, color: 's1' }, pc)
    const c2 = await repo.createAccount({ ...base, name: 'conto', type: 'conto_corrente', initialBalance: 0 }, pc)
    await mv.createMovement(
      { type: 'uscita', date: '2026-11-06', parts: [{ source: `a:${c2.id}`, amount: 200, vouchers: null }], categoryId: casa.id, toAccountId: null, description: 'Dal PC', notes: '' },
      pc,
    )
    await core.firstLink(pc, drive, key, 'merge')
    const accounts = (await pc.accounts.toArray()).filter((a) => a.deletedAt === null)
    expect(accounts.map((a) => a.id)).toEqual([c1.id]) // conto unificato
    const txs = (await pc.transactions.toArray()).map((t) => [t.description, t.accountIds[0], t.categoryId])
    expect(txs).toContainEqual(['Dal PC', c1.id, repo.seedId('uscita', 'Svago')])
    expect((await pc.categories.toArray()).filter((c) => c.name === 'Svago')).toHaveLength(1)

    // un terzo dispositivo sceglie di sostituire i suoi dati con quelli di Drive
    const altro = await device()
    await repo.createAccount({ ...base, name: 'Da buttare', type: 'contanti', initialBalance: 0 }, altro)
    await core.firstLink(altro, drive, key, 'replace')
    expect((await altro.accounts.toArray()).map((a) => a.name)).toEqual(['Conto'])
    expect(await altro.transactions.count()).toBe(2)
  }, 30_000)

  it('una modifica fatta durante la sincronizzazione non viene sovrascritta', async () => {
    const tel = await device()
    const conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, tel)
    const t = await spend(tel, conto.id, 100, 'Vecchia')
    // Drive ha una versione più vecchia dello stesso record rispetto a quella che l'utente sta salvando adesso
    const stale = { ...t, description: 'Da Drive', updatedAt: t.updatedAt + 1 }
    await tel.transactions.update(t.id, { description: 'Appena salvata', updatedAt: t.updatedAt + 2 })
    const written = await core.applyToLocal(tel, { accounts: [], cards: [], categories: [], transactions: [stale], recurring: [], templates: [], goals: [] })
    expect(written).toBe(0)
    expect((await tel.transactions.get(t.id))!.description).toBe('Appena salvata')
  })

  it('backup giornalieri: uno al giorno, massimo 30, ripristino per tutti', async () => {
    const tel = await device()
    const conto = await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, tel)
    await spend(tel, conto.id, 100, 'Prima del backup')
    const r = await core.syncOnce(tel, drive, key)
    await core.dailyBackup(drive, key, r.merged, r.files, '2026-11-01')
    for (let i = 2; i <= 33; i++) {
      await core.dailyBackup(drive, key, r.merged, await drive.list(), `2026-11-${String(i).padStart(2, '0')}`)
    }
    const backups = core.listBackups(await drive.list())
    expect(backups).toHaveLength(30)
    expect(backups[0].name).toBe('statera-backup-2026-11-33.json')
    await core.dailyBackup(drive, key, r.merged, await drive.list(), '2026-11-33')
    expect(core.listBackups(await drive.list())).toHaveLength(30)

    // dopo il backup: nuovo movimento sul telefono e sincronizzazione con il PC
    await spend(tel, conto.id, 999, 'Dopo il backup')
    await core.syncOnce(tel, drive, key)
    const pc = await device()
    await core.firstLink(pc, drive, key, 'merge')
    expect((await pc.transactions.toArray()).filter((t) => t.deletedAt === null)).toHaveLength(2)

    // ripristino dal telefono: il movimento successivo sparisce anche dal PC
    await core.restoreFromBackup(tel, drive, key, backups[0].id)
    await core.syncOnce(pc, drive, key)
    const alivePc = (await pc.transactions.toArray()).filter((t) => t.deletedAt === null).map((t) => t.description)
    expect(alivePc).toEqual(['Prima del backup'])
  }, 60_000)

  it('chiave sbagliata: errore chiaro, nessun dato toccato', async () => {
    const tel = await device()
    await repo.createAccount({ ...base, name: 'Conto', type: 'conto_corrente', initialBalance: 0 }, tel)
    await core.syncOnce(tel, drive, key)
    const other = (await cr.createKeys('altra-password-x', cr.generateRecoveryKey())).dataKey
    const pc = await device()
    await expect(core.syncOnce(pc, drive, other)).rejects.toThrow(/decifrare/)
    expect(await pc.accounts.count()).toBe(0)
  }, 30_000)
})
