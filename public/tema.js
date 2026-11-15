// Applica tema e palette prima che la pagina compaia, così non c'è un lampo di colori sbagliati
// all'apertura. File esterno (la CSP non permette script nella pagina). La gestione completa è in
// src/lib/theme.svelte.ts (palette valide: PALETTES in src/lib/theme.ts).
;(function () {
  var t = 'auto'
  var p = 'indaco'
  try {
    t = localStorage.getItem('statera.tema') || 'auto'
    p = localStorage.getItem('statera.colori') || 'indaco'
  } catch (e) {}
  if (t !== 'light' && t !== 'dark') t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  if (!/^(indaco|zafferano|petrolio|ciclamino|ottone|lime)$/.test(p)) p = 'indaco'
  document.documentElement.setAttribute('data-theme', t)
  document.documentElement.setAttribute('data-palette', p)
})()
