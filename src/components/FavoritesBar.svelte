<script lang="ts">
  import TemplatesSheet from './TemplatesSheet.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import type { Refs } from '../lib/data/refs.svelte'
  import * as tp from '../lib/data/templates'
  import { deleteMovement } from '../lib/data/transactions'
  import type { Template } from '../lib/data/types'
  import { errorMessage, today, withTimeout } from '../lib/data/util'
  import { formatEuro } from '../lib/format'
  import { toast } from '../lib/toast.svelte'

  let { refs, onopen }: { refs: Refs; onopen: (t: Template) => void } = $props()

  const list = live(
    async () => (await db.templates.toArray()).filter((t) => t.deletedAt === null).sort(tp.byOrder),
    [] as Template[],
  )
  let managing = $state(false)
  let busy = $state(false)

  function amountOf(t: Template): string {
    if (!tp.hasAmount(t)) return ''
    const cents = t.parts.reduce((s, p) => {
      if (p.vouchers) {
        const [, id] = p.source.split(':')
        return s + p.vouchers * (refs.accountMap.get(id)?.voucherValue ?? 0)
      }
      return s + p.amount
    }, 0)
    return formatEuro(cents)
  }

  async function tap(t: Template) {
    if (!tp.hasAmount(t)) return onopen(t)
    if (busy) return
    busy = true
    try {
      const m = await withTimeout(tp.registerTemplate(t, today()))
      toast.show(`${t.name} registrato · ${amountOf(t)}`, {
        label: 'Annulla',
        run: async () => {
          await deleteMovement(m.id)
          toast.show(`${t.name}: registrazione annullata`)
        },
      })
    } catch (e) {
      toast.show(`${t.name}: ${errorMessage(e)}. Puoi modificarlo da "Gestisci".`)
    } finally {
      busy = false
    }
  }
</script>

{#if list.value.length}
  <section class="fav" aria-label="Preferiti">
    <div class="chips">
      {#each list.value as t (t.id)}
        <button class="chip" class:expense={t.type === 'uscita'} class:income={t.type === 'entrata'} onclick={() => tap(t)} disabled={busy}>
          <span class="name">{t.name}</span>
          {#if tp.hasAmount(t)}
            <span class="amount num">{amountOf(t)}</span>
          {:else}
            <span class="amount ask">scrivi l'importo</span>
          {/if}
        </button>
      {/each}
      <button class="chip manage" onclick={() => (managing = true)}>Gestisci</button>
    </div>
  </section>
{/if}

{#if managing}
  <TemplatesSheet templates={list.value} {refs} onclose={() => (managing = false)} />
{/if}

<style>
  .fav {
    margin-bottom: var(--space-3);
  }

  .chips {
    display: flex;
    gap: var(--space-2);
    overflow-x: auto;
    padding-bottom: var(--space-1);
    scrollbar-width: thin;
  }

  .chip {
    flex: none;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
    min-height: 48px;
    max-width: 180px;
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    color: var(--color-text);
    font: inherit;
    cursor: pointer;
  }

  .chip:hover {
    border-color: var(--color-accent);
  }

  .chip:disabled {
    opacity: 0.6;
  }

  .name {
    font-weight: 600;
    font-size: var(--text-sm);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }

  .amount {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .chip.expense .amount {
    color: var(--color-expense);
  }

  .chip.income .amount {
    color: var(--color-income);
  }

  .chip .amount.ask {
    color: var(--color-text-muted);
  }

  .manage {
    justify-content: center;
    color: var(--color-accent);
    font-weight: 600;
    font-size: var(--text-sm);
    border-style: dashed;
  }
</style>
