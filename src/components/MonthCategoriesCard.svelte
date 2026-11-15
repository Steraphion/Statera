<script lang="ts">
  import Card from './Card.svelte'
  import CategoryBars from './charts/CategoryBars.svelte'
  import { byCategory, periodRange } from '../lib/data/analytics'
  import { EMPTY_FILTERS } from '../lib/data/transactions'
  import type { Category, Transaction } from '../lib/data/types'
  import { ui } from '../lib/ui.svelte'

  /**
   * «Dove vanno i soldi»: le prime 5 categorie di uscita del mese mostrato (PC). Nella colonna di destra di
   * Movimenti quando non ci sono budget, così la colonna non resta vuota; nella colonna sinistra quando
   * l'area è molto larga. Toccando una categoria si apre Cerca coi suoi movimenti del mese.
   */
  let { rows, month, categories, limit = 5 }: { rows: Transaction[]; month: string; categories: Category[]; limit?: number } =
    $props()

  const groups = $derived(byCategory(rows, 'uscita', categories).slice(0, limit))

  function show(c: Category) {
    const r = periodRange({ kind: 'mese', month })
    Object.assign(ui.filters, EMPTY_FILTERS, { categoryId: c.id, from: r.from, to: r.to, type: 'uscita' })
    location.hash = '/cerca'
  }

  function openAnalysis() {
    Object.assign(ui.analysis, { kind: 'mese', month })
  }
</script>

{#if groups.length}
  <Card>
    <section class="month-cats" aria-labelledby="month-cats-title">
      <div class="head">
        <h2 id="month-cats-title">Dove vanno i soldi</h2>
        <a class="btn btn-ghost btn-small" href="#/analisi" onclick={openAnalysis}>Analisi</a>
      </div>
      <CategoryBars {groups} color="var(--chart-expense)" onshow={show} />
    </section>
  </Card>
{/if}

<style>
  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }

  h2 {
    font-size: var(--text-lg);
  }

  /* Il collegamento a fine riga: allineato al bordo è il testo, non la pillola */
  .head > .btn-ghost {
    margin-right: calc(-1 * var(--space-3));
  }
</style>
