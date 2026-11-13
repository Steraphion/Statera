import { mount } from 'svelte'
import './styles/tokens.css'
import './styles/base.css'
import App from './App.svelte'
import { pwa } from './lib/pwa.svelte'
import { startup } from './lib/startup.svelte'

startup.installHandlers()
pwa.start()

// L'interfaccia parte subito; il database si prepara in parallelo
mount(App, { target: document.getElementById('app')! })
startup.run()
