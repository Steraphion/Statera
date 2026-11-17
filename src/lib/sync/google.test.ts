import { describe, expect, it } from 'vitest'
import { DRIVE_SCOPE, GOOGLE_CLIENT_ID, PENDING_MAX_MS, authUrl, isAuthResponse, parseAuthResponse, redirectUri, type PendingAuth } from './google'

const pending: PendingAuth = { state: 'abc123', purpose: 'connect', db: 'statera-locale', route: '#/altro', at: 1_000_000 }
const ok = (extra = '') => `#access_token=tok-1&token_type=Bearer&expires_in=3599&scope=${encodeURIComponent(DRIVE_SCOPE)}&state=abc123${extra}`

describe('accesso con reindirizzamento', () => {
  it('indirizzo di ritorno: fisso per l\'app pubblicata, la pagina stessa altrove', () => {
    expect(redirectUri({ hostname: 'steraphion.github.io', origin: 'https://steraphion.github.io', pathname: '/statera/index.html' })).toBe(
      'https://steraphion.github.io/Statera/',
    )
    expect(redirectUri({ hostname: 'localhost', origin: 'http://localhost:4173', pathname: '/index.html' })).toBe('http://localhost:4173/')
    expect(redirectUri({ hostname: 'localhost', origin: 'http://localhost:4173', pathname: '/' })).toBe('http://localhost:4173/')
  })

  it('pagina di Google: permesso della sola cartella dell\'app, risposta col permesso', () => {
    const u = new URL(authUrl({ state: 's1', redirect: 'https://steraphion.github.io/Statera/', purpose: 'connect' }))
    expect(u.origin + u.pathname).toBe('https://accounts.google.com/o/oauth2/v2/auth')
    expect(u.searchParams.get('client_id')).toBe(GOOGLE_CLIENT_ID)
    expect(u.searchParams.get('response_type')).toBe('token')
    expect(u.searchParams.get('scope')).toBe(DRIVE_SCOPE)
    expect(u.searchParams.get('state')).toBe('s1')
    expect(u.searchParams.get('redirect_uri')).toBe('https://steraphion.github.io/Statera/')
    expect(u.searchParams.get('prompt')).toBe('select_account')
    const r = new URL(authUrl({ state: 's2', redirect: 'x', purpose: 'reconnect', hint: 'utente.prova@example.com' }))
    expect(r.searchParams.get('prompt')).toBeNull()
    expect(r.searchParams.get('login_hint')).toBe('utente.prova@example.com')
  })

  it('riconosce la risposta di Google e non le schermate dell\'app', () => {
    expect(isAuthResponse(ok())).toBe(true)
    expect(isAuthResponse('#error=access_denied&state=abc123')).toBe(true)
    expect(isAuthResponse('#/movimenti')).toBe(false)
    expect(isAuthResponse('#/conto/abc')).toBe(false)
    expect(isAuthResponse('')).toBe(false)
    expect(isAuthResponse('#access_token=x')).toBe(false)
  })

  it('permesso valido: scadenza con un minuto di margine, schermata di partenza', () => {
    const r = parseAuthResponse(ok(), pending, 1_000_500)!
    expect(r.token).toEqual({ value: 'tok-1', expiresAt: 1_000_500 + 3539 * 1000 })
    expect(r).toMatchObject({ purpose: 'connect', db: 'statera-locale', route: '#/altro' })
    expect(r.error).toBeUndefined()
  })

  it('ignora risposte che non corrispondono alla richiesta in corso', () => {
    expect(parseAuthResponse(ok(), null, 1_000_500)).toBeNull()
    expect(parseAuthResponse(ok().replace('abc123', 'altro'), pending, 1_000_500)).toBeNull()
    expect(parseAuthResponse(ok(), pending, 1_000_000 + PENDING_MAX_MS + 1)).toBeNull()
    expect(parseAuthResponse('#/altro', pending, 1_000_500)).toBeNull()
  })

  it('errori: accesso annullato, permesso della cartella mancante', () => {
    expect(parseAuthResponse('#error=access_denied&state=abc123', pending, 1_000_500)?.error).toBe('Accesso a Google annullato')
    expect(parseAuthResponse('#error=server_error&state=abc123', pending, 1_000_500)?.error).toContain('server_error')
    const noScope = parseAuthResponse('#access_token=t&expires_in=3600&scope=email&state=abc123', pending, 1_000_500)!
    expect(noScope.token).toBeUndefined()
    expect(noScope.error).toContain('cartella')
  })
})
