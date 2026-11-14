<script lang="ts">
  import { SWATCHES, type SwatchKey } from '../lib/data/types'

  let { value = $bindable() }: { value: SwatchKey } = $props()
</script>

<fieldset class="field">
  <legend>Colore</legend>
  <div class="swatches" role="radiogroup">
    {#each SWATCHES as s (s)}
      <button
        type="button"
        role="radio"
        aria-checked={value === s}
        aria-label="Colore {s.slice(1)}"
        class:selected={value === s}
        style:background="var(--swatch-{s})"
        onclick={() => (value = s)}
      ></button>
    {/each}
  </div>
</fieldset>

<style>
  .swatches {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  button {
    width: var(--size-btn-s);
    height: var(--size-btn-s);
    border-radius: 50%;
    border: 3px solid transparent;
    cursor: pointer;
    box-shadow: inset 0 0 0 var(--focus-width) var(--color-surface);
  }

  button.selected {
    border-color: var(--color-text);
  }
</style>
