<script lang="ts">
  import { niceTicks, type WorthPoint } from '../../lib/data/analytics'
  import { formatEuro, parseDay } from '../../lib/format'

  // Linea del patrimonio a fine mese. Una sola serie (il titolo della scheda la nomina, niente legenda),
  // dettaglio al passaggio o al tocco su ogni mese, tabella alternativa.
  let { points }: { points: WorthPoint[] } = $props()

  let width = $state(600)
  let active = $state<number | null>(null)
  let showTable = $state(false)

  const H = 180
  const PAD = { top: 12, right: 8, bottom: 24, left: 48 }
  const values = $derived(points.map((p) => p.value).filter((v): v is number => v !== null))
  const lo = $derived(Math.min(0, ...values))
  const hiTicks = $derived(niceTicks(Math.max(0, ...values)))
  const loTicks = $derived(lo < 0 ? niceTicks(-lo).map((t) => -t).filter((t) => t < 0) : [])
  const ticks = $derived([...loTicks.reverse(), ...hiTicks])
  const min = $derived(ticks[0])
  const max = $derived(ticks[ticks.length - 1] || 1)
  const plotW = $derived(Math.max(0, width - PAD.left - PAD.right))
  const plotH = H - PAD.top - PAD.bottom
  const step = $derived(points.length > 1 ? plotW / (points.length - 1) : 0)

  const x = (i: number) => PAD.left + step * i
  const y = (v: number) => PAD.top + plotH - ((v - min) / (max - min || 1)) * plotH

  const monthShort = new Intl.DateTimeFormat('it-IT', { month: 'short' })
  const monthLong = new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' })
  const label = (m: string) => monthShort.format(parseDay(`${m}-01`)).replace('.', '')
  const longLabel = (m: string) => monthLong.format(parseDay(`${m}-01`))
  function compact(cents: number): string {
    const v = cents / 100
    if (Math.abs(v) >= 1000) return `${(v / 1000).toLocaleString('it-IT', { maximumFractionDigits: 1 })}k`
    return v.toLocaleString('it-IT', { maximumFractionDigits: 0 })
  }

  /** Tratti continui (si interrompe dove il valore manca). */
  const path = $derived.by(() => {
    let d = ''
    let pen = false
    points.forEach((p, i) => {
      if (p.value === null) {
        pen = false
        return
      }
      d += `${pen ? 'L' : 'M'}${x(i)},${y(p.value)} `
      pen = true
    })
    return d
  })
  const tip = $derived(active !== null && points[active].value !== null ? points[active] : null)
  const prev = $derived(active !== null && active > 0 ? points[active - 1].value : null)
</script>

<div class="chart">
  <div class="head">
    <span class="note">A fine mese (il mese in corso: a oggi)</span>
    <button class="btn btn-ghost btn-small" onclick={() => (showTable = !showTable)}>
      {showTable ? 'Grafico' : 'Tabella'}
    </button>
  </div>
  {#if showTable}
    <table>
      <thead><tr><th>Mese</th><th>Patrimonio</th></tr></thead>
      <tbody>
        {#each [...points].reverse().filter((p) => p.value !== null) as p (p.month)}
          <tr><td>{longLabel(p.month)}</td><td class="num" class:amount-neg={(p.value ?? 0) < 0}>{formatEuro(p.value ?? 0)}</td></tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <div class="plot" bind:clientWidth={width}>
      <svg {width} height={H} role="img" aria-label="Patrimonio negli ultimi {points.length} mesi">
        {#each ticks as t (t)}
          <line class="grid" class:zero={t === 0} x1={PAD.left} x2={width - PAD.right} y1={y(t)} y2={y(t)} />
          <text class="tick" x={PAD.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{compact(t)}</text>
        {/each}
        <path class="line" d={path} />
        {#each points as p, i (p.month)}
          {#if p.value !== null}
            <circle class="dot" class:on={active === i} cx={x(i)} cy={y(p.value)} r={active === i ? 5 : 4} />
          {/if}
          {#if i % (points.length > 8 && width < 480 ? 2 : 1) === 0 || i === points.length - 1}
            <text class="tick" x={x(i)} y={H - 6} text-anchor="middle">{label(p.month)}</text>
          {/if}
          <rect
            class="hit"
            x={x(i) - step / 2}
            y={PAD.top}
            width={Math.max(step, 24)}
            height={plotH + PAD.bottom}
            role="button"
            tabindex="0"
            aria-label="{longLabel(p.month)}: {p.value === null ? 'nessun conto' : formatEuro(p.value)}"
            onpointerenter={() => (active = i)}
            onpointerleave={() => (active = null)}
            onfocus={() => (active = i)}
            onblur={() => (active = null)}
            onclick={() => (active = active === i ? null : i)}
            onkeydown={(e) => e.key === 'Escape' && (active = null)}
          />
        {/each}
        {#if tip && active !== null}
          <line class="cross" x1={x(active)} x2={x(active)} y1={PAD.top} y2={PAD.top + plotH} />
        {/if}
      </svg>
      {#if tip && active !== null}
        <div class="tooltip" class:left={x(active) > width / 2} style:left="{x(active)}px" role="status">
          <strong>{longLabel(tip.month)}</strong>
          <span><b class="num" class:amount-neg={(tip.value ?? 0) < 0}>{formatEuro(tip.value ?? 0)}</b></span>
          {#if prev !== null}
            {@const d = (tip.value ?? 0) - prev}
            <span>{d >= 0 ? '+' : '−'}{formatEuro(Math.abs(d))} sul mese prima</span>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2);
  }

  .note {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .plot {
    position: relative;
    width: 100%;
  }

  svg {
    display: block;
    overflow: visible;
  }

  .grid {
    stroke: var(--chart-grid);
    stroke-width: 1;
  }

  .grid.zero {
    stroke: var(--color-text-muted);
  }

  .tick {
    font-size: 11px;
    fill: var(--color-text-muted);
  }

  .line {
    fill: none;
    stroke: var(--chart-worth);
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
  }

  .dot {
    fill: var(--chart-worth);
    stroke: var(--color-surface);
    stroke-width: 2;
  }

  .hit {
    fill: transparent;
    cursor: pointer;
    outline: none;
  }

  .cross {
    stroke: var(--color-text-muted);
    stroke-width: 1;
  }

  .grid,
  .tick,
  .line,
  .dot,
  .cross {
    pointer-events: none;
  }

  .tooltip {
    position: absolute;
    top: 0;
    transform: translateX(12px);
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-2);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    pointer-events: none;
    white-space: nowrap;
    z-index: 2;
  }

  .tooltip.left {
    transform: translateX(calc(-100% - 12px));
  }

  .tooltip strong {
    color: var(--color-text);
    text-transform: capitalize;
  }

  .tooltip b {
    color: var(--color-text);
    font-weight: 700;
    font-size: var(--text-sm);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-sm);
  }

  th {
    text-align: right;
    font-weight: 600;
    color: var(--color-text-muted);
    padding: var(--space-1) 0;
  }

  th:first-child,
  td:first-child {
    text-align: left;
    text-transform: capitalize;
  }

  td {
    text-align: right;
    padding: var(--space-1) 0;
    border-top: 1px solid var(--color-border);
  }
</style>
