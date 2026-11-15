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
  import { screen } from '../lib/screen.svelte'
  import { enterIf, leaveIf } from '../lib/motion'
  import { columns } from '../lib/columns.svelte'
  import Splitter from '../components/Splitter.svelte'
  import MonthBudgetCard from '../components/MonthBudgetCard.svelte'
  import MonthCategoriesCard from '../components/MonthCategoriesCard.svelte'
  import { budgetStatus } from '../lib/data/analytics'
  import SyncLine from '../components/sync/SyncLine.svelte'

  const refs = useRefs()

  // La lettura dipende dal mese scelto: cambiando mese si riparte da capo
  let rows = $state<Transaction[]>([])
  let loaded = $state(false)
  $effect(() => {
    const month = ui.month
    loaded = false
    const ready = screen.track()
    const sub = liveQuery(() => mv.movementsOfMonth(month)).subscribe({
      next: (v) => {
        rows = v
        loaded = true
        ready()
      },
      error: (e) => {
        ready()
        console.error('Errore di lettura movimenti', e)
      },
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
  // PC: colonne secondo la larghezza dell'area (columns.ts). Da "larga" importi in una riga, azioni rapide
  // nella testata ed elenco a colonne; da "molto larga" calendario e categorie sempre visibili a sinistra
  const larga = $derived(columns.at('larga'))
  const molto = $derived(columns.at('molto'))
  const hasBudgets = $derived(refs.ready && budgetStatus(rows, ui.month, refs.value.categories).length > 0)

  // Con il calendario sempre visibile l'elenco mostra tutto il mese: toccando un giorno ci si va
  const shownDays = $derived(ui.view === 'calendario' && !molto ? days.filter((g) => g.date === selectedDay) : days)

  function pickDay(v: string) {
    picked = v
    if (molto) document.getElementById(`giorno-${v}`)?.scrollIntoView({ block: 'start' })
  }
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
    // Un'altra finestra aperta (preferiti, budget, scorciatoie): le frecce sono sue
    if (document.querySelector('dialog[open]')) return
    if (e.key === 'ArrowLeft') ui.month = shiftMonth(ui.month, -1)
    else if (e.key === 'ArrowRight') ui.month = shiftMonth(ui.month, 1)
  }

</script>

<svelte:window onkeydown={onKey} />

<!-- Telefono: tutto in colonna, nell'ordine del codice. PC (da 900 px): elenco a sinistra e, accanto, la
     colonna di destra (guida esclusa) con preferiti, da registrare, riepilogo e budget, larga a piacere -->
<div class="layout" style:--col-w={columns.width('aside') === null ? null : `${columns.width('aside')}px`}>
<div class="lead">
<header class="month">
  <button class="btn btn-ghost nav" aria-label="Mese precedente" title="Mese precedente (freccia a sinistra)" onclick={() => (ui.month = shiftMonth(ui.month, -1))}>
    <Icon name="chevron-left" />
  </button>
  <h1>{formatMonth(parseDay(`${ui.month}-01`))}</h1>
  <button class="btn btn-ghost nav" aria-label="Mese successivo" title="Mese successivo (freccia a destra)" onclick={() => (ui.month = shiftMonth(ui.month, 1))}>
    <Icon name="chevron-right" />
  </button>
  <span class="spacer"></span>
  {#if !isCurrentMonth}
    <button class="btn btn-small" onclick={() => (ui.month = monthOf(today()))}>Oggi</button>
  {/if}
  {#if larga && !noAccounts}
    <!-- Area larga: le azioni rapide diventano pulsanti compatti nella testata -->
    <div class="quick-pc">
      <button class="btn btn-soft btn-small" data-no-autoauth aria-label="Nuova spesa" onclick={() => (sheet = { type: 'uscita' })}>
        <Icon name="arrow-up-right" size={16} />Spesa
      </button>
      <button class="btn btn-soft btn-small" data-no-autoauth aria-label="Nuova entrata" onclick={() => (sheet = { type: 'entrata' })}>
        <Icon name="arrow-down-left" size={16} />Entrata
      </button>
      <button class="btn btn-soft btn-small" data-no-autoauth aria-label="Nuovo trasferimento" onclick={() => (sheet = { type: 'trasferimento' })}>
        <Icon name="arrow-left-right" size={16} />Trasferisci
      </button>
    </div>
  {/if}
  <a class="btn btn-ghost nav" href="#/cerca" aria-label="Cerca" title="Cerca (/)">
    <Icon name="search" />
  </a>
</header>

{#if !columns.pc}
  <SyncLine />
{/if}

{#if refs.ready}
  <SetupGuide hasAccounts={!noAccounts} onnew={() => (sheet = {})} />
{/if}
</div>

{#if columns.pc}
  <Splitter
    id="aside"
    token="--size-aside"
    grows="left"
    controls="mov-aside"
    label="Larghezza della colonna di destra"
    reserve={molto ? ['--size-cal', '--space-6'] : []}
  />
{/if}

<aside class="aside" id="mov-aside" aria-label="Preferiti, da registrare e budget">
<PendingCard refs={refs.value} />

{#if refs.ready && !noAccounts}
  <MonthRecapCard categories={refs.value.categories} />
{/if}

{#if !noAccounts}
  <FavoritesBar refs={refs.value} onopen={(t) => (sheet = { template: t })} />
{/if}

{#if columns.pc && refs.ready}
  <!-- Senza budget, «Dove vanno i soldi» (da molto larga sta già nella colonna sinistra) -->
  {#if hasBudgets}
    <MonthBudgetCard {rows} month={ui.month} categories={refs.value.categories} />
  {:else if !molto}
    <MonthCategoriesCard {rows} month={ui.month} categories={refs.value.categories} />
  {/if}
  {@render keysHint()}
{/if}
</aside>

{#snippet keysHint()}
  <p class="keys-hint">
    <kbd>N</kbd> nuovo <span aria-hidden="true">·</span> <kbd>/</kbd> cerca <span aria-hidden="true">·</span>
    <kbd>←</kbd><kbd>→</kbd> mese <span aria-hidden="true">·</span>
    <button class="all-keys" onclick={() => (ui.shortcuts = true)}><kbd>?</kbd> tutte le scorciatoie</button>
  </p>
{/snippet}

{#if molto && refs.ready && !noAccounts}
  <!-- Area molto larga: calendario del mese (toccando un giorno l'elenco ci va) e categorie, sempre visibili -->
  <aside class="cal-col" aria-label="Calendario e categorie del mese">
    <Card>
      <h2 class="cal-title">Calendario</h2>
      <MonthCalendar month={ui.month} {rows} bind:selected={() => selectedDay, pickDay} />
    </Card>
    <MonthCategoriesCard {rows} month={ui.month} categories={refs.value.categories} />
    {@render keysHint()}
  </aside>
{/if}

<div class="body">
<!-- Saldo del mese nel riquadro indaco, poi azioni rapide (accanto, su schermi larghi), entrate e uscite;
     da area larga saldo, entrate e uscite in una riga (.kpis) e le azioni rapide nella testata -->
<div class="kpis">
<div class="top">
<section class="hero balance-box" aria-label="Saldo del mese">
  <span class="bb-label">Saldo del mese</span>
  <span class="bb-amount num">{totals.net > 0 ? '+' : ''}{formatEuro(totals.net)}</span>
</section>

{#if !noAccounts && !larga}
  <div class="quick">
    <button class="q" data-no-autoauth aria-label="Nuova spesa" onclick={() => (sheet = { type: 'uscita' })}>
      <span class="circle"><Icon name="arrow-up-right" size={22} /></span>Spesa
    </button>
    <button class="q" data-no-autoauth aria-label="Nuova entrata" onclick={() => (sheet = { type: 'entrata' })}>
      <span class="circle"><Icon name="arrow-down-left" size={22} /></span>Entrata
    </button>
    <button class="q" data-no-autoauth aria-label="Nuovo trasferimento" onclick={() => (sheet = { type: 'trasferimento' })}>
      <span class="circle"><Icon name="arrow-left-right" size={22} /></span>Trasferisci
    </button>
  </div>
{/if}
</div>

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
</div>

{#if !noAccounts && loaded && rows.length > 0 && !molto}
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
    {#if larga}
      <!-- Area larga: righe a colonne, con le intestazioni -->
      <div class="cols-head row-cols" aria-hidden="true">
        <span></span><span>Descrizione</span><span>Categoria</span><span>Conto o carta</span><span class="r">Importo</span>
      </div>
    {/if}
    <!-- Movimento: si aprono e si chiudono solo le righe (o i giorni) appena salvati, eliminati o
         ripristinati (enterIf / leaveIf e .fold) -->
    {#each shownDays as g (g.date)}
      <div class="fold day-group" id="giorno-{g.date}" in:enterIf={g.items.map((i) => i.id)} out:leaveIf={g.items.map((i) => i.id)}>
        <div>
          <h2 class="day">
            <span>{formatDay(g.date)}</span>
            <span class="num" class:amount-neg={g.net < 0}>{g.net === 0 ? '' : formatEuro(g.net)}</span>
          </h2>
          <ul class="list">
            {#each g.items as t (t.id)}
              <li class="fold" in:enterIf={t.id} out:leaveIf={t.id}>
                <MovementRow {t} refs={refs.value} columns={larga} onclick={() => (sheet = { movement: t })} />
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/each}
  </Card>
{/if}
</div>
</div>

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
  /* Telefono: le schede tra la testata e il saldo si seguono con lo stesso spazio di prima (la guida è nella
     prima parte, le altre nella colonna di destra) */
  .lead:has(:global(.card)) + .aside > :global(.card:first-child) {
    margin-top: var(--space-4);
  }

  .all-keys {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: 0;
    border: 0;
    background: none;
    color: var(--color-accent);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }

  .keys-hint {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-1) var(--space-2);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  /* PC: due colonne. La colonna di destra ha la larghezza scelta (o quella iniziale), mai più di quanto
     lascia libera la colonna principale; il separatore sta nello spazio tra le due. --reserve è lo spazio
     preso dalle altre colonne fisse (da molto larga, la colonna sinistra) */
  @media (min-width: 900px) {
    .layout {
      --reserve: 0px;
      --aside-w: min(
        clamp(var(--size-aside-min), var(--col-w, var(--size-aside)), var(--size-aside-max)),
        max(var(--size-aside-min), 100% - var(--size-main-min) - var(--space-6) - var(--reserve))
      );
      display: grid;
      grid-template-columns: minmax(0, 1fr) var(--space-6) var(--aside-w);
      grid-template-rows: auto 1fr;
      align-items: start;
    }

    .lead {
      grid-column: 1;
      grid-row: 1;
      display: flex;
      flex-direction: column;
      gap: var(--space-4);
      margin-bottom: var(--space-4);
    }

    .lead > :global(*) {
      margin: 0;
    }

    .body {
      grid-column: 1;
      grid-row: 2;
      min-width: 0;
      /* La colonna dell'elenco cambia larghezza (barra stretta, colonna di destra regolabile): saldo e
         azioni rapide si affiancano secondo lo spazio della colonna, non della finestra */
      container: elenco / inline-size;
    }

    .layout > :global(.splitter) {
      grid-column: 2;
      grid-row: 1 / -1;
    }

    .aside,
    .cal-col {
      grid-column: 3;
      grid-row: 1 / -1;
      display: flex;
      flex-direction: column;
      gap: var(--space-4);
      min-width: 0;
    }

    .aside > :global(*),
    .cal-col > :global(*),
    .aside > :global(.card) + :global(.card),
    .cal-col > :global(.card) + :global(.card) {
      margin: 0;
    }

    /* Nelle colonne laterali le schede hanno un po' meno aria ai lati */
    .aside :global(.card),
    .cal-col :global(.card) {
      padding: var(--space-4) var(--space-5);
    }

    .top {
      margin-top: 0;
    }

    /* Colonna di destra senza schede (niente da registrare, preferiti, budget né uscite nel mese): non c'è,
       e l'elenco prende tutto lo spazio */
    .layout:not(:has(> .aside :global(.card))) {
      grid-template-columns: minmax(0, 1fr);
    }

    .layout:not(:has(> .aside :global(.card))) > :is(.aside, :global(.splitter)) {
      display: none;
    }

    /* Area molto larga: a sinistra calendario e «Dove vanno i soldi», larghi --size-cal */
    :global(.l-molto) .layout {
      --reserve: calc(var(--size-cal) + var(--space-6));
      grid-template-columns: var(--size-cal) var(--space-6) minmax(0, 1fr) var(--space-6) var(--aside-w);
    }

    :global(.l-molto) .layout:not(:has(> .aside :global(.card))) {
      grid-template-columns: var(--size-cal) var(--space-6) minmax(0, 1fr);
    }

    .cal-col {
      grid-column: 1;
    }

    :global(.l-molto) .lead,
    :global(.l-molto) .body {
      grid-column: 3;
    }

    :global(.l-molto) .layout > :global(.splitter) {
      grid-column: 4;
    }

    :global(.l-molto) .aside {
      grid-column: 5;
    }

    /* I tasti stanno in fondo alla colonna di destra; a sinistra solo se quella non c'è */
    .cal-col .keys-hint,
    .layout:not(:has(> .aside :global(.card))) > .aside .keys-hint {
      display: none;
    }

    .layout:not(:has(> .aside :global(.card))) > .cal-col .keys-hint {
      display: flex;
    }

    .cal-title {
      margin-bottom: var(--space-3);
      font-size: var(--text-lg);
    }

    /* Toccando un giorno del calendario l'elenco ci va: un po' d'aria sopra l'intestazione */
    .day-group {
      scroll-margin-top: var(--space-4);
    }
  }

  /* Saldo, entrate e uscite: sul telefono e nelle aree strette uno sotto l'altro (come se .kpis non ci
     fosse); da area larga in una riga, col saldo più largo */
  .kpis {
    display: contents;
  }

  :global(.l-larga) .kpis {
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(0, 1fr) minmax(0, 1fr);
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }

  :global(.l-larga) .kpis .top {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    margin: 0;
  }

  :global(.l-larga) .kpis .hero {
    flex: 1;
  }

  :global(.l-larga) .kpis .tiles2 {
    display: contents;
  }

  :global(.l-larga) .kpis .tile {
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-end;
    padding: var(--space-4) var(--space-5);
  }

  :global(.l-larga) .kpis .t-text .num {
    font-size: var(--amount-s);
    letter-spacing: var(--tracking-tight);
  }

  .quick-pc {
    display: flex;
    gap: var(--space-2);
    margin-right: var(--space-2);
  }

  .quick-pc .btn {
    gap: var(--space-1);
  }

  .cols-head + .day-group .day {
    margin-top: var(--space-3);
  }

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

  .top {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    margin: var(--space-4) 0 var(--space-5);
  }

  /* Su schermi larghi le azioni rapide stanno accanto al riquadro, non centrate sotto (su PC se la
     colonna dell'elenco è abbastanza larga) */
  @media (min-width: 600px) and (max-width: 899px) {
    .top {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: var(--space-5);
    }
  }

  @container elenco (min-width: 600px) {
    .top {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: var(--space-5);
    }
  }

  /* Azioni rapide (design system: AzioneRapida) */
  .quick {
    display: flex;
    justify-content: center;
    gap: var(--space-2);
  }

  .q {
    flex: 0 1 calc(var(--size-cat-l) + var(--space-7));
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
    width: var(--size-cat-s);
    height: var(--size-cat-s);
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

  .day-group:first-child .day {
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
