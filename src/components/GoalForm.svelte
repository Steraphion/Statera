<script lang="ts">
  import { amountKeys } from '../lib/keypad.svelte'
  import Sheet from './Sheet.svelte'
  import ColorPicker from './ColorPicker.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import * as gl from '../lib/data/goals'
  import type { Account, Goal, SwatchKey } from '../lib/data/types'
  import { errorMessage, withTimeout } from '../lib/data/util'
  import { centsToInput, parseEuro } from '../lib/format'
  import { untrack } from 'svelte'

  let { goal, accounts, defaultColor = 's3', onclose }: { goal?: Goal; accounts: Account[]; defaultColor?: SwatchKey; onclose: () => void } =
    $props()

  const g0 = untrack(() => goal)
  let name = $state(g0?.name ?? '')
  let targetText = $state(g0 ? centsToInput(g0.target) : '')
  let accountId = $state(g0?.accountId ?? '')
  let savedText = $state(g0 && !g0.accountId && g0.saved ? centsToInput(g0.saved) : '')
  let dueDate = $state(g0?.dueDate ?? '')
  let color = $state<SwatchKey>(g0?.color ?? untrack(() => defaultColor))
  let error = $state('')
  let busy = $state(false)

  const choices = $derived(accounts.filter((a) => a.type !== 'buoni_pasto' && (!a.archived || a.id === g0?.accountId)))

  async function save(e: Event) {
    e.preventDefault()
    error = ''
    const target = parseEuro(targetText)
    if (target === null || target <= 0) {
      error = "Indica l'importo da raggiungere (es. 3000)"
      return
    }
    const saved = savedText.trim() ? parseEuro(savedText) : 0
    if (saved === null) {
      error = "Importo accantonato non valido"
      return
    }
    const input: gl.GoalInput = { name, target, accountId: accountId || null, saved, dueDate: dueDate || null, color }
    busy = true
    try {
      if (g0) await withTimeout(gl.updateGoal(g0.id, input))
      else await withTimeout(gl.createGoal(input))
      onclose()
    } catch (err) {
      error = errorMessage(err)
    } finally {
      busy = false
    }
  }

  async function remove() {
    if (!g0) return
    try {
      await withTimeout(gl.deleteGoal(g0.id))
      onclose()
    } catch (err) {
      error = errorMessage(err)
    }
  }
</script>

<Sheet title={g0 ? 'Modifica obiettivo' : 'Nuovo obiettivo'} {onclose} {error}>
  <form id="goal-form" class="form" novalidate onsubmit={save}>
    <label class="field">
      <span>Nome</span>
      <input class="input" bind:value={name} maxlength="40" placeholder="Es. Fondo emergenze" />
    </label>
    <label class="field">
      <span>Da raggiungere (€)</span>
      <input class="input num" bind:value={targetText} use:amountKeys inputmode="decimal" placeholder="0,00" autocomplete="off" />
    </label>
    <label class="field">
      <span>Dove accantoni</span>
      <select class="input" bind:value={accountId}>
        <option value="">Lo segno io a mano</option>
        {#each choices as a (a.id)}<option value={a.id}>Il saldo del conto {a.name}</option>{/each}
      </select>
      <span class="hint">
        {accountId
          ? 'Il progresso è il saldo del conto: si aggiorna da solo.'
          : 'Aggiungi tu le somme che metti da parte, con il pulsante Aggiungi.'}
      </span>
    </label>
    {#if !accountId}
      <label class="field">
        <span>Già accantonato (€)</span>
        <input class="input num" bind:value={savedText} use:amountKeys inputmode="decimal" placeholder="0,00" autocomplete="off" />
      </label>
    {/if}
    <label class="field">
      <span>Entro il (facoltativo)</span>
      <input class="input" type="date" bind:value={dueDate} />
    </label>
    <div class="field">
      <span>Colore</span>
      <ColorPicker bind:value={color} />
    </div>
  </form>
  {#snippet footer()}
    {#if g0}<DeleteButton onconfirm={remove} />{/if}
    <button type="submit" form="goal-form" class="btn btn-primary" disabled={busy}>Salva</button>
  {/snippet}
</Sheet>
