<script lang="ts">
  import type { Category, CategoryKind } from '../lib/data/types'

  // Scelta della categoria a "bottoni": un tocco per la principale,
  // e se ha sottocategorie compaiono sotto per affinare.
  let {
    categories,
    kind,
    value = $bindable(),
    keepId = null,
  }: { categories: Category[]; kind: CategoryKind; value: string | null; keepId?: string | null } = $props()

  const usable = $derived(
    categories.filter((c) => c.deletedAt === null && c.kind === kind && (!c.archived || c.id === keepId)),
  )
  const tops = $derived(usable.filter((c) => c.parentId === null))
  const selected = $derived(usable.find((c) => c.id === value))
  const activeTop = $derived(selected ? (selected.parentId ?? selected.id) : null)
  const children = $derived(activeTop ? usable.filter((c) => c.parentId === activeTop) : [])
</script>

<fieldset class="field">
  <legend>Categoria</legend>
  <div class="chips" role="radiogroup" aria-label="Categoria">
    {#each tops as c (c.id)}
      <button
        type="button"
        role="radio"
        aria-checked={activeTop === c.id}
        class="chip"
        class:active={activeTop === c.id}
        onclick={() => (value = c.id)}
      >
        <span class="dot" style:background="var(--swatch-{c.color})"></span>
        {c.name}
      </button>
    {/each}
  </div>
  {#if children.length > 0}
    <div class="chips sub" role="radiogroup" aria-label="Sottocategoria">
      {#each children as c (c.id)}
        <button
          type="button"
          role="radio"
          aria-checked={value === c.id}
          class="chip"
          class:active={value === c.id}
          onclick={() => (value = value === c.id ? activeTop : c.id)}
        >
          {c.name}
        </button>
      {/each}
    </div>
  {/if}
</fieldset>

<style>
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  .chips.sub {
    margin-top: var(--space-2);
    padding: var(--space-2);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
  }

  .chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 36px;
    padding: 0 var(--space-3);
    border-radius: 999px;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    color: var(--color-text);
    font-size: var(--text-sm);
    cursor: pointer;
  }

  .chip.active {
    border-color: var(--color-accent);
    background: var(--color-accent-soft);
    font-weight: 600;
  }

  .dot {
    width: 10px;
    height: 10px;
  }
</style>
