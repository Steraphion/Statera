/*
 * Avvio dell'app installata con la finestra già aperta (launch_handler "focus-existing" nel manifest):
 * il browser non ricarica la pagina, ma passa qui l'indirizzo dell'avvio. Se è una scorciatoia
 * dell'icona (es. #/movimenti/nuova-uscita) ci si sposta lì; l'icona normale lascia la schermata com'è.
 */
interface LaunchParams {
  targetURL?: string
}
interface LaunchQueue {
  setConsumer(consumer: (params: LaunchParams) => void): void
}

/** Parte da aprire per un indirizzo di avvio: l'hash di una scorciatoia, o null per l'avvio normale. */
export function launchTarget(targetURL: string | undefined): string | null {
  if (!targetURL) return null
  try {
    const hash = new URL(targetURL).hash
    return hash && hash !== '#' && hash !== '#/' ? hash : null
  } catch {
    return null
  }
}

export function handleLaunches() {
  const queue = (window as unknown as { launchQueue?: LaunchQueue }).launchQueue
  if (!queue) return
  queue.setConsumer((params) => {
    const target = launchTarget(params.targetURL)
    if (target && location.hash !== target) location.hash = target
  })
}
