<script lang="ts">
  // Logo di Statera: la bilancia nel riquadro arrotondato. Disegno generato da scripts/icona-app.mjs
  // (src/lib/logo.ts); colori dai token, così in tema scuro passa al riquadro lilla col simbolo scuro.
  import { LOGO, LOGO_RADIUS, LOGO_SIZE } from '../lib/logo'

  let { size = 36 }: { size?: number } = $props()

  const v = $derived(LOGO[size <= 32 ? 'piccolo' : 'grande'])
</script>

<svg width={size} height={size} viewBox="0 0 {LOGO_SIZE} {LOGO_SIZE}" aria-hidden="true" focusable="false">
  <rect class="tile" width={LOGO_SIZE} height={LOGO_SIZE} rx={LOGO_RADIUS} />
  <g class="glyph" transform={v.transform}>
    {#each v.nodes as [tag, a], i (i)}
      {#if tag === 'path'}<path {...a} />{:else}<circle {...a} />{/if}
    {/each}
  </g>
</svg>

<style>
  svg {
    display: block;
    flex-shrink: 0;
  }

  .tile {
    fill: var(--color-primary);
  }

  .glyph {
    color: var(--color-on-primary);
  }
</style>
