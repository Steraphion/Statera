<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import CategoryForm from '../components/CategoryForm.svelte'
  import Segmented from '../components/Segmented.svelte'
  import Icon from '../components/Icon.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import { SWATCHES, type Category, type CategoryKind } from '../lib/data/types'
  import { alive, byName } from '../lib/data/util'

  const data = live(async () => alive(await db.categories.toArray()).sort(byName), [] as Category[])

  let kind = $state<CategoryKind>('uscita')
  let showArchived = $state(false)
  let sheet = $state<{ category?: Category; parentId?: string } | null>(null)

  const ofKind = $derived(data.value.filter((c) => c.kind === kind))
  const visible = $derived(ofKind.filter((c) => showArchived || !c.archived))
  const tops = $derived(visible.filter((c) => c.parentId === null))
  const archivedCount = $derived(ofKind.filter((c) => c.archived).length)

  function childrenOf(id: string) {
    return visible.filter((c) => c.parentId === id)
  }
</script>

<ScreenHeader title="Categorie" back={{ href: '#/altro', label: 'Altro' }}>
  <button class="btn btn-primary btn-small" onclick={() => (sheet = {})}>
    <Icon name="plus" size={18} /> Categoria
  </button>
</ScreenHeader>


<div class="switch">
  <Segmented
    label="Tipo di categoria"
    bind:value={kind}
    options={[
      { value: 'uscita', label: 'Uscite' },
      { value: 'entrata', label: 'Entrate' },
    ]}
  />
</div>

<p class="tip">Tocca una categoria per modificarla o aggiungere sottocategorie.</p>

<Card>
  {#if data.ready && tops.length === 0}
    <p class="empty-note">Nessuna categoria.</p>
  {:else}
    <ul class="list">
      {#each tops as c (c.id)}
        <li>
          <button class="list-row" onclick={() => (sheet = { category: c })}>
            <span class="dot" style:background="var(--swatch-{c.color})"></span>
            <span class="main">
              <span class="name" class:archived={c.archived}>{c.name}</span>
            </span>
            {#if c.archived}<span class="sub">Archiviata</span>{/if}
          </button>
          {#if childrenOf(c.id).length > 0}
            <ul class="list children">
              {#each childrenOf(c.id) as child (child.id)}
                <li>
                  <button class="list-row" onclick={() => (sheet = { category: child })}>
                    <span class="main">
                      <span class="name child" class:archived={child.archived}>{child.name}</span>
                    </span>
                    {#if child.archived}<span class="sub">Archiviata</span>{/if}
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</Card>

{#if archivedCount > 0}
  <div class="archived-toggle">
    <button class="btn btn-ghost btn-small" onclick={() => (showArchived = !showArchived)}>
      {showArchived ? 'Nascondi archiviate' : `Mostra archiviate (${archivedCount})`}
    </button>
  </div>
{/if}

{#if sheet}
  {#key sheet}
  <CategoryForm
    category={sheet.category}
    categories={data.value}
    defaultKind={kind}
    defaultParentId={sheet.parentId ?? null}
    defaultColor={SWATCHES[tops.length % SWATCHES.length]}
    onaddchild={sheet.category ? () => (sheet = { parentId: sheet!.category!.id }) : undefined}
    onclose={() => (sheet = null)}
  />
  {/key}
{/if}

<style>

  .switch {
    margin-bottom: var(--space-3);
  }

  .tip {
    margin-bottom: var(--space-3);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .children {
    padding-left: calc(12px + var(--space-3));
  }

  .children .list-row {
    min-height: 44px;
  }

  .child {
    font-weight: 400;
  }

  .archived {
    color: var(--color-text-muted);
    text-decoration: line-through;
  }

  .archived-toggle {
    margin-top: var(--space-3);
    text-align: center;
  }
</style>
