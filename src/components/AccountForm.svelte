<script lang="ts">
  import { amountKeys } from '../lib/keypad.svelte'
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import ColorPicker from './ColorPicker.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import * as repo from '../lib/data/repo'
  import { ACCOUNT_TYPE_LABELS, type Account, type AccountType, type SwatchKey } from '../lib/data/types'
  import { today, errorMessage, withTimeout } from '../lib/data/util'
  import { centsToInput, parseEuro } from '../lib/format'

  let {
    account,
    defaultColor = 's1',
    onclose,
  }: { account?: Account; defaultColor?: SwatchKey; onclose: () => void } = $props()

  // Valori di partenza del modulo (letti una volta all'apertura)
  const orig = untrack(() => account)

  const editing = !!orig
  let name = $state(orig?.name ?? '')
  let type = $state<AccountType>(orig?.type ?? 'conto_corrente')
  let initial = $state(orig && orig.type !== 'buoni_pasto' ? centsToInput(orig.initialBalance) : '0,00')
  let initialDate = $state(orig?.initialDate ?? today())
  let voucherValue = $state(orig?.voucherValue ? centsToInput(orig.voucherValue) : '')
  let initialVouchers = $state(String(orig?.initialVouchers ?? 0))
  let color = $state<SwatchKey>(orig?.color ?? untrack(() => defaultColor))
  let error = $state('')
  let busy = $state(false)

  const types = Object.entries(ACCOUNT_TYPE_LABELS) as [AccountType, string][]

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
    const isVoucher = type === 'buoni_pasto'
    const balance = isVoucher ? 0 : parseEuro(initial)
    if (balance === null) {
      error = 'Il saldo iniziale non è un importo valido'
      return
    }
    const value = isVoucher ? parseEuro(voucherValue) : null
    if (isVoucher && (value === null || value <= 0)) {
      error = 'Indica il valore di un buono (es. 8,00)'
      return
    }
    const count = isVoucher ? (/^\d+$/.test(String(initialVouchers).trim()) ? Number(String(initialVouchers).trim()) : NaN) : null
    if (isVoucher && Number.isNaN(count)) {
      error = 'Il numero di buoni deve essere un numero intero (es. 10)'
      return
    }
    const input: repo.AccountInput = {
      name,
      type,
      initialBalance: balance,
      initialDate,
      voucherValue: value,
      initialVouchers: count,
      color,
    }
    run(() => (account ? repo.updateAccount(account.id, input) : repo.createAccount(input)))
  }
</script>

<Sheet title={editing ? 'Modifica conto' : 'Nuovo conto'} {onclose} {error}>
  <form novalidate id="account-form" class="form" onsubmit={save}>
    <label class="field">
      <span>Nome</span>
      <input class="input" bind:value={name} placeholder="Es. Conto principale" maxlength="40" required />
    </label>

    <label class="field">
      <span>Tipo</span>
      <select class="input" bind:value={type}>
        {#each types as [value, label] (value)}
          <option {value}>{label}</option>
        {/each}
      </select>
      {#if editing && account?.type !== type && (type === 'contanti' || type === 'buoni_pasto')}
        <span class="hint">Le carte collegate a questo conto verranno rimosse.</span>
      {/if}
    </label>

    {#if type === 'buoni_pasto'}
      <div class="row-2">
        <label class="field">
          <span>Valore di un buono (€)</span>
          <input class="input num" bind:value={voucherValue} use:amountKeys inputmode="decimal" placeholder="8,00" />
        </label>
        <label class="field">
          <span>Buoni disponibili</span>
          <input class="input num" bind:value={initialVouchers} use:amountKeys={'integer'} inputmode="numeric" />
        </label>
      </div>
    {:else}
      <label class="field">
        <span>Saldo iniziale (€)</span>
        <input class="input num" bind:value={initial} use:amountKeys inputmode="decimal" />
        <span class="hint">Quanto c'è sul conto alla data qui sotto. Può essere negativo.</span>
      </label>
    {/if}

    <label class="field">
      <span>{type === 'buoni_pasto' ? 'Disponibili alla data' : 'Saldo alla data'}</span>
      <input class="input" type="date" bind:value={initialDate} required />
      <span class="hint">
        Il saldo vale dall'inizio di questo giorno: i movimenti con questa data o successivi lo modificano, quelli
        precedenti no. Se il saldo comprende già entrate o spese che vuoi vedere nei totali del mese (es. l'ultimo
        stipendio), registrale con la loro data reale, precedente a questa: compariranno nel mese senza essere contate
        due volte.
      </span>
    </label>

    <ColorPicker bind:value={color} />
  </form>

  {#snippet footer()}
    {#if account}
      <DeleteButton onconfirm={() => run(() => repo.deleteAccount(account.id))} />
      <button
        type="button"
        class="btn"
        onclick={() => run(() => repo.setAccountArchived(account.id, !account.archived))}
      >
        {account.archived ? 'Ripristina' : 'Archivia'}
      </button>
    {/if}
    <button type="submit" form="account-form" class="btn btn-primary" disabled={busy}>Salva</button>
  {/snippet}
</Sheet>
