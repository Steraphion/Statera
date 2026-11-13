<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import Segmented from './Segmented.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import CategoryPicker from './CategoryPicker.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Account, Card, Category, Transaction, TransactionType } from '../lib/data/types'
  import { today } from '../lib/data/util'
  import { centsToInput, formatEuro, parseEuro } from '../lib/format'

  let {
    movement,
    accounts,
    cards,
    categories,
    lastSources,
    onclose,
  }: {
    movement?: Transaction
    accounts: Account[]
    cards: Card[]
    categories: Category[]
    lastSources: Partial<Record<TransactionType, string>>
    onclose: () => void
  } = $props()

  // Valori di partenza del modulo (letti una volta all'apertura)
  const orig = untrack(() => movement)
  const origSource = orig ? mv.sourceKey(orig.parts[0]) : null
  const last = untrack(() => lastSources)

  let type = $state<TransactionType>(orig?.type ?? 'uscita')
  let amountText = $state(orig && orig.parts[0].vouchers === null ? centsToInput(mv.total(orig)) : '')
  let vouchersText = $state(orig?.parts[0].vouchers ? String(orig.parts[0].vouchers) : '')
  let date = $state(orig?.date ?? today())
  let source = $state<string>(origSource ?? '')
  let toAccountId = $state<string>(orig?.toAccountId ?? '')
  let categoryId = $state<string | null>(orig?.categoryId ?? null)
  let description = $state(orig?.description ?? '')
  let notes = $state(orig?.notes ?? '')
  let showNotes = $state(!!orig?.notes)
  let error = $state('')
  let busy = $state(false)
  let savedCount = $state(0)
  let amountInput: HTMLInputElement | undefined = $state()

  const keep = origSource ? [origSource] : []
  const allOptions = $derived(mv.sourceOptions(accounts, cards, keep))
  // Nei trasferimenti si sceglie un conto (non una carta) e niente buoni pasto
  const options = $derived(
    type === 'trasferimento'
      ? allOptions.filter((o) => !o.isCard && o.account.type !== 'buoni_pasto')
      : allOptions,
  )
  const selected = $derived(options.find((o) => o.key === source))
  const isVoucher = $derived(selected?.account.type === 'buoni_pasto')
  const destinations = $derived(
    accounts.filter(
      (a) =>
        a.deletedAt === null &&
        a.type !== 'buoni_pasto' &&
        a.id !== selected?.account.id &&
        (!a.archived || a.id === orig?.toAccountId),
    ),
  )

  // Fonte proposta: quella usata l'ultima volta per questo tipo; altrimenti
  // il primo conto che non sia buoni pasto. Si ricalcola quando cambia il tipo.
  function proposedSource(t: TransactionType): string {
    const preferred = last[t]
    return (
      options.find((o) => o.key === preferred)?.key ??
      options.find((o) => o.account.type !== 'buoni_pasto')?.key ??
      options[0]?.key ??
      ''
    )
  }

  let sourceForType: TransactionType | null = orig ? orig.type : null
  $effect(() => {
    const t = type
    if (sourceForType !== t) {
      sourceForType = t
      if (!(orig && t === orig.type)) {
        source = proposedSource(t)
        return
      }
    }
    if (!options.some((o) => o.key === source)) source = proposedSource(t)
  })

  $effect(() => {
    if (type !== 'trasferimento') return
    if (!destinations.some((a) => a.id === toAccountId)) toAccountId = destinations[0]?.id ?? ''
  })

  // Cambiando tipo, una categoria del tipo sbagliato non vale più
  $effect(() => {
    const cat = categories.find((c) => c.id === categoryId)
    if (cat && cat.kind !== type) categoryId = null
  })

  // Movimento precedente alla data del saldo iniziale: non cambierebbe il saldo
  const beforeStart = $derived.by(() => {
    const involved = [selected?.account, accounts.find((a) => a.id === toAccountId && type === 'trasferimento')]
    return involved.filter((a): a is Account => !!a && date < a.initialDate)
  })

  const voucherPreview = $derived.by(() => {
    const n = Number(vouchersText)
    const v = selected?.account.voucherValue ?? 0
    return Number.isInteger(n) && n > 0 ? formatEuro(n * v) : null
  })

  async function save(addAnother: boolean) {
    error = ''
    const amount = isVoucher ? 0 : parseEuro(amountText)
    if (!isVoucher && (amount === null || amount <= 0)) {
      error = 'Inserisci un importo valido (es. 12,50)'
      amountInput?.focus()
      return
    }
    const input: mv.MovementInput = {
      type,
      date,
      source,
      amount: amount ?? 0,
      vouchers: isVoucher ? Number(vouchersText) : null,
      categoryId: type === 'trasferimento' ? null : categoryId,
      toAccountId: type === 'trasferimento' ? toAccountId : null,
      description,
      notes,
    }
    busy = true
    try {
      if (orig) await mv.updateMovement(orig.id, input)
      else await mv.createMovement(input)
      if (addAnother) {
        amountText = ''
        vouchersText = ''
        description = ''
        notes = ''
        showNotes = false
        categoryId = null
        savedCount++
        amountInput?.focus()
      } else {
        onclose()
      }
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    } finally {
      busy = false
    }
  }

  async function remove() {
    if (!orig) return
    await mv.deleteMovement(orig.id)
    onclose()
  }

  const title = orig ? 'Modifica movimento' : 'Nuovo movimento'
</script>

<Sheet {title} {onclose}>
  {#if options.length === 0}
    <p class="empty-note">Per registrare un movimento crea prima un conto nella sezione Conti.</p>
  {:else}
    <form
      id="movement-form"
      class="form"
      onsubmit={(e) => {
        e.preventDefault()
        save(false)
      }}
    >
      <Segmented
        label="Tipo di movimento"
        bind:value={type}
        options={[
          { value: 'uscita', label: 'Uscita' },
          { value: 'entrata', label: 'Entrata' },
          { value: 'trasferimento', label: 'Trasferimento' },
        ]}
      />

      {#if isVoucher}
        <label class="field">
          <span>Numero di buoni</span>
          <input
            class="input amount num"
            bind:value={vouchersText}
            type="number"
            min="1"
            step="1"
            inputmode="numeric"
            placeholder="0"
          />
          {#if voucherPreview}<span class="hint">Pari a {voucherPreview}</span>{/if}
        </label>
      {:else}
        <label class="field">
          <span>Importo (€)</span>
          <!-- svelte-ignore a11y_autofocus -->
          <input
            bind:this={amountInput}
            class="input amount num"
            class:income={type === 'entrata'}
            class:expense={type === 'uscita'}
            bind:value={amountText}
            inputmode="decimal"
            placeholder="0,00"
            autocomplete="off"
            autofocus={!orig}
          />
        </label>
      {/if}

      <div class="row-2">
        <label class="field">
          <span>{type === 'trasferimento' ? 'Da' : type === 'entrata' ? 'Su' : 'Con'}</span>
          <select class="input" bind:value={source}>
            {#each options as o (o.key)}
              <option value={o.key}>{o.label}</option>
            {/each}
          </select>
        </label>

        {#if type === 'trasferimento'}
          <label class="field">
            <span>A</span>
            <select class="input" bind:value={toAccountId}>
              {#each destinations as a (a.id)}
                <option value={a.id}>{a.name}</option>
              {/each}
            </select>
          </label>
        {:else}
          <label class="field">
            <span>Data</span>
            <input class="input" type="date" bind:value={date} required />
          </label>
        {/if}
      </div>

      {#if type === 'trasferimento'}
        <label class="field">
          <span>Data</span>
          <input class="input" type="date" bind:value={date} required />
        </label>
      {:else}
        <CategoryPicker {categories} kind={type} bind:value={categoryId} keepId={orig?.categoryId ?? null} />
      {/if}

      <label class="field">
        <span>Descrizione</span>
        <input
          class="input"
          bind:value={description}
          maxlength="80"
          placeholder={type === 'trasferimento' ? 'Es. Prelievo' : 'Es. Supermercato'}
        />
      </label>

      {#if showNotes}
        <label class="field">
          <span>Note</span>
          <textarea class="input" bind:value={notes} rows="3" maxlength="500"></textarea>
        </label>
      {:else}
        <button type="button" class="btn btn-ghost add-note" onclick={() => (showNotes = true)}>+ Aggiungi nota</button>
      {/if}

      {#if beforeStart.length > 0}
        <p class="warn">
          La data è precedente al saldo iniziale di {beforeStart.map((a) => a.name).join(' e ')}: il movimento
          verrà registrato ma non cambierà il saldo del conto.
        </p>
      {/if}

      {#if error}
        <p class="error-box" role="alert">{error}</p>
      {/if}
      {#if savedCount > 0 && !error}
        <p class="saved" role="status">
          {savedCount === 1 ? 'Movimento salvato.' : `${savedCount} movimenti salvati.`} Inserisci il prossimo.
        </p>
      {/if}
    </form>
  {/if}

  {#snippet footer()}
    {#if orig}
      <DeleteButton onconfirm={remove} />
    {:else if options.length > 0}
      <button type="button" class="btn" disabled={busy} onclick={() => save(true)}>Salva e nuovo</button>
    {/if}
    {#if options.length > 0}
      <button type="submit" form="movement-form" class="btn btn-primary" disabled={busy}>Salva</button>
    {/if}
  {/snippet}
</Sheet>

<style>
  .amount {
    min-height: 56px;
    font-size: var(--text-xl);
    font-weight: 650;
  }

  .amount.income {
    color: var(--color-income);
  }

  .amount.expense {
    color: var(--color-expense);
  }

  .add-note {
    align-self: flex-start;
    padding: 0;
    min-height: 32px;
  }

  textarea.input {
    resize: vertical;
  }

  .warn {
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
  }

  .saved {
    font-size: var(--text-sm);
    color: var(--color-income);
  }
</style>
