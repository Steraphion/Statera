<script lang="ts">
  import Card from './Card.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { monthRecap } from '../lib/data/analytics'
  import { setRecapSeen } from '../lib/data/repo'
  import type { Category, Transaction } from '../lib/data/types'
  import { today } from '../lib/data/util'
  import { formatEuro, formatMonth, monthOf, parseDay, shiftMonth } from '../lib/format'
  import { ui } from '../lib/ui.svelte'

  /** Nei primi 7 giorni del mese: com'è andato il mese precedente. Si chiude una volta per mese. */
  let { categories }: { categories: Category[] } = $props()

  const now = today()
  const prev = shiftMonth(monthOf(now), -1)
  const early = Number(now.slice(8, 10)) <= 7

  const data = live(
    async () => {
      if (!early) return { seen: true, rows: [] as Transaction[] }
      const seen = (await db.meta.get('riepilogoVisto'))?.value === prev
      const rows = seen ? [] : await db.transactions.where('date').between(`${shiftMonth(prev, -1)}-01`, `${prev}-31`, true, true).toArray()
      return { seen, rows }
    },
    { seen: true, rows: [] as Transaction[] },
  )
  const recap = $derived(data.value.seen ? null : monthRecap(data.value.rows, prev, categories))
  const name = formatMonth(parseDay(`${prev}-01`)).split(' ')[0]
  const before = formatMonth(parseDay(`${shiftMonth(prev, -1)}-01`)).split(' ')[0].toLowerCase()

  function open() {
    ui.analysis.kind = 'mese'
    ui.analysis.month = prev
    void setRecapSeen(prev)
    location.hash = '/analisi'
  }
</script>

{#if recap && recap.count > 0}
  <Card>
    <section class="recap" aria-labelledby="recap-title">
      <h2 id="recap-title">{name} in breve</h2>
      <dl>
        <div><dt>Entrate</dt><dd class="num">{formatEuro(recap.income)}</dd></div>
        <div><dt>Uscite</dt><dd class="num">{formatEuro(recap.expense)}</dd></div>
        <div><dt>Risparmio</dt><dd class="num" class:amount-neg={recap.net < 0}>{formatEuro(recap.net)}</dd></div>
      </dl>
      <ul>
        {#if recap.previousExpense > 0}
          {@const d = recap.expense - recap.previousExpense}
          <li>
            {#if d === 0}Uscite uguali a {before}.{:else}Uscite <strong class="num">{d > 0 ? '+' : '−'}{formatEuro(Math.abs(d))}</strong> rispetto a {before}.{/if}
          </li>
        {/if}
        {#if recap.top}
          <li>La spesa più grande è stata <strong>{recap.top.category.name}</strong> ({formatEuro(recap.top.total)}).</li>
        {/if}
      </ul>
      <div class="actions">
        <button class="btn btn-ghost btn-small" onclick={() => setRecapSeen(prev)}>Chiudi</button>
        <button class="btn btn-small" onclick={open}>Vedi l'analisi</button>
      </div>
    </section>
  </Card>
{/if}

<style>
  h2 {
    font-size: var(--text-lg);
    margin-bottom: var(--space-3);
  }

  dl {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--space-2);
    margin: 0 0 var(--space-3);
  }

  dt {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  dd {
    margin: 0;
    font-weight: 650;
  }

  ul {
    margin: 0 0 var(--space-3);
    padding-left: var(--space-4);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  ul strong {
    color: var(--color-text);
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2);
  }
</style>
