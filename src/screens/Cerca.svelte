<script lang="ts">
  import { pickerAction } from '../lib/picker.svelte'
  import { amountKeys } from '../lib/keypad.svelte'
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import MovementRow from '../components/MovementRow.svelte'
  import Segmented from '../components/Segmented.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Category, Transaction, TransactionType } from '../lib/data/types'
  import { formatEuro, parseEuro } from '../lib/format'
  import { ui } from '../lib/ui.svelte'
  import { csvFileName, downloadText, movementsToCsv } from '../lib/data/csv'
  import { columns } from '../lib/columns.svelte'
  import CategoryBars from '../components/charts/CategoryBars.svelte'
  import { byCategory, monthTotals } from '../lib/data/analytics'
  import { formatMonth, parseDay } from '../lib/format'

  const refs = useRefs()
  const all = live(() => db.transactions.toArray(), [] as Transaction[])

  // I filtri restano impostati se si cambia schermata e poi si torna qui
  const f = ui.filters
  let showFilters = $state(!!(f.from || f.to || f.type || f.source || f.categoryId || f.min || f.max || f.tag))
  let limit = $state(100)
  let sheet = $state<{ movement: Transaction } | null>(null)

  const results = $derived(mv.filterMovements(all.value, f, refs.value))
  const shown = $derived(results.slice(0, limit))
  const totals = $derived(mv.totals(results))
  const sources = $derived(
    mv.sourceOptions(
      refs.value.accounts,
      refs.value.cards,
      [...refs.value.accounts.map((a) => `a:${a.id}`), ...refs.value.cards.map((c) => `c:${c.id}`)],
    ),
  )
  const tops = $derived(refs.value.categories.filter((c) => c.parentId === null))
  const activeCount = $derived([f.from || f.to, f.type, f.source, f.categoryId, f.min || f.max, f.tag].filter(Boolean).length)
  const tagList = $derived(mv.allTags(all.value))
  const badAmount = $derived(
    (!!f.min.trim() && parseEuro(f.min) === null) || (!!f.max.trim() && parseEuro(f.max) === null),
  )

  // PC: filtri sempre aperti a sinistra; da area larga risultati in tabella (con la data in colonna); da molto
  // larga, mentre si cerca, il riepilogo per categoria e per mese a destra. Senza ricerca, gli ultimi movimenti.
  const pc = $derived(columns.at('media'))
  const larga = $derived(columns.at('larga'))
  const searching = $derived(!!f.text || activeCount > 0)
  const summary = $derived(searching && columns.at('molto'))
  const outCats = $derived(summary ? byCategory(results, 'uscita', refs.value.categories).slice(0, 6) : [])
  const inCats = $derived(summary ? byCategory(results, 'entrata', refs.value.categories).slice(0, 6) : [])
  const months = $derived(summary ? monthTotals(results).slice(0, 6) : [])

  /** Dal riepilogo: restringe la ricerca a una categoria. */
  function onlyCategory(c: Category) {
    f.categoryId = c.id
  }

  function exportCsv() {
    downloadText(movementsToCsv(results, refs.value), csvFileName(f.from, f.to))
  }

  function reset() {
    Object.assign(f, mv.EMPTY_FILTERS)
  }

  $effect(() => {
    // Nuova ricerca: si riparte dai primi risultati
    void [f.text, f.from, f.to, f.type, f.source, f.categoryId, f.min, f.max, f.tag]
    limit = 100
  })
</script>

<ScreenHeader title="Cerca" back={{ href: '#/movimenti', label: 'Movimenti' }} />

{#snippet searchBar()}
<div class="search">
  <!-- svelte-ignore a11y_autofocus -->
  <input
    class="input"
    type="search"
    bind:value={f.text}
    placeholder="Descrizione, nota, categoria, conto…"
    aria-label="Cerca"
    autofocus
  />
  {#if !pc}
    <button class="btn btn-small" class:active={showFilters} onclick={() => (showFilters = !showFilters)}>
      Filtri{activeCount ? ` (${activeCount})` : ''}
    </button>
  {/if}
</div>
{/snippet}

{#snippet filtersForm()}
    <div class="form">
      <Segmented
        label="Tipo"
        bind:value={f.type}
        options={[
          { value: '' as TransactionType | '', label: 'Tutti' },
          { value: 'uscita', label: 'Uscite' },
          { value: 'entrata', label: 'Entrate' },
          { value: 'trasferimento', label: 'Trasf.' },
        ]}
      />
      <div class="row-2 dates">
        <label class="field">
          <span>Dal</span>
          <input class="input" type="date" use:pickerAction bind:value={f.from} />
        </label>
        <label class="field">
          <span>Al</span>
          <input class="input" type="date" use:pickerAction bind:value={f.to} />
        </label>
      </div>
      <div class="row-2">
        <label class="field">
          <span>Importo da (€)</span>
          <input class="input num" bind:value={f.min} use:amountKeys inputmode="decimal" placeholder="0,00" autocomplete="off" />
        </label>
        <label class="field">
          <span>Importo a (€)</span>
          <input class="input num" bind:value={f.max} use:amountKeys inputmode="decimal" placeholder="0,00" autocomplete="off" />
        </label>
      </div>
      {#if badAmount}<p class="bad" role="alert">Importo non valido: scrivi ad esempio 50 o 12,50.</p>{/if}
      <label class="field">
        <span>Conto o carta</span>
        <select use:pickerAction class="input" bind:value={f.source}>
          <option value="">Tutti</option>
          {#each sources as o (o.key)}
            <option value={o.key}>{o.label}{o.account.archived ? ' (archiviato)' : ''}</option>
          {/each}
        </select>
      </label>
      <label class="field">
        <span>Categoria</span>
        <select use:pickerAction class="input" bind:value={f.categoryId}>
          <option value="">Tutte</option>
          {#each ['uscita', 'entrata'] as kind (kind)}
            <optgroup label={kind === 'uscita' ? 'Uscite' : 'Entrate'}>
              {#each tops.filter((c) => c.kind === kind) as c (c.id)}
                <option value={c.id}>{c.name}</option>
                {#each refs.value.categories.filter((x) => x.parentId === c.id) as child (child.id)}
                  <option value={child.id}>{c.name} › {child.name}</option>
                {/each}
              {/each}
            </optgroup>
          {/each}
        </select>
      </label>
      {#if tagList.length || f.tag}
        <label class="field">
          <span>Etichetta</span>
          <select use:pickerAction class="input" bind:value={f.tag}>
            <option value="">Tutte</option>
            {#each tagList as t (t)}<option value={t}>#{t}</option>{/each}
          </select>
        </label>
      {/if}
      {#if activeCount > 0 || f.text}
        <button class="btn btn-ghost reset" onclick={reset}>Azzera ricerca</button>
      {/if}
    </div>
{/snippet}

{#snippet resultsList()}
{#if searching || pc}
  {#if !searching}
    <h2 class="section-title latest">Ultimi movimenti</h2>
  {:else}
  <div class="summary">
    <span>{results.length === 1 ? '1 movimento' : `${results.length} movimenti`}</span>
    <span class="num">
      {#if totals.income}<span class="income">+{formatEuro(totals.income)}</span>{/if}
      {#if totals.expense}<span class="expense">−{formatEuro(totals.expense)}</span>{/if}
    </span>
  </div>
  {/if}

  {#if results.length === 0}
    <Card><p class="empty-note">Nessun movimento trovato.</p></Card>
  {:else}
    <Card>
      {#if larga}
        <div class="cols-head row-cols with-date" aria-hidden="true">
          <span>Data</span><span></span><span>Descrizione</span><span>Categoria</span><span>Conto o carta</span><span class="r">Importo</span>
        </div>
      {/if}
      <ul class="list">
        {#each shown as t (t.id)}
          <li><MovementRow {t} refs={refs.value} showDate columns={larga} dateCol={larga} onclick={() => (sheet = { movement: t })} /></li>
        {/each}
      </ul>
    </Card>
    <div class="more">
      {#if results.length > shown.length}
        <button class="btn" onclick={() => (limit += 100)}>Mostra altri ({results.length - shown.length})</button>
      {/if}
      {#if searching}
        <button class="btn btn-ghost" onclick={exportCsv}>Esporta per Excel (CSV)</button>
      {/if}
    </div>
  {/if}
{:else}
  <p class="empty-note">Scrivi qualcosa o usa i filtri per cercare tra tutti i movimenti.</p>
{/if}
{/snippet}

{#if pc}
  <!-- PC: filtri sempre aperti a sinistra, risultati al centro e, da area molto larga, il riepilogo -->
  <div class="sgrid" class:three={summary}>
    <aside class="filters-col" aria-label="Filtri">
      <Card>
        <h2 class="filters-title">Filtri{activeCount ? ` (${activeCount})` : ''}</h2>
        {@render filtersForm()}
      </Card>
    </aside>
    <div class="results-col">
      {@render searchBar()}
      {@render resultsList()}
    </div>
    {#if summary}
      <aside class="summary-col" aria-label="Riepilogo dei risultati">
        {#if outCats.length}
          <Card>
            <h2 class="filters-title">Uscite per categoria</h2>
            <CategoryBars groups={outCats} color="var(--chart-expense)" onshow={onlyCategory} />
          </Card>
        {/if}
        {#if inCats.length}
          <Card>
            <h2 class="filters-title">Entrate per categoria</h2>
            <CategoryBars groups={inCats} color="var(--chart-income)" onshow={onlyCategory} />
          </Card>
        {/if}
        {#if months.length}
          <Card>
            <h2 class="filters-title">Per mese</h2>
            <ul class="months">
              {#each months as m (m.month)}
                <li>
                  <span class="m-name">{formatMonth(parseDay(`${m.month}-01`))}</span>
                  <span class="num">
                    {#if m.income}<span class="income">+{formatEuro(m.income)}</span>{/if}
                    {#if m.expense}<span class="expense">−{formatEuro(m.expense)}</span>{/if}
                  </span>
                </li>
              {/each}
            </ul>
          </Card>
        {/if}
      </aside>
    {/if}
  </div>
{:else}
  {@render searchBar()}
  {#if showFilters}
    <Card>
      {@render filtersForm()}
    </Card>
  {/if}
  {@render resultsList()}
{/if}

{#if sheet}
  <MovementForm
    movement={sheet.movement}
    accounts={refs.value.accounts}
    cards={refs.value.cards}
    categories={refs.value.categories}
    lastSources={refs.value.lastSources}
    onclose={() => (sheet = null)}
  />
{/if}

<style>
  /* PC: filtri a sinistra (--size-filters), risultati al centro, riepilogo a destra (--size-summary) */
  .sgrid {
    display: grid;
    grid-template-columns: var(--size-filters) minmax(0, 1fr);
    gap: var(--space-4) var(--space-6);
    align-items: start;
  }

  .sgrid.three {
    grid-template-columns: var(--size-filters) minmax(0, 1fr) var(--size-summary);
  }

  .filters-col,
  .results-col,
  .summary-col {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .summary-col {
    gap: var(--space-4);
  }

  .summary-col > :global(.card) + :global(.card) {
    margin: 0;
  }

  .filters-col :global(.card),
  .summary-col :global(.card) {
    padding: var(--space-4) var(--space-5);
  }

  /* Nella colonna dei filtri le date stanno una sotto l'altra (il campo data del PC è largo) e le voci del
     tipo un po' più strette, così ci stanno tutte e quattro */
  .filters-col .dates {
    grid-template-columns: minmax(0, 1fr);
  }

  .filters-col :global(.segmented button) {
    padding: 0 var(--space-2);
  }

  .filters-title {
    margin-bottom: var(--space-3);
    font-size: var(--text-lg);
  }

  .latest {
    margin-top: var(--space-2);
  }

  .months {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .months li {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    font-size: var(--text-sm);
  }

  .months li + li {
    border-top: 1px solid var(--color-border);
  }

  .months .num {
    display: flex;
    gap: var(--space-2);
    font-weight: 700;
  }


  .search {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }

  .search .btn {
    min-height: var(--size-touch);
    flex: none;
  }

  .search .btn.active {
    border-color: var(--color-accent);
  }

  .bad {
    font-size: var(--text-sm);
    color: var(--color-danger);
  }

  .reset {
    align-self: flex-start;
    padding: 0;
    min-height: var(--size-cat-s);
  }

  .summary {
    display: flex;
    justify-content: space-between;
    margin: var(--space-4) 0 var(--space-2);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-text-muted);
  }

  .summary .num {
    display: flex;
    gap: var(--space-3);
  }

  .income {
    color: var(--color-income);
  }

  .expense {
    color: var(--color-expense);
  }

  .more {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }
</style>
