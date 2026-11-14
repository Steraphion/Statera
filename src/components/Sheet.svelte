<script lang="ts">
  import type { Snippet } from 'svelte'
  import Keypad from './Keypad.svelte'
  import { enter, leave } from '../lib/motion'

  // Finestra di modifica: pannello dal basso su smartphone, finestra centrata su PC.
  let {
    title,
    onclose,
    children,
    footer,
    error = '',
  }: { title: string; onclose: () => void; children: Snippet; footer?: Snippet; error?: string } = $props()

  let dialog = $state<HTMLDialogElement>()

  $effect(() => {
    const opener = document.activeElement
    dialog!.showModal()
    // Si chiude dopo l'animazione d'uscita (out:leave): Svelte smonta il pannello solo alla fine.
    // Il focus torna a chi l'aveva aperto, se nel frattempo non è andato altrove (es. il blocco).
    return () => {
      dialog!.close()
      const now = document.activeElement
      if (opener instanceof HTMLElement && opener.isConnected && (!now || now === document.body)) {
        opener.focus({ preventScroll: true })
      }
    }
  })
</script>

<dialog
  bind:this={dialog}
  in:enter
  out:leave
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
    <Keypad owner={dialog} />
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
    animation: fade-in var(--duration-slow) var(--ease-standard);
  }

  /* Uscita: data-leaving arriva da out:leave (src/lib/motion.ts), che aspetta --duration-base */
  dialog:global([data-leaving])::backdrop {
    animation: fade-out var(--duration-base) var(--ease-exit) forwards;
  }

  /* Pannello dal basso (telefono) e finestra centrata (PC): design system, Finestra */
  .panel {
    display: flex;
    flex-direction: column;
    max-height: 94dvh;
    background: var(--color-bg);
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    box-shadow: var(--shadow-3);
    padding-bottom: env(safe-area-inset-bottom);
    /* Movimento: il pannello sale dal basso ed esce scendendo */
    animation: sheet-in var(--duration-slow) var(--ease-standard);
  }

  dialog:global([data-leaving]) .panel {
    animation: sheet-out var(--duration-base) var(--ease-exit) forwards;
  }

  @keyframes sheet-in {
    from {
      transform: translateY(100%);
    }
  }

  @keyframes sheet-out {
    to {
      transform: translateY(100%);
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

  .panel::before {
    content: '';
    align-self: center;
    width: 40px;
    height: var(--space-1);
    margin-top: var(--space-2);
    border-radius: var(--radius-full);
    background: var(--color-border);
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-5) var(--space-2);
  }

  h2 {
    font-size: var(--text-xl);
  }

  .body {
    overflow-y: auto;
    padding: var(--space-2) var(--space-5) var(--space-5);
  }

  .sheet-error {
    margin: var(--space-2) var(--space-5) 0;
  }

  footer {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    justify-content: flex-end;
    padding: var(--space-3) var(--space-5) var(--space-5);
    border-top: 1px solid var(--color-border);
  }

  @media (min-width: 600px) {
    dialog {
      width: min(560px, calc(100vw - 32px));
      margin: auto;
    }

    .panel {
      border-radius: var(--radius-xl);
      max-height: 88dvh;
      /* Finestra centrata: compare con un leggero ingrandimento, esce rimpicciolendo appena */
      animation-name: window-in;
    }

    dialog:global([data-leaving]) .panel {
      animation-name: window-out;
    }

    @keyframes window-in {
      from {
        opacity: 0;
        transform: scale(0.96);
      }
    }

    @keyframes window-out {
      to {
        opacity: 0;
        transform: scale(0.98);
      }
    }

    .panel::before {
      display: none;
    }

    header {
      padding-top: var(--space-5);
    }
  }
</style>
