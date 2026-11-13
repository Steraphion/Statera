/** Gli importi sono sempre interi in centesimi: 1234 = 12,34 € */

const euro = new Intl.NumberFormat('it-IT', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
})

export function formatEuro(cents: number): string {
  return euro.format(cents / 100)
}

const monthFmt = new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' })

export function formatMonth(date: Date): string {
  const s = monthFmt.format(date)
  return s.charAt(0).toUpperCase() + s.slice(1)
}
