/**
 * Blocco dell'app con PIN (e impronta, vedi lock.svelte.ts): logica pura, testabile.
 *
 * Il PIN non viene mai salvato: si conserva solo un'impronta PBKDF2-SHA256 con sale casuale.
 * Dopo 5 tentativi sbagliati di fila si deve aspettare, con attese che raddoppiano (max 15 minuti).
 * È una barriera contro chi prende in mano il telefono sbloccato: i dati sul dispositivo non sono
 * cifrati con il PIN (vedi SECURITY.md).
 */

export const LOCK_KEY = 'statera.blocco'
export const PIN_ITERATIONS = 210_000
export const FREE_ATTEMPTS = 5
export const MAX_WAIT_MS = 15 * 60 * 1000

/** Dopo quanto tempo in background l'app si blocca (secondi). 0 = appena la si lascia. */
export const TIMEOUTS: { value: number; label: string }[] = [
  { value: 0, label: 'Subito' },
  { value: 60, label: 'Dopo 1 minuto' },
  { value: 300, label: 'Dopo 5 minuti' },
  { value: 900, label: 'Dopo 15 minuti' },
]

export interface LockConfig {
  v: 1
  salt: string
  iterations: number
  hash: string
  /** Lunghezza del PIN: lo sblocco parte appena si è scritta l'ultima cifra. */
  length: number
  timeout: number
  /** Credenziale WebAuthn del dispositivo (impronta, volto o blocco schermo), o null. */
  bio: { id: string } | null
  fails: number
  /** Prima di questo istante (ms) non si può riprovare. */
  waitUntil: number
}

export interface Storage {
  getItem(k: string): string | null
  setItem(k: string, v: string): void
  removeItem(k: string): void
}

export function pinProblem(pin: string): string | null {
  if (!/^\d+$/.test(pin)) return 'Il PIN può contenere solo cifre'
  if (pin.length < 4) return 'Il PIN deve avere almeno 4 cifre'
  if (pin.length > 8) return 'Il PIN può avere al massimo 8 cifre'
  if (/^(\d)\1+$/.test(pin)) return 'Scegli un PIN meno prevedibile (non tutte cifre uguali)'
  if ('0123456789'.includes(pin) || '9876543210'.includes(pin)) return 'Scegli un PIN meno prevedibile (non una sequenza)'
  return null
}

const b64 = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes))
const unb64 = (s: string) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0))

async function derive(pin: string, salt: Uint8Array, iterations: number): Promise<Uint8Array> {
  const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pin), 'PBKDF2', false, ['deriveBits'])
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: salt as BufferSource, iterations }, base, 256)
  return new Uint8Array(bits)
}

export async function makeConfig(pin: string, timeout: number, iterations = PIN_ITERATIONS): Promise<LockConfig> {
  const problem = pinProblem(pin)
  if (problem) throw new Error(problem)
  const salt = crypto.getRandomValues(new Uint8Array(16))
  const hash = await derive(pin, salt, iterations)
  return { v: 1, salt: b64(salt), iterations, hash: b64(hash), length: pin.length, timeout, bio: null, fails: 0, waitUntil: 0 }
}

/** Confronto a tempo costante. */
function same(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false
  let diff = 0
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i]
  return diff === 0
}

export async function pinMatches(cfg: LockConfig, pin: string): Promise<boolean> {
  if (!/^\d{1,12}$/.test(pin)) return false
  return same(await derive(pin, unb64(cfg.salt), cfg.iterations), unb64(cfg.hash))
}

/** Attesa dopo `fails` errori di fila: 0 fino al quinto, poi 30 s, 60 s, 2 min… fino a 15 min. */
export function waitAfter(fails: number): number {
  if (fails < FREE_ATTEMPTS) return 0
  return Math.min(MAX_WAIT_MS, 30_000 * 2 ** (fails - FREE_ATTEMPTS))
}

export type Attempt = { ok: true; cfg: LockConfig } | { ok: false; cfg: LockConfig; waitMs: number; reason: 'wrong' | 'wait' }

/** Prova un PIN rispettando le attese; restituisce la configurazione aggiornata (contatore errori). */
export async function tryPin(cfg: LockConfig, pin: string, now = Date.now()): Promise<Attempt> {
  if (now < cfg.waitUntil) return { ok: false, cfg, waitMs: cfg.waitUntil - now, reason: 'wait' }
  if (await pinMatches(cfg, pin)) return { ok: true, cfg: { ...cfg, fails: 0, waitUntil: 0 } }
  const fails = cfg.fails + 1
  const wait = waitAfter(fails)
  return { ok: false, cfg: { ...cfg, fails, waitUntil: wait ? now + wait : 0 }, waitMs: wait, reason: 'wrong' }
}

export function readConfig(s: Storage): LockConfig | null {
  try {
    const raw = s.getItem(LOCK_KEY)
    if (!raw) return null
    const c = JSON.parse(raw) as LockConfig
    return c && c.v === 1 && c.hash && c.salt ? c : null
  } catch {
    return null
  }
}

export function writeConfig(s: Storage, cfg: LockConfig | null) {
  if (cfg) s.setItem(LOCK_KEY, JSON.stringify(cfg))
  else s.removeItem(LOCK_KEY)
}

/** Va bloccata al ritorno in primo piano? */
export function shouldLock(cfg: LockConfig | null, hiddenAt: number | null, now = Date.now()): boolean {
  if (!cfg || hiddenAt === null) return false
  return now - hiddenAt >= cfg.timeout * 1000
}

export function formatWait(ms: number): string {
  const s = Math.ceil(ms / 1000)
  if (s < 60) return `${s} secondi`
  const m = Math.ceil(s / 60)
  return m === 1 ? '1 minuto' : `${m} minuti`
}
