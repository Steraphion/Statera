<script lang="ts">
  import Icon from '../Icon.svelte'
  import { sync } from '../../lib/sync/sync.svelte'
  import { syncLine } from '../../lib/sync/labels'
  import { clock } from '../../lib/clock.svelte'
  import { enter, leave } from '../../lib/motion'

  // Telefono, in cima a Movimenti: permesso Google scaduto senza bisogno di avvisi. I dati degli altri
  // dispositivi arrivano quando si tocca "Sincronizza" (o da soli al primo tocco, se ci sono modifiche
  // da inviare). Su PC lo stesso stato è in fondo alla barra laterale (App.svelte).
  // Movimento: si apre in altezza (.grow con un solo figlio).
  const line = $derived(syncLine(sync.view, clock.now))
</script>

{#if line.renew && !line.warn}
  <div class="grow wrap" in:enter out:leave>
    <div>
      <button class="sync-line" title="Rinnova l'accesso a Google e sincronizza" onclick={() => sync.reconnect()}>
        <Icon name="refresh-cw" size={16} />
        <span class="title">{line.title}</span>
        <span class="sep" aria-hidden="true">·</span>
        <span class="act">{line.detail}</span>
      </button>
    </div>
  </div>
{/if}

<style>
  .wrap {
    margin-bottom: var(--space-3);
  }

  .sync-line {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    min-height: var(--size-btn-s);
    padding: 0 var(--space-3);
    border: 0;
    border-radius: var(--radius-full);
    background: var(--color-surface-2);
    color: var(--color-text-muted);
    font: inherit;
    font-size: var(--text-sm);
    font-weight: 600;
    cursor: pointer;
  }

  .sync-line :global(svg) {
    color: var(--color-accent);
  }

  .act {
    color: var(--color-accent);
    font-weight: 700;
  }

  .sep {
    color: var(--color-text-muted);
  }
</style>
