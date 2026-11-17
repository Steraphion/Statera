<script lang="ts">
  import { pickerAction } from '../lib/picker.svelte'
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
    fixedKind = false,
    noAutoauth = false,
    onaddchild,
    onsaved,
    onclose,
  }: {
    category?: Category
    categories: Category[]
    defaultKind: CategoryKind
    defaultParentId?: string | null
    defaultColor?: SwatchKey
    /** Tipo fissato da chi apre il modulo (dal modulo del movimento: uscita o entrata come il movimento). */
    fixedKind?: boolean
    /** Aperto dal modulo del movimento: i tocchi non rinnovano il permesso Google. */
    noAutoauth?: boolean
    /** Apre il modulo per una nuova sottocategoria di questa categoria. */
    onaddchild?: () => void
    /** Categoria appena creata (solo per una categoria nuova), prima della chiusura. */
    onsaved?: (created: Category) => void
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
  // Icona: finché non la si sceglie è automatica (predefinita delle categorie iniziali o dal nome)
  // e non si scrive nei dati; scelta, si salva come chiave (null = "Nessuna", si vede l'iniziale).
  let picked = $state<CategoryIconKey | null | undefined>(
    orig && orig.icon !== undefined ? categoryIconKey(orig) : undefined,
  )
  const autoIcon = $derived(categoryIconKey({ id: orig?.id ?? '', name }))
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
    const changed = picked !== undefined && picked !== (orig?.icon ?? undefined)
    const input = { name, kind, parentId: parentId || null, color, ...(changed ? { icon: picked } : {}) }
    run(async () => {
      if (category) return repo.updateCategory(category.id, input)
      const created = await repo.createCategory(input)
      onsaved?.(created)
    })
  }
</script>

<Sheet title={category ? 'Modifica categoria' : 'Nuova categoria'} {onclose} {error} {noAutoauth}>
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
        disabled={!!category?.parentId || fixedKind}
        options={[
          { value: 'uscita', label: 'Uscita' },
          { value: 'entrata', label: 'Entrata' },
        ]}
      />
      {#if category?.parentId}
        <span class="hint">Il tipo di una sottocategoria segue quello della categoria principale.</span>
      {:else if fixedKind}
        <span class="hint">Come il movimento. Resta tra le categorie, modificabile in Altro&nbsp;→&nbsp;Categorie.</span>
      {/if}
    </div>

    {#if !hasChildren}
      <label class="field">
        <span>Dentro a</span>
        <select use:pickerAction class="input" bind:value={parentId}>
          <option value="">— Nessuna (categoria principale) —</option>
          {#each parents as p (p.id)}
            <option value={p.id}>{p.name}</option>
          {/each}
        </select>
      </label>
    {/if}

    <IconPicker
      bind:value={() => (picked === undefined ? autoIcon : picked), (v) => (picked = v)}
      auto={picked === undefined}
      {color}
      {name}
    />

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
