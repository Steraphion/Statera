<script lang="ts">
  import { liveQuery } from 'dexie'
  import Card from '../components/Card.svelte'
  import Icon from '../components/Icon.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import MovementRow from '../components/MovementRow.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Transaction } from '../lib/data/types'
  import { today } from '../lib/data/util'
  import { formatDay, formatEuro, formatMonth, monthOf, parseDay, shiftMonth } from '../lib/format'
  import { ui } from '../lib/ui.svelte'

  const refs = useRefs()

  // La lettura dipende dal mese scelto: cambiando mese si riparte da capo
  let rows = $state<Transaction[]>([])
  let loaded = $state(false)
  $effect(() => {
    const month = ui.month
    loaded = false
    const sub = liveQuery(() => mv.movementsOfMonth(month)).subscribe({
      next: (v) => {
        rows = v
        loaded = true
      },
      error: (e) => console.error('Errore di lettura movimenti', e),
    })
    return () => sub.unsubscribe()
  })

  const totals = $derived(mv.totals(rows))
  const days = $derived(mv.groupByDay(rows))
  const isCurrentMonth = $derived(ui.month === monthOf(today()))
  const noAccounts = $derived(refs.ready && refs.value.accounts.length === 0)

  let sheet = $state<{ movement?: Transaction } | null>(null)

</script>

<header class="month">
  <button class="btn btn-ghost nav" aria-label="Mese precedente" onclick={() => (ui.month = shiftMonth(ui.month, -1))}>
    <Icon name="left" />
  </button>
  <h1>{formatMonth(parseDay(`${ui.month}-01`))}</h1>
  <button class="btn btn-ghost nav" aria-label="Mese successivo" onclick={() => (ui.month = shiftMonth(ui.month, 1))}>
    <Icon name="right" />
  </button>
  <span class="spacer"></span>
  {#if !isCurrentMonth}
    <button class="btn btn-small" onclick={() => (ui.month = monthOf(today()))}>Oggi</button>
  {/if}
  <a class="btn btn-ghost nav" href="#/cerca" aria-label="Cerca">
    <Icon name="search" />
  </a>
  <button class="btn btn-primary btn-small desktop-add" onclick={() => (sheet = {})}>
    <Icon name="plus" size={18} /> Movimento
  </button>
</header>

<Card>
  <div class="totals">
    <div>
      <span class="label">Entrate</span>
      <span class="num income">{formatEuro(totals.income)}</span>
    </div>
    <div>
      <span class="label">Uscite</span>
      <span class="num expense">{formatEuro(totals.expense)}</span>
    </div>
    <div>
      <span class="label">Saldo</span>
      <span class="num" class:amount-neg={totals.net < 0}>{formatEuro(totals.net)}</span>
    </div>
  </div>
</Card>

{#if noAccounts}
  <Card>
    <div class="empty">
      <p class="title">Benvenuto in Statera</p>
      <p class="hint">Per iniziare crea i tuoi conti: conto corrente, contanti, buoni pasto.</p>
      <a class="btn btn-primary" href="#/conti">Vai ai conti</a>
    </div>
  </Card>
{:else if loaded && rows.length === 0}
  <Card>
    <div class="empty">
      <p class="title">Nessun movimento in questo mese</p>
      <p class="hint">Tocca + per registrare una spesa o un'entrata.</p>
    </div>
  </Card>
{:else}
  {#each days as g (g.date)}
    <h2 class="day">
      <span>{formatDay(g.date)}</span>
      <span class="num" class:amount-neg={g.net < 0}>{g.net === 0 ? '' : formatEuro(g.net)}</span>
    </h2>
    <Card>
      <ul class="list">
        {#each g.items as t (t.id)}
          <li><MovementRow {t} refs={refs.value} onclick={() => (sheet = { movement: t })} /></li>
        {/each}
      </ul>
    </Card>
  {/each}
{/if}

{#if !noAccounts}
  <div class="fab-space" aria-hidden="true"></div>
  <button class="fab" aria-label="Nuovo movimento" onclick={() => (sheet = {})}>
    <Icon name="plus" size={28} />
  </button>
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
  .month {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-bottom: var(--space-4);
  }

  .month h1 {
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

  .totals {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-3);
    text-align: center;
  }

  .totals div {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .label {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-text-muted);
  }

  .totals .num {
    font-weight: 600;
  }

  .income {
    color: var(--color-income);
  }

  .expense {
    color: var(--color-expense);
  }

  .day {
    display: flex;
    justify-content: space-between;
    margin: var(--space-5) 0 var(--space-2);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-text-muted);
  }

  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    text-align: center;
    padding: var(--space-5) 0;
  }

  .title {
    font-weight: 600;
  }

  .hint {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .fab {
    position: fixed;
    right: var(--space-4);
    bottom: calc(var(--nav-height) + var(--space-4) + env(safe-area-inset-bottom));
    z-index: 11;
    display: grid;
    place-items: center;
    width: 60px;
    height: 60px;
    border: none;
    border-radius: 50%;
    background: var(--color-primary);
    color: var(--color-on-primary);
    box-shadow: var(--shadow-2);
    cursor: pointer;
  }

  .fab-space {
    height: 72px;
  }

  .desktop-add {
    display: none;
  }

  @media (min-width: 900px) {
    .fab,
    .fab-space {
      display: none;
    }

    .desktop-add {
      display: inline-flex;
    }
  }
</style>
