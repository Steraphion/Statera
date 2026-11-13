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

/**
 * Chiede a Google un permesso temporaneo. Va chiamata in risposta a un tocco
 * dell'utente (Google apre una finestra). Con `silent` non chiede di nuovo il
 * consenso se già dato.
 */
export async function requestToken(opts: { silent?: boolean; hint?: string } = {}): Promise<Token> {
  const oauth2 = await loadGis()
  return new Promise<Token>((resolve, reject) => {
    const client = oauth2.initTokenClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: DRIVE_SCOPE,
      callback: (r) => {
        if (r.error || !r.access_token) {
          reject(new Error(r.error === 'access_denied' ? 'Accesso a Google annullato' : r.error_description || 'Accesso a Google non riuscito'))
          return
        }
        if (!oauth2.hasGrantedAllScopes(r, DRIVE_SCOPE)) {
          reject(
            new Error(
              'Serve il permesso per la cartella dell\'app su Google Drive: riprova e lascia la casella spuntata',
            ),
          )
          return
        }
        resolve({ value: r.access_token, expiresAt: Date.now() + ((r.expires_in ?? 3600) - 60) * 1000 })
      },
      error_callback: (e) => {
        reject(
          new Error(
            e.type === 'popup_closed'
              ? 'Finestra di Google chiusa prima di completare l\'accesso'
              : e.type === 'popup_failed_to_open'
                ? 'Il browser ha bloccato la finestra di Google: riprova toccando il pulsante'
                : e.message || 'Accesso a Google non riuscito',
          ),
        )
      },
    })
    client.requestAccessToken({ prompt: opts.silent ? '' : 'consent', login_hint: opts.hint })
  })
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
