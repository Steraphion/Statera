<script lang="ts">
  // Pannello dell'app al posto di quello del telefono per elenchi a tendina e date (src/lib/picker.svelte.ts).
  // Riusa Sheet: stesso aspetto, colori della palette e movimento degli altri pannelli.
  import Sheet from './Sheet.svelte'
  import Icon from './Icon.svelte'
  import { picker } from '../lib/picker.svelte'
  import { today } from '../lib/data/util'
  import {
    addMonths,
    inRange,
    longDate,
    monthCells,
    monthInRange,
    monthLabel,
    MONTHS,
    WEEKDAYS,
    ymOf,
    type YM,
  } from '../lib/calendar'

  // Il campo resta lo stesso finché il pannello è aperto
  const el = picker.field!
  const current = el.value

  // --- Elenco a tendina
  interface Opt {
    value: string
    label: string
    disabled: boolean
  }
  interface Group {
    label: string | null
    options: Opt[]
  }

  function opt(o: HTMLOptionElement): Opt {
    return { value: o.value, label: o.label || o.text, disabled: o.disabled }
  }

  function groupsOf(s: HTMLSelectElement): Group[] {
    const out: Group[] = []
    let loose: Group | null = null
    for (const child of Array.from(s.children)) {
      if (child instanceof HTMLOptGroupElement) {
        loose = null
        const options = Array.from(child.children)
          .filter((o): o is HTMLOptionElement => o instanceof HTMLOptionElement && !o.hidden)
          .map(opt)
        if (options.length) out.push({ label: child.label, options })
      } else if (child instanceof HTMLOptionElement && !child.hidden) {
        if (!loose) out.push((loose = { label: null, options: [] }))
        loose.options.push(opt(child))
      }
    }
    return out
  }

  const isSelect = el instanceof HTMLSelectElement
  const groups = el instanceof HTMLSelectElement ? groupsOf(el) : []
  let selectedRow = $state<HTMLButtonElement>()
  $effect(() => {
    selectedRow?.scrollIntoView({ block: 'center' })
  })

  // --- Data
  const min = !isSelect ? (el as HTMLInputElement).min || null : null
  const max = !isSelect ? (el as HTMLInputElement).max || null : null
  const todayIso = today()
  let view = $state<YM>(ymOf(current) ?? ymOf(todayIso)!)
  let mode = $state<'days' | 'months'>('days')
  const yearHasMonths = (year: number) =>
    Array.from({ length: 12 }, (_, m) => monthInRange({ year, month: m }, min, max)).some(Boolean)
</script>

{#snippet dateFooter()}
  {#if !el.required && current}
    <button type="button" class="btn btn-ghost" onclick={() => picker.choose('')}>Cancella</button>
  {/if}
  <button type="button" class="btn btn-soft" disabled={!inRange(todayIso, min, max)} onclick={() => picker.choose(todayIso)}
    >Oggi</button
  >
{/snippet}

<Sheet title={picker.title} onclose={() => picker.close()} footer={isSelect ? undefined : dateFooter} noAutoauth>
  {#if isSelect}
    <div class="options" role="radiogroup" aria-label={picker.title}>
      {#each groups as g, gi (gi)}
        {#if g.label}<p class="group">{g.label}</p>{/if}
        {#each g.options as o (o.value)}
          {#if o.value === current}
            <button
              type="button"
              role="radio"
              class="row on"
              aria-checked="true"
              disabled={o.disabled}
              bind:this={selectedRow}
              onclick={() => picker.choose(o.value)}
            >
              <span class="label">{o.label}</span>
              <Icon name="check" size={20} stroke={2.6} />
            </button>
          {:else}
            <button
              type="button"
              role="radio"
              class="row"
              aria-checked="false"
              disabled={o.disabled}
              onclick={() => picker.choose(o.value)}
            >
              <span class="label">{o.label}</span>
            </button>
          {/if}
        {/each}
      {/each}
    </div>
  {:else}
    <div class="cal">
      <div class="cal-head">
        <button
          type="button"
          class="title"
          aria-expanded={mode === 'months'}
          onclick={() => (mode = mode === 'days' ? 'months' : 'days')}
        >
          {mode === 'days' ? monthLabel(view) : view.year}
          <span class="chev" class:up={mode === 'months'}><Icon name="chevron-down" size={18} /></span>
        </button>
        <span class="nav">
          {#if mode === 'days'}
            <button
              type="button"
              class="nav-btn"
              aria-label="Mese precedente"
              disabled={!monthInRange(addMonths(view, -1), min, max)}
              onclick={() => (view = addMonths(view, -1))}><Icon name="chevron-left" size={22} /></button
            >
            <button
              type="button"
              class="nav-btn"
              aria-label="Mese successivo"
              disabled={!monthInRange(addMonths(view, 1), min, max)}
              onclick={() => (view = addMonths(view, 1))}><Icon name="chevron-right" size={22} /></button
            >
          {:else}
            <button
              type="button"
              class="nav-btn"
              aria-label="Anno precedente"
              disabled={!yearHasMonths(view.year - 1)}
              onclick={() => (view = { ...view, year: view.year - 1 })}><Icon name="chevron-left" size={22} /></button
            >
            <button
              type="button"
              class="nav-btn"
              aria-label="Anno successivo"
              disabled={!yearHasMonths(view.year + 1)}
              onclick={() => (view = { ...view, year: view.year + 1 })}><Icon name="chevron-right" size={22} /></button
            >
          {/if}
        </span>
      </div>

      {#if mode === 'days'}
        <div class="days" role="group" aria-label={monthLabel(view)}>
          {#each WEEKDAYS as w, i (i)}
            <span class="wd" aria-hidden="true">{w}</span>
          {/each}
          {#each monthCells(view) as d, i (d ?? `vuoto-${i}`)}
            {#if d}
              <button
                type="button"
                class="day num"
                class:sel={d === current}
                class:today={d === todayIso}
                aria-pressed={d === current}
                aria-current={d === todayIso ? 'date' : undefined}
                aria-label={longDate(d)}
                disabled={!inRange(d, min, max)}
                onclick={() => picker.choose(d)}>{Number(d.slice(8))}</button
              >
            {:else}
              <span aria-hidden="true"></span>
            {/if}
          {/each}
        </div>
      {:else}
        <div class="months" role="group" aria-label="Mesi del {view.year}">
          {#each MONTHS as name, m (m)}
            {@const ym = { year: view.year, month: m }}
            <button
              type="button"
              class="month"
              class:sel={ymOf(current)?.year === view.year && ymOf(current)?.month === m}
              aria-label="{name} {view.year}"
              disabled={!monthInRange(ym, min, max)}
              onclick={() => {
                view = ym
                mode = 'days'
              }}>{name.slice(0, 3)}</button
            >
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</Sheet>

<style>
  /* --- Elenco (come la scelta della categoria) */
  .options {
    display: flex;
    flex-direction: column;
    gap: var(--space-hair);
    padding: var(--space-1);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
  }

  .group {
    margin: var(--space-3) var(--space-3) var(--space-1);
    font-size: var(--text-xs);
    font-weight: 800;
    letter-spacing: var(--tracking-caps);
    text-transform: uppercase;
    color: var(--color-text-muted);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-field);
    padding: var(--space-2) var(--space-4);
    border: 0;
    border-radius: var(--radius-md);
    background: none;
    color: var(--color-text);
    font: inherit;
    font-size: var(--text-md);
    text-align: left;
    cursor: pointer;
  }

  .row:active {
    background: var(--color-surface-2);
  }

  .row.on {
    background: var(--color-accent-soft);
    color: var(--color-text);
    font-weight: 700;
  }

  .row.on :global(svg) {
    color: var(--color-accent);
  }

  .row:disabled {
    opacity: var(--opacity-disabled);
    cursor: default;
  }

  .label {
    flex: 1;
    min-width: 0;
    line-height: var(--leading-compact);
  }

  /* --- Calendario */
  .cal {
    padding: var(--space-3) var(--space-2) var(--space-2);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
  }

  .cal-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
    padding-left: var(--space-2);
  }

  .title {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    min-height: var(--size-touch);
    padding: 0 var(--space-2);
    margin-left: calc(-1 * var(--space-2));
    border: 0;
    border-radius: var(--radius-full);
    background: none;
    color: var(--color-text);
    font: inherit;
    font-size: var(--text-lg);
    font-weight: 800;
    letter-spacing: var(--tracking-tight);
    cursor: pointer;
  }

  .title::first-letter {
    text-transform: uppercase;
  }

  .chev {
    display: inline-grid;
    color: var(--color-text-muted);
    transition: transform var(--duration-fast) var(--ease-standard);
  }

  .chev.up {
    transform: rotate(180deg);
  }

  .nav {
    display: flex;
    gap: var(--space-1);
  }

  .nav-btn {
    display: grid;
    place-items: center;
    width: var(--size-touch);
    height: var(--size-touch);
    border: 0;
    border-radius: var(--radius-full);
    background: var(--color-accent-soft);
    color: var(--color-accent);
    cursor: pointer;
  }

  .nav-btn:disabled,
  .day:disabled,
  .month:disabled {
    opacity: var(--opacity-disabled);
    cursor: default;
  }

  .days {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    row-gap: var(--space-1);
    justify-items: center;
  }

  .wd {
    padding: var(--space-1) 0 var(--space-2);
    font-size: var(--text-xs);
    font-weight: 800;
    color: var(--color-text-muted);
  }

  .day {
    display: grid;
    place-items: center;
    width: var(--size-touch);
    height: var(--size-touch);
    padding: 0;
    border: 0;
    border-radius: var(--radius-full);
    background: none;
    color: var(--color-text);
    font: inherit;
    font-size: var(--text-md);
    font-weight: 600;
    cursor: pointer;
    transition: background-color var(--duration-fast) var(--ease-standard);
  }

  .day:active {
    background: var(--color-surface-2);
  }

  /* Oggi: anello nel colore d'accento; il giorno scelto: pieno nel principale */
  .day.today {
    box-shadow: inset 0 0 0 var(--focus-width) var(--color-accent);
    color: var(--color-accent);
    font-weight: 800;
  }

  .day.sel,
  .month.sel {
    background: var(--color-primary);
    color: var(--color-on-primary);
    box-shadow: none;
    font-weight: 800;
  }

  .months {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--space-2);
    padding: var(--space-1);
  }

  .month {
    min-height: var(--size-field);
    border: 0;
    border-radius: var(--radius-full);
    background: var(--color-surface-2);
    color: var(--color-text);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }
</style>
