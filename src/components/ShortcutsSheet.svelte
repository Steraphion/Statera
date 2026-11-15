<script lang="ts">
  import Sheet from './Sheet.svelte'

  /** Elenco delle scorciatoie da tastiera (tasto ?): si apre da ovunque su PC, dalla riga in Movimenti e da Altro. */
  let { onclose }: { onclose: () => void } = $props()

  const GROUPS: { title: string; items: { keys: string[][]; what: string }[] }[] = [
    {
      title: 'Ovunque',
      items: [
        { keys: [['N']], what: 'Nuovo movimento' },
        { keys: [['/']], what: 'Cerca' },
        { keys: [['?']], what: 'Questo elenco' },
        { keys: [['Esc']], what: 'Chiude la finestra' },
      ],
    },
    {
      title: 'Movimenti, Conti, Analisi',
      items: [
        { keys: [['←'], ['→']], what: 'Mese precedente e successivo' },
        { keys: [['↑'], ['↓']], what: 'Conto precedente e successivo (Conti)' },
      ],
    },
    {
      title: 'Nelle finestre',
      items: [
        { keys: [['Invio']], what: 'Salva (nelle note va a capo)' },
        { keys: [['Ctrl', 'Invio']], what: 'Salva anche dalle note' },
        { keys: [['↑'], ['↓']], what: 'Scorre i suggerimenti della descrizione; Invio sceglie' },
        { keys: [['Tab']], what: 'Campo successivo' },
      ],
    },
    {
      title: 'Colonne (separatore)',
      items: [
        { keys: [['←'], ['→']], what: 'Sposta il separatore; con Maiuscole di più' },
        { keys: [['Inizio'], ['Fine']], what: 'Colonna più stretta o più larga possibile' },
        { keys: [['Invio']], what: 'Larghezza iniziale (anche con doppio clic)' },
      ],
    },
  ]
</script>

<Sheet title="Scorciatoie da tastiera" {onclose} wide>
  <div class="groups">
    {#each GROUPS as g (g.title)}
      <section aria-labelledby="sc-{g.title}">
        <h3 id="sc-{g.title}">{g.title}</h3>
        <dl>
          {#each g.items as it (it.what)}
            <div class="item">
              <dt>
                {#each it.keys as combo, i (i)}
                  {#if i > 0}<span class="sep" aria-hidden="true"> </span>{/if}
                  {#each combo as k, j (j)}{#if j > 0}<span class="plus">+</span>{/if}<kbd>{k}</kbd>{/each}
                {/each}
              </dt>
              <dd>{it.what}</dd>
            </div>
          {/each}
        </dl>
      </section>
    {/each}
  </div>
  <p class="note">Mentre scrivi in un campo le lettere restano lettere: N, / e ? funzionano solo fuori dai campi.</p>
</Sheet>

<style>
  .groups {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-5) var(--space-6);
  }

  @media (min-width: 600px) {
    .groups {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  h3 {
    margin-bottom: var(--space-2);
    font-size: var(--text-xs);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: var(--tracking-caps);
    color: var(--color-text-muted);
  }

  dl {
    margin: 0;
  }

  .item {
    display: grid;
    grid-template-columns: calc(2 * var(--space-8) + var(--space-6)) minmax(0, 1fr);
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border-top: 1px solid var(--color-border);
  }

  dt {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: var(--space-1);
  }

  .plus {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  dd {
    margin: 0;
    font-size: var(--text-sm);
    font-weight: 600;
    line-height: var(--leading-compact);
  }

  .note {
    margin-top: var(--space-5);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }
</style>
