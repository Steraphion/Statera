import 'fake-indexeddb/auto'
import { describe, expect, it } from 'vitest'
import { StateraDB } from './db'
import * as repo from './repo'
import * as im from './csvImport'
import { movementsToCsv } from './csv'

describe('lettura del CSV', () => {
  it('separatore, virgolette, a capo e BOM', () => {
    expect(im.parseCsv('﻿a;b;c\r\n1;"x;""y""";3\r\n\r\n"riga\nnuova";2;3')).toEqual([['a', 'b', 'c'], ['1', 'x;"y"', '3'], ['riga\nnuova', '2', '3']])
    expect(im.parseCsv('Date,Amount\n2026-01-02,"1,234.50"')).toEqual([['Date', 'Amount'], ['2026-01-02', '1,234.50']])
  })
  it('date e importi', () => {
    expect(im.parseDate('05/11/2026')).toBe('2026-11-05')
    expect(im.parseDate('5.1.26')).toBe('2026-01-05')
    expect(im.parseDate('2026-11-05T10:00')).toBe('2026-11-05')
    expect(im.parseDate('31/02/2026')).toBeNull()
    expect(im.parseAmount('-1.234,56')).toBe(-123456)
    expect(im.parseAmount('1,234.56')).toBe(123456)
    expect(im.parseAmount('€ 12,5')).toBe(1250)
    expect(im.parseAmount('12.50-')).toBe(-1250)
    expect(im.parseAmount('(30,00)')).toBe(-3000)
    expect(im.parseAmount('1.000')).toBe(100000)
    expect(im.parseAmount('abc')).toBeNull()
  })
  it('colonne riconosciute', () => {
    expect(im.guessMapping(['Data operazione', 'Descrizione', 'Importo (EUR)', 'Note'])).toEqual({ date: 0, description: 1, amount: 2, notes: 3 })
  })
})

describe('importazione', () => {
  it('dal file esportato da Statera: tipo, categorie, etichette, doppioni', async () => {
    const d = new StateraDB('import-1')
    await d.open()
    await repo.ensureSeeded(d)
    const acc = await repo.createAccount({ name: 'Conto', type: 'conto_corrente', initialBalance: 0, initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1' }, d)
    const cats = await d.categories.toArray()
    const catMap = new Map(cats.map((c) => [c.id, c]))
    const base = { createdAt: 1, updatedAt: 1, deletedAt: null, notes: '', toAccountId: null, accountIds: [acc.id] }
    const csv = movementsToCsv(
      [
        { ...base, id: 'x1', type: 'uscita', date: '2026-11-03', categoryId: repo.seedId('uscita', 'Casa', 'Bollette'), description: 'Luce', parts: [{ accountId: acc.id, cardId: null, amount: 6050, vouchers: null, voucherValue: null }], tags: ['Casa nuova'] },
        { ...base, id: 'x2', type: 'entrata', date: '2026-11-01', categoryId: repo.seedId('entrata', 'Stipendio'), description: 'Stipendio', parts: [{ accountId: acc.id, cardId: null, amount: 150000, vouchers: null, voucherValue: null }] },
        { ...base, id: 'x3', type: 'trasferimento', date: '2026-11-02', categoryId: null, description: 'Prelievo', toAccountId: acc.id, parts: [{ accountId: acc.id, cardId: null, amount: 5000, vouchers: null, voucherValue: null }] },
      ],
      { accountMap: new Map([[acc.id, acc]]), cardMap: new Map(), categoryMap: catMap },
    )
    const rows = im.parseCsv(csv)
    const mapping = im.guessMapping(rows[0])
    expect(mapping).toMatchObject({ date: 0, type: 1, category: 2, subcategory: 3, description: 4, amount: 5, notes: 9, tags: 10 })
    let items = im.buildImport(rows, mapping, { accountId: acc.id, categories: cats, existing: [], hasHeader: true })
    const luce = items.find((i) => i.description === 'Luce')!
    expect([luce.type, luce.amount, luce.categoryId, luce.tags]).toEqual(['uscita', 6050, repo.seedId('uscita', 'Casa', 'Bollette'), ['Casa nuova']])
    expect(items.find((i) => i.description === 'Prelievo')!.problem).toContain('Trasferimento')
    expect(await im.importItems(items, acc.id, true, d)).toBe(2)
    // reimportando lo stesso file: tutti doppioni
    items = im.buildImport(rows, mapping, { accountId: acc.id, categories: cats, existing: await d.transactions.toArray(), hasHeader: true })
    expect(items.filter((i) => i.duplicate)).toHaveLength(2)
    expect(await im.importItems(items, acc.id, true, d)).toBe(0)
  })
  it('estratto conto della banca: segno per il tipo, categoria "Altro" se sconosciuta', async () => {
    const d = new StateraDB('import-2')
    await d.open()
    await repo.ensureSeeded(d)
    const cats = await d.categories.toArray()
    const rows = im.parseCsv('Data;Descrizione;Importo\n03/11/2026;PAGAMENTO POS SUPERMERCATO;-45,20\n04/11/2026;BONIFICO RICEVUTO;300,00\n05/11/2026;RIGA ROTTA;xx\n03/11/2026;PAGAMENTO POS SUPERMERCATO;-45,20')
    const items = im.buildImport(rows, im.guessMapping(rows[0]), { accountId: 'a', categories: cats, existing: [], hasHeader: true })
    expect(items.map((i) => [i.type, i.amount, i.categoryGuessed])).toEqual([['uscita', 4520, true], ['entrata', 30000, true], [null, 0, false], ['uscita', 4520, true]])
    expect(items[0].categoryId).toBe(repo.seedId('uscita', 'Altro'))
    expect(items[2].problem).toContain('Importo')
    expect(items[3].duplicate).toBe(true)
  })
})
