<script lang="ts">
  import type { CategoryTotal } from '../../lib/data/analytics'
  import type { Category } from '../../lib/data/types'
  import { formatEuro } from '../../lib/format'

  // Barre orizzontali: una sola serie (quanto per categoria), quindi un solo colore.
  // L'identità della categoria è il pallino accanto al nome; i valori sono scritti in chiaro.
  let {
    groups,
    color,
    onshow,
  }: { groups: CategoryTotal[]; color: string; onshow: (c: Category) => void } = $props()

  let open = $state<string | null>(null)
  const max = $derived(Math.max(1, ...groups.map((g) => g.total)))
  const pct = (share: number) => `${Math.round(share * 100)}%`
</script>

{#if groups.length === 0}
  <p class="empty-note">Nessun movimento in questo periodo.</p>
{:else}
  <ul class="bars">
    {#each groups as g (g.category.id)}
      {@const expanded = open === g.category.id}
      <li>
        <button
          class="row"
          aria-expanded={expanded}
          onclick={() => (open = expanded ? null : g.category.id)}
          title="{g.category.name}: {formatEuro(g.total)} ({pct(g.share)})"
        >
          <span class="label">
            <span class="dot" style:background="var(--swatch-{g.category.color})"></span>
            <span class="name">{g.category.name}</span>
            <span class="share">{pct(g.share)}</span>
          </span>
          <span class="track">
            <span class="bar" style:width="{(g.total / max) * 100}%" style:background={color}></span>
          </span>
          <span class="value num">{formatEuro(g.total)}</span>
        </button>
        {#if expanded}
          <div class="detail">
            {#each g.children as ch (ch.category.id)}
              <div class="sub">
                <span class="name">{ch.direct ? `${g.category.name} (senza sottocategoria)` : ch.category.name}</span>
                <span class="value num">{formatEuro(ch.total)}</span>
              </div>
            {/each}
            <button class="btn btn-ghost btn-small show" onclick={() => onshow(g.category)}>
              Vedi i movimenti ›
            </button>
          </div>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .bars {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
  }

  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas: 'label value' 'track track';
    gap: var(--space-1) var(--space-3);
    width: 100%;
    padding: var(--space-2) 0;
    border: none;
    background: none;
    text-align: left;
  }

  .row:hover .bar,
  .row:focus-visible .bar {
    filter: brightness(1.08);
  }

  .label {
    grid-area: label;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-width: 0;
  }

  .name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 600;
  }

  .share {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .value {
    grid-area: value;
    font-weight: 600;
  }

  .track {
    grid-area: track;
    height: 12px;
    border-radius: 4px;
    background: var(--chart-track);
    overflow: hidden;
  }

  .bar {
    display: block;
    height: 100%;
    min-width: 2px;
    border-radius: 0 4px 4px 0;
  }

  .detail {
    margin: 0 0 var(--space-2) calc(10px + var(--space-2));
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    font-size: var(--text-sm);
  }

  .sub {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-1) 0;
  }

  .sub .name {
    font-weight: 400;
  }

  .show {
    padding: 0;
    min-height: 32px;
  }
</style>
