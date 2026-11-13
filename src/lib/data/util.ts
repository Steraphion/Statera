import type { Base } from './types'

export function newId(): string {
  return crypto.randomUUID()
}

export function baseFields(now = Date.now()): Base {
  return { id: newId(), createdAt: now, updatedAt: now, deletedAt: null }
}

/** Data di oggi nel fuso del dispositivo, formato 'AAAA-MM-GG'. */
export function today(d = new Date()): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** Record visibili: non cancellati. */
export function alive<T extends Base>(rows: T[]): T[] {
  return rows.filter((r) => r.deletedAt === null)
}

export function byOrder<T extends { order: number; name: string }>(a: T, b: T): number {
  return a.order - b.order || a.name.localeCompare(b.name, 'it')
}

/**
 * Attende una promessa ma non all'infinito: se il database non risponde
 * (es. bloccato da un'altra finestra dell'app), meglio un errore chiaro
 * che un pulsante fermo per sempre.
 */
export function withTimeout<T>(p: Promise<T>, ms = 10_000, message = 'Il salvataggio non risponde'): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const t = setTimeout(
      () => reject(new Error(`${message}. Chiudi Statera (anche dalle app recenti) e riaprila.`)),
      ms,
    )
    p.then(
      (v) => {
        clearTimeout(t)
        resolve(v)
      },
      (e) => {
        clearTimeout(t)
        reject(e)
      },
    )
  })
}

export function errorMessage(e: unknown): string {
  if (e instanceof Error) return e.message
  return String(e)
}

/** Ordine alfabetico italiano, senza distinguere maiuscole e accenti. */
export function byName<T extends { name: string }>(a: T, b: T): number {
  return a.name.localeCompare(b.name, 'it', { sensitivity: 'base' })
}
