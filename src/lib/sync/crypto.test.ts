import { describe, expect, it } from 'vitest'
import * as c from './crypto'

describe('cifratura', () => {
  it('chiave di recupero: formato, normalizzazione', () => {
    const k = c.generateRecoveryKey()
    expect(k).toMatch(/^([A-Z2-9]{4}-){7}[A-Z2-9]{4}$/)
    expect(c.isRecoveryKeyShape(k.toLowerCase().replace(/-/g, ' '))).toBe(true)
    expect(c.isRecoveryKeyShape('ABCD')).toBe(false)
    expect(c.generateRecoveryKey()).not.toBe(k)
  })

  it('crea, sblocca con password o con chiave di recupero, cifra e decifra', async () => {
    const rk = c.generateRecoveryKey()
    const { keys, dataKey } = await c.createKeys('password-di-prova', rk)
    const sealed = await c.seal(dataKey, { saluto: 'ciao', n: 42 })
    expect(sealed).not.toContain('ciao')

    const k1 = await c.unlockWithPassword(c.parseKeysFile(JSON.stringify(keys)), 'password-di-prova')
    expect(await c.open(k1, sealed)).toEqual({ saluto: 'ciao', n: 42 })

    const k2 = await c.unlockWithRecovery(keys, rk.toLowerCase())
    expect(await c.open(k2, sealed)).toEqual({ saluto: 'ciao', n: 42 })

    await expect(c.unlockWithPassword(keys, 'sbagliata')).rejects.toBeInstanceOf(c.WrongSecretError)
    await expect(c.unlockWithRecovery(keys, c.generateRecoveryKey())).rejects.toBeInstanceOf(c.WrongSecretError)
  }, 30_000)

  it('la chiave sul dispositivo non è esportabile', async () => {
    const { dataKey } = await c.createKeys('password-di-prova', c.generateRecoveryKey())
    expect(dataKey.extractable).toBe(false)
  }, 30_000)

  it('cambio password (con la vecchia o con la chiave di recupero): i dati restano leggibili', async () => {
    const rk = c.generateRecoveryKey()
    const { keys, dataKey } = await c.createKeys('vecchia-password', rk)
    const sealed = await c.seal(dataKey, [1, 2, 3])

    const k2 = await c.changePassword(keys, { password: 'vecchia-password' }, 'nuova-password-1')
    await expect(c.unlockWithPassword(k2, 'vecchia-password')).rejects.toThrow()
    expect(await c.open(await c.unlockWithPassword(k2, 'nuova-password-1'), sealed)).toEqual([1, 2, 3])

    const k3 = await c.changePassword(k2, { recoveryKey: rk }, 'nuova-password-2')
    expect(await c.open(await c.unlockWithPassword(k3, 'nuova-password-2'), sealed)).toEqual([1, 2, 3])
  }, 60_000)

  it('dati manomessi vengono rifiutati', async () => {
    const { dataKey } = await c.createKeys('password-di-prova', c.generateRecoveryKey())
    const s = JSON.parse(await c.seal(dataKey, { a: 1 }))
    const bytes = c.fromB64(s.data)
    bytes[0] ^= 1
    s.data = c.toB64(bytes)
    await expect(c.open(dataKey, JSON.stringify(s))).rejects.toThrow(/decifrare/)
  }, 30_000)

  it('requisiti password', () => {
    expect(c.passwordProblem('corta')).toMatch(/10/)
    expect(c.passwordProblem('aaaaaaaaaaaa')).toMatch(/semplice/)
    expect(c.passwordProblem('una password lunga')).toBeNull()
  })
})
