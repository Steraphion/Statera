<script lang="ts">
  import { startup } from '../lib/startup.svelte'
</script>

{#if startup.lastError}
  <div class="toast" role="alert">
    <p><strong>Si è verificato un errore.</strong> {startup.lastError}</p>
    <div class="actions">
      <button class="btn btn-small" onclick={() => (startup.lastError = '')}>Chiudi</button>
      <button class="btn btn-primary btn-small" onclick={() => location.reload()}>Ricarica</button>
    </div>
  </div>
{/if}

<style>
  .toast {
    position: fixed;
    left: var(--space-3);
    right: var(--space-3);
    bottom: calc(var(--nav-height) + var(--space-3) + env(safe-area-inset-bottom));
    z-index: 50;
    max-width: 560px;
    margin: 0 auto;
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    border: 1px solid var(--color-expense);
    box-shadow: var(--shadow-2);
    font-size: var(--text-sm);
  }

  p {
    word-break: break-word;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2);
    margin-top: var(--space-2);
  }

  @media (min-width: 900px) {
    .toast {
      bottom: var(--space-4);
    }
  }
</style>
