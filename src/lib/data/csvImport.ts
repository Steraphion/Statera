import { db, type StateraDB } from './db'
import { createMovement, normalize, total } from './transactions'
import { seedId } from './repo'
import type { Category, CategoryKind, Transaction } from './types'

/**
 * Importazione di movimenti da un file CSV (es. l'estratto conto della banca, o un file esportato da Statera).
 * Tutto avviene sul dispositivo. I trasferimenti non si importano; i movimenti già presenti si possono saltare.
 */

export type Field = 'date' | 'amount' | 'description' | 'category' | 'subcategory' | 'type' | 'notes' | 'tags'
export type Mapping = Partial<Record<Field, number>>

export const FIELD_LABELS: Record<Field, string> = {
  date: 'Data',
  amount: 'Importo',
  description: 'Descrizione',
  category: 'Categoria',
  subcategory: 'Sottocategoria',
  type: 'Tipo (entrata/uscita)',
  notes: 'Note',
  tags: 'Etichette',
}

/** Legge il CSV: separatore riconosciuto da solo (; , o tabulazione), virgolette, a capo dentro i campi. */
export function parseCsv(text: string): string[][] {
  const s = text.replace(/^﻿/, '')
  const firstLine = s.split(/\r?\n/, 1)[0] ?? ''
  const count = (ch: string) => {
    let n = 0
    let q = false
    for (const c of firstLine) {
      if (c === '"') q = !q
      else if (!q && c === ch) n++
    }
    return n
  }
  const sep = [';', ',', '\t'].sort((a, b) => count(b) - count(a))[0]
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let q = false
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    if (q) {
      if (c === '"' && s[i + 1] === '"') {
        field += '"'
        i++
      } else if (c === '"') q = false
      else field += c
    } else if (c === '"') q = true
    else if (c === sep) {
      row.push(field)
      field = ''
    } else if (c === '\n' || c === '\r') {
      if (c === '\r' && s[i + 1] === '\n') i++
      row.push(field)
      field = ''
      if (row.some((x) => x.trim() !== '')) rows.push(row)
      row = []
    } else field += c
  }
  row.push(field)
  if (row.some((x) => x.trim() !== '')) rows.push(row)
  return rows
}

const NAMES: Record<Field, string[]> = {
  date: ['data', 'date', 'data operazione', 'data contabile', 'data valuta', 'giorno'],
  amount: ['importo', 'amount', 'valore', 'importo (eur)', 'importo eur', 'euro', 'totale'],
  description: ['descrizione', 'description', 'causale', 'dettagli', 'operazione', 'beneficiario', 'titolo'],
  category: ['categoria', 'category'],
  subcategory: ['sottocategoria', 'subcategory', 'sotto categoria'],
  type: ['tipo', 'type', 'entrata/uscita'],
  notes: ['note', 'notes', 'memo', 'nota'],
  tags: ['etichette', 'tags', 'etichetta', 'tag'],
}

/** Colonne riconosciute dall'intestazione. */
export function guessMapping(header: string[]): Mapping {
  const h = header.map((x) => normalize(x).trim())
  const m: Mapping = {}
  for (const f of Object.keys(NAMES) as Field[]) {
    const i = h.findIndex((x, k) => NAMES[f].includes(x) && !Object.values(m).includes(k))
    if (i >= 0) m[f] = i
  }
  return m
}

/** Date in formato gg/mm/aaaa, gg-mm-aaaa, gg.mm.aa o aaaa-mm-gg → 'AAAA-MM-GG'. */
export function parseDate(s: string): string | null {
  const t = s.trim().slice(0, 10)
  let y: number, m: number, d: number
  let r = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(t)
  if (r) [y, m, d] = [Number(r[1]), Number(r[2]), Number(r[3])]
  else {
    r = /^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2}|\d{4})$/.exec(t)
    if (!r) return null
    ;[d, m, y] = [Number(r[1]), Number(r[2]), Number(r[3])]
    if (y < 100) y += 2000
  }
  const dt = new Date(y, m - 1, d)
  if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

/** Importi italiani ("-1.234,56") o inglesi ("1,234.56"), anche con € → centesimi con segno. */
export function parseAmount(s: string): number | null {
  let t = s.replace(/[€\s ]|EUR/gi, '')
  if (!t) return null
  let sign = 1
  if (/^\(.*\)$/.test(t)) {
    sign = -1
    t = t.slice(1, -1)
  }
  if (t.startsWith('-')) {
    sign = -sign
    t = t.slice(1)
  } else if (t.startsWith('+')) t = t.slice(1)
  if (t.endsWith('-')) {
    sign = -sign
    t = t.slice(0, -1)
  }
  const lastComma = t.lastIndexOf(',')
  const lastDot = t.lastIndexOf('.')
  if (lastComma >= 0 && lastDot >= 0) {
    t = lastComma > lastDot ? t.replace(/\./g, '').replace(',', '.') : t.replace(/,/g, '')
  } else if (lastComma >= 0) {
    t = /,\d{1,2}$/.test(t) && t.split(',').length === 2 ? t.replace(',', '.') : t.replace(/,/g, '')
  } else if (lastDot >= 0 && /^\d{1,3}(\.\d{3})+$/.test(t)) {
    t = t.replace(/\./g, '')
  }
  if (!/^\d+(\.\d{1,2})?$/.test(t)) return null
  const [int, dec = ''] = t.split('.')
  return sign * (Number(int) * 100 + Number(dec.padEnd(2, '0')))
}

export interface ImportItem {
  line: number
  date: string | null
  type: CategoryKind | null
  amount: number
  description: string
  notes: string
  tags: string[]
  categoryId: string | null
  /** Categoria non trovata per nome: si usa "Altro". */
  categoryGuessed: boolean
  duplicate: boolean
  problem: string | null
}

function findCategory(categories: Category[], kind: CategoryKind, name: string, sub: string): { id: string | null; guessed: boolean } {
  const alive = categories.filter((c) => c.deletedAt === null && c.kind === kind)
  const k = (x: string) => normalize(x).replace(/\s+/g, ' ').trim()
  const top = name ? alive.find((c) => c.parentId === null && k(c.name) === k(name)) : undefined
  if (top && sub) {
    const child = alive.find((c) => c.parentId === top.id && k(c.name) === k(sub))
    if (child) return { id: child.id, guessed: false }
  }
  if (top) return { id: top.id, guessed: false }
  // Una sottocategoria scritta da sola (es. "Bollette")
  const any = name ? alive.find((c) => k(c.name) === k(name)) : undefined
  if (any) return { id: any.id, guessed: false }
  const altro = alive.find((c) => c.id === seedId(kind, 'Altro')) ?? alive.find((c) => c.parentId === null && k(c.name) === 'altro')
  return { id: altro?.id ?? alive.find((c) => c.parentId === null)?.id ?? null, guessed: true }
}

/** Prepara le righe da importare (con l'anteprima di cosa succederà a ognuna). */
export function buildImport(
  rows: string[][],
  mapping: Mapping,
  opts: { accountId: string; categories: Category[]; existing: Transaction[]; hasHeader: boolean },
): ImportItem[] {
  const body = opts.hasHeader ? rows.slice(1) : rows
  const cell = (r: string[], f: Field) => (mapping[f] !== undefined ? (r[mapping[f]!] ?? '').trim() : '')
  const seen = new Set(
    opts.existing
      .filter((t) => t.deletedAt === null && t.accountIds.includes(opts.accountId) && t.type !== 'trasferimento')
      .map((t) => `${t.date}|${t.type}|${total(t)}|${normalize(t.description).trim()}`),
  )
  return body.map((r, i) => {
    const date = parseDate(cell(r, 'date'))
    const signed = parseAmount(cell(r, 'amount'))
    const typeText = normalize(cell(r, 'type'))
    let type: CategoryKind | null = null
    let problem: string | null = null
    if (/trasf/.test(typeText)) problem = 'Trasferimento: non si importa'
    else if (/^(entrata|income|accredito|in)/.test(typeText)) type = 'entrata'
    else if (/^(uscita|spesa|expense|addebito|out)/.test(typeText)) type = 'uscita'
    else if (signed !== null) type = signed < 0 ? 'uscita' : 'entrata'
    const amount = Math.abs(signed ?? 0)
    if (!problem && !date) problem = 'Data non riconosciuta'
    else if (!problem && (signed === null || amount === 0)) problem = 'Importo non valido'
    const description = cell(r, 'description').slice(0, 80)
    const cat = type ? findCategory(opts.categories, type, cell(r, 'category'), cell(r, 'subcategory')) : { id: null, guessed: false }
    if (!problem && type && !cat.id) problem = 'Nessuna categoria disponibile'
    const key = `${date}|${type}|${amount}|${normalize(description).trim()}`
    const duplicate = !problem && seen.has(key)
    if (!problem && !duplicate) seen.add(key) // righe ripetute nello stesso file: la seconda è un doppione
    return {
      line: i + (opts.hasHeader ? 2 : 1),
      date,
      type,
      amount,
      description,
      notes: cell(r, 'notes').slice(0, 500),
      tags: cell(r, 'tags')
        .split(/[,;]/)
        .map((x) => x.trim())
        .filter(Boolean)
        .slice(0, 5),
      categoryId: cat.id,
      categoryGuessed: cat.guessed,
      duplicate,
      problem,
    }
  })
}

/** Importa le righe valide (saltando i doppioni se richiesto). Restituisce quanti movimenti sono stati creati. */
export async function importItems(items: ImportItem[], accountId: string, skipDuplicates: boolean, d: StateraDB = db): Promise<number> {
  let n = 0
  for (const it of items) {
    if (it.problem || !it.date || !it.type || !it.categoryId) continue
    if (skipDuplicates && it.duplicate) continue
    await createMovement(
      {
        type: it.type,
        date: it.date,
        parts: [{ source: `a:${accountId}`, amount: it.amount, vouchers: null }],
        categoryId: it.categoryId,
        toAccountId: null,
        description: it.description,
        notes: it.notes,
        tags: it.tags,
      },
      d,
      { remember: false },
    )
    n++
  }
  return n
}
