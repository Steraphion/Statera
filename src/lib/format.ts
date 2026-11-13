/** Gli importi sono sempre interi in centesimi: 1234 = 12,34 € */

const euro = new Intl.NumberFormat('it-IT', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  // In italiano il punto delle migliaia altrimenti compare solo da 10.000 in su
  useGrouping: 'always' as unknown as boolean,
})

export function formatEuro(cents: number): string {
  return euro.format(cents / 100)
}

/** Importo per i campi di modifica, senza simbolo: 123456 → "1234,56" */
export function centsToInput(cents: number): string {
  const sign = cents < 0 ? '-' : ''
  const abs = Math.abs(cents)
  return `${sign}${Math.floor(abs / 100)},${String(abs % 100).padStart(2, '0')}`
}

/**
 * Legge un importo scritto dall'utente e restituisce i centesimi, o null se non valido.
 * Accetta: "12", "12,5", "12,50", "1.234,56", "1234.56", "€ 12", "-3,20".
 */
export function parseEuro(text: string): number | null {
  let s = text.replace(/[€\s]/g, '')
  if (!s) return null
  let sign = 1
  if (s.startsWith('-')) {
    sign = -1
    s = s.slice(1)
  }
  if (s.includes(',')) {
    // Formato italiano: punti = migliaia, virgola = decimali
    s = s.replace(/\./g, '').replace(',', '.')
  } else if (/^\d{1,3}(\.\d{3})+$/.test(s)) {
    // "1.234" senza virgola: punti come separatore delle migliaia
    s = s.replace(/\./g, '')
  }
  if (!/^\d+(\.\d{1,2})?$/.test(s)) return null
  const [int, dec = ''] = s.split('.')
  return sign * (Number(int) * 100 + Number(dec.padEnd(2, '0')))
}

const monthFmt = new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' })

export function formatMonth(date: Date): string {
  const s = monthFmt.format(date)
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export function formatVouchers(n: number): string {
  return n === 1 ? '1 buono' : `${n} buoni`
}
