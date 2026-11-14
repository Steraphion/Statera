<script lang="ts">
  import { liveQuery } from 'dexie'
  import Card from '../components/Card.svelte'
  import Icon from '../components/Icon.svelte'
  import MovementForm from '../components/MovementForm.svelte'
  import MovementRow from '../components/MovementRow.svelte'
  import PendingCard from '../components/PendingCard.svelte'
  import FavoritesBar from '../components/FavoritesBar.svelte'
  import SetupGuide from '../components/SetupGuide.svelte'
  import MonthRecapCard from '../components/MonthRecapCard.svelte'
  import MonthCalendar from '../components/MonthCalendar.svelte'
  import Segmented from '../components/Segmented.svelte'
  import { useRefs } from '../lib/data/refs.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Template, Transaction, TransactionType } from '../lib/data/types'
  import { router } from '../lib/router.svelte'
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

  // Calendario: giorno scelto (oggi nel mese in corso, altrimenti l'ultimo con movimenti)
  let picked = $state('')
  const selectedDay = $derived(
    picked.startsWith(ui.month) ? picked : isCurrentMonth ? today() : (days[0]?.date ?? `${ui.month}-01`),
  )
  const shownDays = $derived(ui.view === 'calendario' ? days.filter((g) => g.date === selectedDay) : days)
  const noAccounts = $derived(refs.ready && refs.value.accounts.length === 0)

  let sheet = $state<{ movement?: Transaction; type?: TransactionType; template?: Template } | null>(null)

  // Il + della barra (#/movimenti/nuovo) e le scorciatoie dall'icona dell'app (#/movimenti/nuova-uscita, nuova-entrata)
  $effect(() => {
    const p = router.param
    if (!(p === 'nuovo' || p.startsWith('nuova-')) || !refs.ready) return
    const t = p === 'nuova-entrata' ? 'entrata' : p === 'nuova-trasferimento' ? 'trasferimento' : p === 'nuovo' ? undefined : 'uscita'
    if (!noAccounts) sheet = { type: t }
    // Si torna a #/movimenti senza lasciare la scorciatoia nella cronologia
    location.replace('#/movimenti')
  })

  // Scorciatoie da tastiera (PC): frecce = mese (N e / valgono ovunque: App.svelte)
  function onKey(e: KeyboardEvent) {
    if (sheet || e.ctrlKey || e.metaKey || e.altKey) return
    const el = e.target as HTMLElement
    if (el.closest('input, textarea, select, [contenteditable]')) return
    if (e.key === 'ArrowLeft') ui.month = shiftMonth(ui.month, -1)
    else if (e.key === 'ArrowRight') ui.month = shiftMonth(ui.month, 1)
  }

</script>

<svelte:window onkeydown={onKey} />

<header class="month">
  <button class="btn btn-ghost nav" aria-label="Mese precedente" onclick={() => (ui.month = shiftMonth(ui.month, -1))}>
    <Icon name="chevron-left" />
  </button>
  <h1>{formatMonth(parseDay(`${ui.month}-01`))}</h1>
  <button class="btn btn-ghost nav" aria-label="Mese successivo" onclick={() => (ui.month = shiftMonth(ui.month, 1))}>
    <Icon name="chevron-right" />
  </button>
  <span class="spacer"></span>
  {#if !isCurrentMonth}
    <button class="btn btn-small" onclick={() => (ui.month = monthOf(today()))}>Oggi</button>
  {/if}
  <a class="btn btn-ghost nav" href="#/cerca" aria-label="Cerca" title="Cerca (/)">
    <Icon name="search" />
  </a>
</header>

{#if refs.ready}
  <SetupGuide hasAccounts={!noAccounts} onnew={() => (sheet = {})} />
{/if}

<PendingCard refs={refs.value} />

{#if refs.ready && !noAccounts}
  <MonthRecapCard categories={refs.value.categories} />
{/if}

{#if !noAccounts}
  <FavoritesBar refs={refs.value} onopen={(t) => (sheet = { template: t })} />
{/if}

<!-- Saldo del mese al centro, azioni rapide, entrate e uscite (design system: stile Vivace) -->
<section class="hero" aria-label="Saldo del mese">
  <span class="hero-label">Saldo del mese</span>
  <span class="hero-amount num">{totals.net > 0 ? '+' : ''}{formatEuro(totals.net)}</span>
</section>

{#if !noAccounts}
  <div class="quick">
    <button class="q" aria-label="Nuova spesa" onclick={() => (sheet = { type: 'uscita' })}>
      <span class="circle"><Icon name="arrow-up-right" size={22} /></span>Spesa
    </button>
    <button class="q" aria-label="Nuova entrata" onclick={() => (sheet = { type: 'entrata' })}>
      <span class="circle"><Icon name="arrow-down-left" size={22} /></span>Entrata
    </button>
    <button class="q" aria-label="Nuovo trasferimento" onclick={() => (sheet = { type: 'trasferimento' })}>
      <span class="circle"><Icon name="arrow-left-right" size={22} /></span>Trasferisci
    </button>
  </div>
{/if}

<div class="tiles2">
  <div class="tile">
    <span class="t-icon in"><Icon name="arrow-down-left" size={18} stroke={2.2} /></span>
    <span class="t-text"><span class="label">Entrate</span><span class="num">{formatEuro(totals.income)}</span></span>
  </div>
  <div class="tile">
    <span class="t-icon out"><Icon name="arrow-up-right" size={18} stroke={2.2} /></span>
    <span class="t-text"><span class="label">Uscite</span><span class="num">{formatEuro(totals.expense)}</span></span>
  </div>
</div>

{#if !noAccounts && loaded && rows.length > 0}
  <div class="view">
    <Segmented
      label="Vista"
      bind:value={ui.view}
      options={[
        { value: 'elenco', label: 'Elenco' },
        { value: 'calendario', label: 'Calendario' },
      ]}
    />
  </div>
  {#if ui.view === 'calendario'}
    <Card>
      <MonthCalendar month={ui.month} {rows} bind:selected={() => selectedDay, (v) => (picked = v)} />
    </Card>
    {#if shownDays.length === 0}
      <p class="empty-note">Nessun movimento il {formatDay(selectedDay).toLowerCase()}.</p>
    {/if}
  {/if}
{/if}

{#if noAccounts}
  <!-- La guida al primo avvio spiega come iniziare -->
{:else if loaded && rows.length === 0}
  <Card>
    <div class="empty">
      <p class="title">Nessun movimento in questo mese</p>
      <p class="hint">Tocca + per registrare una spesa o un'entrata.</p>
    </div>
  </Card>
{:else if shownDays.length}
  <!-- Un'unica scheda con i giorni come intestazioni -->
  <Card>
    {#each shownDays as g (g.date)}
      <h2 class="day">
        <span>{formatDay(g.date)}</span>
        <span class="num" class:amount-neg={g.net < 0}>{g.net === 0 ? '' : formatEuro(g.net)}</span>
      </h2>
      <ul class="list">
        {#each g.items as t (t.id)}
          <li><MovementRow {t} refs={refs.value} onclick={() => (sheet = { movement: t })} /></li>
        {/each}
      </ul>
    {/each}
  </Card>
{/if}

{#if sheet}
  <MovementForm
    movement={sheet.movement}
    defaultType={sheet.type}
    template={sheet.template}
    accounts={refs.value.accounts}
    cards={refs.value.cards}
    categories={refs.value.categories}
    lastSources={refs.value.lastSources}
    onclose={() => (sheet = null)}
  />
{/if}

<style>
  .view {
    display: flex;
    justify-content: flex-end;
    margin: 0 0 var(--space-3);
  }

  .month {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-bottom: var(--space-4);
  }

  .month h1 {
    font-size: var(--text-2xl);
    white-space: nowrap;
  }

  .hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    margin: var(--space-2) 0 var(--space-5);
  }

  .hero-label {
    font-size: var(--text-md);
    font-weight: 500;
    color: var(--color-text-muted);
  }

  .hero-amount {
    font-size: var(--amount-l);
    font-weight: 800;
    letter-spacing: var(--tracking-tighter);
    line-height: 1.1;
  }

  /* Azioni rapide (design system: AzioneRapida) */
  .quick {
    display: flex;
    justify-content: center;
    gap: var(--space-2);
    margin-bottom: var(--space-5);
  }

  .q {
    flex: 0 1 96px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    padding: 0;
    border: none;
    background: none;
    color: var(--color-text);
    font-size: var(--text-sm);
    font-weight: 600;
    cursor: pointer;
  }

  .circle {
    display: grid;
    place-items: center;
    width: var(--size-cat-l);
    height: var(--size-cat-l);
    border-radius: var(--radius-full);
    background: var(--color-accent-soft);
    color: var(--color-accent);
    transition: transform var(--duration-fast) var(--ease-standard);
  }

  .q:active .circle {
    transform: scale(0.94);
  }

  .tiles2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }

  .tile {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    min-width: 0;
  }

  .t-icon {
    flex: none;
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
  }

  .t-icon.in {
    color: var(--color-income);
    background: color-mix(in srgb, var(--color-income) 16%, transparent);
  }

  .t-icon.out {
    color: var(--color-expense-icon);
    background: color-mix(in srgb, var(--color-expense-icon) 16%, transparent);
  }

  .t-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .t-text .num {
    font-size: var(--text-lg);
    font-weight: 800;
  }

  .nav {
    min-height: 40px;
    padding: 0 var(--space-1);
    color: var(--color-text-muted);
  }

  .spacer {
    flex: 1;
  }



  .label {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-text-muted);
  }




  .day {
    display: flex;
    justify-content: space-between;
    margin: var(--space-4) 0 var(--space-1);
    font-size: var(--text-sm);
    font-weight: 600;
    letter-spacing: 0;
    color: var(--color-text-muted);
  }

  .day:first-child {
    margin-top: var(--space-1);
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
</style>
