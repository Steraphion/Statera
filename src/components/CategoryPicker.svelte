<script lang="ts">
  import CategoryIcon from './CategoryIcon.svelte'
  import type { Category, CategoryKind } from '../lib/data/types'
  import { byName } from '../lib/data/util'

  // Scelta della categoria: elenco verticale scorrevole, in ordine alfabetico,
  // con le sottocategorie rientrate sotto la loro categoria principale.
  let {
    categories,
    kind,
    value = $bindable(),
    keepId = null,
  }: { categories: Category[]; kind: CategoryKind; value: string | null; keepId?: string | null } = $props()

  const usable = $derived(
    categories.filter((c) => c.deletedAt === null && c.kind === kind && (!c.archived || c.id === keepId)),
  )
  const rows = $derived.by(() => {
    const out: { c: Category; child: boolean }[] = []
    for (const top of usable.filter((c) => c.parentId === null).sort(byName)) {
      out.push({ c: top, child: false })
      for (const ch of usable.filter((c) => c.parentId === top.id).sort(byName)) out.push({ c: ch, child: true })
    }
    return out
  })
  const selected = $derived(usable.find((c) => c.id === value))
  const selectedLabel = $derived.by(() => {
    if (!selected) return ''
    const parent = selected.parentId ? usable.find((c) => c.id === selected.parentId) : null
    return parent ? `${parent.name} › ${selected.name}` : selected.name
  })

  let list: HTMLDivElement | undefined = $state()

  // All'apertura in modifica, porta in vista la categoria già scelta
  $effect(() => {
    const el = list?.querySelector<HTMLElement>('[aria-checked="true"]')
    if (el && list) list.scrollTop = el.offsetTop - list.clientHeight / 2 + el.clientHeight / 2
  })

</script>

<fieldset class="field">
  <legend>
    Categoria{#if selectedLabel}: <strong>{selectedLabel}</strong>{/if}
  </legend>
  <div class="cat-list" role="radiogroup" aria-label="Categoria" bind:this={list}>
    {#each rows as { c, child } (c.id)}
      <button
        type="button"
        role="radio"
        aria-checked={value === c.id}
        class="cat"
        class:child
        class:active={value === c.id}
        onclick={() => (value = c.id)}
      >
        <CategoryIcon category={c} size={child ? 's' : 'm'} />
        <span class="label">{c.name}</span>
        {#if value === c.id}<span class="check" aria-hidden="true">✓</span>{/if}
      </button>
    {/each}
    {#if rows.length === 0}
      <p class="empty-note">Nessuna categoria di questo tipo. Creale in Altro → Categorie.</p>
    {/if}
  </div>
</fieldset>

<style>
  legend strong {
    color: var(--color-text);
  }

  /* Elenco verticale con le icone (design system: IconaCategoria), sottocategorie rientrate */
  .cat-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-hair);
    max-height: 288px;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: var(--space-2);
    border-radius: var(--radius-lg);
    background: var(--color-surface);
  }

  .cat {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-field);
    padding: 0 var(--space-3) 0 var(--space-1);
    border: none;
    border-radius: var(--radius-md);
    background: transparent;
    color: var(--color-text);
    text-align: left;
    font-size: var(--text-md);
    font-weight: 600;
    flex: none;
  }

  .cat.child {
    min-height: var(--size-touch);
    margin-left: calc(var(--size-cat) / 2 + var(--space-1));
    padding-left: var(--space-3);
    border-left: var(--space-hair) solid var(--chart-track);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    font-size: var(--text-sm);
  }

  .cat.active {
    background: var(--color-accent-soft);
    font-weight: 800;
  }

  .label {
    flex: 1;
  }

  .check {
    color: var(--color-accent);
    font-weight: 800;
  }
</style>
