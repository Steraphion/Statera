<script lang="ts">
  import { pwa } from '../lib/pwa.svelte'
</script>

{#if pwa.updateReady}
  <div class="banner" role="status">
    <span>È disponibile una nuova versione di Statera.</span>
    <button class="btn btn-primary btn-small" disabled={pwa.updating} onclick={() => pwa.update()}>
      {pwa.updating ? 'Aggiornamento…' : 'Aggiorna'}
    </button>
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
    border: 1px solid var(--color-border);
    font-size: var(--text-sm);
    font-weight: 500;
  }
</style>
