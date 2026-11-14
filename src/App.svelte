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
  import LockScreen from './components/LockScreen.svelte'
  import { lock } from './lib/lock.svelte'
  import { startup } from './lib/startup.svelte'
</script>

<!-- Con l'app bloccata il contenuto resta montato (nessun inserimento perso) ma invisibile e inattivo -->
<div class="app-root" class:locked={lock.locked} inert={lock.locked} aria-hidden={lock.locked}>
{#if startup.state === 'failed'}
  <Recovery message={startup.failure} />
{:else}

<div class="shell">
  <nav class="nav" aria-label="Sezioni">
    <div class="brand">
      <img src="./favicon.svg" alt="" width="32" height="32" />
      <span>Statera</span>
    </div>
    <ul>
      {#each ROUTES as r (r.id)}
        <li>
          <a
            href="#/{r.id}"
            class:active={router.section === r.id}
            aria-current={router.section === r.id ? 'page' : undefined}
          >
            <Icon name={r.icon} />
            <span>{r.label}</span>
          </a>
        </li>
      {/each}
    </ul>
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
    padding: var(--space-5) var(--space-4)
      calc(var(--nav-height) + var(--space-5) + env(safe-area-inset-bottom));
  }

  /* --- Smartphone: barra di navigazione in basso --- */
  .nav {
    position: fixed;
    inset: auto 0 0 0;
    z-index: 10;
    background: var(--color-surface);
    border-top: 1px solid var(--color-border);
    padding-bottom: env(safe-area-inset-bottom);
  }

  .brand {
    display: none;
  }

  ul {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    height: var(--nav-height);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  a {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    height: 100%;
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    text-decoration: none;
  }

  a.active {
    color: var(--color-accent);
    font-weight: 600;
  }

  /* --- PC: barra laterale --- */
  @media (min-width: 900px) {
    .shell {
      display: grid;
      grid-template-columns: 220px 1fr;
    }

    .nav {
      position: sticky;
      top: 0;
      inset: auto;
      height: 100dvh;
      border-top: none;
      border-right: 1px solid var(--color-border);
      padding: var(--space-5) var(--space-3);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: 0 var(--space-3) var(--space-5);
      font-size: var(--text-lg);
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    ul {
      grid-template-columns: 1fr;
      grid-auto-rows: 44px;
      height: auto;
      gap: var(--space-1);
    }

    a {
      flex-direction: row;
      justify-content: flex-start;
      gap: var(--space-3);
      padding: 0 var(--space-3);
      border-radius: var(--radius-sm);
      font-size: var(--text-md);
    }

    a:hover {
      background: var(--color-surface-2);
    }

    a.active {
      background: var(--color-accent-soft);
    }

    .content {
      width: 100%;
      padding: var(--space-6) var(--space-5);
    }
  }
</style>
