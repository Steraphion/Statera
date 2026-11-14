import { mount } from 'svelte'
import './styles/tokens.css'
import './styles/base.css'
import App from './App.svelte'
import { pwa } from './lib/pwa.svelte'
import { startup } from './lib/startup.svelte'
import { lock } from './lib/lock.svelte'
import { theme } from './lib/theme.svelte'

// Protezione: Statera non funziona se un altro sito la mostra dentro una sua pagina
// (tecnica usata per far toccare pulsanti all'utente a sua insaputa).
if (window.top !== window.self) {
  document.getElementById('app')!.textContent = 'Per sicurezza Statera non può essere aperta dentro un altro sito.'
} else {
  theme.start()
  startup.installHandlers()
  pwa.start()
  lock.start()
  // L'interfaccia parte subito; il database si prepara in parallelo
  mount(App, { target: document.getElementById('app')! })
  startup.run()
}
