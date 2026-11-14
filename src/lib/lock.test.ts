import { describe, expect, it } from 'vitest'
import * as lk from './lock'

const mem = () => {
  const m = new Map<string, string>()
  return { getItem: (k: string) => m.get(k) ?? null, setItem: (k: string, v: string) => void m.set(k, v), removeItem: (k: string) => void m.delete(k), m }
}

describe('PIN', () => {
  it('regole del PIN', () => {
    expect(lk.pinProblem('12a4')).toContain('cifre')
    expect(lk.pinProblem('123')).toContain('almeno 4')
    expect(lk.pinProblem('123456789')).toContain('massimo 8')
    expect(lk.pinProblem('0000')).toContain('prevedibile')
    expect(lk.pinProblem('123456')).toContain('sequenza')
    expect(lk.pinProblem('654321')).toContain('sequenza')
    expect(lk.pinProblem('274913')).toBeNull()
  })
  it('si salva solo l\'impronta; verifica', async () => {
    const cfg = await lk.makeConfig('274913', 60, 1000)
    expect(JSON.stringify(cfg)).not.toContain('274913')
    expect(cfg.length).toBe(6)
    expect(await lk.pinMatches(cfg, '274913')).toBe(true)
    expect(await lk.pinMatches(cfg, '274914')).toBe(false)
    const other = await lk.makeConfig('274913', 60, 1000)
    expect(other.salt).not.toBe(cfg.salt)
    expect(other.hash).not.toBe(cfg.hash)
  })
  it('attese crescenti dopo 5 errori, azzerate dal PIN giusto', async () => {
    let cfg = await lk.makeConfig('274913', 60, 1000)
    let now = 1_000_000
    for (let i = 1; i <= 4; i++) {
      const r = await lk.tryPin(cfg, '1111', now)
      expect(r.ok).toBe(false)
      cfg = r.cfg
      expect(cfg.waitUntil).toBe(0)
    }
    const r5 = await lk.tryPin(cfg, '1111', now)
    cfg = r5.cfg
    expect(cfg.waitUntil).toBe(now + 30_000)
    // durante l'attesa anche il PIN giusto viene rifiutato
    const blocked = await lk.tryPin(cfg, '274913', now + 10_000)
    expect(blocked.ok).toBe(false)
    expect(blocked.ok === false && blocked.reason).toBe('wait')
    now += 31_000
    const r6 = await lk.tryPin(cfg, '0000', now)
    expect(r6.ok === false && r6.waitMs).toBe(60_000)
    cfg = r6.cfg
    now += 61_000
    const good = await lk.tryPin(cfg, '274913', now)
    expect(good.ok).toBe(true)
    expect(good.cfg.fails).toBe(0)
    expect(lk.waitAfter(30)).toBe(lk.MAX_WAIT_MS)
  })
  it('salvataggio e lettura; dati rovinati = nessun blocco', async () => {
    const s = mem()
    const cfg = await lk.makeConfig('274913', 300, 1000)
    lk.writeConfig(s, cfg)
    expect(lk.readConfig(s)).toEqual(cfg)
    s.setItem(lk.LOCK_KEY, '{rotto')
    expect(lk.readConfig(s)).toBeNull()
    lk.writeConfig(s, null)
    expect(s.m.has(lk.LOCK_KEY)).toBe(false)
  })
  it('quando bloccare', async () => {
    const cfg = await lk.makeConfig('274913', 60, 1000)
    expect(lk.shouldLock(cfg, 0, 59_000)).toBe(false)
    expect(lk.shouldLock(cfg, 0, 60_000)).toBe(true)
    expect(lk.shouldLock({ ...cfg, timeout: 0 }, 0, 1)).toBe(true)
    expect(lk.shouldLock(null, 0, 999_999)).toBe(false)
    expect(lk.formatWait(30_000)).toBe('30 secondi')
    expect(lk.formatWait(120_000)).toBe('2 minuti')
  })
})
