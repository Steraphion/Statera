<script lang="ts">
  import { pwa } from '../lib/pwa.svelte'
</script>

<!-- Movimento: si apre in altezza (.grow in base.css) -->
{#if pwa.updateReady}
  <div class="grow notice">
  <div class="banner" role="status">
    <span>È disponibile una nuova versione di Statera.</span>
    <button class="btn btn-primary btn-small" disabled={pwa.updating} onclick={() => pwa.update()}>
      {pwa.updating ? 'Aggiornamento…' : 'Aggiorna'}
    </button>
  </div>
  </div>
{/if}

<style>
  .notice {
    margin-bottom: var(--space-4);
  }

  .banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    background: var(--color-accent-soft);
    border: 1px solid var(--color-border);
    font-size: var(--text-sm);
    font-weight: 500;
  }
</style>
