<script lang="ts">
  // Scelta della palette (Altro → Aspetto). Ogni anteprima ha data-palette: tokens.css le dà i colori
  // di quella palette nel tema in uso, quindi mostra il riquadro del saldo, un'azione rapida e il +.
  import Icon from './Icon.svelte'
  import { theme } from '../lib/theme.svelte'
  import { PALETTES } from '../lib/theme'
</script>

<div class="grid" role="radiogroup" aria-label="Colori">
  {#each PALETTES as p (p.id)}
    {@const selected = theme.palette === p.id}
    <button
      type="button"
      role="radio"
      class="pal"
      class:selected
      aria-checked={selected}
      data-palette={p.id}
      onclick={() => theme.setPalette(p.id)}
    >
      <span class="preview" aria-hidden="true">
        <span class="box num">+585 €</span>
        <span class="dot soft"><Icon name="arrow-up-right" size={16} /></span>
        <span class="dot fab"><Icon name="plus" size={16} stroke={2.4} /></span>
      </span>
      <span class="name">
        {p.name}
        {#if selected}<span class="check"><Icon name="check" size={16} stroke={2.6} /></span>{/if}
      </span>
    </button>
  {/each}
</div>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-2);
  }

  @media (min-width: 600px) {
    .grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  .pal {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-2) var(--space-3);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    color: var(--color-text);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }

  /* Bordo nel colore principale della palette stessa */
  .pal.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 1px var(--color-primary);
  }

  .preview {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-2);
    border-radius: var(--radius-md);
    background: var(--color-bg);
  }

  .box {
    display: flex;
    align-items: center;
    height: var(--size-cat-s);
    padding: 0 var(--space-2);
    border-radius: var(--radius-xs);
    background: var(--color-primary);
    color: var(--color-on-primary);
    font-size: var(--text-xs);
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
  }

  .dot {
    display: grid;
    place-items: center;
    width: var(--size-cat-s);
    height: var(--size-cat-s);
    border-radius: var(--radius-full);
  }

  .soft {
    background: var(--color-accent-soft);
    color: var(--color-accent);
  }

  .fab {
    background: var(--color-fab);
    color: var(--color-on-fab);
  }

  .name {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--space-1);
    padding: 0 var(--space-1);
    font-size: var(--text-sm);
    font-weight: 700;
    line-height: var(--leading-compact);
  }

  .check {
    flex: none;
    color: var(--color-primary);
  }
</style>
