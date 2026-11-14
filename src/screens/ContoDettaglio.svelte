<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import AccountForm from '../components/AccountForm.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import AlignSheet from '../components/AlignSheet.svelte'
  import MovementRow from '../components/MovementRow.svelte'
  import Icon from '../components/Icon.svelte'
  import CategoryIcon from '../components/CategoryIcon.svelte'
  import { ACCOUNT_ICONS } from '../lib/categoryIcon'
  import { db } from '../lib/data/db'
  import { router } from '../lib/router.svelte'
  import { live } from '../lib/data/live.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import { accountBalance, accountLedger, cardsOf } from '../lib/data/balances'
  import { ACCOUNT_TYPE_LABELS, type Transaction } from '../lib/data/types'
  import { formatEuro, formatMonth, formatShortDay, formatVouchers, parseDay } from '../lib/format'

  let { id }: { id: string } = $props()

  const refs = useRefs()
  const txs = live(() => db.transactions.toArray(), [] as Transaction[])

  const account = $derived(refs.value.accountMap.get(id))
  const balance = $derived(account ? accountBalance(account, txs.value) : null)
  const ledger = $derived(account ? accountLedger(account, txs.value) : [])
  const cards = $derived(account ? cardsOf(account, refs.value.cards) : [])

  /** Estratto conto diviso per mese. */
  const months = $derived.by(() => {
    const groups: { month: string; entries: typeof ledger }[] = []
    for (const e of ledger) {
      const m = e.t.date.slice(0, 7)
      let g = groups[groups.length - 1]
      if (!g || g.month !== m) groups.push((g = { month: m, entries: [] }))
      g.entries.push(e)
    }
    return groups
  })

  // Conto eliminato (o indirizzo sbagliato): si torna all'elenco
  $effect(() => {
    if (refs.ready && !account) router.go('conti')
  })

  let editAccount = $state(false)
  let aligning = $state(false)
  let movementSheet = $state<{ movement?: Transaction } | null>(null)
</script>

{#if account && balance}
  <ScreenHeader title={account.name} back={{ href: '#/conti', label: 'Conti' }}>
    <button class="btn btn-small" onclick={() => (editAccount = true)}>Modifica</button>
  </ScreenHeader>

  <section class="summary" aria-label="Saldo del conto">
      <CategoryIcon icon={ACCOUNT_ICONS[account.type]} color={account.color} size="l" />
      <span class="type">{ACCOUNT_TYPE_LABELS[account.type]}{account.archived ? ' · archiviato' : ''}</span>
      <span class="num value" class:amount-neg={balance.amount < 0}>{formatEuro(balance.amount)}</span>
      {#if balance.vouchers !== null}
        <span class="sub">{formatVouchers(balance.vouchers)} da {formatEuro(account.voucherValue ?? 0)}</span>
      {/if}
      {#if cards.length > 0}
        <span class="sub">Carte: {cards.map((c) => c.name).join(', ')}</span>
      {/if}
      {#if !account.archived}
        <button class="btn btn-soft btn-small align" onclick={() => (aligning = true)}>
          <Icon name="scale" size={16} /> Allinea al saldo reale
        </button>
      {/if}
  </section>

  {#each months as g (g.month)}
    <h2 class="section-title">{formatMonth(parseDay(`${g.month}-01`))}</h2>
    <Card>
      <ul class="list">
        {#each g.entries as e (e.t.id)}
          <li>
            <MovementRow
              t={e.t}
              refs={refs.value}
              effect={e.effect}
              balanceAfter={e.balanceAfter}
              muted={!e.counted}
              showDate
              onclick={() => (movementSheet = { movement: e.t })}
            />
          </li>
        {/each}
      </ul>
    </Card>
  {/each}

  <h2 class="section-title">Inizio</h2>
  <Card>
    <div class="start">
      <span class="main">
        <span class="name">Saldo iniziale</span>
        <span class="sub">al {formatShortDay(account.initialDate)}</span>
      </span>
      <span class="num">{formatEuro(account.initialBalance)}</span>
    </div>
  </Card>
  {#if ledger.some((e) => !e.counted)}
    <p class="note">
      I movimenti segnati "non incide" hanno una data precedente al saldo iniziale: compaiono nei totali del mese ma
      non cambiano il saldo, perché sono già compresi nel saldo iniziale.
    </p>
  {/if}

  <div class="fab-space" aria-hidden="true"></div>
  <button class="fab" data-no-autoauth aria-label="Nuovo movimento" onclick={() => (movementSheet = {})}>
    <Icon name="plus" size={28} />
  </button>

  {#if aligning}
    <AlignSheet {account} transactions={txs.value} onclose={() => (aligning = false)} />
  {/if}

  {#if editAccount}
    <AccountForm account={account} onclose={() => (editAccount = false)} />
  {/if}

  {#if movementSheet}
    <MovementForm
      movement={movementSheet.movement}
      accounts={refs.value.accounts}
      cards={refs.value.cards}
      categories={refs.value.categories}
      lastSources={movementSheet.movement ? refs.value.lastSources : { uscita: `a:${account.id}`, entrata: `a:${account.id}`, trasferimento: `a:${account.id}` }}
      onclose={() => (movementSheet = null)}
    />
  {/if}
{/if}

<style>
  .align {
    margin-top: var(--space-3);
  }


  /* Saldo grande al centro (stile Vivace) */
  .summary {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    padding: 0 0 var(--space-2);
    text-align: center;
  }

  .type {
    margin-top: var(--space-2);
    font-size: var(--text-md);
    font-weight: 500;
    color: var(--color-text-muted);
  }

  .value {
    font-size: var(--amount-m);
    font-weight: 800;
    letter-spacing: var(--tracking-tighter);
    line-height: 1.15;
  }

  .sub {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .start {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .start .main {
    display: flex;
    flex-direction: column;
  }

  .start .name {
    font-weight: 600;
  }

  .note {
    margin-top: var(--space-3);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .fab-space {
    height: 80px;
  }

  /* Qui non c'è la barra in basso: il + del conto sta nell'angolo */
  .fab {
    position: fixed;
    right: var(--space-5);
    bottom: calc(var(--space-5) + env(safe-area-inset-bottom));
    z-index: 11;
    display: grid;
    place-items: center;
    width: var(--size-fab);
    height: var(--size-fab);
    border: none;
    border-radius: var(--radius-full);
    background: var(--color-primary);
    color: var(--color-on-primary);
    box-shadow: var(--shadow-fab);
    cursor: pointer;
  }

  @media (min-width: 900px) {
    .fab {
      right: var(--space-6);
      bottom: var(--space-6);
    }
  }
</style>
