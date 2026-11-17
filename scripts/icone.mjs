// Genera src/lib/icons.ts con le sole icone Lucide usate dall'app (licenza ISC).
// Nessuna dipendenza: si passa la cartella del pacchetto lucide-static già estratto.
//   npm pack lucide-static@1.73.0 && tar -xzf lucide-static-1.73.0.tgz
//   node scripts/icone.mjs package
// Per aggiungere un'icona: inserire il suo nome Lucide in UI o una chiave in CATEGORIE e rigenerare.
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const pkg = process.argv[2]
if (!pkg) {
  console.error('Uso: node scripts/icone.mjs <cartella del pacchetto lucide-static>')
  process.exit(1)
}
const version = JSON.parse(readFileSync(join(pkg, 'package.json'), 'utf8')).version

/** Icone dell'interfaccia, col nome Lucide. */
const UI = [
  'chevron-left', 'chevron-right', 'chevron-down', 'chevron-up', 'arrow-up', 'arrow-down', 'plus', 'minus', 'x', 'check',
  'search', 'list', 'wallet', 'chart-column', 'ellipsis', 'arrow-left-right', 'arrow-down-left', 'arrow-up-right', 'scale',
  'star', 'calendar', 'credit-card', 'pencil', 'trash-2', 'lock', 'fingerprint', 'cloud-check', 'cloud', 'cloud-off',
  'shield-check', 'repeat', 'triangle-alert', 'circle-alert', 'info', 'download', 'upload', 'tag', 'target', 'landmark',
  'banknote', 'ticket', 'piggy-bank', 'key-round', 'users', 'unlink', 'keyboard', 'receipt', 'delete', 'circle-check',
  'pause', 'play', 'clock', 'table', 'palette', 'wifi-off', 'smartphone', 'refresh-cw', 'log-out', 'file-text', 'history',
  'split', 'archive', 'archive-restore', 'eye', 'eye-off', 'coins', 'layers', 'sparkles',
]

/**
 * Chiavi salvate nel campo `icon` delle categorie → icona Lucide.
 * Le chiavi sono astratte (come s1…s8 per i colori): cambiare set di icone non tocca i dati.
 */
const CATEGORIE = {
  // categorie iniziali
  spesa: 'shopping-cart', pasti: 'utensils', casa: 'house', affitto: 'key-round', bollette: 'zap', manutenzione: 'wrench',
  trasporti: 'route', carburante: 'fuel', mezzi: 'bus', auto: 'car', salute: 'heart-pulse', abbigliamento: 'shirt',
  sport: 'dumbbell', svago: 'popcorn', viaggi: 'plane', regali: 'gift', abbonamenti: 'calendar-sync', altro: 'shapes',
  stipendio: 'briefcase-business', buoni: 'ticket', rimborsi: 'hand-coins', rettifica: 'scale',
  // scelta libera
  caffe: 'coffee', pizza: 'pizza', vino: 'wine', birra: 'beer', gelato: 'ice-cream-cone', colazione: 'croissant',
  arredamento: 'sofa', bambini: 'baby', animali: 'paw-print', giardino: 'sprout', elettrodomestici: 'washing-machine',
  internet: 'wifi', telefono: 'smartphone', tv: 'tv', bici: 'bike', treno: 'train-front', taxi: 'car-taxi-front',
  parcheggio: 'square-parking', traghetto: 'ship', farmaci: 'pill', medico: 'stethoscope', parrucchiere: 'scissors',
  bellezza: 'sparkles', ottico: 'glasses', musica: 'music', cinema: 'clapperboard', libri: 'book-open',
  videogiochi: 'gamepad-2', foto: 'camera', feste: 'party-popper', studio: 'graduation-cap', computer: 'laptop',
  monete: 'coins', tasse: 'percent', scontrino: 'receipt', investimenti: 'trending-up', assicurazioni: 'umbrella',
  cuore: 'heart', mondo: 'globe', campeggio: 'tent', alloggio: 'bed-double', cane: 'dog', donazioni: 'hand-heart',
  // v0.37: altre icone per la scelta libera
  fastfood: 'hamburger',
  pesce: 'fish',
  insalata: 'salad',
  dolci: 'cake-slice',
  snack: 'cookie',
  bibite: 'cup-soda',
  cocktail: 'martini',
  frutta: 'apple',
  verdura: 'carrot',
  carne: 'drumstick',
  panino: 'sandwich',
  cucina: 'cooking-pot',
  latticini: 'milk',
  negozi: 'store',
  shopping: 'shopping-bag',
  mercato: 'shopping-basket',
  luce: 'lightbulb',
  gas: 'flame',
  acqua: 'droplet',
  rifiuti: 'trash-2',
  lavori: 'paint-roller',
  bricolage: 'hammer',
  bagno: 'bath',
  elettricita: 'plug',
  sicurezza: 'shield',
  condominio: 'building-2',
  pulizie: 'spray-can',
  moto: 'motorbike',
  monopattino: 'scooter',
  tram: 'tram-front',
  furgone: 'truck',
  bagagli: 'luggage',
  luoghi: 'map-pin',
  montagna: 'mountain',
  mare: 'tree-palm',
  barca: 'sailboat',
  camper: 'caravan',
  ricarica: 'plug-zap',
  neve: 'snowflake',
  hotel: 'hotel',
  biglietti: 'tickets',
  vaccini: 'syringe',
  soccorso: 'bandage',
  psicologo: 'brain',
  ospedale: 'hospital',
  fitness: 'activity',
  corsa: 'footprints',
  nuoto: 'waves',
  pallavolo: 'volleyball',
  gare: 'trophy',
  fiori: 'flower-2',
  benessere: 'leaf',
  teatro: 'drama',
  arte: 'palette',
  strumenti: 'guitar',
  cuffie: 'headphones',
  karaoke: 'mic',
  giochi: 'dices',
  hobby: 'puzzle',
  lunapark: 'ferris-wheel',
  film: 'film',
  giornali: 'newspaper',
  pittura: 'brush',
  gioielli: 'gem',
  orologi: 'watch',
  risparmi: 'piggy-bank',
  portafoglio: 'wallet',
  contanti: 'banknote',
  carta: 'credit-card',
  banca: 'landmark',
  ufficio: 'building',
  lavoro: 'briefcase',
  consulenze: 'handshake',
  documenti: 'file-text',
  commercialista: 'calculator',
  budget: 'chart-pie',
  cripto: 'bitcoin',
  legale: 'gavel',
  posta: 'mail',
  pacchi: 'package',
  stampa: 'printer',
  cloud: 'cloud',
  famiglia: 'users',
  personale: 'user',
  chiesa: 'church',
  scuola: 'school',
  gatto: 'cat',
  uccelli: 'bird',
  volontariato: 'heart-handshake',
}

/** Nome dell'icona letto dagli screen reader nella scelta dell'icona (descrive il disegno). */
const NOMI = {
  spesa: 'Carrello', pasti: 'Posate', casa: 'Casa', affitto: 'Chiave', bollette: 'Fulmine', manutenzione: 'Chiave inglese',
  trasporti: 'Percorso', carburante: 'Pompa di benzina', mezzi: 'Autobus', auto: 'Auto', salute: 'Cuore con battito',
  abbigliamento: 'Maglietta', sport: 'Manubrio', svago: 'Popcorn', viaggi: 'Aereo', regali: 'Pacco regalo',
  abbonamenti: 'Calendario con frecce', altro: 'Forme', stipendio: 'Valigetta', buoni: 'Biglietto',
  rimborsi: 'Mano con monete', rettifica: 'Bilancia', caffe: 'Tazza', pizza: 'Pizza', vino: 'Calice', birra: 'Boccale',
  gelato: 'Gelato', colazione: 'Cornetto', arredamento: 'Divano', bambini: 'Bambino', animali: 'Zampa',
  giardino: 'Germoglio', elettrodomestici: 'Lavatrice', internet: 'Wi-Fi', telefono: 'Telefono', tv: 'Televisore',
  bici: 'Bicicletta', treno: 'Treno', taxi: 'Taxi', parcheggio: 'Parcheggio', traghetto: 'Nave', farmaci: 'Pillola',
  medico: 'Stetoscopio', parrucchiere: 'Forbici', bellezza: 'Scintille', ottico: 'Occhiali', musica: 'Note musicali',
  cinema: 'Ciak', libri: 'Libro', videogiochi: 'Controller', foto: 'Macchina fotografica', feste: 'Coriandoli',
  studio: 'Tocco di laurea', computer: 'Portatile', monete: 'Monete', tasse: 'Percentuale', scontrino: 'Scontrino',
  investimenti: 'Grafico in crescita', assicurazioni: 'Ombrello', cuore: 'Cuore', mondo: 'Mappamondo',
  campeggio: 'Tenda', alloggio: 'Letto', cane: 'Cane', donazioni: 'Mano con cuore',
  fastfood: 'Hamburger',
  pesce: 'Pesce',
  insalata: 'Insalata',
  dolci: 'Fetta di torta',
  snack: 'Biscotto',
  bibite: 'Bibita',
  cocktail: 'Cocktail',
  frutta: 'Mela',
  verdura: 'Carota',
  carne: 'Coscia di pollo',
  panino: 'Panino',
  cucina: 'Pentola',
  latticini: 'Latte',
  negozi: 'Negozio',
  shopping: 'Borsa della spesa',
  mercato: 'Cestino',
  luce: 'Lampadina',
  gas: 'Fiamma',
  acqua: 'Goccia',
  rifiuti: 'Cestino dei rifiuti',
  lavori: 'Rullo per pittura',
  bricolage: 'Martello',
  bagno: 'Vasca da bagno',
  elettricita: 'Spina',
  sicurezza: 'Scudo',
  condominio: 'Palazzo',
  pulizie: 'Spruzzino',
  moto: 'Moto',
  monopattino: 'Monopattino',
  tram: 'Tram',
  furgone: 'Furgone',
  bagagli: 'Valigia',
  luoghi: 'Segnaposto',
  montagna: 'Montagna',
  mare: 'Palma',
  barca: 'Barca a vela',
  camper: 'Roulotte',
  ricarica: 'Spina con fulmine',
  neve: 'Fiocco di neve',
  hotel: 'Hotel',
  biglietti: 'Biglietti',
  vaccini: 'Siringa',
  soccorso: 'Cerotto',
  psicologo: 'Cervello',
  ospedale: 'Ospedale',
  fitness: 'Battito',
  corsa: 'Impronte',
  nuoto: 'Onde',
  pallavolo: 'Pallone da pallavolo',
  gare: 'Coppa',
  fiori: 'Fiore',
  benessere: 'Foglia',
  teatro: 'Maschere',
  arte: 'Tavolozza',
  strumenti: 'Chitarra',
  cuffie: 'Cuffie',
  karaoke: 'Microfono',
  giochi: 'Dadi',
  hobby: 'Puzzle',
  lunapark: 'Ruota panoramica',
  film: 'Pellicola',
  giornali: 'Giornale',
  pittura: 'Pennello',
  gioielli: 'Gemma',
  orologi: 'Orologio',
  risparmi: 'Salvadanaio',
  portafoglio: 'Portafoglio',
  contanti: 'Banconota',
  carta: 'Carta di pagamento',
  banca: 'Banca',
  ufficio: 'Edificio',
  lavoro: 'Valigetta da lavoro',
  consulenze: 'Stretta di mano',
  documenti: 'Documento',
  commercialista: 'Calcolatrice',
  budget: 'Grafico a torta',
  cripto: 'Bitcoin',
  legale: 'Martelletto',
  posta: 'Busta',
  pacchi: 'Pacco',
  stampa: 'Stampante',
  cloud: 'Nuvola',
  famiglia: 'Persone',
  personale: 'Persona',
  chiesa: 'Chiesa',
  scuola: 'Scuola',
  gatto: 'Gatto',
  uccelli: 'Uccello',
  volontariato: 'Mani e cuore',
}

/** Gruppi della scelta dell'icona nel modulo della categoria. */
const GRUPPI = [
  ['Suggerite', ['spesa', 'pasti', 'casa', 'bollette', 'trasporti', 'carburante', 'salute', 'abbigliamento', 'sport', 'svago', 'viaggi', 'regali', 'abbonamenti', 'stipendio', 'buoni', 'rimborsi', 'altro']],
  ['Cibo e spesa', ['caffe', 'colazione', 'pizza', 'fastfood', 'panino', 'pesce', 'carne', 'insalata', 'frutta', 'verdura', 'latticini', 'dolci', 'gelato', 'snack', 'bibite', 'vino', 'birra', 'cocktail', 'cucina', 'mercato', 'negozi', 'shopping']],
  ['Casa', ['affitto', 'condominio', 'manutenzione', 'lavori', 'bricolage', 'pulizie', 'arredamento', 'elettrodomestici', 'luce', 'gas', 'acqua', 'elettricita', 'rifiuti', 'bagno', 'internet', 'telefono', 'tv', 'sicurezza', 'giardino', 'fiori']],
  ['Trasporti', ['auto', 'moto', 'monopattino', 'bici', 'mezzi', 'tram', 'treno', 'taxi', 'traghetto', 'furgone', 'parcheggio', 'ricarica']],
  ['Viaggi', ['bagagli', 'alloggio', 'hotel', 'campeggio', 'camper', 'mare', 'montagna', 'neve', 'barca', 'luoghi', 'mondo', 'biglietti']],
  ['Salute e benessere', ['farmaci', 'medico', 'vaccini', 'soccorso', 'ospedale', 'psicologo', 'ottico', 'parrucchiere', 'bellezza', 'benessere']],
  ['Sport', ['fitness', 'corsa', 'nuoto', 'pallavolo', 'gare']],
  ['Tempo libero', ['cinema', 'film', 'teatro', 'musica', 'strumenti', 'cuffie', 'karaoke', 'libri', 'giornali', 'videogiochi', 'giochi', 'hobby', 'arte', 'pittura', 'foto', 'lunapark', 'feste']],
  ['Persone e animali', ['famiglia', 'personale', 'bambini', 'scuola', 'studio', 'animali', 'cane', 'gatto', 'uccelli', 'cuore', 'donazioni', 'volontariato', 'chiesa']],
  ['Soldi e lavoro', ['lavoro', 'ufficio', 'computer', 'consulenze', 'documenti', 'commercialista', 'legale', 'posta', 'pacchi', 'stampa', 'cloud', 'risparmi', 'portafoglio', 'contanti', 'carta', 'banca', 'monete', 'investimenti', 'budget', 'cripto', 'tasse', 'assicurazioni', 'scontrino', 'gioielli', 'orologi', 'rettifica']],
]


const TAGS = new Set(['path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse'])
const ATTRS = new Set(['d', 'cx', 'cy', 'r', 'rx', 'ry', 'x', 'y', 'width', 'height', 'x1', 'y1', 'x2', 'y2', 'points'])

function nodes(name) {
  const svg = readFileSync(join(pkg, 'icons', `${name}.svg`), 'utf8')
  const out = []
  for (const m of svg.matchAll(/<([a-z]+)\s([^>]*?)\/?>/g)) {
    if (!TAGS.has(m[1])) continue
    const attrs = {}
    for (const a of m[2].matchAll(/([a-z][a-z0-9-]*)="([^"]*)"/g)) if (ATTRS.has(a[1])) attrs[a[1]] = a[2]
    out.push([m[1], attrs])
  }
  if (!out.length) throw new Error(`Icona vuota: ${name}`)
  return out
}

const names = [...new Set([...UI, ...Object.values(CATEGORIE)])].sort()
for (const [, keys] of GRUPPI) for (const k of keys) if (!(k in CATEGORIE)) throw new Error(`Chiave sconosciuta: ${k}`)
for (const k of Object.keys(CATEGORIE)) if (!NOMI[k]) throw new Error(`Manca il nome dell'icona: ${k}`)
const inGruppi = new Set(GRUPPI.flatMap(([, keys]) => keys))
for (const k of Object.keys(CATEGORIE)) if (!inGruppi.has(k)) throw new Error(`Icona fuori dai gruppi: ${k}`)
const body = names.map((n) => `  '${n}': ${JSON.stringify(nodes(n))},`).join('\n')

const ts = `// GENERATO da scripts/icone.mjs con lucide-static ${version}: non modificare a mano.
// Icone Lucide (https://lucide.dev), licenza ISC: © Lucide Icons and Contributors (vedi public/licenze.html).

export type IconNode = [tag: 'path' | 'circle' | 'rect' | 'line' | 'polyline' | 'polygon' | 'ellipse', attrs: Record<string, string>]

export const ICONS = {
${body}
} satisfies Record<string, IconNode[]>

export type IconName = keyof typeof ICONS

/** Chiavi del campo \`icon\` delle categorie → icona. */
export const CATEGORY_ICONS = ${JSON.stringify(CATEGORIE, null, 2).replace(/"([a-z]+)":/g, '$1:').replace(/"/g, "'")} satisfies Record<string, IconName>

export type CategoryIconKey = keyof typeof CATEGORY_ICONS

/** Nome di ogni icona per gli screen reader. */
export const CATEGORY_ICON_LABELS: Record<CategoryIconKey, string> = ${JSON.stringify(NOMI, null, 2).replace(/"([a-z]+)":/g, '$1:').replace(/"/g, "'")}

/** Gruppi della scelta dell'icona nel modulo della categoria. */
export const CATEGORY_ICON_GROUPS: { label: string; keys: CategoryIconKey[] }[] = ${JSON.stringify(GRUPPI.map(([label, keys]) => ({ label, keys })), null, 2).replace(/"/g, "'")}

export function isCategoryIconKey(k: unknown): k is CategoryIconKey {
  return typeof k === 'string' && Object.prototype.hasOwnProperty.call(CATEGORY_ICONS, k)
}
`
writeFileSync(new URL('../src/lib/icons.ts', import.meta.url), ts)
console.log(`src/lib/icons.ts: ${names.length} icone (lucide-static ${version})`)
