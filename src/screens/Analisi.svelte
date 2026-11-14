<script lang="ts">
  import Card from '../components/Card.svelte'
  import Icon from '../components/Icon.svelte'
  import Segmented from '../components/Segmented.svelte'
  import BudgetSheet from '../components/BudgetSheet.svelte'
  import CategoryBars from '../components/charts/CategoryBars.svelte'
  import MonthlyColumns from '../components/charts/MonthlyColumns.svelte'
  import BudgetMeters from '../components/charts/BudgetMeters.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import * as an from '../lib/data/analytics'
  import { totals, EMPTY_FILTERS } from '../lib/data/transactions'
  import type { Category, CategoryKind, Transaction } from '../lib/data/types'
  import { today } from '../lib/data/util'
  import { formatEuro, formatMonth, monthOf, parseDay, shiftMonth } from '../lib/format'
  import { ui } from '../lib/ui.svelte'
  import { csvFileName, downloadText, movementsToCsv } from '../lib/data/csv'

  const refs = useRefs()
  const all = live(() => db.transactions.toArray(), [] as Transaction[])

  const a = ui.analysis
  let kind = $state<CategoryKind>('uscita')
  let budgetSheet = $state(false)

  const period = $derived<an.Period>(
    a.kind === 'mese' ? { kind: 'mese', month: a.month } : { kind: 'anno', year: a.month.slice(0, 4) },
  )
  const rows = $derived(an.periodRows(all.value, period))
  const sums = $derived(totals(rows))
  const savingRate = $derived(sums.income > 0 ? sums.net / sums.income : null)
  const groups = $derived(an.byCategory(rows, kind, refs.value.categories))
  const endMonth = $derived(a.kind === 'mese' ? a.month : `${a.month.slice(0, 4)}-12`)
  const series = $derived(an.monthlySeries(all.value, endMonth, 12))
  const budgets = $derived(a.kind === 'mese' ? an.budgetStatus(all.value, a.month, refs.value.categories) : [])
  const isCurrent = $derived(
    a.kind === 'mese' ? a.month === monthOf(today()) : a.month.slice(0, 4) === today().slice(0, 4),
  )

  const title = $derived(a.kind === 'mese' ? formatMonth(parseDay(`${a.month}-01`)) : a.month.slice(0, 4))

  function shift(delta: number) {
    a.month = shiftMonth(a.month, a.kind === 'mese' ? delta : delta * 12)
  }

  function exportCsv() {
    const r = an.periodRange(period)
    downloadText(movementsToCsv(rows, refs.value), csvFileName(r.from, r.to))
  }

  /** Apre la ricerca con i movimenti di quella categoria nel periodo. */
  function showMovements(c: Category) {
    const r = an.periodRange(period)
    Object.assign(ui.filters, EMPTY_FILTERS, { categoryId: c.id, from: r.from, to: r.to, type: c.kind })
    location.hash = '/cerca'
  }
</script>

<header class="top">
  <button class="btn btn-ghost nav" aria-label="Periodo precedente" onclick={() => shift(-1)}><Icon name="left" /></button>
  <h1>{title}</h1>
  <button class="btn btn-ghost nav" aria-label="Periodo successivo" onclick={() => shift(1)}><Icon name="right" /></button>
  <span class="spacer"></span>
  {#if !isCurrent}
    <button class="btn btn-small" onclick={() => (a.month = monthOf(today()))}>Oggi</button>
  {/if}
</header>

<div class="filters">
  <Segmented
    label="Periodo"
    bind:value={a.kind}
    options={[
      { value: 'mese', label: 'Mese' },
      { value: 'anno', label: 'Anno' },
    ]}
  />
</div>

<div class="tiles">
  <div class="tile">
    <span class="label">Entrate</span>
    <span class="value num">{formatEuro(sums.income)}</span>
  </div>
  <div class="tile">
    <span class="label">Uscite</span>
    <span class="value num">{formatEuro(sums.expense)}</span>
  </div>
  <div class="tile">
    <span class="label">Risparmio</span>
    <span class="value num" class:amount-neg={sums.net < 0}>{formatEuro(sums.net)}</span>
    {#if savingRate !== null}<span class="delta">{Math.round(savingRate * 100)}% delle entrate</span>{/if}
  </div>
</div>

<Card>
  <div class="card-head">
    <h2>{kind === 'uscita' ? 'Uscite' : 'Entrate'} per categoria</h2>
    <div class="small-seg">
      <Segmented
        label="Tipo"
        bind:value={kind}
        options={[
          { value: 'uscita', label: 'Uscite' },
          { value: 'entrata', label: 'Entrate' },
        ]}
      />
    </div>
  </div>
  <CategoryBars
    {groups}
    color={kind === 'uscita' ? 'var(--chart-expense)' : 'var(--chart-income)'}
    onshow={showMovements}
  />
</Card>

{#if a.kind === 'mese'}
  <Card>
    <div class="card-head">
      <h2>Budget del mese</h2>
      <button class="btn btn-ghost btn-small" onclick={() => (budgetSheet = true)}>
        {budgets.length ? 'Modifica' : 'Imposta budget'}
      </button>
    </div>
    {#if budgets.length}
      <BudgetMeters items={budgets} daysLeft={an.daysLeftInMonth(a.month, today())} />
    {:else}
      <p class="empty-note">
        Nessun budget impostato. Un budget ti avvisa quando una categoria si avvicina al limite mensile.
      </p>
    {/if}
  </Card>
{/if}

<Card>
  <div class="card-head">
    <h2>Andamento ultimi 12 mesi</h2>
  </div>
  <MonthlyColumns points={series} highlight={a.kind === 'mese' ? a.month : ''} />
</Card>

<div class="export">
  <button class="btn btn-ghost" onclick={exportCsv} disabled={rows.length === 0} aria-label="Esporta i movimenti del periodo per Excel (CSV)">
    Esporta per Excel (CSV)
  </button>
</div>

{#if budgetSheet}
  <BudgetSheet categories={refs.value.categories} onclose={() => (budgetSheet = false)} />
{/if}

<style>
  .export {
    display: flex;
    justify-content: center;
    margin: var(--space-2) 0 var(--space-4);
  }

  .top {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-bottom: var(--space-3);
  }

  .top h1 {
    font-size: var(--text-xl);
    font-weight: 650;
    letter-spacing: -0.01em;
    white-space: nowrap;
  }

  .nav {
    min-height: 40px;
    padding: 0 var(--space-1);
    color: var(--color-text-muted);
  }

  .spacer {
    flex: 1;
  }

  .filters {
    margin-bottom: var(--space-3);
    max-width: 280px;
  }

  .tiles {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }

  .tile {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    min-width: 0;
  }

  .tile .label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .tile .value {
    font-weight: 650;
    font-size: var(--text-md);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tile .delta {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    margin-bottom: var(--space-3);
    flex-wrap: wrap;
  }

  h2 {
    font-size: var(--text-md);
    font-weight: 650;
  }

  .small-seg {
    min-width: 190px;
  }

  @media (max-width: 420px) {
    .tile .value {
      font-size: var(--text-sm);
    }
  }
</style>
