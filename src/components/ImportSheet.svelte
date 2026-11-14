<script lang="ts">
  import Sheet from './Sheet.svelte'
  import { db } from '../lib/data/db'
  import * as im from '../lib/data/csvImport'
  import type { Account, Category, Transaction } from '../lib/data/types'
  import { alive, byOrder, errorMessage } from '../lib/data/util'
  import { formatEuro, formatShortDay } from '../lib/format'
  import { toast } from '../lib/toast.svelte'

  let { onclose }: { onclose: () => void } = $props()

  let fileInput: HTMLInputElement | undefined = $state()
  let fileName = $state('')
  let rows = $state.raw<string[][]>([])
  let mapping = $state<im.Mapping>({})
  let hasHeader = $state(true)
  let accountId = $state('')
  let skipDuplicates = $state(true)
  let error = $state('')
  let busy = $state(false)

  let accounts = $state.raw<Account[]>([])
  let categories = $state.raw<Category[]>([])
  let existing = $state.raw<Transaction[]>([])
  Promise.all([db.accounts.toArray(), db.categories.toArray(), db.transactions.toArray()]).then(([a, c, t]) => {
    accounts = alive(a)
      .filter((x) => !x.archived && x.type !== 'buoni_pasto')
      .sort(byOrder)
    categories = c
    existing = t
    accountId = accounts[0]?.id ?? ''
  })

  const FIELDS = Object.keys(im.FIELD_LABELS) as im.Field[]
  const width = $derived(Math.max(0, ...rows.slice(0, 5).map((r) => r.length)))
  const columns = $derived(
    Array.from({ length: width }, (_, i) => (hasHeader && rows[0]?.[i]?.trim() ? rows[0][i].trim() : `Colonna ${i + 1}`)),
  )
  const items = $derived(
    rows.length && accountId && mapping.date !== undefined && mapping.amount !== undefined
      ? im.buildImport(rows, mapping, { accountId, categories, existing, hasHeader })
      : [],
  )
  const ok = $derived(items.filter((i) => !i.problem && !(skipDuplicates && i.duplicate)))
  const dupes = $derived(items.filter((i) => !i.problem && i.duplicate).length)
  const bad = $derived(items.filter((i) => i.problem).length)
  const guessed = $derived(ok.filter((i) => i.categoryGuessed).length)
  const catName = $derived(new Map(categories.map((c) => [c.id, c.name])))

  async function pick(e: Event) {
    error = ''
    const f = (e.currentTarget as HTMLInputElement).files?.[0]
    if (!f) return
    if (f.size > 5 * 1024 * 1024) {
      error = 'File troppo grande (massimo 5 MB)'
      return
    }
    try {
      const parsed = im.parseCsv(await f.text())
      if (parsed.length === 0) throw new Error('Il file è vuoto')
      const guess = im.guessMapping(parsed[0])
      hasHeader = Object.keys(guess).length >= 2
      mapping = hasHeader ? guess : {}
      rows = parsed
      fileName = f.name
    } catch (err) {
      error = errorMessage(err)
    } finally {
      if (fileInput) fileInput.value = ''
    }
  }

  function setField(f: im.Field, v: string) {
    const next = { ...mapping }
    if (v === '') delete next[f]
    else next[f] = Number(v)
    mapping = next
  }

  async function run() {
    error = ''
    if (!ok.length) {
      error = 'Nessun movimento da importare'
      return
    }
    busy = true
    try {
      const n = await im.importItems(items, accountId, skipDuplicates)
      toast.show(n === 1 ? '1 movimento importato' : `${n} movimenti importati`)
      onclose()
    } catch (err) {
      error = errorMessage(err)
    } finally {
      busy = false
    }
  }
</script>

<Sheet title="Importa da CSV" {onclose} {error}>
  <div class="form">
    <p class="hint">
      Va bene un file esportato da Statera o l'estratto conto in CSV della tua banca. Il file viene letto solo sul
      dispositivo. I trasferimenti non si importano.
    </p>
    <div class="pick">
      <button type="button" class="btn" onclick={() => fileInput?.click()}>{fileName ? 'Cambia file' : 'Scegli il file CSV'}</button>
      {#if fileName}<span class="file">{fileName}</span>{/if}
      <input bind:this={fileInput} type="file" accept=".csv,text/csv,text/plain" class="visually-hidden" tabindex="-1" aria-label="File CSV" onchange={pick} />
    </div>

    {#if rows.length}
      <label class="check">
        <input type="checkbox" bind:checked={hasHeader} />
        <span>La prima riga contiene i nomi delle colonne</span>
      </label>

      <fieldset class="field">
        <legend>Colonne del file</legend>
        <div class="map">
          {#each FIELDS as f (f)}
            <label class="field">
              <span>{im.FIELD_LABELS[f]}{f === 'date' || f === 'amount' ? ' *' : ''}</span>
              <select class="input" value={mapping[f] ?? ''} onchange={(e) => setField(f, e.currentTarget.value)}>
                <option value="">—</option>
                {#each columns as c, i (i)}<option value={i}>{c}</option>{/each}
              </select>
            </label>
          {/each}
        </div>
        <span class="hint">Senza la colonna Tipo: importi negativi = uscite, positivi = entrate.</span>
      </fieldset>

      <label class="field">
        <span>Sul conto</span>
        <select class="input" bind:value={accountId}>
          {#each accounts as a (a.id)}<option value={a.id}>{a.name}</option>{/each}
        </select>
      </label>
      <label class="check">
        <input type="checkbox" bind:checked={skipDuplicates} />
        <span>Salta i movimenti già presenti (stessa data, importo e descrizione)</span>
      </label>

      {#if mapping.date === undefined || mapping.amount === undefined}
        <p class="warn">Indica almeno le colonne Data e Importo.</p>
      {:else}
        <p class="summary" role="status">
          <strong>{ok.length}</strong> da importare{dupes ? ` · ${dupes} già presenti` : ''}{bad ? ` · ${bad} con problemi (non importati)` : ''}{guessed
            ? ` · ${guessed} senza categoria riconosciuta (andranno in "Altro")`
            : ''}
        </p>
        <ul class="preview">
          {#each items.slice(0, 8) as it (it.line)}
            <li class:off={!!it.problem || (skipDuplicates && it.duplicate)}>
              <span class="d">{it.date ? formatShortDay(it.date) : '—'}</span>
              <span class="t">
                {it.description || '(senza descrizione)'}
                <small>
                  {#if it.problem}Riga {it.line}: {it.problem}{:else if it.duplicate}Già presente{:else}{catName.get(it.categoryId ?? '') ?? '—'}{it.categoryGuessed ? ' (non riconosciuta)' : ''}{/if}
                </small>
              </span>
              <span class="num a" class:income={it.type === 'entrata'}>{it.type === 'uscita' ? '−' : it.type === 'entrata' ? '+' : ''}{formatEuro(it.amount)}</span>
            </li>
          {/each}
        </ul>
        {#if items.length > 8}<p class="hint">…e altre {items.length - 8} righe.</p>{/if}
      {/if}
    {/if}
  </div>
  {#snippet footer()}
    <button type="button" class="btn" onclick={onclose}>Annulla</button>
    <button type="button" class="btn btn-primary" disabled={busy || ok.length === 0} onclick={run}>
      {ok.length === 1 ? 'Importa 1 movimento' : `Importa ${ok.length} movimenti`}
    </button>
  {/snippet}
</Sheet>

<style>
  .hint {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .pick {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
  }

  .file {
    font-size: var(--text-sm);
    word-break: break-all;
  }

  .map {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-2) var(--space-3);
  }

  .check {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-height: 40px;
    font-size: var(--text-sm);
  }

  .check input {
    width: 20px;
    height: 20px;
    flex: none;
    accent-color: var(--color-accent);
  }

  .warn {
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
  }

  .summary {
    font-size: var(--text-sm);
  }

  .preview {
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: var(--text-sm);
  }

  .preview li {
    display: grid;
    grid-template-columns: 56px minmax(0, 1fr) auto;
    gap: var(--space-2);
    padding: var(--space-2) 0;
    border-top: 1px solid var(--color-border);
  }

  .preview li.off {
    opacity: 0.55;
  }

  .preview .d {
    color: var(--color-text-muted);
  }

  .preview .t {
    display: flex;
    flex-direction: column;
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .preview small {
    color: var(--color-text-muted);
    font-size: var(--text-xs);
  }

  .preview .a {
    color: var(--color-expense);
  }

  .preview .a.income {
    color: var(--color-income);
  }
</style>
