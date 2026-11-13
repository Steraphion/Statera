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
