// Applica il tema prima che la pagina compaia, così non c'è un lampo chiaro/scuro all'apertura.
// File esterno (la CSP non permette script nella pagina). La gestione completa è in src/lib/theme.svelte.ts.
;(function () {
  var t = 'auto'
  try {
    t = localStorage.getItem('statera.tema') || 'auto'
  } catch (e) {}
  if (t !== 'light' && t !== 'dark') t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', t)
})()
