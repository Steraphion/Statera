import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig, type Plugin } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import { readFileSync } from 'node:fs'

const pkg = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8'))

/**
 * Content Security Policy: l'app può caricare risorse SOLO da se stessa,
 * più i soli indirizzi Google necessari alla sincronizzazione (Fase 2):
 * - accounts.google.com/gsi: libreria e finestra di accesso di Google
 * - www.googleapis.com: Google Drive (cartella nascosta dell'app)
 * Applicata solo alla build pubblicata: in sviluppo Vite usa script inline.
 */
const CSP = [
  "default-src 'self'",
  "script-src 'self' https://accounts.google.com/gsi/client",
  "style-src 'self' https://accounts.google.com/gsi/style",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  "connect-src 'self' https://www.googleapis.com https://accounts.google.com/gsi/",
  "frame-src https://accounts.google.com/gsi/",
  "worker-src 'self'",
  "manifest-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'none'",
].join('; ')

function contentSecurityPolicy(): Plugin {
  return {
    name: 'statera-csp',
    apply: 'build',
    transformIndexHtml(html) {
      return html.replace(
        '<meta charset="UTF-8" />',
        `<meta charset="UTF-8" />\n    <meta http-equiv="Content-Security-Policy" content="${CSP}" />`,
      )
    },
  }
}

export default defineConfig({
  // Percorsi relativi: l'app funziona in qualsiasi sottocartella (es. GitHub Pages)
  base: './',
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
  plugins: [
    svelte(),
    contentSecurityPolicy(),
    VitePWA({
      // Nuova versione: l'app mostra un avviso "Aggiorna" (src/lib/pwa.svelte.ts)
      registerType: 'prompt',
      injectRegister: false,
      includeAssets: ['favicon.svg', 'icons/apple-touch-icon.png', 'licenze.html'],
      manifest: {
        id: './',
        name: 'Statera',
        short_name: 'Statera',
        description: 'Entrate e spese personali, offline e private.',
        lang: 'it',
        start_url: './',
        scope: './',
        display: 'standalone',
        orientation: 'any',
        // Aprendo l'app (anche con doppio clic o dalle scorciatoie) torna in primo piano la finestra già
        // aperta invece di aprirne un'altra; la scorciatoia scelta arriva a src/lib/launch.ts
        launch_handler: { client_mode: ['focus-existing', 'auto'] },
        background_color: '#F4F5FB',
        theme_color: '#F4F5FB',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
        // Tenendo premuta l'icona dell'app (Android) o con il tasto destro (Windows)
        shortcuts: [
          {
            name: 'Nuova uscita',
            short_name: 'Uscita',
            url: './#/movimenti/nuova-uscita',
            icons: [{ src: 'icons/shortcut-uscita.png', sizes: '96x96', type: 'image/png' }],
          },
          {
            name: 'Nuova entrata',
            short_name: 'Entrata',
            url: './#/movimenti/nuova-entrata',
            icons: [{ src: 'icons/shortcut-entrata.png', sizes: '96x96', type: 'image/png' }],
          },
          {
            name: 'Cerca',
            short_name: 'Cerca',
            url: './#/cerca',
            icons: [{ src: 'icons/shortcut-cerca.png', sizes: '96x96', type: 'image/png' }],
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2,webmanifest}'],
        navigateFallback: 'index.html',
        // Le pagine statiche (es. informativa privacy) non vanno sostituite dall'app
        navigateFallbackDenylist: [/privacy\.html$/, /licenze\.html$/],
        cleanupOutdatedCaches: true,
        // La nuova versione, una volta attivata, prende subito il controllo della pagina
        clientsClaim: true,
      },
    }),
  ],
})
