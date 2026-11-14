<script lang="ts">
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
  import type { Transaction, TransactionType } from '../lib/data/types'
  import { formatEuro, parseEuro } from '../lib/format'
  import { ui } from '../lib/ui.svelte'
  import { csvFileName, downloadText, movementsToCsv } from '../lib/data/csv'

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
  <button class="btn btn-small" class:active={showFilters} onclick={() => (showFilters = !showFilters)}>
    Filtri{activeCount ? ` (${activeCount})` : ''}
  </button>
</div>

{#if showFilters}
  <Card>
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
      <div class="row-2">
        <label class="field">
          <span>Dal</span>
          <input class="input" type="date" bind:value={f.from} />
        </label>
        <label class="field">
          <span>Al</span>
          <input class="input" type="date" bind:value={f.to} />
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
        <select class="input" bind:value={f.source}>
          <option value="">Tutti</option>
          {#each sources as o (o.key)}
            <option value={o.key}>{o.label}{o.account.archived ? ' (archiviato)' : ''}</option>
          {/each}
        </select>
      </label>
      <label class="field">
        <span>Categoria</span>
        <select class="input" bind:value={f.categoryId}>
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
          <select class="input" bind:value={f.tag}>
            <option value="">Tutte</option>
            {#each tagList as t (t)}<option value={t}>#{t}</option>{/each}
          </select>
        </label>
      {/if}
      {#if activeCount > 0 || f.text}
        <button class="btn btn-ghost reset" onclick={reset}>Azzera ricerca</button>
      {/if}
    </div>
  </Card>
{/if}

{#if f.text || activeCount > 0}
  <div class="summary">
    <span>{results.length === 1 ? '1 movimento' : `${results.length} movimenti`}</span>
    <span class="num">
      {#if totals.income}<span class="income">+{formatEuro(totals.income)}</span>{/if}
      {#if totals.expense}<span class="expense">−{formatEuro(totals.expense)}</span>{/if}
    </span>
  </div>

  {#if results.length === 0}
    <Card><p class="empty-note">Nessun movimento trovato.</p></Card>
  {:else}
    <Card>
      <ul class="list">
        {#each shown as t (t.id)}
          <li><MovementRow {t} refs={refs.value} showDate onclick={() => (sheet = { movement: t })} /></li>
        {/each}
      </ul>
    </Card>
    <div class="more">
      {#if results.length > shown.length}
        <button class="btn" onclick={() => (limit += 100)}>Mostra altri ({results.length - shown.length})</button>
      {/if}
      <button class="btn btn-ghost" onclick={exportCsv}>Esporta per Excel (CSV)</button>
    </div>
  {/if}
{:else}
  <p class="empty-note">Scrivi qualcosa o usa i filtri per cercare tra tutti i movimenti.</p>
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

  .search {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }

  .search .btn {
    min-height: 44px;
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
    min-height: 32px;
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
