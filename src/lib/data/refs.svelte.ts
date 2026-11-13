import { db } from './db'
import { live } from './live.svelte'
import { lastSources } from './transactions'
import type { Account, Card, Category, TransactionType } from './types'
import { alive, byName, byOrder } from './util'

export interface Refs {
  accounts: Account[]
  cards: Card[]
  categories: Category[]
  lastSources: Partial<Record<TransactionType, string>>
  accountMap: Map<string, Account>
  cardMap: Map<string, Card>
  categoryMap: Map<string, Category>
}

/**
 * Dati di riferimento usati da molte schermate (conti, carte, categorie),
 * sempre aggiornati. Va chiamata durante l'inizializzazione di un componente.
 */
export function useRefs() {
  return live<Refs>(
    async () => {
      const [accounts, cards, categories, last] = await Promise.all([
        db.accounts.toArray(),
        db.cards.toArray(),
        db.categories.toArray(),
        lastSources(),
      ])
      const a = alive(accounts).sort(byOrder)
      const c = alive(cards).sort(byOrder)
      const k = alive(categories).sort(byName) // categorie sempre in ordine alfabetico
      return {
        accounts: a,
        cards: c,
        categories: k,
        lastSources: last,
        accountMap: new Map(a.map((x) => [x.id, x])),
        cardMap: new Map(c.map((x) => [x.id, x])),
        categoryMap: new Map(k.map((x) => [x.id, x])),
      }
    },
    {
      accounts: [],
      cards: [],
      categories: [],
      lastSources: {},
      accountMap: new Map(),
      cardMap: new Map(),
      categoryMap: new Map(),
    },
  )
}
