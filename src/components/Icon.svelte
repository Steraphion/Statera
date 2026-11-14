<script lang="ts">
  // Icone Lucide copiate nel codice (src/lib/icons.ts, generato da scripts/icone.mjs): nessun caricamento esterno.
  // Si colorano con il colore del testo (currentColor).
  import { ICONS, type IconName } from '../lib/icons'

  let { name, size = 20, stroke = 2 }: { name: IconName; size?: number; stroke?: number } = $props()

  const nodes = $derived(ICONS[name] ?? [])
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={stroke}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
  focusable="false"
>
  {#each nodes as [tag, a], i (i)}
    {#if tag === 'path'}<path {...a} />{:else if tag === 'circle'}<circle {...a} />{:else if tag === 'rect'}<rect
        {...a}
      />{:else if tag === 'line'}<line {...a} />{:else if tag === 'polyline'}<polyline
        {...a}
      />{:else if tag === 'polygon'}<polygon {...a} />{:else}<ellipse {...a} />{/if}
  {/each}
</svg>

<style>
  svg {
    display: block;
    flex-shrink: 0;
  }
</style>
