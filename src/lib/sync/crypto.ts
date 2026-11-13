/**
 * CIFRATURA DI STATERA (Web Crypto, nessuna libreria esterna)
 *
 * - Una "chiave dati" casuale AES-256-GCM cifra tutto ciò che va su Drive.
 * - La chiave dati è salvata su Drive solo "incartata" (cifrata) due volte:
 *   con una chiave derivata dalla password (PBKDF2-SHA256, 600.000 iterazioni)
 *   e con una chiave derivata dalla chiave di recupero.
 * - Sul dispositivo la chiave dati è conservata come CryptoKey NON esportabile.
 * - La password e la chiave di recupero non lasciano mai il dispositivo.
 */

const subtle = globalThis.crypto.subtle
const enc = new TextEncoder()
const dec = new TextDecoder()

export const PASSWORD_ITERATIONS = 600_000
export const RECOVERY_ITERATIONS = 100_000

// ---------- base64 ----------

export function toB64(bytes: ArrayBuffer | Uint8Array): string {
  const u = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes)
  let s = ''
  for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000))
  return btoa(s)
}

export function fromB64(b64: string): Uint8Array<ArrayBuffer> {
  const s = atob(b64)
  const u = new Uint8Array(s.length)
  for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i)
  return u
}

function random(n: number): Uint8Array<ArrayBuffer> {
  return globalThis.crypto.getRandomValues(new Uint8Array(n))
}

// ---------- chiave di recupero ----------

const B32 = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789' // senza I, O, 0, 1: niente confusione

/** Chiave di recupero leggibile: 8 gruppi da 4 caratteri (160 bit). */
export function generateRecoveryKey(): string {
  const bytes = random(32)
  let out = ''
  for (const b of bytes) out += B32[b % 32]
  return out.match(/.{4}/g)!.join('-')
}

/** Normalizza ciò che l'utente digita: maiuscole, senza spazi né trattini. */
export function normalizeRecoveryKey(text: string): string {
  return text.toUpperCase().replace(/[^A-Z0-9]/g, '')
}

export function isRecoveryKeyShape(text: string): boolean {
  const n = normalizeRecoveryKey(text)
  return n.length === 32 && [...n].every((c) => B32.includes(c))
}

// ---------- derivazione e incarto ----------

async function deriveKek(secret: string, salt: Uint8Array<ArrayBuffer>, iterations: number): Promise<CryptoKey> {
  const base = await subtle.importKey('raw', enc.encode(secret), 'PBKDF2', false, ['deriveKey'])
  return subtle.deriveKey(
    { name: 'PBKDF2', hash: 'SHA-256', salt, iterations },
    base,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt'],
  )
}

interface Wrapped {
  salt: string
  iv: string
  data: string
  iterations: number
}

async function wrap(raw: Uint8Array<ArrayBuffer>, secret: string, iterations: number): Promise<Wrapped> {
  const salt = random(16)
  const iv = random(12)
  const kek = await deriveKek(secret, salt, iterations)
  const data = await subtle.encrypt({ name: 'AES-GCM', iv }, kek, raw)
  return { salt: toB64(salt), iv: toB64(iv), data: toB64(data), iterations }
}

async function unwrap(w: Wrapped, secret: string): Promise<Uint8Array<ArrayBuffer>> {
  const kek = await deriveKek(secret, fromB64(w.salt), w.iterations)
  try {
    return new Uint8Array(await subtle.decrypt({ name: 'AES-GCM', iv: fromB64(w.iv) }, kek, fromB64(w.data)))
  } catch {
    throw new WrongSecretError()
  }
}

export class WrongSecretError extends Error {
  constructor() {
    super('Password o chiave di recupero non corretta')
    this.name = 'WrongSecretError'
  }
}

/** File delle chiavi salvato su Drive: contiene solo la chiave dati "incartata". */
export interface KeysFile {
  format: 'statera-keys'
  v: 1
  createdAt: string
  password: Wrapped
  recovery: Wrapped
}

function importDataKey(raw: Uint8Array<ArrayBuffer>, extractable = false): Promise<CryptoKey> {
  return subtle.importKey('raw', raw, { name: 'AES-GCM' }, extractable, ['encrypt', 'decrypt'])
}

/** Prima attivazione: crea la chiave dati e la incarta con password e chiave di recupero. */
export async function createKeys(
  password: string,
  recoveryKey: string,
): Promise<{ keys: KeysFile; dataKey: CryptoKey }> {
  const raw = random(32)
  const keys: KeysFile = {
    format: 'statera-keys',
    v: 1,
    createdAt: new Date().toISOString(),
    password: await wrap(raw, password, PASSWORD_ITERATIONS),
    recovery: await wrap(raw, normalizeRecoveryKey(recoveryKey), RECOVERY_ITERATIONS),
  }
  return { keys, dataKey: await importDataKey(raw) }
}

/** Sblocco con la password. */
export async function unlockWithPassword(keys: KeysFile, password: string): Promise<CryptoKey> {
  return importDataKey(await unwrap(keys.password, password))
}

/** Sblocco con la chiave di recupero. */
export async function unlockWithRecovery(keys: KeysFile, recoveryKey: string): Promise<CryptoKey> {
  return importDataKey(await unwrap(keys.recovery, normalizeRecoveryKey(recoveryKey)))
}

/**
 * Nuova password: serve la password attuale oppure la chiave di recupero.
 * La chiave dati non cambia, quindi i dati e i backup restano leggibili.
 */
export async function changePassword(
  keys: KeysFile,
  current: { password?: string; recoveryKey?: string },
  newPassword: string,
): Promise<KeysFile> {
  const raw = current.password
    ? await unwrap(keys.password, current.password)
    : await unwrap(keys.recovery, normalizeRecoveryKey(current.recoveryKey ?? ''))
  return { ...keys, password: await wrap(raw, newPassword, PASSWORD_ITERATIONS) }
}

export function parseKeysFile(text: string): KeysFile {
  const k = JSON.parse(text) as KeysFile
  if (k?.format !== 'statera-keys' || k.v !== 1 || !k.password?.data || !k.recovery?.data) {
    throw new Error('File delle chiavi su Drive non riconosciuto')
  }
  return k
}

// ---------- cifratura dei dati ----------

export interface Sealed {
  format: 'statera-sync'
  v: 1
  iv: string
  data: string
}

export async function seal(key: CryptoKey, value: unknown): Promise<string> {
  const iv = random(12)
  const data = await subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(JSON.stringify(value)))
  const out: Sealed = { format: 'statera-sync', v: 1, iv: toB64(iv), data: toB64(data) }
  return JSON.stringify(out)
}

export async function open<T>(key: CryptoKey, text: string): Promise<T> {
  const s = JSON.parse(text) as Sealed
  if (s?.format !== 'statera-sync' || s.v !== 1) throw new Error('File di sincronizzazione non riconosciuto')
  try {
    const plain = await subtle.decrypt({ name: 'AES-GCM', iv: fromB64(s.iv) }, key, fromB64(s.data))
    return JSON.parse(dec.decode(plain)) as T
  } catch {
    throw new Error('Impossibile decifrare i dati su Drive: la chiave di questo dispositivo non corrisponde')
  }
}

/** Requisiti minimi della password. Restituisce un messaggio d'errore o null. */
export function passwordProblem(pw: string): string | null {
  if (pw.length < 10) return 'La password deve avere almeno 10 caratteri'
  if (/^(.)\1+$/.test(pw)) return 'La password è troppo semplice'
  return null
}
