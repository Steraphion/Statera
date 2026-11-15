import { describe, expect, it } from 'vitest'
import { statusLabel, syncLine, updatedText, type SyncView } from './labels'

const now = new Date(2026, 10, 15, 18, 0).getTime()
const at = new Date(2026, 10, 15, 14, 32).getTime()
const view = (v: Partial<SyncView>): SyncView => ({ status: 'idle', lastSyncAt: at, pending: false, askReconnect: false, ...v })

describe('updatedText', () => {
  it('ora dell\'ultima sincronizzazione, o "mai"', () => {
    expect(updatedText(at, now)).toBe('Aggiornato alle 14:32')
    expect(updatedText(null, now)).toBe('Mai sincronizzato')
  })
})

describe('syncLine', () => {
  it('permesso scaduto senza modifiche: ora dell\'aggiornamento e "Sincronizza", senza avviso', () => {
    expect(syncLine(view({ status: 'needs-auth' }), now)).toEqual({
      title: 'Aggiornato alle 14:32',
      detail: 'Sincronizza',
      renew: true,
      warn: false,
    })
  })

  it('permesso scaduto con modifiche da inviare', () => {
    const l = syncLine(view({ status: 'needs-auth', pending: true }), now)
    expect(l.title).toBe('Modifiche da inviare')
    expect(l.renew).toBe(true)
    expect(l.warn).toBe(false)
  })

  it('rinnovo automatico non riuscito: avviso', () => {
    const l = syncLine(view({ status: 'needs-auth', pending: true, askReconnect: true }), now)
    expect(l).toMatchObject({ title: 'In pausa', detail: 'Riconnetti a Google', renew: true, warn: true })
  })

  it('tutto a posto, senza rete, bloccata', () => {
    expect(syncLine(view({}), now)).toMatchObject({ title: 'Sincronizzato', detail: 'Aggiornato alle 14:32', renew: false })
    expect(syncLine(view({ status: 'offline', pending: true }), now).detail).toBe('Modifiche salvate qui')
    expect(syncLine(view({ status: 'offline' }), now).detail).toBe('Aggiornato alle 14:32')
    expect(syncLine(view({ status: 'locked' }), now)).toMatchObject({ renew: false, warn: true })
    expect(syncLine(view({ status: 'off' }), now).title).toBe('Solo su questo dispositivo')
  })
})

describe('statusLabel', () => {
  it('permesso scaduto: dipende dalle modifiche da inviare', () => {
    expect(statusLabel('needs-auth')).toBe('In pausa: riconnettiti a Google')
    expect(statusLabel('needs-auth', { pending: false, askReconnect: false })).toBe('In pausa: nessuna modifica da inviare')
    expect(statusLabel('needs-auth', { pending: true, askReconnect: false })).toMatch(/^Modifiche da inviare/)
    expect(statusLabel('needs-auth', { pending: false, askReconnect: true })).toBe('In pausa: riconnettiti a Google')
  })
})
