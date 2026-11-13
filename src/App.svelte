<script lang="ts">
  import Icon from './components/Icon.svelte'
  import { router, ROUTES } from './lib/router.svelte'
  import Movimenti from './screens/Movimenti.svelte'
  import Altro from './screens/Altro.svelte'
  import Placeholder from './screens/Placeholder.svelte'
</script>

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
            class:active={router.current === r.id}
            aria-current={router.current === r.id ? 'page' : undefined}
          >
            <Icon name={r.icon} />
            <span>{r.label}</span>
          </a>
        </li>
      {/each}
    </ul>
  </nav>

  <main class="content">
    {#if router.current === 'movimenti'}
      <Movimenti />
    {:else if router.current === 'conti'}
      <Placeholder title="Conti" text="Conti, carte e buoni pasto arrivano nella Fase 1.2." />
    {:else if router.current === 'analisi'}
      <Placeholder title="Analisi" text="Grafici e budget arrivano nella Fase 3." />
    {:else}
      <Altro />
    {/if}
  </main>
</div>

<style>
  .shell {
    min-height: 100dvh;
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
