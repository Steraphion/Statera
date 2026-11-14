<script lang="ts">
  // Cerchio colorato con l'icona della categoria (design system: IconaCategoria).
  // Tema chiaro: tinta al 15% e icona colorata; scuro: tinta al 30% e icona bianca (base.css, .cat-icon).
  import Icon from './Icon.svelte'
  import type { IconName } from '../lib/icons'
  import { categoryIconName, initial } from '../lib/categoryIcon'
  import type { SwatchKey } from '../lib/data/types'

  let {
    category = null,
    color = null,
    icon = null,
    size = 'm',
  }: {
    /** Categoria (id, nome, colore, icona). Senza categoria serve `icon`. */
    category?: { id: string; name: string; color: SwatchKey; icon?: string | null } | null
    /** Tinta; se manca si usa quella della categoria, poi il colore d'accento. */
    color?: SwatchKey | null
    /** Icona fissa (es. trasferimento, conto). */
    icon?: IconName | null
    size?: 's' | 'm' | 'l'
  } = $props()

  const name = $derived(icon ?? (category ? categoryIconName(category) : null))
  const tint = $derived(color ?? category?.color ?? null)
  const px = $derived(size === 's' ? 16 : size === 'l' ? 22 : 20)
</script>

<span
  class="cat-icon"
  class:small={size === 's'}
  class:large={size === 'l'}
  class:neutral={!tint}
  style:--cat={tint ? `var(--swatch-${tint})` : null}
  aria-hidden="true"
>
  {#if name}
    <Icon {name} size={px} />
  {:else}
    {initial(category?.name ?? '')}
  {/if}
</span>

<style>
  .neutral {
    background: var(--color-accent-soft);
    color: var(--color-accent);
  }
</style>
