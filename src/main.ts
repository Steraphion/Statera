import { mount } from 'svelte'
import './styles/tokens.css'
import './styles/base.css'
import App from './App.svelte'
import { ensureSeeded } from './lib/data/repo'

// Al primo avvio prepara le categorie iniziali, poi mostra l'app
ensureSeeded()
  .catch((e) => console.error('Preparazione dati non riuscita', e))
  .finally(() => mount(App, { target: document.getElementById('app')! }))
