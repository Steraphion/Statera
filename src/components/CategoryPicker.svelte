<script lang="ts">
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

  function color(c: Category): string {
    const top = c.parentId ? usable.find((x) => x.id === c.parentId) : c
    return `var(--swatch-${(top ?? c).color})`
  }
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
        {#if !child}<span class="dot" style:background={color(c)}></span>{/if}
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

  .cat-list {
    display: flex;
    flex-direction: column;
    max-height: 240px;
    overflow-y: auto;
    overscroll-behavior: contain;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-bg);
  }

  .cat {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-height: 44px;
    padding: 0 var(--space-3);
    border: none;
    border-bottom: 1px solid var(--color-border);
    background: transparent;
    color: var(--color-text);
    text-align: left;
    font-size: var(--text-md);
    flex: none;
  }

  .cat:last-child {
    border-bottom: none;
  }

  .cat.child {
    min-height: 40px;
    padding-left: calc(var(--space-3) + 10px + var(--space-2));
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .cat.active {
    background: var(--color-accent-soft);
    color: var(--color-text);
    font-weight: 600;
  }

  .label {
    flex: 1;
  }

  .check {
    color: var(--color-accent);
    font-weight: 700;
  }

  .dot {
    width: 10px;
    height: 10px;
  }
</style>
