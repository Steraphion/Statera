/**
 * Ora corrente, aggiornata ogni minuto: per i testi che dipendono da adesso
 * ("Aggiornato alle 14:32" che dopo mezzanotte diventa "ieri alle 14:32").
 */
class Clock {
  now = $state(Date.now())

  constructor() {
    if (typeof window !== 'undefined') setInterval(() => (this.now = Date.now()), 60_000)
  }
}

export const clock = new Clock()
