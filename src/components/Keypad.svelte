<script lang="ts">
  // Tastierino degli importi (design system: Tastierino). Compare solo su telefono, quando un campo
  // con use:amountKeys è attivo. Dentro un pannello sta sopra i pulsanti; altrimenti in fondo alla pagina.
  import Icon from './Icon.svelte'
  import { keypad } from '../lib/keypad.svelte'
  import type { Key } from '../lib/keypad'

  let { owner = null }: { owner?: HTMLElement | null } = $props()

  const visible = $derived(
    !!keypad.target && (owner ? owner.contains(keypad.target) : !keypad.target.closest('dialog')),
  )
  const integer = $derived(keypad.mode === 'integer')

  const DIGITS: Key[][] = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
  ]
</script>

{#if visible}
  <!-- I tasti non prendono il focus: il cursore resta nel campo -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="keypad" class:floating={!owner} role="group" aria-label="Tastierino" onpointerdown={(e) => e.preventDefault()}>
    {#each DIGITS as row, r (r)}
      {#each row as d (d)}
        <button type="button" class="key" onclick={() => keypad.press(d)}>{d}</button>
      {/each}
      {#if r === 0}
        <button type="button" class="key op" aria-label="Cancella" onclick={() => keypad.press('back')}>
          <Icon name="delete" size={22} />
        </button>
      {:else if r === 1}
        <button type="button" class="key op" class:off={integer} aria-label="Più" disabled={integer} onclick={() => keypad.press('+')}>
          <Icon name="plus" size={22} />
        </button>
      {:else}
        <button type="button" class="key op" class:off={integer} aria-label="Meno" disabled={integer} onclick={() => keypad.press('-')}>
          <Icon name="minus" size={22} />
        </button>
      {/if}
    {/each}
    <button type="button" class="key" class:off={integer} aria-label="Virgola" disabled={integer} onclick={() => keypad.press(',')}>,</button>
    <button type="button" class="key" onclick={() => keypad.press('0')}>0</button>
    <button type="button" class="key op" class:off={integer} aria-label="Calcola" disabled={integer} onclick={() => keypad.press('=')}>=</button>
    <button type="button" class="key done" onclick={() => keypad.done()}>Fatto</button>
  </div>
{/if}

<style>
  .keypad {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--space-2);
    padding: var(--space-3) var(--space-5);
    background: var(--color-bg);
    border-top: 1px solid var(--color-border);
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
  }

  .floating {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 40;
    padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom));
    border-top: none;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    box-shadow: var(--shadow-3);
  }

  .key {
    display: grid;
    place-items: center;
    height: var(--size-key);
    padding: 0;
    border: 0;
    border-radius: var(--radius-md);
    background: var(--color-surface);
    color: var(--color-text);
    font: inherit;
    font-size: var(--text-xl);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
    transition: background-color var(--duration-fast) var(--ease-standard);
  }

  .key:active {
    background: var(--color-surface-2);
  }

  .key.op {
    background: var(--color-accent-soft);
    color: var(--color-accent);
  }

  .key.done {
    background: var(--color-primary);
    color: var(--color-on-primary);
    font-size: var(--text-md);
    font-weight: 800;
  }

  .key.off {
    visibility: hidden;
  }
</style>
