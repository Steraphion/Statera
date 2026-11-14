<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import ColorPicker from './ColorPicker.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import Segmented from './Segmented.svelte'
  import IconPicker from './IconPicker.svelte'
  import { categoryIconKey } from '../lib/categoryIcon'
  import type { CategoryIconKey } from '../lib/icons'
  import * as repo from '../lib/data/repo'
  import { errorMessage, withTimeout } from '../lib/data/util'
  import type { Category, CategoryKind, SwatchKey } from '../lib/data/types'

  let {
    category,
    categories,
    defaultKind,
    defaultParentId = null,
    defaultColor = 's1',
    onaddchild,
    onclose,
  }: {
    category?: Category
    categories: Category[]
    defaultKind: CategoryKind
    defaultParentId?: string | null
    defaultColor?: SwatchKey
    /** Apre il modulo per una nuova sottocategoria di questa categoria. */
    onaddchild?: () => void
    onclose: () => void
  } = $props()

  // Valori di partenza del modulo (letti una volta all'apertura)
  const orig = untrack(() => category)
  const initKind = untrack(() => defaultKind)
  const initParentId = untrack(() => defaultParentId)

  let name = $state(orig?.name ?? '')
  let kind = $state<CategoryKind>(orig?.kind ?? initKind)
  let parentId = $state<string>(orig?.parentId ?? initParentId ?? '')
  let color = $state<SwatchKey>(
    orig?.color ??
      untrack(() => categories.find((c) => c.id === defaultParentId)?.color ?? defaultColor),
  )
  // Icona: si salva solo se cambiata, così le categorie iniziali seguono l'icona predefinita
  const initIcon: CategoryIconKey | null = orig ? categoryIconKey(orig) : null
  let icon = $state<CategoryIconKey | null>(initIcon)
  let error = $state('')
  let busy = $state(false)

  const hasChildren = $derived(!!category && categories.some((c) => c.parentId === category.id))
  const parents = $derived(
    categories.filter((c) => c.parentId === null && c.kind === kind && !c.archived && c.id !== category?.id),
  )

  // Cambiando tipo, la categoria principale scelta potrebbe non valere più
  $effect(() => {
    if (parentId && !parents.some((p) => p.id === parentId)) parentId = ''
  })

  async function run(action: () => Promise<unknown>) {
    error = ''
    busy = true
    try {
      await withTimeout(action())
      onclose()
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }

  function save(e: SubmitEvent) {
    e.preventDefault()
    const input = { name, kind, parentId: parentId || null, color, ...(icon !== initIcon ? { icon } : {}) }
    run(() => (category ? repo.updateCategory(category.id, input) : repo.createCategory(input)))
  }
</script>

<Sheet title={category ? 'Modifica categoria' : 'Nuova categoria'} {onclose} {error}>
  <form novalidate id="category-form" class="form" onsubmit={save}>
    <label class="field">
      <span>Nome</span>
      <input class="input" bind:value={name} maxlength="40" required />
    </label>

    <div class="field">
      <span>Tipo</span>
      <Segmented
        label="Tipo"
        bind:value={kind}
        disabled={!!category?.parentId}
        options={[
          { value: 'uscita', label: 'Uscita' },
          { value: 'entrata', label: 'Entrata' },
        ]}
      />
      {#if category?.parentId}
        <span class="hint">Il tipo di una sottocategoria segue quello della categoria principale.</span>
      {/if}
    </div>

    {#if !hasChildren}
      <label class="field">
        <span>Dentro a</span>
        <select class="input" bind:value={parentId}>
          <option value="">— Nessuna (categoria principale) —</option>
          {#each parents as p (p.id)}
            <option value={p.id}>{p.name}</option>
          {/each}
        </select>
      </label>
    {/if}

    <IconPicker bind:value={icon} {color} {name} />

    <ColorPicker bind:value={color} />

    {#if category && !category.parentId && !category.archived && onaddchild}
      <button type="button" class="btn btn-ghost add-child" onclick={onaddchild}>+ Aggiungi sottocategoria</button>
    {/if}
  </form>

  {#snippet footer()}
    {#if category}
      <DeleteButton onconfirm={() => run(() => repo.deleteCategory(category.id))} />
      <button
        type="button"
        class="btn"
        onclick={() => run(() => repo.setCategoryArchived(category.id, !category.archived))}
      >
        {category.archived ? 'Ripristina' : 'Archivia'}
      </button>
    {/if}
    <button type="submit" form="category-form" class="btn btn-primary" disabled={busy}>Salva</button>
  {/snippet}
</Sheet>

<style>
  .add-child {
    align-self: flex-start;
    padding: 0;
  }
</style>
