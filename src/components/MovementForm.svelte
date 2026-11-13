<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import Segmented from './Segmented.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import CategoryPicker from './CategoryPicker.svelte'
  import DateField from './DateField.svelte'
  import * as mv from '../lib/data/transactions'
  import * as rec from '../lib/data/recurring'
  import type { Account, Card, Category, Frequency, Recurring, Transaction, TransactionType } from '../lib/data/types'
  import { errorMessage, today, withTimeout } from '../lib/data/util'
  import { centsToInput, formatEuro, parseEuro } from '../lib/format'

  let {
    movement,
    recurring,
    confirm,
    defaultRepeat,
    accounts,
    cards,
    categories,
    lastSources,
    onclose,
  }: {
    movement?: Transaction
    /** Modifica di una ripetizione (modello). */
    recurring?: Recurring
    /** Conferma di un'occorrenza "da confermare". */
    confirm?: { r: Recurring; date: string }
    /** Nuovo movimento con ripetizione già impostata. */
    defaultRepeat?: Frequency
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
  const rec0 = untrack(() => recurring)
  const conf0 = untrack(() => confirm)
  /** Modello da cui partire (ripetizione in modifica o da confermare). */
  const tpl = rec0 ?? conf0?.r ?? null
  const initType = orig?.type ?? tpl?.type ?? null
  const last = untrack(() => lastSources)
  const origKeys = orig ? orig.parts.map(mv.sourceKey) : tpl ? tpl.parts.map((p) => p.source) : []

  let type = $state<TransactionType>(initType ?? 'uscita')
  let parts = $state<PartRow[]>(
    orig
      ? orig.parts.map((p) => ({
          source: mv.sourceKey(p),
          amountText: p.vouchers === null ? centsToInput(p.amount) : '',
          vouchersText: p.vouchers ? String(p.vouchers) : '',
        }))
      : tpl
        ? tpl.parts.map((p) => ({
            source: p.source,
            amountText: p.vouchers === null ? centsToInput(p.amount) : '',
            vouchersText: p.vouchers ? String(p.vouchers) : '',
          }))
        : [{ source: '', amountText: '', vouchersText: '' }],
  )
  let date = $state(orig?.date ?? (rec0 ? (rec.nextDate(rec0) ?? today()) : (conf0?.date ?? today())))
  let toAccountId = $state<string>(orig?.toAccountId ?? tpl?.toAccountId ?? '')
  let categoryId = $state<string | null>(orig?.categoryId ?? tpl?.categoryId ?? null)
  let description = $state(orig?.description ?? tpl?.description ?? '')
  let notes = $state(orig?.notes ?? tpl?.notes ?? '')
  let showNotes = $state(!!(orig?.notes || tpl?.notes))

  // Ripetizione
  const canRepeat = !orig && !conf0
  let repeat = $state<Frequency | ''>(rec0?.frequency ?? untrack(() => defaultRepeat) ?? '')
  let mode = $state<'auto' | 'conferma'>(rec0 && !rec0.auto ? 'conferma' : 'auto')
  let endDate = $state(rec0?.endDate ?? '')
  const dateLabel = rec0 ? 'Prossima data' : 'Data'
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
        (!a.archived || a.id === (orig?.toAccountId ?? tpl?.toAccountId)),
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

  let sourceForType: TransactionType | null = initType
  $effect(() => {
    const t = type
    if (sourceForType !== t) {
      sourceForType = t
      if (t !== 'uscita' && parts.length > 1) parts = [parts[0]]
      if (!(initType && t === initType)) {
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
  /** Numero intero scritto dall'utente (accetta spazi), o NaN. */
  function intOf(text: unknown): number {
    const t = String(text ?? '').trim()
    return /^\d+$/.test(t) ? Number(t) : NaN
  }

  function rowAmount(r: PartRow): number | null {
    if (isVoucher(r.source)) {
      const n = intOf(r.vouchersText)
      return Number.isInteger(n) && n > 0 ? n * (optionOf(r.source)?.account.voucherValue ?? 0) : null
    }
    const c = parseEuro(r.amountText)
    return c !== null && c > 0 ? c : null
  }

  const mixedTotal = $derived(parts.reduce((s, r) => s + (rowAmount(r) ?? 0), 0))

  /** Nuova riga del pagamento misto: propone la fonte più probabile. */
  function addPart() {
    const used = new Set(parts.map((p) => p.source))
    const free = options.filter((o) => !used.has(o.key))
    const hasVoucher = parts.some((p) => isVoucher(p.source))
    const lastKey = last.uscita
    const next = hasVoucher
      ? // ci sono già i buoni: il resto di solito si paga con la carta/conto usato l'ultima volta
        (free.find((o) => o.key === lastKey && o.account.type !== 'buoni_pasto') ??
        free.find((o) => o.account.type !== 'buoni_pasto'))
      : // altrimenti di solito si aggiungono i buoni pasto
        free.find((o) => o.account.type === 'buoni_pasto')
    parts.push({ source: (next ?? free[0])?.key ?? '', amountText: '', vouchersText: '' })
  }

  /** Cambio fonte di una riga: se la fonte era già in un'altra riga, le due si scambiano. */
  function setSource(i: number, key: string) {
    const prev = parts[i].source
    const j = parts.findIndex((p, k) => k !== i && p.source === key)
    if (j >= 0) parts[j].source = prev
    parts[i].source = key
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
        vouchers: isVoucher(r.source) ? intOf(r.vouchersText) : null,
      })),
      categoryId: type === 'trasferimento' ? null : categoryId,
      toAccountId: type === 'trasferimento' ? toAccountId : null,
      description,
      notes,
    }
    busy = true
    try {
      const schedule = { frequency: (repeat || 'mensile') as Frequency, date, endDate: endDate || null, auto: mode === 'auto' }
      if (rec0) await withTimeout(rec.updateRecurring(rec0.id, input, schedule))
      else if (conf0) await withTimeout(rec.confirmOccurrence(conf0.r, input, conf0.date))
      else if (orig) await withTimeout(mv.updateMovement(orig.id, input))
      else if (repeat) await withTimeout(rec.createRecurring(input, schedule, today()))
      else await withTimeout(mv.createMovement(input))
      if (addAnother) {
        parts = [{ source: parts[0].source, amountText: '', vouchersText: '' }]
        description = ''
        notes = ''
        showNotes = false
        categoryId = null
        repeat = ''
        endDate = ''
        savedCount++
        amountInput?.focus()
      } else {
        onclose()
      }
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }

  async function remove() {
    if (!orig) return
    try {
      await withTimeout(mv.deleteMovement(orig.id))
      onclose()
    } catch (e) {
      error = errorMessage(e)
    }
  }

  async function act(fn: () => Promise<unknown>) {
    error = ''
    try {
      await withTimeout(fn())
      onclose()
    } catch (e) {
      error = errorMessage(e)
    }
  }

  const title = rec0
    ? 'Modifica ripetizione'
    : conf0
      ? 'Conferma movimento'
      : orig
        ? 'Modifica movimento'
        : 'Nuovo movimento'
  const sourceLabel = $derived(type === 'trasferimento' ? 'Da' : type === 'entrata' ? 'Su' : 'Con')
</script>

<Sheet {title} {onclose} {error}>
  {#if options.length === 0}
    <p class="empty-note">Per registrare un movimento crea prima un conto nella sezione Conti.</p>
  {:else}
    <form
      novalidate
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
            <DateField bind:value={date} label={dateLabel} />
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
                <select
                  class="input"
                  aria-label="Fonte {i + 1}"
                  value={r.source}
                  onchange={(e) => setSource(i, e.currentTarget.value)}
                >
                  {#each options as o (o.key)}
                    <option value={o.key}>{o.label}</option>
                  {/each}
                </select>
                {#if isVoucher(r.source)}
                  <input
                    class="input num small-input"
                    aria-label="Buoni {i + 1}"
                    bind:value={r.vouchersText}
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
        <DateField bind:value={date} label={dateLabel} />
      {/if}

      {#if type === 'trasferimento'}
        <DateField bind:value={date} label={dateLabel} />
      {:else}
        <CategoryPicker {categories} kind={type} bind:value={categoryId} keepId={orig?.categoryId ?? tpl?.categoryId ?? null} />
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

      {#if canRepeat || rec0}
        <div class="repeat">
          <label class="field">
            <span>Ripeti</span>
            <select class="input" bind:value={repeat}>
              {#if !rec0}<option value="">Non si ripete</option>{/if}
              <option value="settimanale">Ogni settimana</option>
              <option value="mensile">Ogni mese</option>
              <option value="annuale">Ogni anno</option>
            </select>
            {#if repeat}
              <span class="hint">
                {rec.describeFrequency({ frequency: repeat, startDate: date })}.
                {rec0 ? 'Le modifiche valgono dalla prossima data; i movimenti già registrati non cambiano.' : ''}
              </span>
            {/if}
          </label>
          {#if repeat}
            <div class="field">
              <span>Registrazione</span>
              <Segmented
                label="Registrazione"
                bind:value={mode}
                options={[
                  { value: 'auto', label: 'Automatica' },
                  { value: 'conferma', label: 'Da confermare' },
                ]}
              />
              <span class="hint">
                {mode === 'auto'
                  ? 'Il movimento viene registrato da solo alla data prevista.'
                  : "Alla data prevista te lo chiede, così puoi correggere l'importo (utile per le bollette)."}
              </span>
            </div>
            <label class="field">
              <span>Fino al (facoltativo)</span>
              <input class="input" type="date" bind:value={endDate} />
            </label>
          {/if}
        </div>
      {/if}

      {#if beforeStart.length > 0}
        <p class="warn">
          La data è precedente al saldo iniziale di {beforeStart.join(' e ')}: il movimento verrà registrato e
          comparirà nei totali del mese, ma non cambierà il saldo del conto (lo considera già compreso).
        </p>
      {/if}
      {#if savedCount > 0 && !error}
        <p class="saved" role="status">
          {savedCount === 1 ? 'Movimento salvato.' : `${savedCount} movimenti salvati.`} Inserisci il prossimo.
        </p>
      {/if}
    </form>
  {/if}

  {#snippet footer()}
    {#if rec0}
      <DeleteButton
        label="Elimina ripetizione"
        onconfirm={() => act(() => rec.deleteRecurring(rec0.id))}
      />
      <button type="button" class="btn" onclick={() => act(() => rec.setRecurringPaused(rec0.id, !rec0.paused))}>
        {rec0.paused ? 'Riprendi' : 'Sospendi'}
      </button>
    {:else if conf0}
      <button type="button" class="btn" onclick={() => act(() => rec.skipOccurrence(conf0.r, conf0.date))}>Salta</button>
    {:else if orig}
      <DeleteButton onconfirm={remove} />
    {:else if options.length > 0}
      <button type="button" class="btn" disabled={busy} onclick={() => save(true)}>Salva e nuovo</button>
    {/if}
    {#if options.length > 0}
      <button type="submit" form="movement-form" class="btn btn-primary" disabled={busy}>
        {conf0 ? 'Registra' : 'Salva'}
      </button>
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

  .repeat {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
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
