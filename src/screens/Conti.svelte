<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import AccountForm from '../components/AccountForm.svelte'
  import CardForm from '../components/CardForm.svelte'
  import Icon from '../components/Icon.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { accountBalance, cardEligible, netWorth } from '../lib/data/balances'
  import { ACCOUNT_TYPE_LABELS, SWATCHES, type Account, type Card as CardT } from '../lib/data/types'
  import { alive, byOrder } from '../lib/data/util'
  import { formatEuro, formatVouchers } from '../lib/format'

  const data = live(
    async () => {
      const [accounts, cards, transactions] = await Promise.all([
        db.accounts.toArray(),
        db.cards.toArray(),
        db.transactions.toArray(),
      ])
      return { accounts: alive(accounts).sort(byOrder), cards: alive(cards).sort(byOrder), transactions }
    },
    { accounts: [] as Account[], cards: [] as CardT[], transactions: [] },
  )

  const active = $derived(data.value.accounts.filter((a) => !a.archived))
  const archived = $derived(data.value.accounts.filter((a) => a.archived))
  const total = $derived(netWorth(data.value.accounts, data.value.transactions))
  const accountName = $derived(new Map(data.value.accounts.map((a) => [a.id, a.name])))
  const eligible = $derived(active.filter(cardEligible))

  let showArchived = $state(false)
  let accountSheet = $state<{ account?: Account } | null>(null)
  let cardSheet = $state<{ card?: CardT } | null>(null)
</script>

<ScreenHeader title="Conti">
  <button class="btn btn-primary btn-small" onclick={() => (accountSheet = {})}>
    <Icon name="plus" size={18} /> Conto
  </button>
</ScreenHeader>

<Card>
  <div class="total">
    <span class="label">Patrimonio</span>
    <span class="num value" class:amount-neg={total < 0}>{formatEuro(total)}</span>
  </div>
</Card>

{#snippet accountRow(a: Account)}
  {@const b = accountBalance(a, data.value.transactions)}
  <li>
    <a class="list-row" href="#/conto/{a.id}">
      <span class="dot" style:background="var(--swatch-{a.color})"></span>
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

<h2 class="section-title">I tuoi conti</h2>
<Card>
  {#if !data.ready}
    <p class="empty-note">Caricamento…</p>
  {:else if active.length === 0}
    <p class="empty-note">Nessun conto. Inizia aggiungendo il tuo conto corrente, i contanti e i buoni pasto.</p>
  {:else}
    <ul class="list">
      {#each active as a (a.id)}
        {@render accountRow(a)}
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
  .total {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-2) 0;
  }

  .label {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-text-muted);
  }

  .value {
    font-size: var(--text-xl);
    font-weight: 650;
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
