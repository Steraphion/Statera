<script lang="ts">
  import type { Snippet } from 'svelte'

  // Finestra di modifica: pannello dal basso su smartphone, finestra centrata su PC.
  let {
    title,
    onclose,
    children,
    footer,
    error = '',
  }: { title: string; onclose: () => void; children: Snippet; footer?: Snippet; error?: string } = $props()

  let dialog: HTMLDialogElement

  $effect(() => {
    dialog.showModal()
    return () => dialog.close()
  })
</script>

<dialog
  bind:this={dialog}
  aria-label={title}
  oncancel={(e) => {
    e.preventDefault()
    onclose()
  }}
  onclick={(e) => {
    if (e.target === dialog) onclose()
  }}
>
  <div class="panel">
    <header>
      <h2>{title}</h2>
      <button class="btn btn-ghost btn-small" onclick={onclose}>Chiudi</button>
    </header>
    <div class="body">
      {@render children()}
    </div>
    {#if error}
      <p class="error-box sheet-error" role="alert">{error}</p>
    {/if}
    {#if footer}
      <footer>{@render footer()}</footer>
    {/if}
  </div>
</dialog>

<style>
  dialog {
    padding: 0;
    border: none;
    background: transparent;
    max-width: 100vw;
    max-height: 100dvh;
    width: 100%;
    margin: auto auto 0;
    color: var(--color-text);
  }

  dialog::backdrop {
    background: var(--color-backdrop);
  }

  .panel {
    display: flex;
    flex-direction: column;
    max-height: 92dvh;
    background: var(--color-surface);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-2);
    padding-bottom: env(safe-area-inset-bottom);
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-4) var(--space-2);
  }

  h2 {
    font-size: var(--text-lg);
  }

  .body {
    overflow-y: auto;
    padding: var(--space-2) var(--space-4) var(--space-4);
  }

  .sheet-error {
    margin: var(--space-2) var(--space-4) 0;
  }

  footer {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    justify-content: flex-end;
    padding: var(--space-3) var(--space-4) var(--space-4);
    border-top: 1px solid var(--color-border);
  }

  @media (min-width: 600px) {
    dialog {
      width: min(520px, calc(100vw - 32px));
      margin: auto;
    }

    .panel {
      border-radius: var(--radius-lg);
      max-height: 86dvh;
    }
  }
</style>
