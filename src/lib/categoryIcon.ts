import { CATEGORY_ICONS, isCategoryIconKey, type CategoryIconKey, type IconName } from './icons'
import { seedId } from './data/repo'
import type { AccountType, CategoryKind } from './data/types'

/**
 * Icone predefinite delle categorie iniziali, dal loro id fisso: valgono finché l'utente non ne sceglie
 * un'altra, senza bisogno di aggiornare i dati (e quindi senza modifiche da sincronizzare).
 */
const SEED: [CategoryKind, string[], CategoryIconKey][] = [
  ['uscita', ['Spesa alimentare'], 'spesa'],
  ['uscita', ['Pasti fuori'], 'pasti'],
  ['uscita', ['Casa'], 'casa'],
  ['uscita', ['Casa', 'Affitto/mutuo'], 'affitto'],
  ['uscita', ['Casa', 'Bollette'], 'bollette'],
  ['uscita', ['Casa', 'Manutenzione'], 'manutenzione'],
  ['uscita', ['Trasporti'], 'trasporti'],
  ['uscita', ['Trasporti', 'Carburante'], 'carburante'],
  ['uscita', ['Trasporti', 'Mezzi pubblici'], 'mezzi'],
  ['uscita', ['Trasporti', 'Auto'], 'auto'],
  ['uscita', ['Salute'], 'salute'],
  ['uscita', ['Abbigliamento'], 'abbigliamento'],
  ['uscita', ['Sport'], 'sport'],
  ['uscita', ['Svago'], 'svago'],
  ['uscita', ['Viaggi'], 'viaggi'],
  ['uscita', ['Regali'], 'regali'],
  ['uscita', ['Abbonamenti'], 'abbonamenti'],
  ['uscita', ['Altro'], 'altro'],
  ['uscita', ['Rettifica saldo'], 'rettifica'],
  ['entrata', ['Stipendio'], 'stipendio'],
  ['entrata', ['Buoni pasto'], 'buoni'],
  ['entrata', ['Rimborsi'], 'rimborsi'],
  ['entrata', ['Regali ricevuti'], 'regali'],
  ['entrata', ['Altro'], 'altro'],
  ['entrata', ['Rettifica saldo'], 'rettifica'],
]
export const SEED_ICONS: ReadonlyMap<string, CategoryIconKey> = new Map(SEED.map(([k, names, icon]) => [seedId(k, ...names), icon]))

/** Chiave dell'icona di una categoria: quella scelta, altrimenti la predefinita; null = si mostra l'iniziale. */
export function categoryIconKey(c: { id: string; icon?: string | null }): CategoryIconKey | null {
  if (c.icon === null) return null
  if (isCategoryIconKey(c.icon)) return c.icon
  // Assente (o di una versione più recente dell'app): icona predefinita delle categorie iniziali
  return SEED_ICONS.get(c.id) ?? null
}

export function categoryIconName(c: { id: string; icon?: string | null }): IconName | null {
  const k = categoryIconKey(c)
  return k ? CATEGORY_ICONS[k] : null
}

/** Iniziale del nome, per le categorie senza icona. */
export function initial(name: string): string {
  return (name.trim()[0] ?? '?').toLocaleUpperCase('it')
}

/** Icona di un conto, dal tipo (nessun campo nei dati). */
export const ACCOUNT_ICONS: Record<AccountType, IconName> = {
  conto_corrente: 'landmark',
  contanti: 'banknote',
  buoni_pasto: 'ticket',
  altro: 'piggy-bank',
}
