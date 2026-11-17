<script lang="ts">
  import { SWATCH_NAMES, SWATCHES, type SwatchKey } from '../lib/data/types'

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
        aria-label={SWATCH_NAMES[s]}
        title={SWATCH_NAMES[s]}
        class:selected={value === s}
        style:background="var(--swatch-{s})"
        onclick={() => (value = s)}
      ></button>
    {/each}
  </div>
</fieldset>

<style>
  /* Sedici tinte in due file da otto, anche sul telefono */
  .swatches {
    display: grid;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    gap: var(--space-2);
    max-width: calc(8 * var(--size-touch) + 7 * var(--space-2));
  }

  button {
    width: 100%;
    max-width: var(--size-touch);
    aspect-ratio: 1;
    padding: 0;
    justify-self: center;
    border-radius: 50%;
    border: 3px solid transparent;
    cursor: pointer;
    box-shadow: inset 0 0 0 var(--focus-width) var(--color-surface);
  }

  button.selected {
    border-color: var(--color-text);
  }
</style>
