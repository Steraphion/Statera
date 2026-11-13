import Dexie, { type Table } from 'dexie'
import type { Account, Card, Category, Meta, Transaction } from './types'

/**
 * Database locale (IndexedDB). Un database per profilo: oggi c'è un solo
 * profilo locale; con la Fase 2 ogni account Google avrà il proprio.
 */
export class StateraDB extends Dexie {
  accounts!: Table<Account, string>
  cards!: Table<Card, string>
  categories!: Table<Category, string>
  transactions!: Table<Transaction, string>
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
  }
}

export const db = new StateraDB()
