import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as mv from './transactions'
import * as bk from './backup'

let n = 0
const fresh = async () => {
  const d = new StateraDB(`bk-${++n}`)
  await d.open()
  return d
}

let src: StateraDB

beforeEach(async () => {
  src = await fresh()
  await repo.ensureSeeded(src)
  const a = await repo.createAccount(
    { name: 'Conto', type: 'conto_corrente', initialBalance: 1000, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's1' },
    src,
  )
  const cat = (await src.categories.toArray()).find((c) => c.kind === 'uscita')!
  const t = await mv.createMovement(
    { type: 'uscita', date: '2026-11-02', parts: [{ source: `a:${a.id}`, amount: 250, vouchers: null }], categoryId: cat.id, toAccountId: null, description: 'Esempio', notes: '' },
    src,
  )
  await mv.createMovement(
    { type: 'uscita', date: '2026-11-03', parts: [{ source: `a:${a.id}`, amount: 100, vouchers: null }], categoryId: cat.id, toAccountId: null, description: 'Da cancellare', notes: '' },
    src,
  )
  await mv.deleteMovement((await src.transactions.toArray()).find((x) => x.description === 'Da cancellare')!.id, src)
  void t
})

describe('backup', () => {
  it('esporta e ripristina tutto, cancellati compresi', async () => {
    const file = await bk.buildBackup('test', src)
    const text = JSON.stringify(file)
    const parsed = bk.parseBackup(text)
    expect(bk.summarize(parsed)).toMatchObject({ accounts: 1, transactions: 1 })

    const dst = await fresh()
    await repo.ensureSeeded(dst)
    await repo.createAccount(
      { name: 'Da sostituire', type: 'contanti', initialBalance: 0, initialDate: '2026-11-01', voucherValue: null, initialVouchers: null, color: 's2' },
      dst,
    )
    await bk.markBackupDone(dst)
    await bk.restoreBackup(parsed, dst)

    expect((await dst.accounts.toArray()).map((a) => a.name)).toEqual(['Conto'])
    expect(await dst.transactions.count()).toBe(2)
    expect(await dst.categories.count()).toBe(await src.categories.count())
    expect(await bk.lastBackupAt(dst)).not.toBeNull()
    expect((await mv.lastSources(dst)).uscita).toBeDefined()
    // dopo il ripristino le categorie iniziali non vengono ricaricate
    await repo.ensureSeeded(dst)
    expect(await dst.categories.count()).toBe(await src.categories.count())
  })

  it.each([
    ['non json', /formato/],
    [JSON.stringify({ format: 'altro' }), /non è un backup/],
    [JSON.stringify({ format: 'statera-backup', schema: 99, data: {} }), /più recente/],
    [JSON.stringify({ format: 'statera-backup', schema: 1, data: { accounts: [] } }), /danneggiato/],
  ])('rifiuta file non validi (%#)', (text, err) => {
    expect(() => bk.parseBackup(text)).toThrow(err)
  })

  it('azzera e ricarica le categorie di base', async () => {
    await bk.wipeAll(src)
    expect(await src.accounts.count()).toBe(0)
    expect(await src.transactions.count()).toBe(0)
    expect(await src.categories.count()).toBeGreaterThan(10)
  })

  it('backup protetto da password: illeggibile senza, ripristinabile con', async () => {
    const file = await bk.buildBackup('test', src)
    const enc = await bk.encryptBackup(file, 'password-del-backup')
    const text = JSON.stringify(enc)
    expect(text).not.toContain('Esempio')
    expect(text).not.toContain('Conto')
    const read = bk.readBackupFile(text)
    expect('encrypted' in read).toBe(true)
    if (!('encrypted' in read)) return
    await expect(bk.decryptBackup(read.encrypted, 'sbagliata')).rejects.toThrow(/non corretta/)
    const opened = await bk.decryptBackup(read.encrypted, 'password-del-backup')
    expect(bk.summarize(opened)).toMatchObject({ accounts: 1, transactions: 1 })
    // i file in chiaro si leggono ancora
    expect('plain' in bk.readBackupFile(JSON.stringify(file))).toBe(true)
  }, 30_000)

  it('nome file con la data', () => {
    expect(bk.backupFileName(new Date(2026, 10, 3), true)).toBe('statera-backup-protetto-2026-11-03.json')
    expect(bk.backupFileName(new Date(2026, 10, 3))).toBe('statera-backup-2026-11-03.json')
  })
})
