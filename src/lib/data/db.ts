import Dexie, { type Table } from 'dexie'
import type { Account, Card, Category, Meta, Recurring, Transaction } from './types'
import { activeDbName } from '../profiles'

/**
 * Database locale (IndexedDB). Un database per profilo: ogni account Google
 * ha il proprio (vedi profiles.ts).
 */
export class StateraDB extends Dexie {
  accounts!: Table<Account, string>
  cards!: Table<Card, string>
  categories!: Table<Category, string>
  transactions!: Table<Transaction, string>
  recurring!: Table<Recurring, string>
  meta!: Table<Meta, string>

  constructor(name = 'statera-locale') {
    super(name)
    this.version(1).stores({
      accounts: 'id, updatedAt',
      cards: 'id, accountId, updatedAt',
      categories: 'id, kind, parentId, updatedAt',
      transactions: 'id, date, type, categoryId, *accountIds, updatedAt',
      meta: 'key',
    })
    // v2 (Fase 3): movimenti ricorrenti
    this.version(2).stores({
      recurring: 'id, updatedAt',
    })
  }
}

export const db = new StateraDB(typeof localStorage === 'undefined' ? 'statera-locale' : activeDbName())
