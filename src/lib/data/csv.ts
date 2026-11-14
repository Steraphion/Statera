import { categoryShares, partLabel, sortMovements, total } from './transactions'
import type { Account, Card, Category, Transaction } from './types'

/**
 * Esportazione CSV pensata per Excel in italiano:
 * separatore ";", decimali con la virgola, date gg/mm/aaaa, codifica UTF-8 con BOM
 * (così Excel legge gli accenti), righe CRLF.
 * Protezione da "formula injection": un testo che inizia con = + - @ viene preceduto da '
 * (altrimenti Excel potrebbe eseguirlo come formula).
 */

const HEADER = ['Data', 'Tipo', 'Categoria', 'Sottocategoria', 'Descrizione', 'Importo', 'Conto o carta', 'Verso', 'Buoni', 'Note', 'Etichette']

const TYPE: Record<Transaction['type'], string> = { entrata: 'Entrata', uscita: 'Uscita', trasferimento: 'Trasferimento' }

function text(v: string): string {
  let s = v ?? ''
  if (/^[=+\-@\t\r]/.test(s)) s = `'${s}`
  return field(s)
}

function field(s: string): string {
  return /[;"\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function amount(cents: number): string {
  const sign = cents < 0 ? '-' : ''
  const abs = Math.abs(cents)
  return `${sign}${Math.floor(abs / 100)},${String(abs % 100).padStart(2, '0')}`
}

function date(day: string): string {
  const [y, m, d] = day.split('-')
  return `${d}/${m}/${y}`
}

export function movementsToCsv(
  rows: Transaction[],
  refs: { accountMap: Map<string, Account>; cardMap: Map<string, Card>; categoryMap: Map<string, Category> },
): string {
  const lines = [HEADER.join(';')]
  for (const t of sortMovements(rows.filter((r) => r.deletedAt === null)).reverse()) {
    const sign = t.type === 'uscita' ? -1 : 1
    const vouchers = t.parts.reduce((s, p) => s + (p.vouchers ?? 0), 0)
    const shares = categoryShares(t)
    // Movimento ripartito: una riga per categoria, così in Excel i totali per categoria tornano
    const pieces = shares.length >= 2 ? shares : [{ categoryId: t.categoryId, amount: total(t) }]
    pieces.forEach((piece, i) => {
      const c = piece.categoryId ? refs.categoryMap.get(piece.categoryId) : undefined
      const parent = c?.parentId ? refs.categoryMap.get(c.parentId) : undefined
      const desc = pieces.length > 1 ? `${t.description}${t.description ? ' ' : ''}(parte ${i + 1} di ${pieces.length})` : t.description
      lines.push(
        [
          date(t.date),
          TYPE[t.type],
          text(parent ? parent.name : (c?.name ?? '')),
          text(parent ? (c?.name ?? '') : ''),
          text(desc),
          amount(sign * piece.amount),
          text(t.parts.map((p) => partLabel(p, refs.accountMap, refs.cardMap)).join(' + ')),
          text(t.toAccountId ? (refs.accountMap.get(t.toAccountId)?.name ?? '') : ''),
          vouchers && i === 0 ? String(vouchers) : '',
          text(i === 0 ? t.notes : ''),
          text((t.tags ?? []).join(', ')),
        ].join(';'),
      )
    })
  }
  return '\uFEFF' + lines.join('\r\n') + '\r\n'
}

export function csvFileName(from: string, to: string): string {
  return from && to ? `statera-movimenti-${from}_${to}.csv` : 'statera-movimenti.csv'
}

/** Scarica il testo come file (nel browser). */
export function downloadText(content: string, name: string, type = 'text/csv;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const a = document.createElement('a')
  a.href = url
  a.download = name
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
}
