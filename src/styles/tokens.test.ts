/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

// Ogni var(--nome) usato negli stili deve esistere in tokens.css (o essere una variabile
// locale dichiarata in un componente, come --cat). Un nome sbagliato non dà errori:
// il browser usa il valore ereditato e il colore cambia senza che nessuno se ne accorga.

// Componenti e moduli con import.meta.glob; i fogli .css da disco, perché in vitest un .css?raw arriva vuoto.
const sources: Record<string, string> = {
  ...import.meta.glob<string>(['../**/*.{svelte,ts}', '!../**/*.test.ts'], { query: '?raw', import: 'default', eager: true }),
  './tokens.css': readFileSync(new URL('./tokens.css', import.meta.url), 'utf8'),
  './base.css': readFileSync(new URL('./base.css', import.meta.url), 'utf8'),
}

const declared = (text: string) =>
  [...text.matchAll(/--([A-Za-z0-9-]+)\s*:|style:--([A-Za-z0-9-]+)/g)].map((m) => m[1] ?? m[2])

describe('token degli stili', () => {
  it('legge i sorgenti, tokens.css compreso', () => {
    expect(sources['./tokens.css']).toContain('--color-text-muted:')
    expect(Object.keys(sources)).toContain('../components/IconPicker.svelte')
  })

  it('ogni var(--…) usato è definito', () => {
    const defined = new Set(Object.values(sources).flatMap(declared))
    const missing: string[] = []
    for (const [file, text] of Object.entries(sources)) {
      for (const m of text.matchAll(/var\(--([A-Za-z0-9-]+)/g)) {
        const name = m[1]
        if (name.endsWith('-')) continue // nome composto nel codice, es. var(--swatch-${key})
        if (!defined.has(name)) missing.push(`${file}: --${name}`)
      }
    }
    expect(missing).toEqual([])
  })
})
