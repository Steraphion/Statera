<script lang="ts">
  import Sheet from './Sheet.svelte'
  import type { Refs } from '../lib/data/refs.svelte'
  import * as tp from '../lib/data/templates'
  import { categoryLabel } from '../lib/data/transactions'
  import type { Template } from '../lib/data/types'
  import { errorMessage, withTimeout } from '../lib/data/util'
  import { formatEuro } from '../lib/format'

  let { templates, refs, onclose }: { templates: Template[]; refs: Refs; onclose: () => void } = $props()

  let error = $state('')
  let armed = $state<string | null>(null)

  function detail(t: Template): string {
    const src = t.parts
      .map((p) => {
        const [k, id] = p.source.split(':')
        return (k === 'c' ? refs.cardMap.get(id)?.name : refs.accountMap.get(id)?.name) ?? '—'
      })
      .join(' + ')
    const cat = t.type === 'trasferimento'
      ? `→ ${refs.accountMap.get(t.toAccountId ?? '')?.name ?? '—'}`
      : categoryLabel(t.categoryId, refs.categoryMap)
    const amount = tp.hasAmount(t) ? formatEuro(t.parts.reduce((s, p) => s + p.amount, 0)) : 'importo da scrivere'
    return [cat, src, t.parts.some((p) => p.vouchers) ? '' : amount].filter(Boolean).join(' · ')
  }

  async function act(fn: () => Promise<unknown>) {
    error = ''
    try {
      await withTimeout(fn())
    } catch (e) {
      error = errorMessage(e)
    }
  }
</script>

<Sheet title="Preferiti" {onclose} {error}>
  <p class="hint">
    Un tocco su un preferito lo registra con la data di oggi. Per aggiungerne uno, nel modulo del movimento scegli
    "Salva anche tra i preferiti".
  </p>
  <ul class="list">
    {#each templates as t, i (t.id)}
      <li class="row">
        <div class="main">
          <input
            class="input"
            aria-label="Nome del preferito {i + 1}"
            value={t.name}
            maxlength="30"
            onchange={(e) => act(() => tp.renameTemplate(t.id, e.currentTarget.value))}
          />
          <span class="detail">{detail(t)}</span>
        </div>
        <div class="tools">
          <button class="btn btn-ghost icon" aria-label="Sposta {t.name} prima" disabled={i === 0} onclick={() => act(() => tp.moveTemplate(t.id, -1))}>↑</button>
          <button class="btn btn-ghost icon" aria-label="Sposta {t.name} dopo" disabled={i === templates.length - 1} onclick={() => act(() => tp.moveTemplate(t.id, 1))}>↓</button>
          <button
            class="btn btn-ghost icon danger"
            class:armed={armed === t.id}
            aria-label={armed === t.id ? `Conferma: elimina ${t.name}` : `Elimina ${t.name}`}
            onclick={() => {
              if (armed === t.id) act(() => tp.deleteTemplate(t.id))
              else {
                armed = t.id
                setTimeout(() => (armed = armed === t.id ? null : armed), 4000)
              }
            }}>{armed === t.id ? 'Elimina' : '×'}</button
          >
        </div>
      </li>
    {/each}
  </ul>
  {#snippet footer()}
    <button class="btn btn-primary" onclick={onclose}>Fatto</button>
  {/snippet}
</Sheet>

<style>
  .hint {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    margin-bottom: var(--space-3);
  }

  .list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: var(--space-2);
    align-items: start;
  }

  .main {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    min-width: 0;
  }

  .detail {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .tools {
    display: flex;
    gap: var(--space-hair);
  }

  .icon {
    min-width: 40px;
    min-height: var(--size-touch);
    padding: 0 var(--space-2);
  }

  .danger {
    color: var(--color-danger);
  }

  .armed {
    border: 1px solid var(--color-danger);
  }
</style>
