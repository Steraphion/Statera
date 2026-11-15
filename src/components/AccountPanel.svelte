<script lang="ts">
  import Card from './Card.svelte'
  import Icon from './Icon.svelte'
  import CategoryIcon from './CategoryIcon.svelte'
  import AccountForm from './AccountForm.svelte'
  import AlignSheet from './AlignSheet.svelte'
  import MovementForm from './MovementForm.svelte'
  import { ACCOUNT_ICONS } from '../lib/categoryIcon'
  import { accountBalance, accountLedger, cardsOf, ledgerMonth } from '../lib/data/balances'
  import type { Refs } from '../lib/data/refs.svelte'
  import * as mv from '../lib/data/transactions'
  import { ACCOUNT_TYPE_LABELS, type Account, type Transaction } from '../lib/data/types'
  import { formatDayMonth, formatEuro, formatMonth, formatShortDay, formatVouchers, parseDay, shiftMonth } from '../lib/format'

  /**
   * Dettaglio di un conto accanto all'elenco (Conti su PC): saldo, azioni e i movimenti di un mese in
   * tabella, con il saldo dopo ogni movimento e il saldo da cui parte il mese.
   */
  let {
    account,
    transactions,
    refs,
    month = $bindable(),
  }: { account: Account; transactions: Transaction[]; refs: Refs; month: string } = $props()

  const balance = $derived(accountBalance(account, transactions))
  const ledger = $derived(accountLedger(account, transactions))
  const view = $derived(ledgerMonth(account, ledger, month))
  const cards = $derived(cardsOf(account, refs.cards))
  const monthName = $derived(formatMonth(parseDay(`${month}-01`)))

  let editAccount = $state(false)
  let aligning = $state(false)
  let movementSheet = $state<{ movement?: Transaction } | null>(null)

  /**
   * Seconda riga della descrizione: categoria (se c'è una descrizione), fonte, ricorrente, etichette. Con la
   * colonna Categoria (dettaglio largo) la categoria non si ripete: `withCat = false`.
   */
  function detail(t: Transaction, withCat = true): string {
    // La fonte si scrive solo se dice qualcosa in più del conto che si sta guardando (una carta, un altro conto)
    const others = t.parts.filter((p) => p.cardId || p.accountId !== account.id)
    const from = others.map((p) => mv.partLabel(p, refs.accountMap, refs.cardMap)).join(' + ')
    const all = t.parts.map((p) => mv.partLabel(p, refs.accountMap, refs.cardMap)).join(' + ')
    const pieces: string[] = []
    if (t.id.startsWith('rec-')) pieces.push('↻ ricorrente')
    if (t.type === 'trasferimento') pieces.push(`${all} → ${refs.accountMap.get(t.toAccountId ?? '')?.name ?? '—'}`)
    else {
      if (t.description && withCat) pieces.push(mv.categoryText(t, refs.categoryMap))
      if (from) pieces.push(from)
    }
    for (const tag of t.tags ?? []) pieces.push(`#${tag}`)
    return pieces.join(' · ')
  }

  function signed(n: number): string {
    return `${n > 0 ? '+' : n < 0 ? '−' : ''}${formatEuro(Math.abs(n))}`
  }
</script>

<Card>
  <section class="detail" aria-label="Dettaglio di {account.name}">
    <div class="head">
      <CategoryIcon icon={ACCOUNT_ICONS[account.type]} color={account.color} size="l" />
      <div class="who">
        <h2>{account.name}</h2>
        <p class="sub">
          {ACCOUNT_TYPE_LABELS[account.type]}{account.archived ? ' · archiviato' : ''}{cards.length
            ? ` · ${cards.length === 1 ? 'carta' : 'carte'} ${cards.map((c) => c.name).join(', ')}`
            : ''}
        </p>
      </div>
      <div class="today">
        <span class="sub">Saldo di oggi</span>
        <span class="num value" class:amount-neg={balance.amount < 0}>{formatEuro(balance.amount)}</span>
        {#if balance.vouchers !== null}
          <span class="sub">{formatVouchers(balance.vouchers)} da {formatEuro(account.voucherValue ?? 0)}</span>
        {/if}
      </div>
    </div>

    <div class="actions">
      {#if !account.archived}
        <button class="btn btn-soft btn-small" onclick={() => (aligning = true)}>
          <Icon name="scale" size={16} /> Allinea al saldo reale
        </button>
      {/if}
      <button class="btn btn-small" data-no-autoauth onclick={() => (movementSheet = {})}>
        <Icon name="plus" size={16} /> Movimento
      </button>
      <button class="btn btn-small" onclick={() => (editAccount = true)}>
        <Icon name="pencil" size={16} /> Modifica
      </button>
    </div>

    <div class="month-bar">
      <div class="month">
        <button class="btn btn-ghost nav" aria-label="Mese precedente" title="Mese precedente (freccia a sinistra)" onclick={() => (month = shiftMonth(month, -1))}>
          <Icon name="chevron-left" />
        </button>
        <h3>{monthName}</h3>
        <button class="btn btn-ghost nav" aria-label="Mese successivo" title="Mese successivo (freccia a destra)" onclick={() => (month = shiftMonth(month, 1))}>
          <Icon name="chevron-right" />
        </button>
      </div>
      <dl class="sums">
        <div><dt>Entrate</dt><dd class="num" class:income={view.income > 0}>{signed(view.income)}</dd></div>
        <div><dt>Uscite</dt><dd class="num">{signed(view.expense)}</dd></div>
        {#if view.transfers !== 0}
          <div><dt>Trasferimenti</dt><dd class="num">{signed(view.transfers)}</dd></div>
        {/if}
      </dl>
    </div>

    {#if view.entries.length}
      <table>
        <caption class="visually-hidden">Movimenti di {account.name}, {monthName.toLowerCase()}</caption>
        <colgroup>
          <col class="c-date" />
          <col />
          <col class="c-cat cat" />
          <col class="c-amount" />
          <col class="c-amount bal" />
        </colgroup>
        <thead>
          <tr>
            <th scope="col">Data</th>
            <th scope="col">Descrizione</th>
            <th scope="col" class="cat">Categoria</th>
            <th scope="col" class="r">Importo</th>
            <th scope="col" class="r bal">Saldo</th>
          </tr>
        </thead>
        <tbody>
          {#each view.entries as e (e.t.id)}
            {@const t = e.t}
            <!-- Tutta la riga si apre col mouse; da tastiera c'è il pulsante della descrizione -->
            <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
            <tr class:muted={!e.counted} onclick={() => (movementSheet = { movement: t })}>
              <td class="date">{formatDayMonth(t.date)}</td>
              <td>
                <button class="desc" data-no-autoauth onclick={(ev) => { ev.stopPropagation(); movementSheet = { movement: t } }}>
                  {#if t.type === 'trasferimento'}
                    <CategoryIcon icon="arrow-left-right" size="s" />
                  {:else if t.splits?.length}
                    {@const c = t.categoryId ? (refs.categoryMap.get(t.categoryId) ?? null) : null}
                    <CategoryIcon icon="split" color={c?.color ?? null} size="s" />
                  {:else}
                    <CategoryIcon category={t.categoryId ? (refs.categoryMap.get(t.categoryId) ?? null) : null} size="s" />
                  {/if}
                  <span class="text">
                    <span class="name">{mv.movementTitle(t, refs.categoryMap)}</span>
                    <span class="sub with-cat">{detail(t)}</span>
                    <span class="sub no-cat">{detail(t, false)}</span>
                  </span>
                </button>
              </td>
              <td class="cat cat-cell">{t.type === 'trasferimento' ? 'Trasferimento' : mv.categoryText(t, refs.categoryMap)}</td>
              <td class="r num amount" class:income={e.effect > 0}>{signed(e.effect)}</td>
              <td class="r num bal">
                {#if e.counted}
                  <span class="after">{formatEuro(e.balanceAfter)}</span>
                {:else}
                  <span class="chip" title="Data precedente al saldo iniziale: conta nei totali, non nel saldo">non incide</span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p class="empty-note">Nessun movimento su questo conto in {monthName.toLowerCase()}.</p>
    {/if}

    <div class="opening">
      {#if view.opening.kind === 'prima'}
        <span class="sub">
          Prima del saldo iniziale (al {formatShortDay(account.initialDate)}): questi movimenti non cambiano il saldo.
        </span>
      {:else}
        <span>
          <b>{view.opening.kind === 'iniziale' ? 'Saldo iniziale' : 'Saldo a inizio mese'}</b>
          {#if view.opening.kind === 'iniziale'}<span class="sub"> al {formatShortDay(account.initialDate)}</span>{/if}
        </span>
        <b class="num" class:amount-neg={view.opening.amount < 0}>{formatEuro(view.opening.amount)}</b>
      {/if}
    </div>
    {#if view.entries.some((e) => !e.counted)}
      <p class="note">
        I movimenti segnati "non incide" hanno una data precedente al saldo iniziale: compaiono nei totali del mese ma non
        cambiano il saldo, perché sono già compresi nel saldo iniziale.
      </p>
    {/if}
  </section>
</Card>

{#if aligning}
  <AlignSheet {account} {transactions} onclose={() => (aligning = false)} />
{/if}

{#if editAccount}
  <AccountForm {account} onclose={() => (editAccount = false)} />
{/if}

{#if movementSheet}
  <MovementForm
    movement={movementSheet.movement}
    accounts={refs.accounts}
    cards={refs.cards}
    categories={refs.categories}
    lastSources={movementSheet.movement ? refs.lastSources : { uscita: `a:${account.id}`, entrata: `a:${account.id}`, trasferimento: `a:${account.id}` }}
    onclose={() => (movementSheet = null)}
  />
{/if}

<style>
  .detail {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .head {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .who {
    flex: 1;
    min-width: 0;
  }

  h2 {
    font-size: var(--text-xl);
    overflow-wrap: anywhere;
  }

  .sub {
    font-size: var(--text-sm);
    line-height: var(--leading-compact);
    color: var(--color-text-muted);
  }

  .today {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    text-align: right;
  }

  .value {
    font-size: var(--amount-m);
    font-weight: 800;
    letter-spacing: var(--tracking-tighter);
    line-height: var(--leading-tight);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  /* Mese e totali del mese su un fondo appena diverso */
  .month-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2) var(--space-5);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    background: var(--color-bg);
  }

  .month {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .month h3 {
    font-size: var(--text-lg);
    white-space: nowrap;
  }

  .nav {
    min-height: var(--size-touch);
    padding: 0 var(--space-1);
    color: var(--color-text-muted);
  }

  .sums {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1) var(--space-5);
    margin: 0;
  }

  .sums div {
    display: flex;
    flex-direction: column;
  }

  .sums dt {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .sums dd {
    margin: 0;
    font-weight: 800;
  }

  /* Tabella: larghezze fisse per data e importi, la descrizione prende il resto e va coi puntini */
  table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: var(--text-sm);
  }

  .c-date {
    width: calc(var(--space-8) + var(--space-4));
  }

  .c-amount {
    width: calc(2 * var(--space-8) + var(--space-4));
  }

  .c-cat {
    width: 30%;
  }

  /* Colonna Categoria: solo col dettaglio largo (area larga o molto larga); allora la seconda riga della
     descrizione non la ripete */
  .cat,
  .sub.no-cat {
    display: none;
  }

  .cat-cell {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--color-text-muted);
  }

  @container dettaglio (min-width: 820px) {
    .cat {
      display: table-cell;
    }

    col.cat {
      display: table-column;
    }

    .sub.no-cat {
      display: block;
    }

    .sub.with-cat {
      display: none;
    }
  }

  th {
    padding: var(--space-2);
    font-size: var(--text-xs);
    font-weight: 700;
    text-align: left;
    color: var(--color-text-muted);
  }

  td {
    padding: var(--space-1) var(--space-2);
    border-top: 1px solid var(--color-border);
    vertical-align: middle;
  }

  tbody tr {
    cursor: pointer;
  }

  @media (hover: hover) {
    tbody tr:hover {
      background: color-mix(in srgb, var(--color-surface-2) 60%, transparent);
    }
  }

  .r {
    text-align: right;
  }

  .date {
    white-space: nowrap;
    color: var(--color-text-muted);
  }

  .desc {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    min-height: var(--size-touch);
    padding: 0;
    border: 0;
    background: none;
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
  }

  .text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .text .name {
    font-weight: 700;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .text .sub {
    font-size: var(--text-xs);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .amount {
    font-weight: 700;
  }

  .income {
    color: var(--color-income);
  }

  .after {
    color: var(--color-text-muted);
  }

  .muted .desc,
  .muted .amount {
    opacity: 0.55;
  }

  .chip {
    display: inline-block;
    padding: var(--space-hair) var(--space-2);
    border-radius: var(--radius-full);
    background: var(--color-surface-2);
    color: var(--color-text-muted);
    font-size: var(--text-2xs);
    font-weight: 700;
    white-space: nowrap;
  }

  /* Dettaglio stretto: la colonna del saldo dopo ogni movimento lascia spazio alla descrizione (il saldo
     di oggi resta in testata, quello di inizio mese in fondo) */
  @container dettaglio (max-width: 560px) {
    .bal {
      display: none;
    }
  }

  .opening {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-2) 0;
    border-top: 1px dashed var(--color-border);
  }

  .note {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }
</style>
