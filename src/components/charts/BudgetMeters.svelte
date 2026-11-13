<script lang="ts">
  import type { BudgetStatus } from '../../lib/data/analytics'
  import { formatEuro } from '../../lib/format'

  // Indicatori di budget: il colore segue lo stato, sempre con un'etichetta (mai solo colore).
  let { items }: { items: BudgetStatus[] } = $props()

  const LABEL: Record<BudgetStatus['state'], string> = {
    ok: 'Nei limiti',
    attenzione: 'Quasi esaurito',
    superato: 'Superato',
  }
</script>

<ul class="meters">
  {#each items as b (b.category.id)}
    {@const left = b.budget - b.spent}
    <li class={b.state}>
      <div class="top">
        <span class="name"><span class="dot" style:background="var(--swatch-{b.category.color})"></span>{b.category.name}</span>
        <span class="state">{b.state === 'ok' ? '' : b.state === 'superato' ? '▲ ' : '! '}{LABEL[b.state]}</span>
      </div>
      <div
        class="track"
        role="meter"
        aria-label="Budget {b.category.name}"
        aria-valuemin="0"
        aria-valuemax={b.budget}
        aria-valuenow={b.spent}
      >
        <span class="fill" style:width="{Math.min(100, b.ratio * 100)}%"></span>
      </div>
      <div class="bottom num">
        <span>{formatEuro(b.spent)} di {formatEuro(b.budget)}</span>
        <span>{left >= 0 ? `restano ${formatEuro(left)}` : `oltre di ${formatEuro(-left)}`}</span>
      </div>
    </li>
  {/each}
</ul>

<style>
  .meters {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .top,
  .bottom {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
  }

  .name {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: 600;
  }

  .state {
    font-size: var(--text-xs);
    font-weight: 650;
    color: var(--color-text-muted);
  }

  .attenzione .state {
    color: var(--status-warning);
  }

  .superato .state {
    color: var(--status-critical);
  }

  .track {
    margin: var(--space-2) 0 var(--space-1);
    height: 10px;
    border-radius: 4px;
    background: var(--chart-track);
    overflow: hidden;
  }

  .fill {
    display: block;
    height: 100%;
    border-radius: 0 4px 4px 0;
    background: var(--chart-income);
  }

  .attenzione .fill {
    background: var(--status-warning);
  }

  .superato .fill {
    background: var(--status-critical);
  }

  .bottom {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
