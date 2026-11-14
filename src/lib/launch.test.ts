import { describe, expect, it } from 'vitest'
import { launchTarget } from './launch'

describe('avvio con la finestra già aperta', () => {
  it('scorciatoie dell\'icona: si va alla schermata scelta', () => {
    expect(launchTarget('https://esempio.it/Statera/#/movimenti/nuova-uscita')).toBe('#/movimenti/nuova-uscita')
    expect(launchTarget('https://esempio.it/Statera/#/cerca')).toBe('#/cerca')
  })
  it('icona normale o indirizzo strano: la schermata resta com\'è', () => {
    expect(launchTarget('https://esempio.it/Statera/')).toBeNull()
    expect(launchTarget('https://esempio.it/Statera/#/')).toBeNull()
    expect(launchTarget(undefined)).toBeNull()
    expect(launchTarget('non un indirizzo')).toBeNull()
  })
})
