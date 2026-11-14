// Genera logo e icone di Statera dal simbolo "Bilancia a tratto" (direzione E, scelta il 14/11/2026).
// Sorgente unica: il disegno del simbolo qui sotto, in una griglia di 100 unità. Uso: node scripts/icona-app.mjs
//
// Produce:
//   icona/simbolo.svg, icona/simbolo-piccolo.svg      simbolo da solo (sorgenti, colore pieno)
//   icona/android/primo-piano.svg|png, sfondo.svg|png  icona adattiva a due livelli (108 dp → 432 px)
//   public/icons/icon.svg, icon-{16,24,32,48,192,512}.png   icona "any" (riquadro arrotondato)
//   public/icons/maskable.svg, maskable-{192,512}.png       icona "maskable" (piena, simbolo nella zona sicura)
//   public/icons/monochrome.svg, monochrome-512.png         icona "monochrome" (solo forma, trasparente)
//   public/icons/apple-touch-icon.png                       180 px, pieno (iOS arrotonda da sé)
//   public/icons/shortcut-{uscita,entrata,cerca}.png        icone delle scorciatoie, 96 px
//   public/favicon.svg, public/favicon.ico (16, 32, 48)
//   src/lib/logo.ts                                         simbolo per il componente Logo dell'app
//
// Rasterizzazione con @resvg/resvg-js (solo sviluppo): i file prodotti sono nel repository, la build non lo usa.
import { Resvg } from '@resvg/resvg-js'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')

/** Colori dalla palette Indaco morbido (src/styles/tokens.css). */
const INDACO = '#535AA6'
const BIANCO = '#FFFFFF'

/**
 * Simbolo in una griglia 100 × 100. `C` = colore. Due disegni:
 * - grande, da 48 px in su: colonna, base, braccio, pomello, tiranti e piatti;
 * - piccolo, fino a 32 px: tratti più spessi, un tirante per piatto, piatti più grandi.
 */
const SIMBOLO = {
  grande: [
    ['path', { d: 'M50 24V82', fill: 'none', stroke: 'C', 'stroke-width': 7.5, 'stroke-linecap': 'round' }],
    ['path', { d: 'M33 84H67', fill: 'none', stroke: 'C', 'stroke-width': 8, 'stroke-linecap': 'round' }],
    ['path', { d: 'M14 30H86', fill: 'none', stroke: 'C', 'stroke-width': 7.5, 'stroke-linecap': 'round' }],
    ['path', { d: 'M8 58L20 30L32 58M68 58L80 30L92 58', fill: 'none', stroke: 'C', 'stroke-width': 4.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }],
    ['circle', { cx: 50, cy: 20, r: 7, fill: 'C' }],
    ['path', { d: 'M4 58H36A16 16 0 0 1 4 58Z', fill: 'C' }],
    ['path', { d: 'M64 58H96A16 16 0 0 1 64 58Z', fill: 'C' }],
  ],
  piccolo: [
    ['path', { d: 'M50 22V82M30 86H70M10 28H90', fill: 'none', stroke: 'C', 'stroke-width': 11, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }],
    ['path', { d: 'M20 30V50M80 30V50', fill: 'none', stroke: 'C', 'stroke-width': 8, 'stroke-linecap': 'round' }],
    ['path', { d: 'M0 52H40A20 20 0 0 1 0 52Z', fill: 'C' }],
    ['path', { d: 'M60 52H100A20 20 0 0 1 60 52Z', fill: 'C' }],
  ],
}

const variante = (px) => (px <= 32 ? 'piccolo' : 'grande')

const attrs = (a, colore) =>
  Object.entries(a)
    .map(([k, v]) => `${k}="${v === 'C' ? colore : v}"`)
    .join(' ')
const disegno = (v, colore) => SIMBOLO[v].map(([t, a]) => `<${t} ${attrs(a, colore)}/>`).join('')
const svg = (n, corpo) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${n} ${n}">${corpo}</svg>\n`

/** Riquadro del disegno (unità della griglia), misurato rasterizzando a 1200 px (tratti compresi). */
function bbox(v) {
  const s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 120 120" width="1200" height="1200">${disegno(v, '#000')}</svg>`
  const img = new Resvg(s).render()
  const px = img.pixels // il getter copia il buffer: leggerlo una volta sola
  let x0 = Infinity, y0 = Infinity, x1 = -1, y1 = -1
  for (let y = 0; y < img.height; y++)
    for (let x = 0; x < img.width; x++)
      if (px[(y * img.width + x) * 4 + 3] > 8) {
        if (x < x0) x0 = x
        if (x > x1) x1 = x
        if (y < y0) y0 = y
        if (y > y1) y1 = y
      }
  const u = (p) => p / 10 - 10
  return { x0: u(x0), y0: u(y0), x1: u(x1 + 1), y1: u(y1 + 1) }
}
const BB = { grande: bbox('grande'), piccolo: bbox('piccolo') }

const r = (x) => Math.round(x * 1000) / 1000

/** Trasformazione che centra il simbolo in un quadrato di lato n. */
function posa(v, n, modo) {
  const b = BB[v]
  const w = b.x1 - b.x0, h = b.y1 - b.y0
  // riquadro: il lato lungo occupa il 60% (68% nella versione piccola, che ha bisogno di più pixel)
  // pieno: tutto il simbolo dentro il cerchio della zona sicura (66% del lato), con un piccolo margine
  const sc = modo === 'riquadro' ? (n * (v === 'piccolo' ? 0.68 : 0.6)) / Math.max(w, h) : (0.33 * n * 0.96) / (Math.hypot(w, h) / 2)
  const cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2
  return `translate(${r(n / 2 - cx * sc)} ${r(n / 2 - cy * sc)}) scale(${r(sc)})`
}

const N = 512
const RAGGIO = 115 // ≈ 22,5% del lato, come lo squircle delle tavole
const icona = (px) => {
  const v = variante(px)
  return svg(N, `<rect width="${N}" height="${N}" rx="${RAGGIO}" fill="${INDACO}"/><g transform="${posa(v, N, 'riquadro')}">${disegno(v, BIANCO)}</g>`)
}
const piena = (px, colore = BIANCO, sfondo = INDACO, modo = 'pieno') => {
  const v = variante(px)
  const fondo = sfondo ? `<rect width="${N}" height="${N}" fill="${sfondo}"/>` : ''
  return svg(N, `${fondo}<g transform="${posa(v, N, modo)}">${disegno(v, colore)}</g>`)
}

function png(s, px) {
  return new Resvg(s, { fitTo: { mode: 'width', value: px } }).render().asPng()
}

function scrivi(rel, dati) {
  const p = join(ROOT, rel)
  mkdirSync(dirname(p), { recursive: true })
  writeFileSync(p, dati)
  console.log('  ' + rel)
}

/** ICO con immagini PNG dentro (supportato da Windows Vista in poi e da tutti i browser). */
function ico(immagini) {
  const testa = Buffer.alloc(6 + 16 * immagini.length)
  testa.writeUInt16LE(0, 0)
  testa.writeUInt16LE(1, 2)
  testa.writeUInt16LE(immagini.length, 4)
  let offset = testa.length
  immagini.forEach(({ px, dati }, i) => {
    const e = 6 + 16 * i
    testa.writeUInt8(px >= 256 ? 0 : px, e)
    testa.writeUInt8(px >= 256 ? 0 : px, e + 1)
    testa.writeUInt8(0, e + 2)
    testa.writeUInt8(0, e + 3)
    testa.writeUInt16LE(1, e + 4)
    testa.writeUInt16LE(32, e + 6)
    testa.writeUInt32LE(dati.length, e + 8)
    testa.writeUInt32LE(offset, e + 12)
    offset += dati.length
  })
  return Buffer.concat([testa, ...immagini.map((x) => x.dati)])
}

/** Icone Lucide già copiate nell'app (src/lib/icons.ts), per le scorciatoie. */
function lucide(nome) {
  const src = readFileSync(join(ROOT, 'src/lib/icons.ts'), 'utf8')
  const riga = src.split('\n').find((l) => l.startsWith(`  '${nome}': `))
  if (!riga) throw new Error(`Icona ${nome} non trovata in src/lib/icons.ts`)
  const nodi = JSON.parse(riga.slice(riga.indexOf(': ') + 2).replace(/,\s*$/, ''))
  return nodi.map(([t, a]) => `<${t} ${Object.entries(a).map(([k, v]) => `${k}="${v}"`).join(' ')}/>`).join('')
}
/** Scorciatoia: cerchio indaco con l'icona bianca, come le azioni rapide dell'app. */
const scorciatoia = (nome) =>
  svg(96, `<circle cx="48" cy="48" r="48" fill="${INDACO}"/><g transform="translate(24 24) scale(2)" fill="none" stroke="${BIANCO}" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">${lucide(nome)}</g>`)

console.log('Simbolo, riquadri misurati:', JSON.stringify(BB))

// Sorgenti del simbolo
scrivi('icona/simbolo.svg', svg(100, disegno('grande', INDACO)))
scrivi('icona/simbolo-piccolo.svg', svg(100, disegno('piccolo', INDACO)))

// Icona adattiva Android: primo piano trasparente con il simbolo nella zona sicura, sfondo separato
const A = 432
const primoPiano = svg(A, `<g transform="${posa('grande', A, 'pieno')}">${disegno('grande', BIANCO)}</g>`)
const sfondo = svg(A, `<rect width="${A}" height="${A}" fill="${INDACO}"/>`)
scrivi('icona/android/primo-piano.svg', primoPiano)
scrivi('icona/android/primo-piano.png', png(primoPiano, A))
scrivi('icona/android/sfondo.svg', sfondo)
scrivi('icona/android/sfondo.png', png(sfondo, A))

// Icona "any"
scrivi('public/icons/icon.svg', icona(512))
for (const px of [16, 24, 32, 48, 192, 512]) scrivi(`public/icons/icon-${px}.png`, png(icona(px), px))

// Maskable: pieno, simbolo dentro la zona sicura del 66%
scrivi('public/icons/maskable.svg', piena(512))
for (const px of [192, 512]) scrivi(`public/icons/maskable-${px}.png`, png(piena(px), px))

// Monochrome: solo la forma (Android la colora col tema), stessa zona sicura
scrivi('public/icons/monochrome.svg', piena(512, BIANCO, null))
scrivi('public/icons/monochrome-512.png', png(piena(512, BIANCO, null), 512))

// iOS: quadrato pieno, il sistema arrotonda gli angoli
scrivi('public/icons/apple-touch-icon.png', png(piena(180, BIANCO, INDACO, 'riquadro'), 180))

// Scorciatoie
for (const [file, nome] of [['uscita', 'arrow-up-right'], ['entrata', 'arrow-down-left'], ['cerca', 'search']])
  scrivi(`public/icons/shortcut-${file}.png`, png(scorciatoia(nome), 96))

// Favicon: SVG col disegno piccolo (le schede sono di 16 px), ICO con 16, 32 e 48
scrivi('public/favicon.svg', icona(16))
scrivi('public/favicon.ico', ico([16, 32, 48].map((px) => ({ px, dati: png(icona(px), px) }))))

// Simbolo per il componente Logo dell'app (riquadro e colori dai token)
const nodi = (v) =>
  SIMBOLO[v].map(([t, a]) => [t, Object.fromEntries(Object.entries(a).map(([k, x]) => [k, x === 'C' ? 'currentColor' : String(x)]))])
scrivi(
  'src/lib/logo.ts',
  `// Generato da scripts/icona-app.mjs: non modificare a mano.
// Simbolo di Statera (bilancia a tratto) su una griglia di ${N} unità, già centrato nel riquadro.
export type LogoNode = ['path' | 'circle', Record<string, string>]

export const LOGO_SIZE = ${N}
export const LOGO_RADIUS = ${RAGGIO}

/** Disegno grande (da 48 px) e piccolo (fino a 32 px), con la trasformazione che lo centra. */
export const LOGO: Record<'grande' | 'piccolo', { transform: string; nodes: LogoNode[] }> = ${JSON.stringify(
    {
      grande: { transform: posa('grande', N, 'riquadro'), nodes: nodi('grande') },
      piccolo: { transform: posa('piccolo', N, 'riquadro'), nodes: nodi('piccolo') },
    },
    null,
    2,
  )}
`,
)
console.log('Fatto.')
