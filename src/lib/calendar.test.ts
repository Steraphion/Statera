import { describe, expect, it } from 'vitest'
import { addMonths, inRange, longDate, monthCells, monthInRange, monthLabel, ymOf } from './calendar'

describe('calendario della scelta della data', () => {
  it('settimane da lunedì e giorni del mese', () => {
    const nov = monthCells({ year: 2026, month: 10 })
    // 1 novembre 2026 è domenica: sei celle vuote prima
    expect(nov.slice(0, 7)).toEqual([null, null, null, null, null, null, '2026-11-01'])
    expect(nov.at(-1)).toBe('2026-11-30')
    expect(monthCells({ year: 2028, month: 1 }).filter(Boolean)).toHaveLength(29)
  })

  it('mesi avanti e indietro, anche a cavallo dell\'anno', () => {
    expect(addMonths({ year: 2026, month: 0 }, -1)).toEqual({ year: 2025, month: 11 })
    expect(addMonths({ year: 2026, month: 11 }, 1)).toEqual({ year: 2027, month: 0 })
    expect(addMonths({ year: 2026, month: 5 }, -18)).toEqual({ year: 2024, month: 11 })
  })

  it('limiti min e max del campo', () => {
    expect(inRange('2026-11-15', '2026-11-01', '2026-11-30')).toBe(true)
    expect(inRange('2026-10-31', '2026-11-01')).toBe(false)
    expect(inRange('2026-12-01', null, '2026-11-30')).toBe(false)
    expect(monthInRange({ year: 2026, month: 9 }, '2026-10-31')).toBe(true)
    expect(monthInRange({ year: 2026, month: 9 }, '2026-11-01')).toBe(false)
  })

  it('nomi in italiano', () => {
    expect(ymOf('2026-11-15')).toEqual({ year: 2026, month: 10 })
    expect(ymOf('')).toBeNull()
    expect(monthLabel({ year: 2026, month: 10 })).toBe('novembre 2026')
    expect(longDate('2026-11-15')).toBe('domenica 15 novembre 2026')
  })
})
