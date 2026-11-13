import { describe, expect, it } from 'vitest'
import { movementsToCsv, csvFileName } from './csv'
import type { Account, Card, Category, Transaction } from './types'

const base = { createdAt: 1, updatedAt: 1, deletedAt: null }
const acc = (id: string, name: string): Account => ({ ...base, id, name, type: 'conto_corrente', initialBalance: 0, initialDate: '2026-01-01', voucherValue: null, initialVouchers: null, color: 's1', order: 1, archived: false })
const refs = {
  accountMap: new Map([['a', acc('a', 'Conto')], ['b', { ...acc('b', 'Buoni'), type: 'buoni_pasto' as const }], ['c', acc('c', 'Contanti')]]),
  cardMap: new Map<string, Card>([['k', { ...base, id: 'k', name: 'Bancomat', accountId: 'a', order: 1, archived: false }]]),
  categoryMap: new Map<string, Category>([
    ['casa', { ...base, id: 'casa', name: 'Casa', kind: 'uscita', parentId: null, color: 's1', order: 1, archived: false }],
    ['boll', { ...base, id: 'boll', name: 'Bollette', kind: 'uscita', parentId: 'casa', color: 's1', order: 1, archived: false }],
  ]),
}
const tx = (over: Partial<Transaction>): Transaction => ({
  ...base, id: Math.random().toString(), type: 'uscita', date: '2026-11-05', categoryId: 'boll', description: '', notes: '',
  parts: [{ accountId: 'a', cardId: null, amount: 1234567, vouchers: null, voucherValue: null }], toAccountId: null, accountIds: ['a'], ...over,
})

describe('CSV per Excel', () => {
  const csv = movementsToCsv(
    [
      tx({ description: 'Luce; "bolletta"', notes: 'riga1\nriga2', date: '2026-11-07' }),
      tx({ description: '=SOMMA(A1)', parts: [{ accountId: 'b', cardId: null, amount: 1600, vouchers: 2, voucherValue: 800 }, { accountId: 'a', cardId: 'k', amount: 740, vouchers: null, voucherValue: null }] }),
      tx({ type: 'trasferimento', categoryId: null, description: 'Prelievo', toAccountId: 'c', parts: [{ accountId: 'a', cardId: null, amount: 5000, vouchers: null, voucherValue: null }] }),
      tx({ description: 'Cancellato', deletedAt: 5 }),
    ],
    refs,
  )
  const lines = csv.split('\r\n')

  it('BOM, intestazione, ordine per data, cancellati esclusi', () => {
    expect(csv.startsWith('﻿Data;Tipo;Categoria;Sottocategoria;Descrizione;Importo;Conto o carta;Verso;Buoni;Note')).toBe(true)
    expect(csv).not.toContain('Cancellato')
    expect(lines[1].startsWith('05/11/2026')).toBe(true)
  })

  it('importi con la virgola e il segno; categorie separate', () => {
    expect(csv).toContain('05/11/2026;Uscita;Casa;Bollette;')
    expect(csv).toContain(';-23,40;Buoni + Bancomat;;2;')
    expect(csv).toContain('05/11/2026;Trasferimento;;;Prelievo;50,00;Conto;Contanti;;')
  })

  it('testo con ; " e a capo correttamente racchiuso', () => {
    expect(csv).toContain('"Luce; ""bolletta"""')
    expect(csv).toContain('-12345,67')
    expect(csv).toContain('"riga1\nriga2"')
  })

  it('niente formule eseguibili', () => {
    expect(csv).toContain(";'=SOMMA(A1);")
  })

  it('nome file', () => {
    expect(csvFileName('2026-11-01', '2026-11-30')).toBe('statera-movimenti-2026-11-01_2026-11-30.csv')
  })
})
