import { db, type StateraDB } from './db'
import { isCategoryIconKey } from '../icons'
import type { Account, AccountType, Card, Category, CategoryKind, SwatchKey } from './types'
import { baseFields, today } from './util'

/*
 * Operazioni sui dati. Tutte le modifiche passano da qui, così
 * updatedAt e la cancellazione logica sono sempre gestiti allo stesso modo.
 */

// ---------- Conti ----------

export interface AccountInput {
  name: string
  type: AccountType
  /** Per i buoni pasto viene ignorato: si usa initialVouchers × voucherValue. */
  initialBalance: number
  initialDate: string
  voucherValue: number | null
  initialVouchers: number | null
  color: SwatchKey
}

function normalizeAccount(input: AccountInput): AccountInput {
  const name = input.name.trim()
  if (!name) throw new Error('Il nome del conto è obbligatorio')
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.initialDate)) throw new Error('Indica la data del saldo')
  // Solo i campi del conto: un oggetto con altri campi (es. un conto esistente) non li porta con sé
  const base = { name, type: input.type, initialDate: input.initialDate, color: input.color }
  if (input.type === 'buoni_pasto') {
    const value = input.voucherValue ?? 0
    const count = input.initialVouchers ?? 0
    if (value <= 0) throw new Error('Indica il valore di un buono')
    if (!Number.isInteger(count) || count < 0) throw new Error('Il numero di buoni non è valido')
    return { ...base, voucherValue: value, initialVouchers: count, initialBalance: value * count }
  }
  return { ...base, initialBalance: input.initialBalance, voucherValue: null, initialVouchers: null }
}

export async function createAccount(input: AccountInput, d: StateraDB = db): Promise<Account> {
  const data = normalizeAccount(input)
  const order = (await d.accounts.count()) + 1
  const account: Account = { ...baseFields(), ...data, order, archived: false }
  await d.accounts.add(account)
  return account
}

/**
 * Nuovo conto e, se indicata, la sua carta di debito, insieme (es. conto corrente + "Carta del conto").
 * La carta si crea solo per i tipi che possono averne.
 */
export async function createAccountWithCard(input: AccountInput, cardName: string, d: StateraDB = db): Promise<Account> {
  const card = cardName.replace(/\s+/g, ' ').trim()
  if (card && input.type !== 'conto_corrente' && input.type !== 'altro') {
    throw new Error('Si può collegare una carta solo a un conto corrente o a un altro conto')
  }
  return d.transaction('rw', d.accounts, d.cards, async () => {
    const account = await createAccount(input, d)
    if (card) await createCard({ name: card, accountId: account.id }, d)
    return account
  })
}

export async function updateAccount(id: string, input: AccountInput, d: StateraDB = db) {
  const data = normalizeAccount(input)
  await d.transaction('rw', d.accounts, d.cards, async () => {
    await d.accounts.update(id, { ...data, updatedAt: Date.now() })
    // Un conto che non può più avere carte (es. diventato contanti) le perde
    if (data.type === 'contanti' || data.type === 'buoni_pasto') {
      const linked = await d.cards.where('accountId').equals(id).toArray()
      for (const c of linked.filter((c) => c.deletedAt === null)) {
        await d.cards.update(c.id, { deletedAt: Date.now(), updatedAt: Date.now() })
      }
    }
  })
}

export async function setAccountArchived(id: string, archived: boolean, d: StateraDB = db) {
  await d.accounts.update(id, { archived, updatedAt: Date.now() })
}

export async function accountHasTransactions(id: string, d: StateraDB = db): Promise<boolean> {
  const rows = await d.transactions.where('accountIds').equals(id).toArray()
  return rows.some((t) => t.deletedAt === null)
}

/** Elimina un conto (e le sue carte). Non permesso se ha movimenti: in quel caso si archivia. */
export async function deleteAccount(id: string, d: StateraDB = db) {
  if (await accountHasTransactions(id, d)) {
    throw new Error('Il conto ha dei movimenti: puoi archiviarlo ma non eliminarlo')
  }
  const now = Date.now()
  await d.transaction('rw', d.accounts, d.cards, async () => {
    await d.accounts.update(id, { deletedAt: now, updatedAt: now })
    const linked = await d.cards.where('accountId').equals(id).toArray()
    for (const c of linked) await d.cards.update(c.id, { deletedAt: now, updatedAt: now })
  })
}

// ---------- Carte ----------

export interface CardInput {
  name: string
  accountId: string
}

function normalizeCard(input: CardInput): CardInput {
  const name = input.name.trim()
  if (!name) throw new Error('Il nome della carta è obbligatorio')
  if (!input.accountId) throw new Error('Scegli il conto collegato')
  return { name, accountId: input.accountId }
}

export async function createCard(input: CardInput, d: StateraDB = db): Promise<Card> {
  const order = (await d.cards.count()) + 1
  const card: Card = { ...baseFields(), ...normalizeCard(input), order, archived: false }
  await d.cards.add(card)
  return card
}

export async function updateCard(id: string, input: CardInput, d: StateraDB = db) {
  await d.cards.update(id, { ...normalizeCard(input), updatedAt: Date.now() })
}

export async function setCardArchived(id: string, archived: boolean, d: StateraDB = db) {
  await d.cards.update(id, { archived, updatedAt: Date.now() })
}

export async function deleteCard(id: string, d: StateraDB = db) {
  const rows = await d.transactions.toArray()
  if (rows.some((t) => t.deletedAt === null && t.parts.some((p) => p.cardId === id))) {
    throw new Error('La carta è usata in alcuni movimenti: puoi archiviarla ma non eliminarla')
  }
  await d.cards.update(id, { deletedAt: Date.now(), updatedAt: Date.now() })
}

// ---------- Categorie ----------

export interface CategoryInput {
  name: string
  kind: CategoryKind
  parentId: string | null
  color: SwatchKey
  /** Chiave dell'icona; null = nessuna (iniziale); non indicata = resta com'è. */
  icon?: string | null
}

async function normalizeCategory(input: CategoryInput, selfId: string | null, d: StateraDB) {
  const name = input.name.trim()
  if (!name) throw new Error('Il nome della categoria è obbligatorio')
  if (input.parentId) {
    const parent = await d.categories.get(input.parentId)
    if (!parent || parent.deletedAt !== null) throw new Error('Categoria principale non trovata')
    if (parent.parentId !== null) throw new Error('Sono ammessi solo due livelli')
    if (parent.kind !== input.kind) throw new Error('La sottocategoria deve essere dello stesso tipo')
    if (parent.id === selfId) throw new Error('Una categoria non può contenere se stessa')
    if (selfId) {
      const children = await d.categories.where('parentId').equals(selfId).toArray()
      if (children.some((c) => c.deletedAt === null)) {
        throw new Error('Questa categoria ha sottocategorie: non può diventare a sua volta una sottocategoria')
      }
    }
  }
  await assertNoTwin(name, input.kind, input.parentId ?? null, selfId, d)
  const { icon, ...rest } = input
  if (icon === undefined) return { ...rest, name }
  return { ...rest, name, icon: isCategoryIconKey(icon) ? icon : null }
}

/** Minuscolo, senza accenti e spazi doppi: «Caffè » e «caffe» sono lo stesso nome. */
function sameName(a: string, b: string): boolean {
  const k = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim()
  return k(a) === k(b)
}

/**
 * Niente due categorie con lo stesso nome nello stesso posto (stesso tipo e stessa categoria principale),
 * archiviate comprese: chi crea una categoria dal modulo del movimento spesso non ha visto che c'era già.
 * Modificando una categoria il controllo vale solo se cambiano nome, tipo o posto, così i doppioni
 * nati prima della v0.36 restano modificabili.
 */
async function assertNoTwin(name: string, kind: CategoryKind, parentId: string | null, selfId: string | null, d: StateraDB) {
  if (selfId) {
    const self = await d.categories.get(selfId)
    if (self && sameName(self.name, name) && self.kind === kind && self.parentId === parentId) return
  }
  const twin = (await d.categories.toArray()).find(
    (c) => c.deletedAt === null && c.id !== selfId && c.kind === kind && c.parentId === parentId && sameName(c.name, name),
  )
  if (!twin) return
  const where = parentId ? ' qui dentro' : kind === 'uscita' ? ' tra le uscite' : ' tra le entrate'
  throw new Error(
    twin.archived
      ? `La categoria «${twin.name}» esiste già${where}, archiviata: ripristinala da Altro → Categorie`
      : `La categoria «${twin.name}» esiste già${where}`,
  )
}

export async function createCategory(input: CategoryInput, d: StateraDB = db): Promise<Category> {
  const data = await normalizeCategory(input, null, d)
  const order = (await d.categories.count()) + 1
  const cat: Category = { ...baseFields(), ...data, order, archived: false }
  await d.categories.add(cat)
  return cat
}

export async function updateCategory(id: string, input: CategoryInput, d: StateraDB = db) {
  const data = await normalizeCategory(input, id, d)
  await d.transaction('rw', d.categories, async () => {
    await d.categories.update(id, { ...data, updatedAt: Date.now() })
    // Se cambia tipo, le sottocategorie lo seguono
    const children = await d.categories.where('parentId').equals(id).toArray()
    for (const c of children) {
      if (c.kind !== data.kind) await d.categories.update(c.id, { kind: data.kind, updatedAt: Date.now() })
    }
  })
}

/** Budget mensile di una categoria principale di spesa (null = nessun budget). */
export async function setCategoryBudget(id: string, cents: number | null, d: StateraDB = db) {
  const c = await d.categories.get(id)
  if (!c || c.deletedAt !== null) throw new Error('Categoria non trovata')
  if (c.parentId !== null || c.kind !== 'uscita') throw new Error('Il budget si imposta sulle categorie principali di spesa')
  if (cents !== null && (!Number.isInteger(cents) || cents <= 0)) throw new Error('Il budget deve essere un importo maggiore di zero')
  await d.categories.update(id, { monthlyBudget: cents, updatedAt: Date.now() })
}

export async function setCategoryArchived(id: string, archived: boolean, d: StateraDB = db) {
  const now = Date.now()
  await d.transaction('rw', d.categories, async () => {
    await d.categories.update(id, { archived, updatedAt: now })
    if (archived) {
      const children = await d.categories.where('parentId').equals(id).toArray()
      for (const c of children) await d.categories.update(c.id, { archived: true, updatedAt: now })
    }
  })
}

export async function deleteCategory(id: string, d: StateraDB = db) {
  const children = (await d.categories.where('parentId').equals(id).toArray()).filter(
    (c) => c.deletedAt === null,
  )
  const ids = [id, ...children.map((c) => c.id)]
  const used = await d.transactions.where('categoryId').anyOf(ids).toArray()
  if (used.some((t) => t.deletedAt === null)) {
    throw new Error('La categoria è usata in alcuni movimenti: puoi archiviarla ma non eliminarla')
  }
  const now = Date.now()
  await d.transaction('rw', d.categories, async () => {
    for (const cid of ids) await d.categories.update(cid, { deletedAt: now, updatedAt: now })
  })
}

// ---------- Primo avvio ----------

const DEFAULT_CATEGORIES: { kind: CategoryKind; name: string; color: SwatchKey; children?: string[] }[] = [
  { kind: 'uscita', name: 'Spesa alimentare', color: 's1' },
  { kind: 'uscita', name: 'Pasti fuori', color: 's2' },
  { kind: 'uscita', name: 'Casa', color: 's3', children: ['Affitto/mutuo', 'Bollette', 'Manutenzione'] },
  { kind: 'uscita', name: 'Trasporti', color: 's4', children: ['Carburante', 'Mezzi pubblici', 'Auto'] },
  { kind: 'uscita', name: 'Salute', color: 's5' },
  { kind: 'uscita', name: 'Abbigliamento', color: 's6' },
  { kind: 'uscita', name: 'Sport', color: 's7' },
  { kind: 'uscita', name: 'Svago', color: 's8' },
  { kind: 'uscita', name: 'Viaggi', color: 's1' },
  { kind: 'uscita', name: 'Regali', color: 's2' },
  { kind: 'uscita', name: 'Abbonamenti', color: 's3' },
  { kind: 'uscita', name: 'Altro', color: 's4' },
  { kind: 'entrata', name: 'Stipendio', color: 's5' },
  { kind: 'entrata', name: 'Buoni pasto', color: 's6' },
  { kind: 'entrata', name: 'Rimborsi', color: 's7' },
  { kind: 'entrata', name: 'Regali ricevuti', color: 's8' },
  { kind: 'entrata', name: 'Altro', color: 's1' },
]

/** Id fisso delle categorie iniziali: uguale su tutti i dispositivi, così la sincronizzazione non crea doppioni. */
export function seedId(kind: CategoryKind, ...names: string[]): string {
  const slug = (n: string) =>
    n
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
  return ['seed', kind, ...names.map(slug)].join('-')
}

export const ADJUST_CATEGORY_NAME = 'Rettifica saldo'

/**
 * Categoria per i movimenti di "Allinea saldo". Ha un id fisso, così due dispositivi non ne creano
 * due copie; se era stata cancellata o archiviata torna disponibile.
 */
export async function ensureAdjustCategory(kind: CategoryKind, d: StateraDB = db): Promise<Category> {
  const id = seedId(kind, ADJUST_CATEGORY_NAME)
  const existing = await d.categories.get(id)
  const now = Date.now()
  if (existing) {
    if (existing.deletedAt !== null || existing.archived) {
      await d.categories.update(id, { deletedAt: null, archived: false, updatedAt: now })
    }
    return (await d.categories.get(id))!
  }
  const cat: Category = {
    ...baseFields(),
    id,
    name: ADJUST_CATEGORY_NAME,
    kind,
    parentId: null,
    color: 's4',
    order: (await d.categories.count()) + 1,
    archived: false,
  }
  await d.categories.add(cat)
  return cat
}

/** Al primo avvio carica le categorie iniziali. Non si ripete mai, anche se le cancelli. */
export async function ensureSeeded(d: StateraDB = db) {
  await d.transaction('rw', d.meta, d.categories, async () => {
    if (await d.meta.get('seeded')) return
    const now = Date.now()
    let order = 0
    for (const def of DEFAULT_CATEGORIES) {
      const parentId = seedId(def.kind, def.name)
      await d.categories.put({
        id: parentId,
        createdAt: now,
        updatedAt: now,
        deletedAt: null,
        name: def.name,
        kind: def.kind,
        parentId: null,
        color: def.color,
        order: ++order,
        archived: false,
      })
      for (const child of def.children ?? []) {
        await d.categories.put({
          id: seedId(def.kind, def.name, child),
          createdAt: now,
          updatedAt: now,
          deletedAt: null,
          name: child,
          kind: def.kind,
          parentId,
          color: def.color,
          order: ++order,
          archived: false,
        })
      }
    }
    await d.meta.put({ key: 'seeded', value: { at: now, date: today() } })
  })
}

// ---------- Ordine ----------

/** Sposta un conto di una posizione (su = -1, giù = +1) tra i conti attivi. */
/** Sposta un conto di un posto, dentro il suo gruppo (stesso tipo): Conti mostra i conti divisi per tipo. */
export async function moveAccount(id: string, dir: -1 | 1, d: StateraDB = db) {
  await d.transaction('rw', d.accounts, async () => {
    const list = (await d.accounts.toArray())
      .filter((a) => a.deletedAt === null && !a.archived)
      .sort((a, b) => a.order - b.order || a.name.localeCompare(b.name, 'it'))
    const i = list.findIndex((a) => a.id === id)
    if (i < 0) return
    const group = list.filter((a) => a.type === list[i].type)
    const gi = group.findIndex((a) => a.id === id)
    const other = group[gi + dir]
    if (!other) return
    const j = list.indexOf(other)
    ;[list[i], list[j]] = [list[j], list[i]]
    const now = Date.now()
    // Rinumera tutti: ordine sempre compatto e senza pari merito
    for (let k = 0; k < list.length; k++) {
      if (list[k].order !== k + 1) await d.accounts.update(list[k].id, { order: k + 1, updatedAt: now })
    }
  })
}

// ---------- Guida al primo avvio ----------

export async function guideDismissed(d: StateraDB = db): Promise<boolean> {
  return !!(await d.meta.get('guidaChiusa'))?.value
}

export async function dismissGuide(d: StateraDB = db) {
  await d.meta.put({ key: 'guidaChiusa', value: true })
}

// ---------- Riepilogo del mese ----------

export async function recapSeen(d: StateraDB = db): Promise<string | null> {
  return ((await d.meta.get('riepilogoVisto'))?.value as string | undefined) ?? null
}

export async function setRecapSeen(month: string, d: StateraDB = db) {
  await d.meta.put({ key: 'riepilogoVisto', value: month })
}
