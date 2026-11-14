<script lang="ts">
  import { niceTicks, type MonthPoint } from '../../lib/data/analytics'
  import { formatEuro, parseDay } from '../../lib/format'

  // Colonne affiancate entrate/uscite per mese. Un solo asse, legenda sempre presente,
  // dettaglio al passaggio o al tocco su ogni mese, e tabella alternativa.
  let { points, highlight }: { points: MonthPoint[]; highlight: string } = $props()

  let width = $state(600)
  let active = $state<number | null>(null)
  let showTable = $state(false)

  const H = 200
  const PAD = { top: 8, right: 4, bottom: 24, left: 44 }
  const ticks = $derived(niceTicks(Math.max(...points.map((p) => Math.max(p.income, p.expense)), 0)))
  const top = $derived(ticks[ticks.length - 1] || 1)
  const plotW = $derived(Math.max(0, width - PAD.left - PAD.right))
  const plotH = H - PAD.top - PAD.bottom
  const band = $derived(plotW / points.length)
  const barW = $derived(Math.max(3, Math.min(12, (band - 6) / 2)))

  const y = (v: number) => PAD.top + plotH - (v / top) * plotH
  const monthShort = new Intl.DateTimeFormat('it-IT', { month: 'short' })
  const monthLong = new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' })
  const label = (m: string) => monthShort.format(parseDay(`${m}-01`)).replace('.', '')
  const longLabel = (m: string) => monthLong.format(parseDay(`${m}-01`))

  function compact(cents: number): string {
    const v = cents / 100
    if (v >= 1000) return `${(v / 1000).toLocaleString('it-IT', { maximumFractionDigits: 1 })}k`
    return v.toLocaleString('it-IT', { maximumFractionDigits: 0 })
  }

  /** Colonna con estremo superiore arrotondato (4px) e base dritta. */
  function column(x: number, v: number): string {
    const h = Math.max(0, (v / top) * plotH)
    if (h === 0) return ''
    const r = Math.min(4, h, barW / 2)
    const yt = PAD.top + plotH - h
    const yb = PAD.top + plotH
    return `M${x},${yb} V${yt + r} Q${x},${yt} ${x + r},${yt} H${x + barW - r} Q${x + barW},${yt} ${x + barW},${yt + r} V${yb} Z`
  }

  const tip = $derived(active !== null ? points[active] : null)
  const tipX = $derived(active !== null ? PAD.left + band * active + band / 2 : 0)
</script>

<div class="chart">
  <div class="head">
    <div class="legend" aria-hidden="true">
      <span><i style:background="var(--chart-income)"></i>Entrate</span>
      <span><i style:background="var(--chart-expense)"></i>Uscite</span>
    </div>
    <button class="btn btn-ghost btn-small" onclick={() => (showTable = !showTable)}>
      {showTable ? 'Grafico' : 'Tabella'}
    </button>
  </div>

  {#if showTable}
    <table>
      <thead><tr><th>Mese</th><th>Entrate</th><th>Uscite</th><th>Saldo</th></tr></thead>
      <tbody>
        {#each [...points].reverse() as p (p.month)}
          <tr class:hl={p.month === highlight}>
            <td>{longLabel(p.month)}</td>
            <td class="num">{formatEuro(p.income)}</td>
            <td class="num">{formatEuro(p.expense)}</td>
            <td class="num" class:amount-neg={p.net < 0}>{formatEuro(p.net)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <div class="plot" bind:clientWidth={width}>
      <svg {width} height={H} role="img" aria-label="Entrate e uscite degli ultimi {points.length} mesi">
        {#each ticks as t (t)}
          <line class="grid" x1={PAD.left} x2={width - PAD.right} y1={y(t)} y2={y(t)} />
          <text class="tick" x={PAD.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{compact(t)}</text>
        {/each}
        {#each points as p, i (p.month)}
          {@const x0 = PAD.left + band * i + (band - (barW * 2 + 2)) / 2}
          <g class:dim={active !== null && active !== i}>
            <path d={column(x0, p.income)} fill="var(--chart-income)" />
            <path d={column(x0 + barW + 2, p.expense)} fill="var(--chart-expense)" />
          </g>
          <text
            class="tick"
            class:strong={p.month === highlight}
            x={PAD.left + band * i + band / 2}
            y={H - 6}
            text-anchor="middle">{label(p.month)}</text
          >
          <!-- area sensibile: tutta la colonna del mese, più grande delle barre -->
          <rect
            class="hit"
            x={PAD.left + band * i}
            y={PAD.top}
            width={band}
            height={plotH + PAD.bottom}
            role="button"
            tabindex="0"
            aria-label="{longLabel(p.month)}: entrate {formatEuro(p.income)}, uscite {formatEuro(p.expense)}"
            onpointerenter={() => (active = i)}
            onpointerleave={() => (active = null)}
            onfocus={() => (active = i)}
            onblur={() => (active = null)}
            onclick={() => (active = active === i ? null : i)}
            onkeydown={(e) => e.key === 'Escape' && (active = null)}
          />
        {/each}
        {#if active !== null}
          <line class="cross" x1={tipX} x2={tipX} y1={PAD.top} y2={PAD.top + plotH} />
        {/if}
      </svg>
      {#if tip}
        <div class="tooltip" class:left={tipX > width / 2} style:left="{tipX}px" role="status">
          <strong>{longLabel(tip.month)}</strong>
          <span><i style:background="var(--chart-income)"></i><b class="num">{formatEuro(tip.income)}</b> entrate</span>
          <span><i style:background="var(--chart-expense)"></i><b class="num">{formatEuro(tip.expense)}</b> uscite</span>
          <span class="net"><b class="num" class:amount-neg={tip.net < 0}>{formatEuro(tip.net)}</b> saldo</span>
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

  .legend {
    display: flex;
    gap: var(--space-4);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .legend span,
  .tooltip span {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
  }

  .legend i {
    width: 10px;
    height: 10px;
    border-radius: var(--radius-2xs);
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

  .tick {
    font-size: var(--text-2xs);
    fill: var(--color-text-muted);
  }

  .tick.strong {
    fill: var(--color-text);
    font-weight: 700;
  }

  .dim {
    opacity: 0.45;
  }


  .hit {
    fill: transparent;
    cursor: pointer;
    outline: none;
  }

  .cross {
    stroke: var(--color-text-muted);
    stroke-width: 1;
    pointer-events: none;
  }

  .dim,
  .tick,
  .grid {
    pointer-events: none;
  }

  .tooltip {
    position: absolute;
    top: 0;
    transform: translateX(12px);
    display: flex;
    flex-direction: column;
    gap: var(--space-hair);
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
  }

  .tooltip i {
    width: 10px;
    height: var(--space-hair);
  }

  .tooltip .net {
    margin-top: var(--space-hair);
    padding-left: var(--space-4);
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
  }

  td {
    text-align: right;
    padding: var(--space-1) 0;
    border-top: 1px solid var(--color-border);
  }

  td:first-child {
    text-transform: capitalize;
  }

  tr.hl td {
    font-weight: 700;
  }
</style>
