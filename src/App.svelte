<script lang="ts">
  import Icon from './components/Icon.svelte'
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
  import { lock } from './lib/lock.svelte'
  import { startup } from './lib/startup.svelte'
  import { sync } from './lib/sync/sync.svelte'
  import { statusLabel } from './lib/sync/labels'

  // Nuovo movimento da qualsiasi schermata: Movimenti apre il modulo (#/movimenti/nuovo)
  function newMovement() {
    location.hash = '/movimenti/nuovo'
  }

  // Scorciatoie da tastiera (PC), valide ovunque: N = nuovo movimento, / = cerca.
  // Non scattano mentre si scrive in un campo o con un pannello aperto.
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
    }
  }
</script>

<svelte:window onkeydown={onKey} />

<!-- Con l'app bloccata il contenuto resta montato (nessun inserimento perso) ma invisibile e inattivo -->
<div class="app-root" class:locked={lock.locked} inert={lock.locked} aria-hidden={lock.locked}>
{#if startup.state === 'failed'}
  <Recovery message={startup.failure} />
{:else}

<div class="shell" class:sub={router.current !== router.section}>
  <nav class="nav" aria-label="Sezioni">
    <div class="brand">
      <span class="mark" aria-hidden="true"><Icon name="scale" /></span>
      <span>Statera</span>
    </div>
    <!-- PC: comando principale in cima alla barra laterale -->
    <button class="new-pc btn btn-primary" aria-label="Nuovo movimento" aria-keyshortcuts="N" onclick={newMovement}>
      <Icon name="plus" stroke={2.4} />
      <span class="grow" aria-hidden="true">Nuovo movimento</span>
      <kbd aria-hidden="true">N</kbd>
    </button>
    <ul>
      {#each ROUTES as r, i (r.id)}
        {#if i === 2}
          <!-- Telefono: il + al centro della barra -->
          <li class="plus">
            <button class="fab" aria-label="Nuovo movimento" onclick={newMovement}>
              <Icon name="plus" size={26} stroke={2.4} />
            </button>
          </li>
        {/if}
        <li>
          <a
            href="#/{r.id}"
            class:active={router.section === r.id}
            aria-current={router.section === r.id ? 'page' : undefined}
          >
            <Icon name={r.icon} size={22} stroke={router.section === r.id ? 2.2 : 1.8} />
            <span>{r.label}</span>
          </a>
        </li>
      {/each}
      <li class="pc-only">
        <a href="#/cerca" class:active={router.current === 'cerca'} aria-current={router.current === 'cerca' ? 'page' : undefined}>
          <Icon name="search" size={22} />
          <span>Cerca</span>
          <kbd aria-hidden="true">/</kbd>
        </a>
      </li>
    </ul>
    <a class="sync-state" href="#/altro" class:off={sync.status === 'off'}>
      <Icon name={sync.status === 'idle' || sync.status === 'syncing' ? 'cloud-check' : sync.status === 'off' ? 'smartphone' : 'cloud-off'} />
      <span>
        <b>{sync.status === 'off' ? 'Solo su questo dispositivo' : statusLabel(sync.status)}</b>
        <small>{sync.status === 'off' ? 'Sincronizzazione non attiva' : 'Google Drive, cifrato'}</small>
      </span>
    </a>
  </nav>

  <main class="content">
    <UpdateBanner />
    <SyncBanner />
    {#if startup.state === 'loading'}
      <p class="loading">Caricamento…</p>
    {:else}
    <!-- Se una schermata va in errore, si mostra il recupero invece di bloccare tutto -->
    <svelte:boundary onerror={(e) => console.error(e)}>
    {#if router.current === 'movimenti'}
      <Movimenti />
    {:else if router.current === 'conti'}
      <Conti />
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
      {#snippet failed(error, reset)}
        <Recovery message={error instanceof Error ? error.message : String(error)} onretry={reset} />
      {/snippet}
    </svelte:boundary>
    {/if}
  </main>
</div>
<Toast />
<Keypad />
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

  /* Schermate aperte da un'altra: niente barra in basso sul telefono */
  .sub .content {
    padding-bottom: calc(var(--space-8) + env(safe-area-inset-bottom));
  }

  kbd {
    min-width: 24px;
    height: 24px;
    padding: 0 6px;
    border-radius: var(--radius-xs);
    display: inline-grid;
    place-items: center;
    font: inherit;
    font-size: var(--text-xs);
    font-weight: 700;
    background: var(--color-surface-2);
    color: var(--color-text-muted);
    border: 1px solid var(--color-border);
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
  .sync-state {
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
    background: var(--color-primary);
    color: var(--color-on-primary);
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
      grid-template-columns: var(--size-sidebar) 1fr;
      gap: var(--space-2);
      padding: var(--space-4);
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

    .mark {
      display: grid;
      place-items: center;
      width: 36px;
      height: 36px;
      border-radius: var(--radius-full);
      background: var(--color-primary);
      color: var(--color-on-primary);
    }

    .new-pc {
      display: flex;
      justify-content: flex-start;
      padding: 0 var(--space-2) 0 var(--space-4);
    }

    .new-pc .grow {
      flex: 1;
      text-align: left;
    }

    .new-pc kbd {
      background: color-mix(in srgb, var(--color-on-primary) 18%, transparent);
      color: var(--color-on-primary);
      border-color: transparent;
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

    .sync-state span {
      display: flex;
      flex-direction: column;
      color: var(--color-text);
      font-size: var(--text-sm);
      line-height: 1.3;
    }

    .sync-state small {
      font-size: var(--text-xs);
      font-weight: 500;
      color: var(--color-text-muted);
    }

    .content {
      width: 100%;
      padding: var(--space-4) var(--space-5) var(--space-8);
    }

    .sub .content {
      padding-bottom: var(--space-8);
    }
  }
</style>
