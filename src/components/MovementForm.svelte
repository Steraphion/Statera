<script lang="ts">
  import { amountKeys, HAS_KEYPAD } from '../lib/keypad.svelte'
  import { onMount, untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import Segmented from './Segmented.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import CategoryPicker from './CategoryPicker.svelte'
  import DateField from './DateField.svelte'
  import * as mv from '../lib/data/transactions'
  import * as rec from '../lib/data/recurring'
  import * as tp from '../lib/data/templates'
  import type { Account, Card, Category, Frequency, Recurring, Template, Transaction, TransactionType } from '../lib/data/types'
  import { db } from '../lib/data/db'
  import { errorMessage, today, withTimeout } from '../lib/data/util'
  import { centsToInput, evalAmount, formatEuro, isExpression } from '../lib/format'

  let {
    movement,
    recurring,
    confirm,
    defaultRepeat,
    defaultType,
    template,
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
    /** Nuovo movimento di questo tipo (es. dalla scorciatoia "Nuova entrata"). */
    defaultType?: TransactionType
    /** Nuovo movimento a partire da un preferito (senza importo fisso). */
    template?: Template
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
  const fav0 = untrack(() => template)
  /** Modello da cui partire (ripetizione in modifica o da confermare, oppure un preferito). */
  const tpl: (Pick<Recurring, 'type' | 'parts' | 'categoryId' | 'toAccountId' | 'description'> & { notes?: string }) | null =
    rec0 ?? conf0?.r ?? fav0 ?? null
  const initType = orig?.type ?? tpl?.type ?? null
  const last = untrack(() => lastSources)
  const origKeys = orig ? orig.parts.map(mv.sourceKey) : tpl ? tpl.parts.map((p) => p.source) : []

  let type = $state<TransactionType>(initType ?? untrack(() => defaultType) ?? 'uscita')
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
            amountText: p.vouchers === null && p.amount > 0 ? centsToInput(p.amount) : '',
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
  // Etichette
  let tags = $state<string[]>(orig?.tags ?? [])
  let tagText = $state('')
  let showTags = $state((orig?.tags?.length ?? 0) > 0)

  // Ripartizione su più categorie
  interface SplitRow {
    categoryId: string
    amountText: string
  }
  const canSplit = !rec0 && !conf0
  let splitMode = $state((orig?.splits?.length ?? 0) >= 2)
  let splitRows = $state<SplitRow[]>(
    (orig?.splits ?? []).map((sp) => ({ categoryId: sp.categoryId, amountText: centsToInput(sp.amount) })),
  )

  // Salva anche tra i preferiti
  const canFavorite = !rec0 && !conf0 && !fav0
  let favorite = $state(false)
  let favName = $state('')
  let favAmount = $state(true)
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
    if (type === 'trasferimento' && splitMode) splitMode = false
    for (const r of splitRows) {
      const c = categories.find((x) => x.id === r.categoryId)
      if (c && c.kind !== type) r.categoryId = ''
    }
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
    const c = evalAmount(r.amountText)
    return c !== null && c > 0 ? c : null
  }

  /** Un calcolo nel campo importo (es. "12,50+3,20") diventa il risultato quando si esce dal campo. */
  function settleAmount(r: PartRow) {
    if (!isExpression(r.amountText)) return
    const c = evalAmount(r.amountText)
    if (c !== null && c > 0) r.amountText = centsToInput(c)
  }

  /** Aggiunge "+" all'importo (le tastiere numeriche dei telefoni spesso non lo hanno). */
  function appendPlus() {
    const t = parts[0].amountText.trim()
    if (t && !/[+\-*/x×÷:]$/i.test(t)) parts[0].amountText = t + '+'
    amountInput?.focus()
  }

  // ---------- Suggerimenti dalla descrizione ----------
  let history = $state.raw<Transaction[]>([])
  let descFocused = $state(false)
  let pickedDesc = $state<string | null>(null)
  let activeSuggestion = $state(-1)
  onMount(() => {
    // Ultimi 18 mesi: bastano per i movimenti abituali
    const d = new Date()
    d.setMonth(d.getMonth() - 18)
    const from = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
    db.transactions
      .where('date')
      .aboveOrEqual(from)
      .toArray()
      .then((rows) => (history = rows))
      .catch(() => {})
  })
  const suggestions = $derived(
    descFocused && description !== pickedDesc && !orig && !tpl
      ? mv.descriptionSuggestions(history, type, description)
      : [],
  )

  function applySuggestion(sg: mv.Suggestion) {
    const t = sg.last
    description = sg.description
    pickedDesc = sg.description
    activeSuggestion = -1
    // Categoria, se non ne è già stata scelta una e se esiste ancora
    const cat = categories.find((c) => c.id === t.categoryId)
    if (categoryId === null && cat && cat.kind === type && !cat.archived) categoryId = cat.id
    const keys = t.parts.map(mv.sourceKey)
    const valid = keys.every((k) => options.some((o) => o.key === k))
    const emptyAmounts = parts.every((r) => !r.amountText.trim() && !r.vouchersText.trim())
    if (valid && emptyAmounts) {
      // Nessun importo scritto: si riprende tutto il pagamento dell'ultima volta
      parts = t.parts.map((p) => ({
        source: mv.sourceKey(p),
        amountText: p.vouchers === null ? centsToInput(p.amount) : '',
        vouchersText: p.vouchers ? String(p.vouchers) : '',
      }))
    } else if (valid && keys.length === 1 && parts.length === 1) {
      parts[0].source = keys[0]
    }
    if (type === 'trasferimento' && t.toAccountId && destinations.some((a) => a.id === t.toAccountId)) {
      toAccountId = t.toAccountId
    }
  }

  function onDescKey(e: KeyboardEvent) {
    if (!suggestions.length) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      activeSuggestion = (activeSuggestion + 1) % suggestions.length
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      activeSuggestion = (activeSuggestion - 1 + suggestions.length) % suggestions.length
    } else if (e.key === 'Enter' && activeSuggestion >= 0) {
      e.preventDefault()
      applySuggestion(suggestions[activeSuggestion])
    } else if (e.key === 'Escape') {
      e.stopPropagation()
      pickedDesc = description
    }
  }

  function suggestionDetail(sg: mv.Suggestion): string {
    const t = sg.last
    const cat = t.categoryId ? mv.categoryLabel(t.categoryId, new Map(categories.map((c) => [c.id, c]))) : ''
    const src = t.parts
      .map((p) => optionOf(mv.sourceKey(p))?.label ?? '')
      .filter(Boolean)
      .join(' + ')
    return [cat, src, formatEuro(mv.total(t))].filter(Boolean).join(' · ')
  }

  const mixedTotal = $derived(parts.reduce((s, r) => s + (rowAmount(r) ?? 0), 0))
  const grandTotal = $derived(mixed ? mixedTotal : (rowAmount(parts[0]) ?? 0))

  // ---------- Etichette ----------
  const knownTags = $derived(mv.allTags(history))
  function addTag() {
    const t = tagText.trim()
    if (!t) return
    try {
      tags = mv.cleanTags([...tags, t])
      tagText = ''
    } catch (e) {
      error = errorMessage(e)
    }
  }

  // ---------- Ripartizione ----------
  /** Categorie del tipo scelto: le principali in ordine alfabetico, ognuna seguita dalle sue sottocategorie. */
  const catOptions = $derived.by(() => {
    const list = categories.filter((c) => c.kind === type && c.deletedAt === null && (!c.archived || splitRows.some((r) => r.categoryId === c.id)))
    const tops = list.filter((c) => c.parentId === null).sort((a, b) => a.name.localeCompare(b.name, 'it'))
    return tops.flatMap((t) => [
      { id: t.id, label: t.name },
      ...list
        .filter((c) => c.parentId === t.id)
        .sort((a, b) => a.name.localeCompare(b.name, 'it'))
        .map((c) => ({ id: c.id, label: `${t.name} › ${c.name}` })),
    ])
  })
  const splitSum = $derived(splitRows.reduce((s, r) => s + (evalAmount(r.amountText) ?? 0), 0))

  function startSplit() {
    splitRows = [
      { categoryId: categoryId ?? '', amountText: grandTotal ? centsToInput(grandTotal) : '' },
      { categoryId: '', amountText: '' },
    ]
    splitMode = true
  }
  function stopSplit() {
    const first = splitRows.find((r) => r.categoryId)
    if (first) categoryId = first.categoryId
    splitMode = false
    splitRows = []
  }

  /** Righe della ripartizione pronte da salvare; una sola riga senza importo prende il resto. */
  function splitsForSave(): { categoryId: string; amount: number }[] {
    const rows = splitRows.map((r) => ({ categoryId: r.categoryId, amount: r.amountText.trim() ? evalAmount(r.amountText) : null }))
    const empty = rows.filter((r) => r.amount === null)
    if (empty.length === 1) {
      const rest = grandTotal - rows.reduce((s, r) => s + (r.amount ?? 0), 0)
      if (rest > 0) empty[0].amount = rest
    }
    if (rows.some((r) => !r.categoryId)) throw new Error('Scegli la categoria di ogni parte della ripartizione')
    if (rows.some((r) => r.amount === null || r.amount <= 0)) throw new Error('Scrivi l\'importo di ogni parte della ripartizione')
    return rows.map((r) => ({ categoryId: r.categoryId, amount: r.amount! }))
  }

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
    if (tagText.trim()) addTag()
    let splits: { categoryId: string; amount: number }[] | undefined
    if (splitMode && type !== 'trasferimento') {
      try {
        splits = splitsForSave()
      } catch (e) {
        error = errorMessage(e)
        return
      }
    }
    const input: mv.MovementInput = {
      type,
      date,
      parts: parts.map((r) => ({
        source: r.source,
        amount: isVoucher(r.source) ? 0 : (evalAmount(r.amountText) ?? 0),
        vouchers: isVoucher(r.source) ? intOf(r.vouchersText) : null,
      })),
      categoryId: type === 'trasferimento' ? null : splits ? splits[0].categoryId : categoryId,
      toAccountId: type === 'trasferimento' ? toAccountId : null,
      description,
      notes,
      tags,
      splits,
    }
    busy = true
    try {
      if (favorite) {
        const catName = categories.find((c) => c.id === input.categoryId)?.name ?? ''
        const fav = favAmount ? input : { ...input, parts: input.parts.map((p) => ({ ...p, amount: 0, vouchers: null })) }
        await withTimeout(tp.createTemplate(favName.trim() || tp.suggestedName(input, catName), fav))
      }
      const schedule = { frequency: (repeat || 'mensile') as Frequency, date, endDate: endDate || null, auto: mode === 'auto' }
      if (rec0) await withTimeout(rec.updateRecurring(rec0.id, input, schedule))
      else if (conf0) await withTimeout(rec.confirmOccurrence(conf0.r, input, conf0.date))
      else if (orig) await withTimeout(mv.updateMovement(orig.id, input))
      else if (repeat) await withTimeout(rec.createRecurring(input, schedule, today()))
      else await withTimeout(mv.createMovement(input))
      if (addAnother) {
        parts = [{ source: parts[0].source, amountText: '', vouchersText: '' }]
        description = ''
        pickedDesc = null
        notes = ''
        showNotes = false
        categoryId = null
        repeat = ''
        endDate = ''
        favorite = false
        favName = ''
        tags = []
        showTags = false
        splitMode = false
        splitRows = []
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
              use:amountKeys={'integer'}
              inputmode="numeric"
              placeholder="0"
            />
            {#if preview}<span class="hint">Pari a {formatEuro(preview)}</span>{/if}
          </label>
        {:else}
          {@const calc = isExpression(parts[0].amountText) ? evalAmount(parts[0].amountText) : null}
          <div class="field">
            <label for="amount-input">Importo (€)</label>
            <div class="amount-row">
              <!-- svelte-ignore a11y_autofocus -->
              <input
                id="amount-input"
                bind:this={amountInput}
                class="input amount num"
                class:income={type === 'entrata'}
                class:expense={type === 'uscita'}
                bind:value={parts[0].amountText}
                use:amountKeys
                inputmode="decimal"
                placeholder="0,00"
                autocomplete="off"
                autofocus={!orig}
              />
              {#if !HAS_KEYPAD}
                <button
                  type="button"
                  class="btn plus"
                  aria-label="Aggiungi un importo (somma)"
                  title="Somma più importi, es. 12,50+3,20"
                  onmousedown={(e) => e.preventDefault()}
                  onclick={appendPlus}>+</button
                >
              {/if}
            </div>
            {#if isExpression(parts[0].amountText)}
              <span class="hint num" role="status">{calc !== null ? `= ${formatEuro(calc)}` : 'Calcolo non valido'}</span>
            {/if}
          </div>
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
                    use:amountKeys={'integer'}
                    inputmode="numeric"
                    placeholder="n. buoni"
                  />
                {:else}
                  <input
                    class="input num small-input"
                    aria-label="Importo {i + 1}"
                    bind:value={r.amountText}
                    onblur={() => settleAmount(r)}
                    use:amountKeys
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

      <div class="field desc">
        <label for="desc-input">Descrizione</label>
        <input
          id="desc-input"
          class="input"
          bind:value={description}
          onfocus={() => (descFocused = true)}
          onblur={() => (descFocused = false)}
          oninput={() => (activeSuggestion = -1)}
          onkeydown={onDescKey}
          maxlength="80"
          autocomplete="off"
          role="combobox"
          aria-expanded={suggestions.length > 0}
          aria-controls="desc-suggestions"
          aria-autocomplete="list"
          placeholder={type === 'trasferimento' ? 'Es. Prelievo' : 'Es. Supermercato'}
        />
        {#if suggestions.length}
          <ul class="suggestions" id="desc-suggestions" role="listbox" aria-label="Suggerimenti">
            {#each suggestions as sg, i (sg.description)}
              <li role="option" aria-selected={i === activeSuggestion}>
                <button
                  type="button"
                  class="suggestion"
                  class:active={i === activeSuggestion}
                  onmousedown={(e) => e.preventDefault()}
                  onclick={() => applySuggestion(sg)}
                >
                  <span class="s-name">{sg.description}</span>
                  <span class="s-detail">{suggestionDetail(sg)}</span>
                </button>
              </li>
            {/each}
          </ul>
        {/if}
      </div>

      {#if type === 'trasferimento'}
        <DateField bind:value={date} label={dateLabel} />
      {:else if splitMode}
        <fieldset class="field">
          <legend>Categorie (ripartizione)</legend>
          <div class="parts">
            {#each splitRows as r, i (i)}
              <div class="part">
                <select class="input" aria-label="Categoria {i + 1}" bind:value={r.categoryId}>
                  <option value="" disabled>Scegli…</option>
                  {#each catOptions as o (o.id)}
                    <option value={o.id} disabled={o.id !== r.categoryId && splitRows.some((x) => x.categoryId === o.id)}>{o.label}</option>
                  {/each}
                </select>
                <input
                  class="input num small-input"
                  aria-label="Importo categoria {i + 1}"
                  bind:value={r.amountText}
                  use:amountKeys
                  inputmode="decimal"
                  placeholder={i === splitRows.length - 1 ? 'il resto' : '0,00'}
                  autocomplete="off"
                />
                {#if splitRows.length > 2}
                  <button type="button" class="btn btn-ghost remove" aria-label="Togli categoria {i + 1}" onclick={() => splitRows.splice(i, 1)}>×</button>
                {:else}
                  <span></span>
                {/if}
              </div>
            {/each}
          </div>
          <div class="parts-foot">
            <button type="button" class="btn btn-ghost link" onclick={() => splitRows.push({ categoryId: '', amountText: '' })}>+ Aggiungi categoria</button>
            <span
              class="num split-sum"
              class:off={grandTotal > 0 && (splitSum > grandTotal || (splitSum < grandTotal && splitRows.filter((r) => !r.amountText.trim()).length !== 1))}
            >
              {formatEuro(splitSum)} di {formatEuro(grandTotal)}
            </span>
          </div>
          {#if grandTotal > 0 && splitSum < grandTotal && splitRows.filter((r) => !r.amountText.trim()).length === 1}
            <span class="hint">La riga senza importo prende il resto: {formatEuro(grandTotal - splitSum)}.</span>
          {/if}
          <button type="button" class="btn btn-ghost link" onclick={stopSplit}>Una sola categoria</button>
        </fieldset>
      {:else}
        <CategoryPicker {categories} kind={type} bind:value={categoryId} keepId={orig?.categoryId ?? tpl?.categoryId ?? null} />
        {#if canSplit}
          <button type="button" class="btn btn-ghost link" onclick={startSplit}>Dividi tra più categorie</button>
        {/if}
      {/if}

      {#if showTags}
        <div class="field">
          <label for="tag-input">Etichette</label>
          {#if tags.length}
            <div class="tags">
              {#each tags as tg, i (tg)}
                <span class="tag">#{tg}<button type="button" aria-label="Togli l'etichetta {tg}" onclick={() => tags.splice(i, 1)}>×</button></span>
              {/each}
            </div>
          {/if}
          <input
            id="tag-input"
            class="input"
            list="tag-options"
            bind:value={tagText}
            maxlength="24"
            autocomplete="off"
            placeholder="Es. Vacanze estate, poi Invio"
            onkeydown={(e) => {
              if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault()
                addTag()
              }
            }}
            onblur={addTag}
          />
          <datalist id="tag-options">
            {#each knownTags.filter((k) => !tags.includes(k)) as k (k)}<option value={k}></option>{/each}
          </datalist>
          <span class="hint">Servono a ritrovare e sommare le spese di un viaggio, un evento, un progetto.</span>
        </div>
      {:else}
        <button type="button" class="btn btn-ghost link" onclick={() => (showTags = true)}>+ Aggiungi etichette</button>
      {/if}

      {#if showNotes}
        <label class="field">
          <span>Note</span>
          <textarea class="input" bind:value={notes} rows="3" maxlength="500"></textarea>
        </label>
      {:else}
        <button type="button" class="btn btn-ghost link" onclick={() => (showNotes = true)}>+ Aggiungi nota</button>
      {/if}

      {#if canFavorite}
        <div class="favorite">
          <label class="check">
            <input type="checkbox" bind:checked={favorite} />
            <span>Salva anche tra i preferiti</span>
          </label>
          {#if favorite}
            <label class="field">
              <span>Nome del preferito</span>
              <input
                class="input"
                bind:value={favName}
                maxlength="30"
                placeholder={tp.suggestedName({ description }, categories.find((c) => c.id === categoryId)?.name ?? '')}
              />
            </label>
            <label class="check">
              <input type="checkbox" bind:checked={favAmount} />
              <span>Ricorda anche l'importo</span>
            </label>
            <span class="hint">
              {favAmount
                ? 'Un tocco sul preferito registra subito il movimento.'
                : "Un tocco sul preferito apre il modulo già compilato: scrivi solo l'importo."}
            </span>
          {/if}
        </div>
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
    min-height: var(--size-row);
    font-size: var(--text-xl);
    font-weight: 700;
  }

  .amount.income {
    color: var(--color-income);
  }

  .amount.expense {
    color: var(--color-expense);
  }

  .amount-row {
    display: grid;
    grid-auto-flow: column;
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-2);
  }

  .plus {
    min-width: var(--size-row);
    min-height: var(--size-row);
    font-size: var(--text-xl);
    padding: 0;
  }

  .desc {
    position: relative;
  }

  /* Sovrapposto al modulo: comparendo e scomparendo non sposta le voci sotto */
  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 5;
    list-style: none;
    margin: var(--space-1) 0 0;
    padding: var(--space-1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    box-shadow: var(--shadow-1);
  }

  .suggestion {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
    min-height: var(--size-touch);
    padding: var(--space-2) var(--space-3);
    border: 0;
    border-radius: var(--radius-sm);
    background: none;
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
  }

  .suggestion:hover,
  .suggestion.active {
    background: var(--color-accent-soft);
  }

  .s-name {
    font-weight: 600;
  }

  .s-detail {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .link {
    align-self: flex-start;
    padding: 0;
    min-height: var(--size-cat-s);
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
    min-height: var(--size-btn-s);
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

  .split-sum {
    font-size: var(--text-sm);
    font-weight: 700;
  }

  .split-sum.off {
    color: var(--color-danger);
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1);
  }

  .tag {
    display: inline-flex;
    align-items: center;
    gap: var(--space-hair);
    padding: var(--space-hair) var(--space-hair) var(--space-hair) var(--space-2);
    border-radius: var(--radius-sm);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
  }

  .tag button {
    min-width: var(--size-step);
    min-height: var(--size-step);
    border: 0;
    background: none;
    color: var(--color-text-muted);
    font-size: var(--text-lg);
    cursor: pointer;
  }

  .total {
    font-weight: 700;
  }

  textarea.input {
    resize: vertical;
  }

  .favorite {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
  }

  .favorite .hint {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .check {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-height: 40px;
    cursor: pointer;
  }

  .check input {
    width: 20px;
    height: 20px;
    accent-color: var(--color-accent);
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
