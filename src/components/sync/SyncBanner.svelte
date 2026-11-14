<script lang="ts">
  import { sync } from '../../lib/sync/sync.svelte'

  // Avviso in cima a ogni schermata solo quando serve un intervento dell'utente.
  // Permesso Google scaduto: prima si prova il rinnovo automatico al primo tocco (App.svelte),
  // l'avviso compare solo se non è riuscito.
</script>

{#if sync.meta && sync.status === 'needs-auth' && sync.askReconnect}
  <div class="banner" role="status">
    <span>Sincronizzazione in pausa: l'accesso a Google è scaduto.</span>
    <button class="btn btn-primary btn-small" onclick={() => sync.reconnect()}>Riconnetti</button>
  </div>
{:else if sync.meta && sync.status === 'locked'}
  <div class="banner" role="status">
    <span>Sincronizzazione bloccata: serve la password di Statera.</span>
    <a class="btn btn-primary btn-small" href="#/altro">Apri</a>
  </div>
{:else if sync.meta && sync.status === 'error'}
  <div class="banner error" role="alert">
    <span>Sincronizzazione non riuscita: {sync.error}</span>
    <button class="btn btn-small" onclick={() => sync.syncNow()}>Riprova</button>
  </div>
{/if}

<style>
  .banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
    font-weight: 500;
  }

  .banner.error {
    background: color-mix(in srgb, var(--color-danger) 12%, var(--color-bg));
  }

  .banner span {
    word-break: break-word;
  }
</style>
