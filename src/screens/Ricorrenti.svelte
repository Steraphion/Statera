<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import Icon from '../components/Icon.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import * as rec from '../lib/data/recurring'
  import { categoryLabel } from '../lib/data/transactions'
  import type { Recurring } from '../lib/data/types'
  import { formatEuro, formatShortDay } from '../lib/format'

  const refs = useRefs()
  const list = live(
    async () =>
      (await db.recurring.toArray())
        .filter((r) => r.deletedAt === null)
        .sort((a, b) => (rec.nextDate(a) ?? '9999').localeCompare(rec.nextDate(b) ?? '9999')),
    [] as Recurring[],
  )

  let sheet = $state<{ recurring?: Recurring } | null>(null)

  function title(r: Recurring): string {
    if (r.description) return r.description
    if (r.type === 'trasferimento') return 'Trasferimento'
    return categoryLabel(r.categoryId, refs.value.categoryMap)
  }

  function status(r: Recurring): string {
    if (r.paused) return 'Sospesa'
    const next = rec.nextDate(r)
    if (!next) return 'Conclusa'
    return `Prossima: ${formatShortDay(next)}${r.auto ? '' : ' · da confermare'}`
  }

  function color(r: Recurring): string {
    const c = r.categoryId ? refs.value.categoryMap.get(r.categoryId) : null
    const top = c?.parentId ? refs.value.categoryMap.get(c.parentId) : c
    return top ? `var(--swatch-${top.color})` : 'var(--color-text-muted)'
  }
</script>

<ScreenHeader title="Ricorrenti">
  <button class="btn btn-primary btn-small" onclick={() => (sheet = {})}>
    <Icon name="plus" size={18} /> Ripetizione
  </button>
</ScreenHeader>
<a class="back" href="#/altro">‹ Altro</a>

<p class="tip">
  Stipendio, affitto, abbonamenti, buoni pasto: Statera li registra da sola alla data prevista, oppure te li chiede se
  l'importo cambia ogni volta. Puoi anche creare una ripetizione da un nuovo movimento, scegliendo "Ripeti".
</p>

<Card>
  {#if list.ready && list.value.length === 0}
    <p class="empty-note">Nessun movimento ricorrente.</p>
  {:else}
    <ul class="list">
      {#each list.value as r (r.id)}
        {@const amount = rec.recurringTotal(r, refs.value.accountMap)}
        <li>
          <button class="list-row" class:paused={r.paused} onclick={() => (sheet = { recurring: r })}>
            {#if r.type === 'trasferimento'}
              <span class="icon"><Icon name="arrow-left-right" size={16} /></span>
            {:else}
              <span class="dot" style:background={color(r)}></span>
            {/if}
            <span class="main">
              <span class="name">{title(r)}</span>
              <span class="sub">{rec.describeFrequency(r)}</span>
              <span class="sub">{status(r)}</span>
            </span>
            <span
              class="num amount"
              class:income={r.type === 'entrata'}
              class:expense={r.type === 'uscita'}
            >
              {r.type === 'entrata' ? '+' : r.type === 'uscita' ? '−' : ''}{formatEuro(amount)}
            </span>
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</Card>

{#if sheet}
  <MovementForm
    recurring={sheet.recurring}
    defaultRepeat={sheet.recurring ? undefined : 'mensile'}
    accounts={refs.value.accounts}
    cards={refs.value.cards}
    categories={refs.value.categories}
    lastSources={refs.value.lastSources}
    onclose={() => (sheet = null)}
  />
{/if}

<style>
  .back {
    display: inline-block;
    margin: calc(-1 * var(--space-2)) 0 var(--space-3);
    font-size: var(--text-sm);
    text-decoration: none;
  }

  .tip {
    margin-bottom: var(--space-3);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .icon {
    flex: none;
    display: grid;
    place-items: center;
    width: 12px;
    color: var(--color-text-muted);
  }

  .main .sub {
    font-size: var(--text-xs);
  }

  .amount {
    font-weight: 600;
    white-space: nowrap;
  }

  .income {
    color: var(--color-income);
  }

  .expense {
    color: var(--color-expense);
  }

  .paused {
    opacity: 0.55;
  }
</style>
