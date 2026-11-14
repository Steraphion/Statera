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
  import { accountBalance, cardEligible, netWorth } from '../lib/data/balances'
  import { ACCOUNT_TYPE_LABELS, SWATCHES, type Account, type Card as CardT } from '../lib/data/types'
  import { alive, byOrder } from '../lib/data/util'
  import { formatEuro, formatVouchers } from '../lib/format'

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

  let showArchived = $state(false)
  let sorting = $state(false)
  let accountSheet = $state<{ account?: Account } | null>(null)
  let cardSheet = $state<{ card?: CardT } | null>(null)
  let goalSheet = $state<{ goal?: Goal } | null>(null)
  let goalAdd = $state<Goal | null>(null)
  const now = today()
</script>

<ScreenHeader title="Conti">
  <button class="btn btn-primary btn-small" onclick={() => (accountSheet = {})}>
    <Icon name="plus" size={18} /> Conto
  </button>
</ScreenHeader>

<section class="total balance-box" aria-label="Patrimonio">
  <span class="bb-label">Patrimonio</span>
  <span class="num bb-amount">{formatEuro(total)}</span>
  <span class="bb-pill">{active.length === 1 ? '1 conto attivo' : `${active.length} conti attivi`}{archived.length ? ` · ${archived.length} archiviat${archived.length === 1 ? 'o' : 'i'}` : ''}</span>
</section>

{#snippet accountRow(a: Account)}
  {@const b = accountBalance(a, data.value.transactions)}
  <li>
    <a class="list-row" href="#/conto/{a.id}">
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

<h2 class="section-title">
  I tuoi conti
  {#if active.length > 1}
    <button class="btn btn-ghost btn-small" onclick={() => (sorting = !sorting)}>{sorting ? 'Fatto' : 'Ordina'}</button>
  {/if}
</h2>
<Card>
  {#if !data.ready}
    <p class="empty-note">Caricamento…</p>
  {:else if active.length === 0}
    <p class="empty-note">Nessun conto. Inizia aggiungendo il tuo conto corrente, i contanti e i buoni pasto.</p>
  {:else}
    <ul class="list">
      {#each active as a, i (a.id)}
        {#if sorting}
          <li class="sort-row">
            <CategoryIcon icon={ACCOUNT_ICONS[a.type]} color={a.color} size="s" />
            <span class="name">{a.name}</span>
            <button class="btn btn-ghost btn-small" aria-label="Sposta su {a.name}" disabled={i === 0} onclick={() => moveAccount(a.id, -1)}>↑</button>
            <button class="btn btn-ghost btn-small" aria-label="Sposta giù {a.name}" disabled={i === active.length - 1} onclick={() => moveAccount(a.id, 1)}>↓</button>
          </li>
        {:else}
          {@render accountRow(a)}
        {/if}
      {/each}
    </ul>
  {/if}
</Card>

<h2 class="section-title">
  Carte di debito
  <button class="btn btn-ghost btn-small" onclick={() => (cardSheet = {})}>
    <Icon name="plus" size={16} /> Carta
  </button>
</h2>
<Card>
  {#if data.value.cards.length === 0}
    <p class="empty-note">Nessuna carta. Le carte servono a indicare con cosa hai pagato.</p>
  {:else}
    <ul class="list">
      {#each data.value.cards as c (c.id)}
        <li>
          <button class="list-row" onclick={() => (cardSheet = { card: c })}>
            <CategoryIcon icon="credit-card" />
            <span class="main">
              <span class="name">{c.name}</span>
              <span class="sub">Collegata a {accountName.get(c.accountId) ?? '—'}</span>
            </span>
            {#if c.archived}<span class="sub">Archiviata</span>{/if}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</Card>

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
      ? data.value.accounts.filter((a) => cardEligible(a) && (!a.archived || a.id === cardSheet?.card?.accountId))
      : eligible}
    onclose={() => (cardSheet = null)}
  />
{/if}

<style>
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
