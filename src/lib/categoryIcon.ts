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

/**
 * Parole del nome → icona, per le categorie senza un'icona scelta: le categorie iniziali create da
 * versioni precedenti (con id diversi da quelli fissi) e quelle nuove ("Palestra" → manubrio).
 * Vale la prima parola del nome che corrisponde; le voci lunghe valgono anche come inizio di parola.
 */
const WORDS: [CategoryIconKey, string[]][] = [
  ['spesa', ['spesa', 'spese', 'supermercato', 'alimentari', 'alimentare', 'cibo', 'market']],
  ['pasti', ['pasti', 'pasto', 'ristorante', 'ristoranti', 'pranzo', 'pranzi', 'cena', 'cene', 'mensa', 'trattoria', 'sushi']],
  ['caffe', ['caffe', 'bar', 'caffetteria']],
  ['colazione', ['colazione', 'colazioni', 'cornetto']],
  ['pizza', ['pizza', 'pizzeria']],
  ['vino', ['vino', 'vini', 'aperitivo', 'aperitivi']],
  ['birra', ['birra', 'birre', 'pub']],
  ['gelato', ['gelato', 'gelati', 'dolci', 'pasticceria']],
  ['affitto', ['affitto', 'affitti', 'mutuo', 'condominio']],
  ['bollette', ['bollette', 'bolletta', 'luce', 'gas', 'acqua', 'energia', 'utenze']],
  ['manutenzione', ['manutenzione', 'riparazioni', 'riparazione', 'lavori']],
  ['arredamento', ['arredamento', 'mobili', 'arredo']],
  ['elettrodomestici', ['elettrodomestici', 'elettrodomestico']],
  ['internet', ['internet', 'wifi', 'fibra']],
  ['telefono', ['telefono', 'telefonia', 'cellulare', 'ricarica', 'ricariche']],
  ['tv', ['tv', 'televisione', 'streaming', 'netflix']],
  ['casa', ['casa', 'domestico', 'pulizie']],
  ['carburante', ['carburante', 'benzina', 'gasolio', 'diesel', 'rifornimento']],
  ['mezzi', ['mezzi', 'autobus', 'bus', 'metro', 'metropolitana', 'tram']],
  ['treno', ['treno', 'treni', 'trenitalia', 'italo']],
  ['taxi', ['taxi', 'uber']],
  ['parcheggio', ['parcheggio', 'parcheggi', 'pedaggio', 'pedaggi', 'autostrada', 'telepass']],
  ['traghetto', ['traghetto', 'traghetti', 'nave']],
  ['bici', ['bici', 'bicicletta', 'monopattino']],
  ['auto', ['auto', 'macchina', 'bollo', 'meccanico', 'officina', 'moto']],
  ['trasporti', ['trasporti', 'trasporto', 'spostamenti']],
  ['farmaci', ['farmacia', 'farmaci', 'medicine', 'medicinali']],
  ['medico', ['medico', 'medici', 'visite', 'visita', 'dentista', 'analisi', 'ospedale']],
  ['ottico', ['ottico', 'occhiali', 'lenti']],
  ['parrucchiere', ['parrucchiere', 'barbiere', 'capelli']],
  ['bellezza', ['bellezza', 'cosmetici', 'estetista', 'profumi']],
  ['salute', ['salute', 'benessere']],
  ['abbigliamento', ['abbigliamento', 'vestiti', 'vestiario', 'scarpe', 'abiti']],
  ['sport', ['sport', 'palestra', 'piscina', 'calcio', 'pallavolo', 'volley', 'corsa', 'triathlon', 'fitness']],
  ['cinema', ['cinema', 'film', 'teatro']],
  ['musica', ['musica', 'concerti', 'concerto', 'spotify']],
  ['libri', ['libri', 'libro', 'libreria', 'giornali', 'riviste']],
  ['videogiochi', ['videogiochi', 'videogioco', 'giochi', 'gaming']],
  ['foto', ['foto', 'fotografia']],
  ['svago', ['svago', 'divertimento', 'uscite', 'hobby', 'tempo']],
  ['alloggio', ['hotel', 'alloggio', 'alloggi', 'albergo', 'airbnb', 'b&b']],
  ['campeggio', ['campeggio', 'camping']],
  ['viaggi', ['viaggi', 'viaggio', 'vacanze', 'vacanza', 'voli', 'volo']],
  ['feste', ['feste', 'festa', 'compleanno', 'compleanni', 'eventi']],
  ['donazioni', ['donazioni', 'donazione', 'beneficenza']],
  ['regali', ['regali', 'regalo']],
  ['cane', ['cane', 'cani']],
  ['animali', ['animali', 'animale', 'veterinario', 'gatto', 'gatti']],
  ['bambini', ['bambini', 'bambino', 'figli', 'figlio', 'figlia', 'asilo']],
  ['giardino', ['giardino', 'piante', 'fiori', 'orto']],
  ['studio', ['studio', 'universita', 'scuola', 'corsi', 'corso', 'formazione', 'esami']],
  ['computer', ['computer', 'tecnologia', 'elettronica', 'software', 'pc']],
  ['abbonamenti', ['abbonamenti', 'abbonamento', 'iscrizioni', 'iscrizione']],
  ['assicurazioni', ['assicurazioni', 'assicurazione', 'polizza', 'polizze']],
  ['tasse', ['tasse', 'tassa', 'imposte', 'tributi', 'f24', 'multe', 'multa']],
  ['investimenti', ['investimenti', 'investimento', 'interessi', 'dividendi', 'cedole', 'risparmi']],
  ['stipendio', ['stipendio', 'stipendi', 'salario', 'lavoro', 'tredicesima', 'quattordicesima', 'bonus']],
  ['buoni', ['buoni', 'buono', 'ticket']],
  ['rimborsi', ['rimborsi', 'rimborso', 'resi', 'reso']],
  ['monete', ['contanti', 'prelievi', 'prelievo']],
  ['scontrino', ['commissioni', 'spese bancarie', 'banca']],
  ['rettifica', ['rettifica', 'rettifiche', 'correzione']],
  ['altro', ['altro', 'altre', 'varie', 'vario', 'extra', 'imprevisti']],
]
const WORD_ICONS = new Map<string, CategoryIconKey>()
for (const [key, words] of WORDS) for (const w of words) if (!WORD_ICONS.has(w)) WORD_ICONS.set(w, key)

function normalize(s: string): string {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

/** Icona proposta in base al nome, o null se nessuna parola è riconosciuta. */
export function iconFromName(name: string): CategoryIconKey | null {
  const n = normalize(name).trim()
  if (WORD_ICONS.has(n)) return WORD_ICONS.get(n)!
  for (const w of n.split(/[^a-z0-9&]+/).filter(Boolean)) {
    const exact = WORD_ICONS.get(w)
    if (exact) return exact
    for (const [k, key] of WORD_ICONS) if (k.length >= 5 && w.length > k.length && w.startsWith(k)) return key
  }
  return null
}

/** Chiave dell'icona di una categoria: quella scelta, altrimenti la predefinita; null = si mostra l'iniziale. */
export function categoryIconKey(c: { id: string; name?: string; icon?: string | null }): CategoryIconKey | null {
  if (c.icon === null) return null
  if (isCategoryIconKey(c.icon)) return c.icon
  // Assente (o di una versione più recente dell'app): icona delle categorie iniziali, poi dal nome
  return SEED_ICONS.get(c.id) ?? (c.name ? iconFromName(c.name) : null)
}

export function categoryIconName(c: { id: string; name?: string; icon?: string | null }): IconName | null {
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
