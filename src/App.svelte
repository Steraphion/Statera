<script lang="ts">
  import Icon from './components/Icon.svelte'
  import Logo from './components/Logo.svelte'
  import UpdateBanner from './components/UpdateBanner.svelte'
  import SyncBanner from './components/sync/SyncBanner.svelte'
  import { router, ROUTES } from './lib/router.svelte'
  import Movimenti from './screens/Movimenti.svelte'
  import Altro from './screens/Altro.svelte'
  import Analisi from './screens/Analisi.svelte'
  import Conti from './screens/Conti.svelte'
  import Categorie from './screens/Categorie.svelte'
  import ContoDettaglio from './screens/ContoDettaglio.svelte'
  import Cerca from './screens/Cerca.svelte'
  import Ricorrenti from './screens/Ricorrenti.svelte'
  import Recovery from './components/Recovery.svelte'
  import ErrorToast from './components/ErrorToast.svelte'
  import Toast from './components/Toast.svelte'
  import Keypad from './components/Keypad.svelte'
  import LockScreen from './components/LockScreen.svelte'
  import ShortcutsSheet from './components/ShortcutsSheet.svelte'
  import PickerSheet from './components/PickerSheet.svelte'
  import { picker } from './lib/picker.svelte'
  import { ui } from './lib/ui.svelte'
  import { lock } from './lib/lock.svelte'
  import { startup } from './lib/startup.svelte'
  import { sync } from './lib/sync/sync.svelte'
  import { syncLine } from './lib/sync/labels'
  import { clock } from './lib/clock.svelte'
  import { screen, revealKind } from './lib/screen.svelte'
  import { columns } from './lib/columns.svelte'
  import type { NavId, RouteId } from './lib/router.svelte'

  // Comparsa delle schermate: a ogni cambio di schermata (non per il modulo aperto sopra Movimenti) la
  // nuova resta nascosta finché i suoi dati non sono pronti, poi compare tutta insieme (screen.svelte.ts)
  let shownRoute: { id: RouteId; key: string } | null = null
  $effect.pre(() => {
    if (startup.state !== 'ready') return
    const id = router.current
    // Su PC Conti e il dettaglio di un conto sono la stessa schermata: cambia solo il dettaglio
    const key = columns.pc && (id === 'conti' || id === 'conto') ? 'conti' : id === 'conto' ? `conto/${router.param}` : id
    if (shownRoute?.key === key) return
    screen.start(revealKind(shownRoute?.id ?? null, id, shownRoute?.id === id))
    shownRoute = { id, key }
  })

  // Nuovo movimento da qualsiasi schermata: Movimenti apre il modulo (#/movimenti/nuovo)
  // PC: schermate su più colonne, larghe fino a --content-max-wide (le altre restano a --content-max)
  const WIDE_ROUTES = new Set<RouteId>(['movimenti', 'conti', 'conto', 'analisi', 'cerca'])

  /** Voce evidenziata: su PC Cerca ha la sua voce, quindi Movimenti non resta accesa in Cerca. */
  function isActive(id: NavId): boolean {
    return router.section === id && !(columns.pc && router.current === 'cerca')
  }

  // Stato della sincronizzazione in fondo alla barra laterale (PC)
  const syncState = $derived(syncLine(sync.view, clock.now))
  const syncIcon = $derived(
    syncState.renew ? 'refresh-cw' : sync.status === 'idle' || sync.status === 'syncing' ? 'cloud-check' : sync.status === 'off' ? 'smartphone' : 'cloud-off',
  )

  function newMovement() {
    location.hash = '/movimenti/nuovo'
  }

  // Scorciatoie da tastiera (PC), valide ovunque: N = nuovo movimento, / = cerca, ? = elenco delle scorciatoie.
  // Non scattano mentre si scrive in un campo o con un pannello aperto.
  // Permesso Google scaduto con modifiche da inviare: si rinnova al primo tocco su un pulsante o un link
  // (serve un tocco perché Google apre per un attimo la sua finestra). Senza modifiche da inviare no,
  // tranne sui pulsanti che aprono qualcosa che legge Drive (data-autoauth). Mai sul blocco, nel
  // tastierino, nel modulo del movimento o sui pulsanti che lo aprono, per non disturbare l'inserimento.
  function onTap(e: MouseEvent) {
    if (lock.locked || !sync.meta) return
    const el = (e.target as Element | null)?.closest('a, button')
    if (!el || el.closest('.keypad, dialog.lock, [data-no-autoauth]')) return
    sync.autoReconnect(!!el.closest('[data-autoauth]'))
  }

  function onKey(e: KeyboardEvent) {
    if (lock.locked || e.ctrlKey || e.metaKey || e.altKey) return
    if ((e.target as HTMLElement).closest('input, textarea, select, [contenteditable]')) return
    if (document.querySelector('dialog[open]')) return
    if (e.key === 'n' || e.key === 'N') {
      e.preventDefault()
      newMovement()
    } else if (e.key === '/') {
      e.preventDefault()
      location.hash = '/cerca'
    } else if (e.key === '?') {
      e.preventDefault()
      ui.shortcuts = true
    }
  }
</script>

<svelte:window onkeydown={onKey} />
<svelte:document onclickcapture={onTap} />

<!-- Con l'app bloccata il contenuto resta montato (nessun inserimento perso) ma invisibile e inattivo -->
<div class="app-root" class:locked={lock.locked} inert={lock.locked} aria-hidden={lock.locked}>
{#if startup.state === 'failed'}
  <Recovery message={startup.failure} />
{:else}

<!-- PC: barra laterale stretta (solo icone) sotto i 1200 px o se la si stringe; schermate larghe su due colonne -->
<div
  class="shell"
  class:sub={router.current !== router.section}
  class:rail={columns.railNow}
  class:wide={WIDE_ROUTES.has(router.current)}
>
  <nav class="nav" aria-label="Sezioni">
    <div class="brand">
      <Logo size={36} />
      <span class="label">Statera</span>
    </div>
    <!-- PC: comando principale in cima alla barra laterale -->
    <button
      class="new-pc btn btn-primary"
      data-no-autoauth
      aria-keyshortcuts="N"
      title={columns.railNow ? 'Nuovo movimento (tasto N)' : 'Scorciatoia: tasto N'}
      onclick={newMovement}
    >
      <Icon name="plus" stroke={2.4} />
      <span class="new-label label">Nuovo movimento</span>
    </button>
    <ul>
      {#each ROUTES as r, i (r.id)}
        {#if i === 2}
          <!-- Telefono: il + al centro della barra -->
          <li class="plus">
            <button class="fab" data-no-autoauth aria-label="Nuovo movimento" onclick={newMovement}>
              <Icon name="plus" size={26} stroke={2.4} />
            </button>
          </li>
        {/if}
        <li>
          <a
            href="#/{r.id}"
            class:active={isActive(r.id)}
            aria-current={isActive(r.id) ? 'page' : undefined}
            title={columns.railNow ? r.label : undefined}
          >
            <Icon name={r.icon} size={22} stroke={isActive(r.id) ? 2.2 : 1.8} />
            <span class="label">{r.label}</span>
          </a>
        </li>
      {/each}
      <li class="pc-only">
        <a href="#/cerca" class:active={router.current === 'cerca'} aria-current={router.current === 'cerca' ? 'page' : undefined} aria-keyshortcuts="/" title={columns.railNow ? 'Cerca (tasto /)' : 'Scorciatoia: tasto /'}>
          <Icon name="search" size={22} />
          <span class="label">Cerca</span>
        </a>
      </li>
    </ul>
    <!-- Permesso Google scaduto: toccando si rinnova e si sincronizza; altrimenti porta ad Altro -->
    {#if syncState.renew}
      <button
        class="sync-state renew"
        class:warn={syncState.warn}
        title={columns.railNow ? `${syncState.title} · ${syncState.detail}` : 'Rinnova l\'accesso a Google e sincronizza'}
        onclick={() => sync.reconnect()}
      >
        <Icon name={syncIcon} />
        <span class="label">
          <b>{syncState.title}</b>
          <small>{syncState.detail}</small>
        </span>
      </button>
    {:else}
      <a
        class="sync-state"
        href="#/altro"
        class:off={sync.status === 'off'}
        class:warn={syncState.warn}
        title={columns.railNow ? `${syncState.title} · ${syncState.detail}` : undefined}
      >
        <Icon name={syncIcon} />
        <span class="label">
          <b>{syncState.title}</b>
          <small>{syncState.detail}</small>
        </span>
      </a>
    {/if}
    <!-- Da 1200 px la barra si può stringere alle sole icone (scelta salvata per dispositivo) -->
    {#if columns.wide}
      <button
        class="side-toggle btn btn-ghost btn-small"
        aria-pressed={columns.side === 'stretta'}
        title={columns.side === 'stretta' ? 'Allarga la barra laterale' : 'Stringi la barra laterale'}
        onclick={() => columns.setSide(columns.side === 'stretta' ? 'intera' : 'stretta')}
      >
        <Icon name={columns.side === 'stretta' ? 'chevron-right' : 'chevron-left'} size={18} />
        <span class="label">Stringi la barra</span>
      </button>
    {/if}
  </nav>

  <!-- Classi di larghezza dell'area dei contenuti (PC): le schermate decidono le colonne da qui -->
  <main
    class="content"
    use:columns.observe
    class:l-media={columns.at('media')}
    class:l-larga={columns.at('larga')}
    class:l-molto={columns.at('molto')}
  >
    <UpdateBanner />
    <SyncBanner />
    {#if startup.state === 'loading'}
      <p class="loading">Caricamento…</p>
    {:else}
    <!-- Se una schermata va in errore, si mostra il recupero invece di bloccare tutto -->
    <svelte:boundary onerror={(e) => console.error(e)}>
    <div class="screen" data-reveal={screen.shown ? screen.kind : 'wait'}>
    {#if router.current === 'movimenti'}
      <Movimenti />
    {:else if router.current === 'conti' || (router.current === 'conto' && columns.pc)}
      <Conti selected={router.current === 'conto' ? router.param : null} />
    {:else if router.current === 'conto'}
      {#key router.param}
        <ContoDettaglio id={router.param} />
      {/key}
    {:else if router.current === 'ricorrenti'}
      <Ricorrenti />
    {:else if router.current === 'cerca'}
      <Cerca />
    {:else if router.current === 'categorie'}
      <Categorie />
    {:else if router.current === 'analisi'}
      <Analisi />
    {:else}
      <Altro />
    {/if}
    </div>
      {#snippet failed(error, reset)}
        <Recovery message={error instanceof Error ? error.message : String(error)} onretry={reset} />
      {/snippet}
    </svelte:boundary>
    {/if}
  </main>
</div>
{#if ui.shortcuts}
  <ShortcutsSheet onclose={() => (ui.shortcuts = false)} />
{/if}
<Toast />
<Keypad />
<!-- Elenchi a tendina e date sul telefono: pannello dell'app invece di quello di Android -->
{#if picker.field}
  {#key picker.field}
    <PickerSheet />
  {/key}
{/if}
<ErrorToast />
{/if}
</div>
{#if lock.locked}
  <LockScreen />
{/if}

<style>
  .app-root.locked {
    visibility: hidden;
  }

  .shell {
    min-height: 100dvh;
  }

  .loading {
    padding: var(--space-6) 0;
    text-align: center;
    color: var(--color-text-muted);
  }

  .content {
    max-width: var(--content-max);
    margin: 0 auto;
    padding: var(--space-5) var(--space-5)
      calc(var(--nav-height) + var(--space-4) + var(--space-8) + env(safe-area-inset-bottom));
  }

  /* Comparsa delle schermate (design system: Movimento): invisibile finché i dati non sono pronti,
     poi dissolvenza tra le sezioni, dissolvenza e spostamento verso una schermata secondaria e al ritorno.
     Si animano i figli e non il contenitore: uno spostamento sul contenitore staccherebbe dallo schermo
     gli elementi fissi della schermata (il + del dettaglio conto) */
  .screen[data-reveal='wait'] {
    visibility: hidden;
  }

  .screen[data-reveal='fade'] > :global(*) {
    animation: screen-fade var(--duration-base) var(--ease-standard);
  }

  .screen[data-reveal='forward'] > :global(*) {
    animation: screen-forward var(--duration-base) var(--ease-standard);
  }

  .screen[data-reveal='back'] > :global(*) {
    animation: screen-back var(--duration-base) var(--ease-standard);
  }

  @keyframes screen-fade {
    from {
      opacity: 0;
    }
  }

  @keyframes screen-forward {
    from {
      opacity: 0;
      translate: var(--space-6) 0;
    }
  }

  @keyframes screen-back {
    from {
      opacity: 0;
      translate: calc(-1 * var(--space-6)) 0;
    }
  }

  /* Schermate aperte da un'altra: niente barra in basso sul telefono */
  .sub .content {
    padding-bottom: calc(var(--space-8) + env(safe-area-inset-bottom));
  }

  /* --- Telefono: barra flottante con il + al centro (design system: BarraNavigazione) --- */
  .nav {
    position: fixed;
    left: var(--space-3);
    right: var(--space-3);
    bottom: calc(var(--space-3) + env(safe-area-inset-bottom));
    z-index: 10;
    height: var(--nav-height);
    border-radius: var(--radius-full);
    background: var(--color-surface);
    box-shadow: var(--shadow-2);
  }

  .sub .nav {
    display: none;
  }

  .brand,
  .new-pc,
  .pc-only,
  .sync-state,
  .side-toggle {
    display: none;
  }

  ul {
    display: grid;
    grid-template-columns: repeat(2, 1fr) auto repeat(2, 1fr);
    align-items: center;
    height: 100%;
    margin: 0;
    padding: 0 var(--space-2);
    list-style: none;
  }

  a {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 100%;
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--color-text-muted);
    text-decoration: none;
  }

  a.active {
    color: var(--color-accent);
    font-weight: 800;
  }

  .fab {
    display: grid;
    place-items: center;
    width: var(--size-fab);
    height: var(--size-fab);
    margin: -26px var(--space-2) 0;
    border: 4px solid var(--color-bg);
    border-radius: var(--radius-full);
    background: var(--color-fab);
    color: var(--color-on-fab);
    box-shadow: var(--shadow-fab);
    cursor: pointer;
    transition: transform var(--duration-fast) var(--ease-standard);
  }

  .fab:active {
    transform: scale(0.94);
  }

  /* --- PC: barra laterale (design system: BarraLaterale) --- */
  @media (min-width: 900px) {
    .shell {
      display: grid;
      grid-template-columns: var(--size-sidebar) minmax(0, 1fr);
      gap: var(--space-2);
      padding: var(--space-4);
      transition: grid-template-columns var(--duration-base) var(--ease-standard);
    }

    .nav,
    .sub .nav {
      position: sticky;
      top: var(--space-4);
      left: auto;
      right: auto;
      bottom: auto;
      display: flex;
      flex-direction: column;
      gap: var(--space-4);
      height: calc(100dvh - 2 * var(--space-4));
      padding: var(--space-4) var(--space-3);
      border-radius: var(--radius-lg);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: 0 var(--space-2);
      font-size: var(--text-lg);
      font-weight: 800;
      letter-spacing: var(--tracking-tight);
    }


    .new-pc {
      display: flex;
      justify-content: flex-start;
      padding: 0 var(--space-4);
      /* Stesso colore del + del telefono (in alcune palette diverso dal principale) */
      background: var(--color-fab);
      color: var(--color-on-fab);
    }

    .new-pc .new-label {
      flex: 1;
      text-align: left;
    }

    ul {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: var(--space-1);
      height: auto;
      padding: 0;
    }

    .plus {
      display: none;
    }

    .pc-only {
      display: block;
    }

    a {
      flex-direction: row;
      justify-content: flex-start;
      gap: var(--space-3);
      height: var(--size-touch);
      padding: 0 var(--space-3);
      border-radius: var(--radius-md);
      font-size: var(--text-md);
      font-weight: 700;
      color: var(--color-text);
    }

    a span {
      flex: 1;
    }

    a:hover {
      background: var(--color-surface-2);
    }

    a.active {
      background: var(--color-accent-soft);
      color: var(--color-accent);
    }

    .sync-state {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      height: auto;
      margin-top: auto;
      padding: var(--space-2) var(--space-3);
      border-radius: var(--radius-md);
      background: var(--color-bg);
      color: var(--color-income);
    }

    .sync-state.off {
      color: var(--color-text-muted);
    }

    .sync-state.warn {
      color: var(--status-warning);
    }

    /* Pulsante (permesso da rinnovare): stesso aspetto del collegamento */
    button.sync-state {
      width: 100%;
      border: 0;
      font: inherit;
      text-align: start;
      cursor: pointer;
    }

    button.sync-state:hover {
      background: var(--color-surface-2);
    }

    .sync-state.renew {
      color: var(--color-accent);
    }

    .sync-state.renew.warn {
      color: var(--status-warning);
    }

    .sync-state span {
      display: flex;
      flex-direction: column;
      color: var(--color-text);
      flex: 1;
      font-size: var(--text-sm);
      line-height: var(--leading-compact);
    }

    .sync-state.renew small {
      color: var(--color-accent);
      font-weight: 700;
    }

    .sync-state small {
      font-size: var(--text-xs);
      font-weight: 500;
      color: var(--color-text-muted);
    }

    /* Schermate a una colonna: area larga al massimo --content-max, centrata. Schermate su più colonne: l'area
       occupa tutto lo spazio accanto alla barra laterale (la sua larghezza decide le colonne, columns.observe)
       e dentro schermata e avvisi arrivano fino a --content-max-wide, centrati solo oltre quel tetto */
    .content {
      width: 100%;
      padding: var(--space-4) var(--space-5) var(--space-8);
    }

    .wide .content {
      max-width: none;
    }

    .wide .content > :global(*) {
      max-width: var(--content-max-wide);
      margin-inline: auto;
    }

    .sub .content {
      padding-bottom: var(--space-8);
    }

    .side-toggle {
      display: flex;
      justify-content: flex-start;
      gap: var(--space-2);
      color: var(--color-text-muted);
    }

    /* Barra stretta: solo icone, i nomi restano per gli screen reader e nel suggerimento */
    .shell.rail {
      grid-template-columns: var(--size-rail) minmax(0, 1fr);
    }

    .rail .nav {
      padding: var(--space-4) var(--space-2);
      align-items: center;
    }

    .rail .label {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      white-space: nowrap;
    }

    .rail .brand {
      padding: 0;
    }

    .rail ul {
      align-self: stretch;
      align-items: center;
    }

    .rail .new-pc,
    .rail a,
    .rail .side-toggle {
      justify-content: center;
      width: var(--size-fab);
      padding: 0;
    }

    .rail .new-pc {
      height: var(--size-fab);
    }

    .rail .sync-state {
      padding: var(--space-3) 0;
    }
  }
</style>
