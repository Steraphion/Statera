/**
 * Accesso a Google (Google Identity Services, modello a token) e a Google Drive.
 * Nessun server: il browser chiede a Google un permesso temporaneo (circa 1 ora)
 * limitato alla cartella nascosta dell'app, e parla direttamente con Drive.
 */

export const GOOGLE_CLIENT_ID = '176639576509-mjut55fdo9n0e5ltamq30akmdef9frvc.apps.googleusercontent.com'
export const DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive.appdata'
const GIS_SRC = 'https://accounts.google.com/gsi/client'
const API = 'https://www.googleapis.com/drive/v3'
const UPLOAD = 'https://www.googleapis.com/upload/drive/v3'

// ---------- Google Identity Services ----------

interface TokenResponse {
  access_token?: string
  expires_in?: number
  scope?: string
  error?: string
  error_description?: string
}

interface TokenClient {
  requestAccessToken(overrides?: { prompt?: string; login_hint?: string }): void
}

interface GoogleOAuth2 {
  initTokenClient(config: {
    client_id: string
    scope: string
    callback: (r: TokenResponse) => void
    error_callback?: (e: { type: string; message?: string }) => void
  }): TokenClient
  hasGrantedAllScopes(r: TokenResponse, ...scopes: string[]): boolean
  revoke(token: string, done?: () => void): void
}

declare global {
  interface Window {
    google?: { accounts?: { oauth2?: GoogleOAuth2 } }
  }
}

let gisPromise: Promise<GoogleOAuth2> | null = null

/** Carica la libreria di Google (una volta sola). */
export function loadGis(): Promise<GoogleOAuth2> {
  if (window.google?.accounts?.oauth2) return Promise.resolve(window.google.accounts.oauth2)
  if (gisPromise) return gisPromise
  gisPromise = new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = GIS_SRC
    s.async = true
    s.onload = () => {
      const o = window.google?.accounts?.oauth2
      if (o) resolve(o)
      else reject(new Error('Libreria Google non disponibile'))
    }
    s.onerror = () => {
      gisPromise = null
      reject(new Error('Impossibile contattare Google: controlla la connessione'))
    }
    document.head.appendChild(s)
  })
  return gisPromise
}

export interface Token {
  value: string
  /** Scadenza in ms. */
  expiresAt: number
}

/** La finestra di Google non ha risposto (es. telefono: collegamento con l'app perso). */
export class PopupLostError extends Error {
  constructor() {
    super('La finestra di Google non ha risposto: usa «Riconnetti a Google»')
    this.name = 'PopupLostError'
  }
}

/** Dopo il ritorno all'app, quanto si aspetta la risposta della finestra prima di darla per persa. */
export const POPUP_GRACE_MS = 5000
/** Tempo massimo per un rinnovo con la finestra (senza scelte da fare si chiude in pochi secondi). */
export const POPUP_MAX_MS = 90_000

/**
 * Rinnovo veloce del permesso con la finestra di Google, da chiamare in risposta a un tocco: se
 * l'accesso è già stato dato la finestra si richiude da sola. Per gli accessi con scelte da fare
 * (primo collegamento, «Riconnetti») si usa `startRedirect`, perché sul telefono la finestra può
 * perdere il collegamento con l'app e restare bianca.
 *
 * Se la libreria è già caricata la finestra si apre subito, nello stesso tocco (alcuni browser
 * bloccano le finestre aperte dopo un'attesa). Se la finestra non risponde entro pochi secondi dal
 * ritorno all'app, o comunque entro `POPUP_MAX_MS`, la richiesta fallisce con `PopupLostError`.
 */
export function requestToken(opts: { silent?: boolean; hint?: string } = {}): Promise<Token> {
  const ready = window.google?.accounts?.oauth2
  return ready ? ask(ready, opts) : loadGis().then((o) => ask(o, opts))
}

function ask(oauth2: GoogleOAuth2, opts: { silent?: boolean; hint?: string }): Promise<Token> {
  return new Promise<Token>((resolve, reject) => {
    let settled = false
    let grace: ReturnType<typeof setTimeout> | null = null
    let hidden = false
    const finish = () => {
      settled = true
      clearTimeout(limit)
      if (grace) clearTimeout(grace)
      document.removeEventListener('visibilitychange', onVisibility)
    }
    const ok = (t: Token) => {
      if (settled) return
      finish()
      resolve(t)
    }
    const fail = (e: Error) => {
      if (settled) return
      finish()
      reject(e)
    }
    // Sul telefono la finestra copre l'app: tornati all'app senza risposta, la si dà per persa
    const onVisibility = () => {
      if (document.visibilityState === 'hidden') {
        hidden = true
        if (grace) clearTimeout(grace)
        grace = null
      } else if (hidden && !grace) {
        grace = setTimeout(() => fail(new PopupLostError()), POPUP_GRACE_MS)
      }
    }
    document.addEventListener('visibilitychange', onVisibility)
    const limit = setTimeout(() => fail(new PopupLostError()), POPUP_MAX_MS)

    const client = oauth2.initTokenClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: DRIVE_SCOPE,
      callback: (r) => {
        if (r.error || !r.access_token) {
          fail(new Error(r.error === 'access_denied' ? 'Accesso a Google annullato' : r.error_description || 'Accesso a Google non riuscito'))
          return
        }
        if (!oauth2.hasGrantedAllScopes(r, DRIVE_SCOPE)) {
          fail(new Error(SCOPE_MISSING))
          return
        }
        ok({ value: r.access_token, expiresAt: Date.now() + ((r.expires_in ?? 3600) - 60) * 1000 })
      },
      error_callback: (e) => {
        fail(
          new Error(
            e.type === 'popup_closed'
              ? 'Finestra di Google chiusa prima di completare l\'accesso'
              : e.type === 'popup_failed_to_open'
                ? 'Il browser ha bloccato la finestra di Google: usa «Riconnetti a Google»'
                : e.message || 'Accesso a Google non riuscito',
          ),
        )
      },
    })
    client.requestAccessToken({ prompt: opts.silent ? '' : 'consent', login_hint: opts.hint })
  })
}

const SCOPE_MISSING = 'Serve il permesso per la cartella dell\'app su Google Drive: riprova e lascia la casella spuntata'

// ---------- Accesso con reindirizzamento (pagina di Google e ritorno all'app) ----------

const AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
/** Richiesta in corso (una sola), per riconoscere la risposta al ritorno. */
export const PENDING_AUTH_KEY = 'statera.accessoGoogle'
/** Una risposta arrivata dopo questo tempo non vale più. */
export const PENDING_MAX_MS = 30 * 60 * 1000

/** Perché si va da Google: primo collegamento o rinnovo di un profilo già collegato. */
export type AuthPurpose = 'connect' | 'reconnect'

export interface PendingAuth {
  state: string
  purpose: AuthPurpose
  /** Database del profilo che ha chiesto l'accesso. */
  db: string
  /** Schermata da riaprire al ritorno (hash). */
  route: string
  at: number
}

export interface AuthResult {
  purpose: AuthPurpose
  db: string
  route: string
  token?: Token
  error?: string
}

/**
 * Indirizzo a cui Google rimanda: deve coincidere con un «URI di reindirizzamento autorizzato» del
 * client su Google Cloud. Per l'app pubblicata è fisso; altrove (collaudo in locale) è la pagina stessa.
 */
export function redirectUri(loc: { hostname: string; origin: string; pathname: string }): string {
  if (loc.hostname === 'steraphion.github.io') return 'https://steraphion.github.io/Statera/'
  return loc.origin + loc.pathname.replace(/index\.html$/, '')
}

/** Indirizzo della pagina di Google (flusso «implicit» di OAuth 2.0 per le app nel browser). */
export function authUrl(p: { state: string; redirect: string; purpose: AuthPurpose; hint?: string }): string {
  const q = new URLSearchParams({
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: p.redirect,
    response_type: 'token',
    scope: DRIVE_SCOPE,
    state: p.state,
  })
  // Primo collegamento: si sceglie l'account; rinnovo: si propone quello già collegato
  if (p.purpose === 'connect') q.set('prompt', 'select_account')
  if (p.hint) q.set('login_hint', p.hint)
  return `${AUTH_ENDPOINT}?${q}`
}

/** La parte dopo # contiene una risposta di Google (e non una schermata dell'app). */
export function isAuthResponse(hash: string): boolean {
  const h = hash.replace(/^#/, '')
  if (h.startsWith('/')) return false
  const q = new URLSearchParams(h)
  return q.has('state') && (q.has('access_token') || q.has('error'))
}

/**
 * Legge la risposta di Google. Vale solo se corrisponde alla richiesta in corso (stesso `state`,
 * non scaduta): un permesso arrivato da un link altrui viene ignorato.
 */
export function parseAuthResponse(hash: string, pending: PendingAuth | null, now: number): AuthResult | null {
  if (!isAuthResponse(hash)) return null
  const q = new URLSearchParams(hash.replace(/^#/, ''))
  if (!pending || q.get('state') !== pending.state || now - pending.at > PENDING_MAX_MS || now < pending.at - 60_000) {
    return null
  }
  const base = { purpose: pending.purpose, db: pending.db, route: pending.route }
  const error = q.get('error')
  if (error) {
    return { ...base, error: error === 'access_denied' ? 'Accesso a Google annullato' : `Accesso a Google non riuscito (${error})` }
  }
  const scopes = (q.get('scope') ?? '').split(/\s+/)
  if (!scopes.includes(DRIVE_SCOPE)) return { ...base, error: SCOPE_MISSING }
  const expires = Number(q.get('expires_in')) || 3600
  return { ...base, token: { value: q.get('access_token') ?? '', expiresAt: now + (expires - 60) * 1000 } }
}

function randomState(): string {
  const b = crypto.getRandomValues(new Uint8Array(16))
  return Array.from(b, (x) => x.toString(16).padStart(2, '0')).join('')
}

/**
 * Va alla pagina di Google, che al termine rimanda all'app con il permesso (lo legge
 * `takeAuthResult` all'avvio). Funziona anche dove la finestra non può tornare all'app.
 */
export function startRedirect(purpose: AuthPurpose, db: string, hint?: string) {
  const state = randomState()
  const route = location.hash && !isAuthResponse(location.hash) ? location.hash : '#/altro'
  const pending: PendingAuth = { state, purpose, db, route, at: Date.now() }
  localStorage.setItem(PENDING_AUTH_KEY, JSON.stringify(pending))
  location.assign(authUrl({ state, redirect: redirectUri(location), purpose, hint }))
}

/**
 * All'avvio, prima del router: se l'indirizzo contiene la risposta di Google la legge, toglie il
 * permesso dall'indirizzo (e dalla cronologia) e riporta alla schermata di partenza.
 */
export function takeAuthResult(): AuthResult | null {
  if (typeof location === 'undefined' || !isAuthResponse(location.hash)) return null
  let pending: PendingAuth | null = null
  try {
    pending = JSON.parse(localStorage.getItem(PENDING_AUTH_KEY) ?? 'null') as PendingAuth | null
    localStorage.removeItem(PENDING_AUTH_KEY)
  } catch {
    pending = null
  }
  const result = parseAuthResponse(location.hash, pending, Date.now())
  history.replaceState(null, '', location.pathname + location.search + (result?.route ?? pending?.route ?? '#/altro'))
  return result
}

export async function revokeToken(token: string) {
  try {
    const oauth2 = await loadGis()
    await new Promise<void>((r) => oauth2.revoke(token, () => r()))
  } catch {
    // Non importa: il permesso scade comunque da solo
  }
}

// ---------- Google Drive (cartella nascosta dell'app) ----------

export class AuthExpiredError extends Error {
  constructor() {
    super('Accesso a Google scaduto')
    this.name = 'AuthExpiredError'
  }
}

export class OfflineError extends Error {
  constructor() {
    super('Nessuna connessione')
    this.name = 'OfflineError'
  }
}

export interface DriveFile {
  id: string
  name: string
  modifiedTime?: string
  size?: string
}

export class Drive {
  constructor(private token: string) {}

  private async call(url: string, init: RequestInit = {}): Promise<Response> {
    let res: Response
    try {
      res = await fetch(url, {
        ...init,
        headers: { ...(init.headers ?? {}), Authorization: `Bearer ${this.token}` },
        cache: 'no-store',
      })
    } catch {
      throw new OfflineError()
    }
    if (res.status === 401) throw new AuthExpiredError()
    if (!res.ok) {
      let detail = ''
      try {
        detail = (await res.json())?.error?.message ?? ''
      } catch {
        /* niente */
      }
      throw new Error(`Google Drive ha risposto con un errore (${res.status})${detail ? `: ${detail}` : ''}`)
    }
    return res
  }

  async user(): Promise<{ email: string; name: string } | null> {
    try {
      const r = await this.call(`${API}/about?fields=user(emailAddress,displayName)`)
      const j = await r.json()
      return { email: j.user?.emailAddress ?? '', name: j.user?.displayName ?? '' }
    } catch (e) {
      if (e instanceof AuthExpiredError || e instanceof OfflineError) throw e
      return null
    }
  }

  async list(): Promise<DriveFile[]> {
    const out: DriveFile[] = []
    let page = ''
    do {
      const q = new URLSearchParams({
        spaces: 'appDataFolder',
        fields: 'nextPageToken,files(id,name,modifiedTime,size)',
        pageSize: '200',
        orderBy: 'name',
      })
      if (page) q.set('pageToken', page)
      const j = await (await this.call(`${API}/files?${q}`)).json()
      out.push(...(j.files ?? []))
      page = j.nextPageToken ?? ''
    } while (page)
    return out
  }

  async read(id: string): Promise<string> {
    return (await this.call(`${API}/files/${encodeURIComponent(id)}?alt=media`)).text()
  }

  async create(name: string, content: string): Promise<DriveFile> {
    const boundary = `statera-${crypto.randomUUID()}`
    const body =
      `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n` +
      JSON.stringify({ name, parents: ['appDataFolder'], mimeType: 'application/json' }) +
      `\r\n--${boundary}\r\nContent-Type: application/json\r\n\r\n` +
      content +
      `\r\n--${boundary}--`
    const r = await this.call(`${UPLOAD}/files?uploadType=multipart&fields=id,name,modifiedTime`, {
      method: 'POST',
      headers: { 'Content-Type': `multipart/related; boundary=${boundary}` },
      body,
    })
    return r.json()
  }

  async update(id: string, content: string): Promise<DriveFile> {
    const r = await this.call(`${UPLOAD}/files/${encodeURIComponent(id)}?uploadType=media&fields=id,name,modifiedTime`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: content,
    })
    return r.json()
  }

  async remove(id: string): Promise<void> {
    await this.call(`${API}/files/${encodeURIComponent(id)}`, { method: 'DELETE' })
  }
}
