<script lang="ts">
  import { total } from '../lib/data/transactions'
  import type { Transaction } from '../lib/data/types'
  import { formatDay, formatEuro } from '../lib/format'

  /**
   * Calendario del mese: per ogni giorno le uscite (tinta più intensa = giorno più caro, una sola tinta)
   * e un "+" se ci sono entrate. Toccando un giorno se ne vedono i movimenti.
   */
  let { month, rows, selected = $bindable() }: { month: string; rows: Transaction[]; selected: string } = $props()

  const WEEK = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']

  const cells = $derived.by(() => {
    const [y, m] = month.split('-').map(Number)
    const days = new Date(y, m, 0).getDate()
    const lead = (new Date(y, m - 1, 1).getDay() + 6) % 7
    const sums = new Map<string, { out: number; in: number }>()
    for (const t of rows) {
      if (t.deletedAt !== null || t.type === 'trasferimento') continue
      const s = sums.get(t.date) ?? { out: 0, in: 0 }
      if (t.type === 'uscita') s.out += total(t)
      else s.in += total(t)
      sums.set(t.date, s)
    }
    const max = Math.max(0, ...[...sums.values()].map((s) => s.out))
    const out: ({ date: string; day: number; out: number; in: number; level: number } | null)[] = Array(lead).fill(null)
    for (let d = 1; d <= days; d++) {
      const date = `${month}-${String(d).padStart(2, '0')}`
      const s = sums.get(date) ?? { out: 0, in: 0 }
      const level = s.out && max ? Math.min(4, Math.ceil((s.out / max) * 4)) : 0
      out.push({ date, day: d, ...s, level })
    }
    return out
  })

  function compact(cents: number): string {
    const v = cents / 100
    if (v >= 1000) return `${(v / 1000).toLocaleString('it-IT', { maximumFractionDigits: 1 })}k`
    return Math.round(v).toLocaleString('it-IT')
  }
</script>

<div class="cal" role="grid" aria-label="Calendario del mese">
  <div class="week" role="row">
    {#each WEEK as w (w)}<span role="columnheader">{w}</span>{/each}
  </div>
  <div class="grid" role="row">
    {#each cells as c, i (c?.date ?? `vuoto-${i}`)}
      {#if c}
        <button
          role="gridcell"
          class="day l{c.level}"
          class:sel={c.date === selected}
          aria-selected={c.date === selected}
          aria-label="{formatDay(c.date)}: uscite {formatEuro(c.out)}{c.in ? `, entrate ${formatEuro(c.in)}` : ''}"
          onclick={() => (selected = c.date)}
        >
          <span class="n">{c.day}</span>
          {#if c.out}<span class="out num">{compact(c.out)}</span>{/if}
          {#if c.in}<span class="in" aria-hidden="true">+</span>{/if}
        </button>
      {:else}
        <span class="blank" aria-hidden="true"></span>
      {/if}
    {/each}
  </div>
  <p class="legend">Numeri: uscite del giorno in euro · tinta più scura = giorno più caro · + = entrate</p>
</div>

<style>
  .week,
  .grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: var(--space-1);
  }

  .week span {
    text-align: center;
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    padding-bottom: var(--space-1);
  }

  .day {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    gap: var(--space-hair);
    min-height: var(--size-field);
    padding: var(--space-1) var(--space-hair);
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    color: var(--color-text);
    font: inherit;
    cursor: pointer;
  }

  /* Una sola tinta, dalla più chiara alla più scura */
  .day.l1 {
    background: color-mix(in srgb, var(--chart-expense) 14%, var(--color-surface));
  }
  .day.l2 {
    background: color-mix(in srgb, var(--chart-expense) 28%, var(--color-surface));
  }
  .day.l3 {
    background: color-mix(in srgb, var(--chart-expense) 44%, var(--color-surface));
  }
  .day.l4 {
    background: color-mix(in srgb, var(--chart-expense) 62%, var(--color-surface));
  }

  .day.sel {
    border-color: var(--color-text);
    box-shadow: inset 0 0 0 1px var(--color-text);
  }

  .n {
    font-size: var(--text-xs);
    font-weight: 600;
  }

  .out {
    font-size: var(--text-xs);
  }

  .in {
    position: absolute;
    top: var(--space-hair);
    right: var(--space-1);
    font-size: var(--text-xs);
    font-weight: 700;
    color: var(--color-income);
  }

  .legend {
    margin-top: var(--space-2);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
