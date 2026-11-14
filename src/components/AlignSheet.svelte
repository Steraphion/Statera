<script lang="ts">
  import Sheet from './Sheet.svelte'
  import DateField from './DateField.svelte'
  import { accountBalance } from '../lib/data/balances'
  import { alignBalance } from '../lib/data/transactions'
  import type { Account, Transaction } from '../lib/data/types'
  import { errorMessage, today, withTimeout } from '../lib/data/util'
  import { formatEuro, formatVouchers, parseEuro } from '../lib/format'
  import { toast } from '../lib/toast.svelte'

  let { account, transactions, onclose }: { account: Account; transactions: Transaction[]; onclose: () => void } =
    $props()

  const isVoucher = $derived(account.type === 'buoni_pasto')
  let realText = $state('')
  let date = $state(today())
  let error = $state('')
  let busy = $state(false)

  const current = $derived(accountBalance(account, transactions.filter((t) => t.date <= date)))
  const real = $derived.by(() => {
    const t = realText.trim()
    if (!t) return null
    if (isVoucher) return /^\d+$/.test(t) ? Number(t) : NaN
    return parseEuro(t) ?? NaN
  })
  const delta = $derived(
    real === null || Number.isNaN(real) ? null : isVoucher ? real - (current.vouchers ?? 0) : real - current.amount,
  )
  const fmt = (n: number) => (isVoucher ? formatVouchers(n) : formatEuro(n))

  async function save(e: Event) {
    e.preventDefault()
    error = ''
    if (real === null || Number.isNaN(real)) {
      error = isVoucher ? 'Indica quanti buoni hai (es. 12)' : 'Inserisci il saldo reale (es. 1.234,56)'
      return
    }
    busy = true
    try {
      const m = await withTimeout(alignBalance(account.id, isVoucher ? { vouchers: real } : { amount: real }, date))
      toast.show(m ? `Saldo di ${account.name} allineato` : `Il saldo di ${account.name} era già giusto`)
      onclose()
    } catch (err) {
      error = errorMessage(err)
    } finally {
      busy = false
    }
  }
</script>

<Sheet title="Allinea saldo" {onclose} {error}>
  <form id="align-form" class="form" novalidate onsubmit={save}>
    <p class="hint">
      Scrivi {isVoucher ? 'quanti buoni hai davvero' : "il saldo che vedi nell'app della banca o nel portafoglio"}.
      Statera registra la differenza come movimento "Rettifica saldo", così il saldo torna giusto senza toccare lo
      storico.
    </p>
    <div class="now">
      <span>Saldo in Statera {date === today() ? 'oggi' : 'a quella data'}</span>
      <span class="num">{isVoucher ? formatVouchers(current.vouchers ?? 0) : formatEuro(current.amount)}</span>
    </div>
    <label class="field">
      <span>{isVoucher ? 'Buoni disponibili' : 'Saldo reale (€)'}</span>
      <!-- svelte-ignore a11y_autofocus -->
      <input
        class="input num big"
        bind:value={realText}
        inputmode={isVoucher ? 'numeric' : 'decimal'}
        placeholder={isVoucher ? '0' : '0,00'}
        autocomplete="off"
        autofocus
      />
    </label>
    <DateField bind:value={date} label="Data" />
    {#if date < account.initialDate}
      <p class="warn">La data è precedente al saldo iniziale del conto ({account.initialDate.split('-').reverse().join('/')}).</p>
    {/if}
    {#if delta !== null}
      <p class="result" role="status">
        {#if delta === 0}
          Il saldo è già giusto: non serve nessuna rettifica.
        {:else}
          Differenza <strong class="num">{delta > 0 ? '+' : '−'}{fmt(Math.abs(delta))}</strong>: verrà registrata
          {delta > 0 ? "un'entrata" : "un'uscita"} "Rettifica saldo".
        {/if}
      </p>
    {/if}
  </form>
  {#snippet footer()}
    <button type="button" class="btn" onclick={onclose}>Annulla</button>
    <button type="submit" form="align-form" class="btn btn-primary" disabled={busy}>Allinea</button>
  {/snippet}
</Sheet>

<style>
  .hint {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .now {
    display: flex;
    justify-content: space-between;
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    font-size: var(--text-sm);
  }

  .big {
    min-height: 52px;
    font-size: var(--text-lg);
    font-weight: 700;
  }

  .result {
    font-size: var(--text-sm);
  }

  .warn {
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
  }
</style>
