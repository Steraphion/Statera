<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import AccountForm from '../components/AccountForm.svelte'
  import CardForm from '../components/CardForm.svelte'
  import Icon from '../components/Icon.svelte'
  import CategoryIcon from '../components/CategoryIcon.svelte'
  import { ACCOUNT_ICONS } from '../lib/categoryIcon'
  import GoalForm from '../components/GoalForm.svelte'
  import GoalAddSheet from '../components/GoalAddSheet.svelte'
  import { goalProgress } from '../lib/data/goals'
  import { today } from '../lib/data/util'
  import type { Goal } from '../lib/data/types'
  import { db } from '../lib/data/db'
  import { moveAccount } from '../lib/data/repo'
  import { live } from '../lib/data/live.svelte'
  import { accountBalance, accountGroups, cardEligible, cardsOf, netWorth } from '../lib/data/balances'
  import { ACCOUNT_TYPE_LABELS, SWATCHES, type Account, type Card as CardT } from '../lib/data/types'
  import { alive, byOrder } from '../lib/data/util'
  import { formatEuro, formatVouchers, monthOf, shiftMonth } from '../lib/format'
  import { columns } from '../lib/columns.svelte'
  import Splitter from '../components/Splitter.svelte'
  import AccountPanel from '../components/AccountPanel.svelte'
  import WorthLine from '../components/charts/WorthLine.svelte'
  import { netWorthSeries } from '../lib/data/analytics'
  import { useRefs } from '../lib/data/refs.svelte'

  /** PC: conto mostrato accanto all'elenco (#/conto/<id>); senza, il primo conto attivo. */
  let { selected = null }: { selected?: string | null } = $props()
  const refs = useRefs()

  const data = live(
    async () => {
      const [accounts, cards, transactions, goals] = await Promise.all([
        db.accounts.toArray(),
        db.cards.toArray(),
        db.transactions.toArray(),
        db.goals.toArray(),
      ])
      return {
        accounts: alive(accounts).sort(byOrder),
        cards: alive(cards).sort(byOrder),
        transactions,
        goals: alive(goals).sort((a, b) => a.name.localeCompare(b.name, 'it')),
      }
    },
    { accounts: [] as Account[], cards: [] as CardT[], transactions: [], goals: [] as Goal[] },
  )

  const active = $derived(data.value.accounts.filter((a) => !a.archived))
  const archived = $derived(data.value.accounts.filter((a) => a.archived))
  const total = $derived(netWorth(data.value.accounts, data.value.transactions))
  const accountName = $derived(new Map(data.value.accounts.map((a) => [a.id, a.name])))
  const eligible = $derived(active.filter(cardEligible))
  /** Conti attivi divisi per tipo (conti correnti, carte prepagate, contanti…), ognuno col suo totale. */
  const groups = $derived(accountGroups(active, data.value.transactions))
  const canSort = $derived(groups.some((g) => g.accounts.length > 1))

  let showArchived = $state(false)
  let sorting = $state(false)
  let accountSheet = $state<{ account?: Account } | null>(null)
  let cardSheet = $state<{ card?: CardT } | null>(null)
  let goalSheet = $state<{ goal?: Goal } | null>(null)
  let goalAdd = $state<Goal | null>(null)
  const now = today()

  // --- PC: elenco e dettaglio affiancati ---
  /** Mese del dettaglio: resta lo stesso passando da un conto all'altro. */
  let detailMonth = $state(monthOf(today()))
  const shownList = $derived([...groups.flatMap((g) => g.accounts), ...(showArchived ? archived : [])])
  const current = $derived(
    columns.pc && data.ready ? (data.value.accounts.find((a) => a.id === selected) ?? active[0] ?? null) : null,
  )

  // Conto eliminato (o indirizzo sbagliato): si torna all'elenco, col primo conto
  $effect(() => {
    if (columns.pc && data.ready && selected && !data.value.accounts.some((a) => a.id === selected)) {
      location.replace('#/conti')
    }
  })

  // Area molto larga: terza colonna col saldo del conto a fine mese (12 mesi fino a quello del dettaglio)
  // e gli obiettivi di risparmio, che altrimenti stanno sotto l'elenco
  const molto = $derived(columns.at('molto'))
  const series = $derived(current && molto ? netWorthSeries([current], data.value.transactions, detailMonth, today(), 12) : [])

  /** Mostra un altro conto senza riempire la cronologia (frecce ↑ ↓). */
  function show(id: string) {
    location.replace(`#/conto/${encodeURIComponent(id)}`)
  }

  // Scorciatoie (PC): ↑ ↓ cambiano conto, ← → il mese del dettaglio
  function onKey(e: KeyboardEvent) {
    if (!columns.pc || !current || e.ctrlKey || e.metaKey || e.altKey) return
    if ((e.target as HTMLElement).closest('input, textarea, select, [contenteditable]')) return
    if (document.querySelector('dialog[open]')) return
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault()
      detailMonth = shiftMonth(detailMonth, e.key === 'ArrowLeft' ? -1 : 1)
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      const i = shownList.findIndex((a) => a.id === current.id)
      const next = shownList[i + (e.key === 'ArrowUp' ? -1 : 1)]
      if (next) {
        e.preventDefault()
        show(next.id)
      }
    }
  }
</script>

<svelte:window onkeydown={onKey} />

<ScreenHeader title="Conti">
  <button class="btn btn-primary btn-small" onclick={() => (accountSheet = {})}>
    <Icon name="plus" size={18} /> Conto
  </button>
</ScreenHeader>

<!-- Telefono: elenco (il dettaglio è una schermata a parte). PC: elenco a sinistra, largo a piacere, e
     dettaglio del conto scelto a destra -->
<div class="split" style:--col-w={columns.width('pane') === null ? null : `${columns.width('pane')}px`}>
<div class="list-col" id="conti-list">
<section class="total balance-box" aria-label="Patrimonio">
  <span class="bb-label">Patrimonio</span>
  <span class="num bb-amount">{formatEuro(total)}</span>
  <span class="bb-pill">{active.length === 1 ? '1 conto attivo' : `${active.length} conti attivi`}{archived.length ? ` · ${archived.length} archiviat${archived.length === 1 ? 'o' : 'i'}` : ''}</span>
</section>

{#snippet accountRow(a: Account)}
  {@const b = accountBalance(a, data.value.transactions)}
  {@const sel = current?.id === a.id}
  <li>
    <a class="list-row" class:selected={sel} aria-current={sel ? 'true' : undefined} href="#/conto/{a.id}">
      <CategoryIcon icon={ACCOUNT_ICONS[a.type]} color={a.color} />
      <span class="main">
        <span class="name">{a.name}</span>
        <span class="sub">{ACCOUNT_TYPE_LABELS[a.type]}</span>
      </span>
      <span class="end">
        <span class="num" class:amount-neg={b.amount < 0}>{formatEuro(b.amount)}</span>
        {#if b.vouchers !== null}
          <span class="sub vouchers">{formatVouchers(b.vouchers)}</span>
        {/if}
      </span>
    </a>
  </li>
{/snippet}

{#snippet cardRow(c: CardT)}
  <li class="nested">
    <button class="list-row" onclick={() => (cardSheet = { card: c })} aria-label="Carta {c.name}, collegata a {accountName.get(c.accountId) ?? ''}{c.archived ? ', archiviata' : ''}">
      <CategoryIcon icon="credit-card" size="s" />
      <span class="main">
        <span class="name">{c.name}</span>
        <span class="sub">Carta collegata{c.archived ? ' · archiviata' : ''}</span>
      </span>
    </button>
  </li>
{/snippet}

{#if !data.ready}
  <Card><p class="empty-note">Caricamento…</p></Card>
{:else if active.length === 0}
  <h2 class="section-title">I tuoi conti</h2>
  <Card>
    <p class="empty-note">
      Nessun conto. Inizia aggiungendo il tuo conto corrente (con la sua carta, se vuoi), le carte prepagate, i
      contanti e i buoni pasto.
    </p>
  </Card>
{:else}
  {#each groups as g, gi (g.type)}
    <h2 class="section-title group-title">
      <span>{g.label}</span>
      <span class="group-end">
        {#if gi === 0 && canSort}
          <button class="btn btn-ghost btn-small" onclick={() => (sorting = !sorting)}>{sorting ? 'Fatto' : 'Ordina'}</button>
        {/if}
        <span class="num group-total" class:amount-neg={g.total < 0} aria-label="Totale {g.label}: {formatEuro(g.total)}">{formatEuro(g.total)}</span>
      </span>
    </h2>
    <Card>
      <ul class="list">
        {#each g.accounts as a, i (a.id)}
          {#if sorting}
            <li class="sort-row">
              <CategoryIcon icon={ACCOUNT_ICONS[a.type]} color={a.color} size="s" />
              <span class="name">{a.name}</span>
              <button class="btn btn-ghost btn-small" aria-label="Sposta su {a.name}" disabled={i === 0} onclick={() => moveAccount(a.id, -1)}>↑</button>
              <button class="btn btn-ghost btn-small" aria-label="Sposta giù {a.name}" disabled={i === g.accounts.length - 1} onclick={() => moveAccount(a.id, 1)}>↓</button>
            </li>
          {:else}
            {@render accountRow(a)}
            <!-- Le carte di debito stanno sotto il loro conto: sono un modo di pagare da quel conto -->
            {#each cardsOf(a, data.value.cards) as c (c.id)}
              {@render cardRow(c)}
            {/each}
          {/if}
        {/each}
      </ul>
    </Card>
  {/each}
{/if}

<!-- Obiettivi: sotto l'elenco, o nella terza colonna quando l'area è molto larga -->
{#if !molto}
  {@render goalsBlock()}
{/if}

{#if archived.length > 0}
  <h2 class="section-title">
    Archiviati
    <button class="btn btn-ghost btn-small" onclick={() => (showArchived = !showArchived)}>
      {showArchived ? 'Nascondi' : `Mostra (${archived.length})`}
    </button>
  </h2>
  {#if showArchived}
    <Card>
      <ul class="list">
        {#each archived as a (a.id)}
          {@render accountRow(a)}
        {/each}
      </ul>
    </Card>
  {/if}
{/if}

</div>

{#snippet goalsBlock()}
<h2 class="section-title">
  Obiettivi di risparmio
  <button class="btn btn-ghost btn-small" onclick={() => (goalSheet = {})}>
    <Icon name="plus" size={16} /> Obiettivo
  </button>
</h2>
<Card>
  {#if data.value.goals.length === 0}
    <p class="empty-note">
      Nessun obiettivo. Un obiettivo (es. fondo emergenze, vacanza) ti dice quanto manca e quanto mettere da parte al
      mese.
    </p>
  {:else}
    <ul class="goals">
      {#each data.value.goals as g (g.id)}
        {@const p = goalProgress(g, data.value.accounts, data.value.transactions, now)}
        <li>
          <button class="goal" onclick={() => (goalSheet = { goal: g })} aria-label="Modifica {g.name}">
            <span class="top">
              <span class="name"><span class="dot" style:background="var(--swatch-{g.color})"></span>{g.name}</span>
              <span class="num pct">{p.reached ? '✓ Raggiunto' : `${Math.floor(Math.min(1, p.ratio) * 100)}%`}</span>
            </span>
            <span
              class="track"
              role="meter"
              aria-label="Avanzamento {g.name}"
              aria-valuemin="0"
              aria-valuemax={g.target}
              aria-valuenow={Math.max(0, p.current)}
            >
              <span class="fill" style:width="{Math.max(0, Math.min(100, p.ratio * 100))}%" style:background="var(--swatch-{g.color})"></span>
            </span>
            <span class="sub num">{formatEuro(p.current)} di {formatEuro(g.target)}{p.reached ? '' : ` · mancano ${formatEuro(p.remaining)}`}</span>
            {#if p.perMonth}
              <span class="sub">Circa <strong class="num">{formatEuro(p.perMonth)}</strong> al mese per {p.monthsLeft === 1 ? "l'ultimo mese" : `${p.monthsLeft} mesi`}</span>
            {:else if p.overdue}
              <span class="sub">La data prevista è passata</span>
            {/if}
            {#if g.accountId}
              <span class="sub">Segue il saldo di {accountName.get(g.accountId) ?? '—'}</span>
            {/if}
          </button>
          {#if !g.accountId && !p.reached}
            <button class="btn btn-small add" onclick={() => (goalAdd = g)}>Aggiungi</button>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</Card>
{/snippet}

{#if columns.pc}
  <Splitter
    id="pane"
    token="--size-pane"
    other="--size-detail-min"
    grows="right"
    controls="conti-list"
    label="Larghezza dell'elenco dei conti"
    reserve={molto ? ['--size-extra', '--space-6'] : []}
  />
  <div class="detail-col">
    {#if current}
      {#key current.id}
        <div class="pane-in">
          <AccountPanel account={current} transactions={data.value.transactions} refs={refs.value} bind:month={detailMonth} />
        </div>
      {/key}
    {:else if data.ready}
      <Card><p class="empty-note">Aggiungi un conto per vederne qui il dettaglio.</p></Card>
    {/if}
  </div>
  {#if molto}
    <aside class="extra-col" aria-label="Andamento del conto e obiettivi">
      {#if current && series.some((p) => p.value !== null)}
        <Card>
          <section aria-labelledby="account-trend-title">
            <h2 id="account-trend-title" class="card-title">Saldo a fine mese</h2>
            <p class="card-sub">{current.name}, ultimi 12 mesi</p>
            <WorthLine points={series} />
          </section>
        </Card>
      {/if}
      {@render goalsBlock()}
    </aside>
  {/if}
{/if}
</div>

{#if accountSheet}
  <AccountForm
    account={accountSheet.account}
    defaultColor={SWATCHES[data.value.accounts.length % SWATCHES.length]}
    onclose={() => (accountSheet = null)}
  />
{/if}

{#if goalSheet}
  <GoalForm
    goal={goalSheet.goal}
    accounts={data.value.accounts}
    defaultColor={SWATCHES[(data.value.goals.length + 2) % SWATCHES.length]}
    onclose={() => (goalSheet = null)}
  />
{/if}

{#if goalAdd}
  <GoalAddSheet goal={goalAdd} onclose={() => (goalAdd = null)} />
{/if}

{#if cardSheet}
  <CardForm
    card={cardSheet.card}
    accounts={cardSheet.card
      ? data.value.accounts.filter((a) => a.id === cardSheet?.card?.accountId || (cardEligible(a) && !a.archived))
      : eligible}
    onclose={() => (cardSheet = null)}
  />
{/if}

<style>
  .group-title {
    gap: var(--space-3);
  }

  .group-end {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
  }

  .group-total {
    color: var(--color-text);
    letter-spacing: normal;
    text-transform: none;
  }

  /* Carta sotto il suo conto: rientrata, più piccola, senza importo */
  .nested :global(.list-row) {
    min-height: var(--size-touch);
    padding-left: calc(var(--size-cat) + var(--space-3));
  }

  /* PC: elenco e dettaglio affiancati. L'elenco ha la larghezza scelta (o quella iniziale), mai tanta da
     lasciare il dettaglio sotto --size-detail-min; il separatore sta nello spazio tra i due */
  @media (min-width: 900px) {
    .split {
      display: grid;
      grid-template-columns:
        min(
          clamp(var(--size-pane-min), var(--col-w, var(--size-pane)), var(--size-pane-max)),
          max(var(--size-pane-min), 100% - var(--size-detail-min) - var(--space-6))
        )
        var(--space-6) minmax(0, 1fr);
      align-items: start;
    }

    .list-col {
      min-width: 0;
    }

    /* Area molto larga: terza colonna larga --size-extra; l'elenco tiene conto anche di quella */
    :global(.l-molto) .split {
      grid-template-columns:
        min(
          clamp(var(--size-pane-min), var(--col-w, var(--size-pane)), var(--size-pane-max)),
          max(var(--size-pane-min), 100% - var(--size-detail-min) - 2 * var(--space-6) - var(--size-extra))
        )
        var(--space-6) minmax(0, 1fr) var(--space-6) var(--size-extra);
    }

    .extra-col {
      grid-column: 5;
      min-width: 0;
    }

    .extra-col > :global(.section-title:first-child) {
      margin-top: 0;
    }

    .extra-col :global(.card) {
      padding: var(--space-4) var(--space-5);
    }

    .extra-col > :global(.card) + :global(.section-title) {
      margin-top: var(--space-5);
    }

    .card-title {
      font-size: var(--text-lg);
    }

    .card-sub {
      margin: var(--space-1) 0 var(--space-3);
      font-size: var(--text-sm);
      color: var(--color-text-muted);
    }

    .list-col > :first-child {
      margin-top: 0;
    }

    .list-col :global(.card) {
      padding: var(--space-4) var(--space-5);
    }

    .detail-col {
      min-width: 0;
      /* Il dettaglio adatta la tabella alla sua larghezza (AccountPanel) */
      container: dettaglio / inline-size;
    }

    /* Conto scelto evidenziato; passando col puntatore, un velo */
    .list-row.selected,
    .list-row:hover {
      margin: 0 calc(-1 * var(--space-3));
      padding-left: var(--space-3);
      padding-right: var(--space-3);
      width: calc(100% + 2 * var(--space-3));
    }

    .list-row:hover {
      background: color-mix(in srgb, var(--color-surface-2) 60%, transparent);
    }

    .list-row.selected {
      background: var(--color-accent-soft);
    }
  }

  /* Cambiando conto, il dettaglio compare in dissolvenza (design system: Movimento) */
  .pane-in {
    animation: pane-in var(--duration-base) var(--ease-standard);
  }

  @keyframes pane-in {
    from {
      opacity: 0;
    }
  }

  .goals {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .goals li {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: var(--space-2);
    align-items: start;
  }

  .goal {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    width: 100%;
    padding: 0;
    border: 0;
    background: none;
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
  }

  .goal .top {
    display: flex;
    justify-content: space-between;
    gap: var(--space-2);
  }

  .goal .name {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: 600;
  }

  .goal .dot {
    width: var(--space-3);
    height: var(--space-3);
    border-radius: 50%;
  }

  .goal .pct {
    font-weight: 700;
  }

  .goal .track {
    display: block;
    height: var(--space-2);
    border-radius: var(--radius-2xs);
    background: var(--chart-track);
    overflow: hidden;
  }

  .goal .fill {
    display: block;
    height: 100%;
    border-radius: var(--radius-2xs);
    /* Movimento: scorre al nuovo valore quando cambia (es. dopo «Aggiungi») */
    transition: width var(--duration-slow) var(--ease-standard);
  }

  .goal .sub {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .goal .sub strong {
    color: var(--color-text);
  }

  .add {
    margin-top: var(--space-hair);
  }

  /* Patrimonio grande al centro (stile Vivace) */
  .total {
    margin: var(--space-2) 0 var(--space-2);
  }

  .sort-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-height: var(--size-field);
  }

  .sort-row .name {
    flex: 1;
    margin-left: var(--space-1);
    font-weight: 600;
  }

  .end {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .vouchers {
    font-size: var(--text-xs);
  }
</style>
