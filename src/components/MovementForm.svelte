<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import Segmented from './Segmented.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import CategoryPicker from './CategoryPicker.svelte'
  import DateField from './DateField.svelte'
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

  /** Una riga del pagamento come appare nel modulo. */
  interface PartRow {
    source: string
    amountText: string
    vouchersText: string
  }

  // Valori di partenza del modulo (letti una volta all'apertura)
  const orig = untrack(() => movement)
  const last = untrack(() => lastSources)
  const origKeys = orig ? orig.parts.map(mv.sourceKey) : []

  let type = $state<TransactionType>(orig?.type ?? 'uscita')
  let parts = $state<PartRow[]>(
    orig
      ? orig.parts.map((p) => ({
          source: mv.sourceKey(p),
          amountText: p.vouchers === null ? centsToInput(p.amount) : '',
          vouchersText: p.vouchers ? String(p.vouchers) : '',
        }))
      : [{ source: '', amountText: '', vouchersText: '' }],
  )
  let date = $state(orig?.date ?? today())
  let toAccountId = $state<string>(orig?.toAccountId ?? '')
  let categoryId = $state<string | null>(orig?.categoryId ?? null)
  let description = $state(orig?.description ?? '')
  let notes = $state(orig?.notes ?? '')
  let showNotes = $state(!!orig?.notes)
  let error = $state('')
  let busy = $state(false)
  let savedCount = $state(0)
  let amountInput: HTMLInputElement | undefined = $state()

  const allOptions = $derived(mv.sourceOptions(accounts, cards, origKeys))
  // Nei trasferimenti si sceglie un conto (non una carta) e niente buoni pasto
  const options = $derived(
    type === 'trasferimento'
      ? allOptions.filter((o) => !o.isCard && o.account.type !== 'buoni_pasto')
      : allOptions,
  )
  const mixed = $derived(parts.length > 1)
  const first = $derived(options.find((o) => o.key === parts[0].source))

  function optionOf(key: string) {
    return allOptions.find((o) => o.key === key)
  }
  function isVoucher(key: string): boolean {
    return optionOf(key)?.account.type === 'buoni_pasto'
  }

  const destinations = $derived(
    accounts.filter(
      (a) =>
        a.deletedAt === null &&
        a.type !== 'buoni_pasto' &&
        a.id !== first?.account.id &&
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
      if (t !== 'uscita' && parts.length > 1) parts = [parts[0]]
      if (!(orig && t === orig.type)) {
        parts[0].source = proposedSource(t)
        return
      }
    }
    if (!options.some((o) => o.key === parts[0].source)) parts[0].source = proposedSource(t)
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

  /** Importo di una riga in centesimi, o null se non valido. */
  function rowAmount(r: PartRow): number | null {
    if (isVoucher(r.source)) {
      const n = Number(r.vouchersText)
      return Number.isInteger(n) && n > 0 ? n * (optionOf(r.source)?.account.voucherValue ?? 0) : null
    }
    const c = parseEuro(r.amountText)
    return c !== null && c > 0 ? c : null
  }

  const mixedTotal = $derived(parts.reduce((s, r) => s + (rowAmount(r) ?? 0), 0))

  function addPart() {
    const used = new Set(parts.map((p) => p.source))
    const next = options.find((o) => !used.has(o.key))?.key ?? ''
    parts.push({ source: next, amountText: '', vouchersText: '' })
  }

  // Movimento precedente alla data del saldo iniziale: non cambierebbe il saldo
  const beforeStart = $derived.by(() => {
    const involved = [
      ...parts.map((p) => optionOf(p.source)?.account),
      type === 'trasferimento' ? accounts.find((a) => a.id === toAccountId) : undefined,
    ]
    const names = new Set<string>()
    for (const a of involved) if (a && date < a.initialDate) names.add(a.name)
    return [...names]
  })

  async function save(addAnother: boolean) {
    error = ''
    for (const r of parts) {
      if (rowAmount(r) === null) {
        error = isVoucher(r.source) ? 'Indica quanti buoni' : 'Inserisci un importo valido (es. 12,50)'
        if (!mixed) amountInput?.focus()
        return
      }
    }
    const input: mv.MovementInput = {
      type,
      date,
      parts: parts.map((r) => ({
        source: r.source,
        amount: isVoucher(r.source) ? 0 : (parseEuro(r.amountText) ?? 0),
        vouchers: isVoucher(r.source) ? Number(r.vouchersText) : null,
      })),
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
        parts = [{ source: parts[0].source, amountText: '', vouchersText: '' }]
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
  const sourceLabel = $derived(type === 'trasferimento' ? 'Da' : type === 'entrata' ? 'Su' : 'Con')
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

      {#if !mixed}
        {#if isVoucher(parts[0].source)}
          {@const preview = rowAmount(parts[0])}
          <label class="field">
            <span>Numero di buoni</span>
            <input
              class="input amount num"
              bind:value={parts[0].vouchersText}
              type="number"
              min="1"
              step="1"
              inputmode="numeric"
              placeholder="0"
            />
            {#if preview}<span class="hint">Pari a {formatEuro(preview)}</span>{/if}
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
              bind:value={parts[0].amountText}
              inputmode="decimal"
              placeholder="0,00"
              autocomplete="off"
              autofocus={!orig}
            />
          </label>
        {/if}

        <div class="row-2">
          <label class="field">
            <span>{sourceLabel}</span>
            <select class="input" bind:value={parts[0].source}>
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
            <DateField bind:value={date} />
          {/if}
        </div>

        {#if type === 'uscita' && options.length > 1}
          <button type="button" class="btn btn-ghost link" onclick={addPart}>+ Pagamento misto (es. buoni + carta)</button>
        {/if}
      {:else}
        <fieldset class="field">
          <legend>Pagamento misto</legend>
          <div class="parts">
            {#each parts as r, i (i)}
              <div class="part">
                <select class="input" aria-label="Fonte {i + 1}" bind:value={r.source}>
                  {#each options as o (o.key)}
                    <option value={o.key} disabled={o.key !== r.source && parts.some((p) => p.source === o.key)}>
                      {o.label}
                    </option>
                  {/each}
                </select>
                {#if isVoucher(r.source)}
                  <input
                    class="input num small-input"
                    aria-label="Buoni {i + 1}"
                    bind:value={r.vouchersText}
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    placeholder="n. buoni"
                  />
                {:else}
                  <input
                    class="input num small-input"
                    aria-label="Importo {i + 1}"
                    bind:value={r.amountText}
                    inputmode="decimal"
                    placeholder="0,00"
                    autocomplete="off"
                  />
                {/if}
                <button
                  type="button"
                  class="btn btn-ghost remove"
                  aria-label="Togli fonte {i + 1}"
                  onclick={() => parts.splice(i, 1)}>×</button
                >
              </div>
            {/each}
          </div>
          <div class="parts-foot">
            {#if parts.length < options.length}
              <button type="button" class="btn btn-ghost link" onclick={addPart}>+ Aggiungi fonte</button>
            {:else}
              <span></span>
            {/if}
            <span class="num total">Totale {formatEuro(mixedTotal)}</span>
          </div>
        </fieldset>
        <DateField bind:value={date} />
      {/if}

      {#if type === 'trasferimento'}
        <DateField bind:value={date} />
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
        <button type="button" class="btn btn-ghost link" onclick={() => (showNotes = true)}>+ Aggiungi nota</button>
      {/if}

      {#if beforeStart.length > 0}
        <p class="warn">
          La data è precedente al saldo iniziale di {beforeStart.join(' e ')}: il movimento verrà registrato e
          comparirà nei totali del mese, ma non cambierà il saldo del conto (lo considera già compreso).
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

  .link {
    align-self: flex-start;
    padding: 0;
    min-height: 32px;
  }

  .parts {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .part {
    display: grid;
    grid-template-columns: 1fr 110px 36px;
    gap: var(--space-2);
    align-items: center;
  }

  .remove {
    min-height: 36px;
    padding: 0;
    font-size: var(--text-lg);
    color: var(--color-text-muted);
  }

  .parts-foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: var(--space-1);
  }

  .total {
    font-weight: 650;
    color: var(--color-expense);
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
