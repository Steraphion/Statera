<script lang="ts">
  import Card from './Card.svelte'
  import BudgetMeters from './charts/BudgetMeters.svelte'
  import BudgetSheet from './BudgetSheet.svelte'
  import { budgetStatus, daysLeftInMonth } from '../lib/data/analytics'
  import type { Category, Transaction } from '../lib/data/types'
  import { today } from '../lib/data/util'

  /** Budget del mese mostrato (colonna di destra di Movimenti, su PC). Solo se c'è almeno un budget. */
  let { rows, month, categories }: { rows: Transaction[]; month: string; categories: Category[] } = $props()

  const items = $derived(budgetStatus(rows, month, categories))
  let editing = $state(false)
</script>

{#if items.length}
  <Card>
    <section aria-labelledby="month-budget-title">
      <div class="head">
        <h2 id="month-budget-title">Budget del mese</h2>
        <button class="btn btn-ghost btn-small" onclick={() => (editing = true)}>Modifica</button>
      </div>
      <BudgetMeters {items} daysLeft={daysLeftInMonth(month, today())} />
    </section>
  </Card>
{/if}

{#if editing}
  <BudgetSheet {categories} onclose={() => (editing = false)} />
{/if}

<style>
  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }

  h2 {
    font-size: var(--text-lg);
  }

  /* Il collegamento a fine riga: allineato al bordo è il testo, non la pillola */
  .head > .btn-ghost {
    margin-right: calc(-1 * var(--space-3));
  }
</style>
