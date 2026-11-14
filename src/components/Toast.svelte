<script lang="ts">
  import { toast } from '../lib/toast.svelte'

  async function run() {
    const a = toast.current?.action
    toast.close()
    await a?.run()
  }
</script>

{#if toast.current}
  {#key toast.current.id}
    <div class="toast" role="status">
      <span>{toast.current.text}</span>
      {#if toast.current.action}
        <button class="btn btn-ghost btn-small" onclick={run}>{toast.current.action.label}</button>
      {/if}
    </div>
  {/key}
{/if}

<style>
  .toast {
    position: fixed;
    left: var(--space-3);
    right: var(--space-3);
    /* Sopra il pulsante + (60px) della schermata Movimenti */
    bottom: calc(var(--nav-height) + var(--space-4) + 60px + var(--space-3) + env(safe-area-inset-bottom));
    z-index: 40;
    max-width: 480px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-2) var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    background: var(--toast-bg);
    color: var(--toast-text);
    box-shadow: var(--shadow-2);
    font-size: var(--text-sm);
  }

  .toast .btn {
    color: var(--toast-action);
    font-weight: 700;
  }

  @media (min-width: 900px) {
    .toast {
      bottom: var(--space-4);
    }
  }
</style>
