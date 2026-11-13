<script lang="ts">
  import { liveQuery } from 'dexie'
  import Card from '../components/Card.svelte'
  import Icon from '../components/Icon.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Account, Card as CardT, Category, Transaction, TransactionType } from '../lib/data/types'
  import { alive, byOrder, today } from '../lib/data/util'
  import { formatDay, formatEuro, formatMonth, formatVouchers, monthOf, parseDay, shiftMonth } from '../lib/format'
  import { ui } from '../lib/ui.svelte'

  const refs = live(
    async () => {
      const [accounts, cards, categories, lastSources] = await Promise.all([
        db.accounts.toArray(),
        db.cards.toArray(),
        db.categories.toArray(),
        mv.lastSources(),
      ])
      return {
        accounts: alive(accounts).sort(byOrder),
        cards: alive(cards).sort(byOrder),
        categories: alive(categories).sort(byOrder),
        lastSources,
      }
    },
    {
      accounts: [] as Account[],
      cards: [] as CardT[],
      categories: [] as Category[],
      lastSources: {} as Partial<Record<TransactionType, string>>,
    },
  )

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
  const accountMap = $derived(new Map(refs.value.accounts.map((a) => [a.id, a])))
  const cardMap = $derived(new Map(refs.value.cards.map((c) => [c.id, c])))
  const categoryMap = $derived(new Map(refs.value.categories.map((c) => [c.id, c])))
  const isCurrentMonth = $derived(ui.month === monthOf(today()))
  const noAccounts = $derived(refs.ready && refs.value.accounts.length === 0)

  let sheet = $state<{ movement?: Transaction } | null>(null)

  function title(t: Transaction): string {
    if (t.description) return t.description
    if (t.type === 'trasferimento') return 'Trasferimento'
    return mv.categoryLabel(t.categoryId, categoryMap)
  }

  function subtitle(t: Transaction): string {
    const from = t.parts.map((p) => mv.partLabel(p, accountMap, cardMap)).join(' + ')
    if (t.type === 'trasferimento') return `${from} → ${accountMap.get(t.toAccountId ?? '')?.name ?? '—'}`
    const cat = t.description ? mv.categoryLabel(t.categoryId, categoryMap) : ''
    return cat ? `${cat} · ${from}` : from
  }

  function vouchersOf(t: Transaction): number | null {
    const n = t.parts.reduce((s, p) => s + (p.vouchers ?? 0), 0)
    return n > 0 ? n : null
  }

  function colorOf(t: Transaction): string {
    const c = t.categoryId ? categoryMap.get(t.categoryId) : null
    const top = c?.parentId ? categoryMap.get(c.parentId) : c
    return top ? `var(--swatch-${top.color})` : 'var(--color-text-muted)'
  }
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
          {@const v = vouchersOf(t)}
          <li>
            <button class="list-row" onclick={() => (sheet = { movement: t })}>
              {#if t.type === 'trasferimento'}
                <span class="icon"><Icon name="transfer" size={16} /></span>
              {:else}
                <span class="dot" style:background={colorOf(t)}></span>
              {/if}
              <span class="main">
                <span class="name">{title(t)}</span>
                <span class="sub">{subtitle(t)}</span>
              </span>
              <span class="end">
                <span
                  class="num amount"
                  class:income={t.type === 'entrata'}
                  class:expense={t.type === 'uscita'}
                >
                  {t.type === 'entrata' ? '+' : t.type === 'uscita' ? '−' : ''}{formatEuro(mv.total(t))}
                </span>
                {#if v}<span class="sub small">{formatVouchers(v)}</span>{/if}
              </span>
            </button>
          </li>
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

  .icon {
    flex: none;
    display: grid;
    place-items: center;
    width: 12px;
    color: var(--color-text-muted);
  }

  .end {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .amount {
    font-weight: 600;
  }

  .small {
    font-size: var(--text-xs);
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
