<script lang="ts">
  import { toast } from '../lib/toast.svelte'
  import { enter, leave } from '../lib/motion'

  async function run() {
    const a = toast.current?.action
    toast.close()
    await a?.run()
  }
</script>

<!-- Movimento: l'avviso entra salendo ed esce in dissolvenza; uno nuovo prende il posto del vecchio
     senza aspettare (cambia solo il contenuto, con una breve dissolvenza) -->
{#if toast.current}
  <div class="toast" role="status" in:enter out:leave>
    {#key toast.current.id}
      <div class="msg">
        <span>{toast.current.text}</span>
        {#if toast.current.action}
          <button class="btn btn-ghost btn-small" onclick={run}>{toast.current.action.label}</button>
        {/if}
      </div>
    {/key}
  </div>
{/if}

<style>
  .toast {
    animation: toast-in var(--duration-base) var(--ease-standard);
    position: fixed;
    left: var(--space-3);
    right: var(--space-3);
    /* Sopra la barra flottante (e sopra il + del dettaglio conto, che è alto quanto la barra) */
    bottom: calc(var(--nav-height) + var(--space-3) + var(--space-4) + env(safe-area-inset-bottom));
    z-index: 40;
    max-width: 480px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    padding: var(--space-2) var(--space-2) var(--space-2) var(--space-4);
    min-height: var(--size-field);
    border-radius: var(--radius-md);
    background: var(--toast-bg);
    color: var(--toast-text);
    box-shadow: var(--shadow-2);
    font-size: var(--text-sm);
    font-weight: 600;
  }

  .msg {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    animation: fade-in var(--duration-fast) var(--ease-standard);
  }

  .toast:global([data-leaving]) {
    animation: fade-out var(--duration-base) var(--ease-exit) forwards;
  }

  @keyframes toast-in {
    from {
      opacity: 0;
      translate: 0 var(--space-4);
    }
  }

  @keyframes fade-in {
    from {
      opacity: 0;
    }
  }

  @keyframes fade-out {
    to {
      opacity: 0;
    }
  }

  .toast .btn {
    color: var(--toast-action);
    font-weight: 800;
  }

  @media (min-width: 900px) {
    .toast {
      bottom: var(--space-4);
    }
  }
</style>
