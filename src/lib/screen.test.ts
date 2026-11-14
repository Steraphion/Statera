import { describe, expect, it } from 'vitest'
import { revealKind } from './screen'

describe('revealKind', () => {
  it('prima schermata e cambio di sezione: dissolvenza', () => {
    expect(revealKind(null, 'movimenti')).toBe('fade')
    expect(revealKind('movimenti', 'analisi')).toBe('fade')
    expect(revealKind('altro', 'conti')).toBe('fade')
  })

  it('verso una schermata secondaria: avanti', () => {
    expect(revealKind('conti', 'conto')).toBe('forward')
    expect(revealKind('movimenti', 'cerca')).toBe('forward')
    expect(revealKind('altro', 'categorie')).toBe('forward')
    expect(revealKind('cerca', 'conto')).toBe('forward')
    expect(revealKind('conto', 'conto', true)).toBe('forward')
  })

  it('da una schermata secondaria a una sezione: indietro', () => {
    expect(revealKind('conto', 'conti')).toBe('back')
    expect(revealKind('ricorrenti', 'altro')).toBe('back')
    expect(revealKind('cerca', 'analisi')).toBe('back')
  })
})
