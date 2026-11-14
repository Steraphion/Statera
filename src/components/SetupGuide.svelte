<script lang="ts">
  import Card from './Card.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { dismissGuide } from '../lib/data/repo'
  import { sync } from '../lib/sync/sync.svelte'

  /** Guida in tre passi per chi inizia. Sparisce quando i passi sono fatti o se la si nasconde. */
  let { hasAccounts, onnew }: { hasAccounts: boolean; onnew: () => void } = $props()

  const state = live(
    async () => {
      const [dismissed, firstMovement, backup] = await Promise.all([
        db.meta.get('guidaChiusa'),
        db.transactions.filter((t) => t.deletedAt === null).first(),
        db.meta.get('ultimoBackup'),
      ])
      return { dismissed: !!dismissed?.value, hasMovements: !!firstMovement, hasBackup: !!backup?.value }
    },
    { dismissed: true, hasMovements: false, hasBackup: false },
  )

  const safe = $derived(state.value.hasBackup || sync.status !== 'off')
  const steps = $derived([hasAccounts, state.value.hasMovements, safe])
  const done = $derived(steps.filter(Boolean).length)
  // Senza conti la guida resta: è l'unico modo per capire da dove iniziare
  const visible = $derived(state.ready && done < 3 && (!state.value.dismissed || !hasAccounts))
</script>

{#if visible}
  <Card>
    <section class="guide" aria-labelledby="guide-title">
      <div class="head">
        <h2 id="guide-title">{hasAccounts ? 'Per iniziare' : 'Benvenuto in Statera'}</h2>
        <span class="count">{done} di 3</span>
      </div>
      <ol>
        <li class:done={steps[0]}>
          <span class="mark" aria-hidden="true">{steps[0] ? '✓' : '1'}</span>
          <div>
            <p class="title">Crea i tuoi conti{steps[0] ? ' — fatto' : ''}</p>
            {#if !steps[0]}
              <p class="text">
                Conto corrente, contanti, buoni pasto. Come saldo iniziale scrivi quello di oggi: i movimenti passati non
                vanno registrati.
              </p>
              <a class="btn btn-primary btn-small" href="#/conti">Vai ai conti</a>
              <p class="text small">
                Hai già usato Statera su un altro dispositivo? Collega Google Drive da <a href="#/altro">Altro</a> per
                ritrovare i tuoi dati.
              </p>
            {/if}
          </div>
        </li>
        <li class:done={steps[1]}>
          <span class="mark" aria-hidden="true">{steps[1] ? '✓' : '2'}</span>
          <div>
            <p class="title">Registra il primo movimento{steps[1] ? ' — fatto' : ''}</p>
            {#if !steps[1]}
              <p class="text">
                Tocca + in basso. Scrivendo la descrizione, Statera propone categoria e conto usati l'ultima volta; le
                spese abituali puoi salvarle tra i preferiti.
              </p>
              {#if steps[0]}<button class="btn btn-small" onclick={onnew}>Nuovo movimento</button>{/if}
            {/if}
          </div>
        </li>
        <li class:done={steps[2]}>
          <span class="mark" aria-hidden="true">{steps[2] ? '✓' : '3'}</span>
          <div>
            <p class="title">Metti al sicuro i dati{steps[2] ? ' — fatto' : ''}</p>
            {#if !steps[2]}
              <p class="text">
                Collega Google Drive per avere gli stessi dati su telefono e PC, con backup cifrati ogni giorno. In
                alternativa esporta un backup.
              </p>
              <a class="btn btn-small" href="#/altro">Vai ad Altro</a>
            {/if}
          </div>
        </li>
      </ol>
      {#if hasAccounts}
        <button class="btn btn-ghost btn-small hide" onclick={() => dismissGuide()}>Nascondi la guida</button>
      {/if}
    </section>
  </Card>
{/if}

<style>
  .head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: var(--space-3);
  }

  h2 {
    font-size: var(--text-lg);
  }

  .count {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  ol {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  li {
    display: grid;
    grid-template-columns: var(--size-step) minmax(0, 1fr);
    gap: var(--space-3);
  }

  .mark {
    display: grid;
    place-items: center;
    width: var(--size-step);
    height: var(--size-step);
    border-radius: 50%;
    border: 1px solid var(--color-border);
    font-size: var(--text-sm);
    font-weight: 700;
  }

  li.done .mark {
    background: var(--color-accent-soft);
    border-color: var(--color-accent);
    color: var(--color-accent);
  }

  li.done .title {
    color: var(--color-text-muted);
  }

  .title {
    font-weight: 600;
    min-height: var(--size-step);
    display: flex;
    align-items: center;
  }

  .text {
    margin: var(--space-1) 0 var(--space-2);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .small {
    font-size: var(--text-xs);
    margin-top: var(--space-2);
  }

  .hide {
    margin-top: var(--space-3);
    padding: 0;
    min-height: var(--size-cat-s);
  }
</style>
