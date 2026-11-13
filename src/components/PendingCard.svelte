<script lang="ts">
  import Card from './Card.svelte'
  import MovementForm from './MovementForm.svelte'
  import { live } from '../lib/data/live.svelte'
  import type { Refs } from '../lib/data/refs.svelte'
  import * as rec from '../lib/data/recurring'
  import { categoryLabel } from '../lib/data/transactions'
  import type { Recurring } from '../lib/data/types'
  import { errorMessage, today } from '../lib/data/util'
  import { formatEuro, formatShortDay } from '../lib/format'

  // Movimenti ricorrenti "da confermare" arrivati a scadenza
  let { refs }: { refs: Refs } = $props()

  const pending = live(() => rec.pendingConfirmations(today()), [] as { r: Recurring; date: string }[])
  let sheet = $state<{ r: Recurring; date: string } | null>(null)
  let error = $state('')

  async function skip(p: { r: Recurring; date: string }) {
    try {
      await rec.skipOccurrence(p.r, p.date)
    } catch (e) {
      error = errorMessage(e)
    }
  }
</script>

{#if pending.value.length > 0}
  <Card>
    <h2>Da registrare</h2>
    <ul class="list">
      {#each pending.value as p (p.r.id + p.date)}
        <li class="row">
          <span class="main">
            <span class="name">{p.r.description || categoryLabel(p.r.categoryId, refs.categoryMap)}</span>
            <span class="sub">{formatShortDay(p.date)} · circa {formatEuro(rec.recurringTotal(p.r, refs.accountMap))}</span>
          </span>
          <button class="btn btn-small" onclick={() => skip(p)}>Salta</button>
          <button class="btn btn-primary btn-small" onclick={() => (sheet = p)}>Registra</button>
        </li>
      {/each}
    </ul>
    {#if error}<p class="error-box">{error}</p>{/if}
  </Card>
{/if}

{#if sheet}
  <MovementForm
    confirm={sheet}
    accounts={refs.accounts}
    cards={refs.cards}
    categories={refs.categories}
    lastSources={refs.lastSources}
    onclose={() => (sheet = null)}
  />
{/if}

<style>
  h2 {
    font-size: var(--text-md);
    font-weight: 650;
    margin-bottom: var(--space-2);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-height: 56px;
    border-bottom: 1px solid var(--color-border);
  }

  .row:last-child {
    border-bottom: none;
  }

  .main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sub {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
