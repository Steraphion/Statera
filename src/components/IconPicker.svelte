<script lang="ts">
  // Scelta dell'icona di una categoria: anteprima con il colore scelto e, su richiesta, la griglia
  // delle icone divise per gruppi. "Nessuna" mostra l'iniziale del nome.
  import CategoryIcon from './CategoryIcon.svelte'
  import { CATEGORY_ICONS, CATEGORY_ICON_GROUPS, CATEGORY_ICON_LABELS, type CategoryIconKey } from '../lib/icons'
  import type { SwatchKey } from '../lib/data/types'

  let {
    value = $bindable(),
    auto = false,
    color,
    name,
  }: {
    value: CategoryIconKey | null
    /** L'icona non è stata scelta: è quella proposta in base al nome. */
    auto?: boolean
    color: SwatchKey
    /** Nome della categoria, per l'iniziale quando non c'è un'icona. */
    name: string
  } = $props()

  let open = $state(false)
  const uid = $props.id()
  const preview = $derived({ id: '', name: name.trim() || '?', color, icon: value })
</script>

<fieldset class="field">
  <legend>Icona</legend>
  <div class="current">
    <CategoryIcon category={preview} size="l" />
    <span class="what">
      {value ? CATEGORY_ICON_LABELS[value] : 'Nessuna, si vede l’iniziale'}{#if auto && value}<small> · in base al nome</small>{/if}
    </span>
    <button
      type="button"
      class="btn btn-small btn-soft"
      aria-expanded={open}
      aria-controls="{uid}-grid"
      onclick={() => (open = !open)}
    >
      {open ? 'Chiudi' : value ? 'Cambia' : 'Scegli'}
    </button>
  </div>

  {#if open}
    <div id="{uid}-grid" class="groups" role="radiogroup" aria-label="Icona">
      <div class="grid">
        <button
          type="button"
          role="radio"
          class="opt"
          aria-checked={value === null}
          aria-label="Nessuna icona (iniziale)"
          class:selected={value === null}
          onclick={() => (value = null)}
        >
          <CategoryIcon category={{ ...preview, icon: null }} />
        </button>
      </div>
      {#each CATEGORY_ICON_GROUPS as g, i (g.label)}
        <p class="group" id="{uid}-g{i}">{g.label}</p>
        <div class="grid" role="group" aria-labelledby="{uid}-g{i}">
          {#each g.keys as k (k)}
            <button
              type="button"
              role="radio"
              class="opt"
              aria-checked={value === k}
              aria-label={CATEGORY_ICON_LABELS[k]}
              title={CATEGORY_ICON_LABELS[k]}
              class:selected={value === k}
              onclick={() => (value = k)}
            >
              <CategoryIcon icon={CATEGORY_ICONS[k]} {color} />
            </button>
          {/each}
        </div>
      {/each}
    </div>
  {/if}
</fieldset>

<style>
  .current {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .what {
    flex: 1;
    min-width: 0;
    color: var(--color-muted);
    font-size: var(--text-sm);
  }

  .groups {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }

  .group {
    margin: var(--space-2) 0 0;
    font-size: var(--text-xs);
    font-weight: 800;
    letter-spacing: var(--tracking-caps);
    text-transform: uppercase;
    color: var(--color-muted);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--size-touch), 1fr));
    gap: var(--space-2);
  }

  .opt {
    justify-self: center;
    display: grid;
    place-items: center;
    width: calc(var(--size-cat) + var(--space-2));
    height: calc(var(--size-cat) + var(--space-2));
    padding: 0;
    border: 0;
    border-radius: var(--radius-full);
    background: none;
    cursor: pointer;
  }

  .opt.selected {
    box-shadow: 0 0 0 var(--focus-width) var(--color-text);
  }

  @media (hover: hover) {
    .opt:not(.selected):hover {
      box-shadow: 0 0 0 var(--focus-width) var(--color-border);
    }
  }
</style>
