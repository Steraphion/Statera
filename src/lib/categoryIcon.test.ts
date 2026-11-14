import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import { StateraDB } from './data/db'
import * as repo from './data/repo'
import { categoryIconKey, categoryIconName, initial, SEED_ICONS } from './categoryIcon'
import { CATEGORY_ICONS, CATEGORY_ICON_GROUPS, CATEGORY_ICON_LABELS } from './icons'

let d: StateraDB
let n = 0

beforeEach(async () => {
  d = new StateraDB(`icone-${++n}`)
  await d.open()
})

describe('icone delle categorie', () => {
  it('ogni categoria iniziale ha la sua icona predefinita', async () => {
    await repo.ensureSeeded(d)
    for (const c of await d.categories.toArray()) {
      expect(c.icon, c.name).toBeUndefined()
      expect(categoryIconKey(c), c.name).not.toBeNull()
    }
    expect(categoryIconKey({ id: repo.seedId('uscita', 'Casa', 'Bollette') })).toBe('bollette')
    expect(categoryIconName({ id: repo.seedId('uscita', 'Spesa alimentare') })).toBe('shopping-cart')
    for (const kind of ['uscita', 'entrata'] as const) expect(SEED_ICONS.get(repo.seedId(kind, repo.ADJUST_CATEGORY_NAME))).toBe('rettifica')
  })

  it('icona scelta, nessuna icona e chiavi sconosciute', () => {
    const id = repo.seedId('uscita', 'Svago')
    expect(categoryIconKey({ id, icon: 'cinema' })).toBe('cinema')
    expect(categoryIconKey({ id, icon: null })).toBeNull()
    // chiave di una versione più recente: si torna alla predefinita
    expect(categoryIconKey({ id, icon: 'razzo-spaziale' })).toBe('svago')
    expect(categoryIconKey({ id: 'x', icon: 'razzo-spaziale' })).toBeNull()
    expect(categoryIconKey({ id: 'x' })).toBeNull()
    expect(initial(' ègite')).toBe('È')
  })

  it('ogni icona ha un nome e sta in un gruppo', () => {
    const grouped = CATEGORY_ICON_GROUPS.flatMap((g) => g.keys)
    expect(new Set(grouped).size).toBe(grouped.length)
    expect(new Set(grouped)).toEqual(new Set(Object.keys(CATEGORY_ICONS)))
    for (const k of grouped) expect(CATEGORY_ICON_LABELS[k]).toBeTruthy()
  })
})

describe('campo icon nel salvataggio', () => {
  const base = { name: 'Palestra', kind: 'uscita' as const, parentId: null, color: 's3' as const }

  it('crea con icona, la cambia, la toglie e la conserva se non indicata', async () => {
    const c = await repo.createCategory({ ...base, icon: 'sport' }, d)
    expect((await d.categories.get(c.id))!.icon).toBe('sport')
    await repo.updateCategory(c.id, { ...base, icon: 'bici' }, d)
    expect((await d.categories.get(c.id))!.icon).toBe('bici')
    await repo.updateCategory(c.id, { ...base, name: 'Palestra e piscina' }, d)
    const kept = (await d.categories.get(c.id))!
    expect([kept.name, kept.icon]).toEqual(['Palestra e piscina', 'bici'])
    await repo.updateCategory(c.id, { ...base, icon: null }, d)
    expect((await d.categories.get(c.id))!.icon).toBeNull()
  })

  it('una chiave non valida diventa "nessuna icona" e non si salva mai un disegno', async () => {
    const c = await repo.createCategory({ ...base, icon: '<svg onload=alert(1)>' }, d)
    expect((await d.categories.get(c.id))!.icon).toBeNull()
    const plain = await repo.createCategory({ ...base, name: 'Senza' }, d)
    expect('icon' in (await d.categories.get(plain.id))!).toBe(false)
  })
})
