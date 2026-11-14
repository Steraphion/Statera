<script lang="ts">
  import CategoryIcon from './CategoryIcon.svelte'
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import * as repo from '../lib/data/repo'
  import type { Category } from '../lib/data/types'
  import { byName, errorMessage, withTimeout } from '../lib/data/util'
  import { centsToInput, parseEuro } from '../lib/format'

  let { categories, onclose }: { categories: Category[]; onclose: () => void } = $props()

  const tops = untrack(() =>
    categories.filter((c) => c.deletedAt === null && !c.archived && c.parentId === null && c.kind === 'uscita').sort(byName),
  )
  let values = $state<Record<string, string>>(
    Object.fromEntries(tops.map((c) => [c.id, c.monthlyBudget ? centsToInput(c.monthlyBudget) : ''])),
  )
  let error = $state('')
  let busy = $state(false)

  async function save() {
    error = ''
    const changes: [string, number | null][] = []
    for (const c of tops) {
      const text = values[c.id].trim()
      const cents = text ? parseEuro(text) : null
      if (text && (cents === null || cents <= 0)) {
        error = `Budget di "${c.name}" non valido (es. 300 o 250,50)`
        return
      }
      if ((c.monthlyBudget ?? null) !== cents) changes.push([c.id, cents])
    }
    busy = true
    try {
      await withTimeout(Promise.all(changes.map(([id, cents]) => repo.setCategoryBudget(id, cents))))
      onclose()
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }
</script>

<Sheet title="Budget mensili" {onclose} {error}>
  <form
    novalidate
    class="form"
    onsubmit={(e) => {
      e.preventDefault()
      save()
    }}
  >
    <p class="muted">
      Quanto vuoi spendere al massimo ogni mese per categoria (sottocategorie comprese). Lascia vuoto per nessun
      budget.
    </p>
    {#each tops as c (c.id)}
      <label class="row">
        <span class="name"><CategoryIcon category={c} size="s" />{c.name}</span>
        <input class="input num" bind:value={values[c.id]} inputmode="decimal" placeholder="—" aria-label="Budget {c.name} (€)" />
      </label>
    {/each}
    <button type="submit" hidden aria-hidden="true" tabindex="-1"></button>
  </form>
  {#snippet footer()}
    <button type="button" class="btn btn-primary" disabled={busy} onclick={save}>Salva</button>
  {/snippet}
</Sheet>

<style>
  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 120px;
    align-items: center;
    gap: var(--space-3);
  }

  .name {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: 600;
  }

  .row .input {
    text-align: right;
  }
</style>
