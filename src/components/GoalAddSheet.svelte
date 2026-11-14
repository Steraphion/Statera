<script lang="ts">
  import { amountKeys } from '../lib/keypad.svelte'
  import Sheet from './Sheet.svelte'
  import { addToGoal } from '../lib/data/goals'
  import type { Goal } from '../lib/data/types'
  import { errorMessage, withTimeout } from '../lib/data/util'
  import { evalAmount, formatEuro } from '../lib/format'

  let { goal, onclose }: { goal: Goal; onclose: () => void } = $props()
  let text = $state('')
  let error = $state('')

  async function save(e: Event) {
    e.preventDefault()
    error = ''
    const c = evalAmount(text)
    if (c === null || c === 0) {
      error = 'Inserisci un importo (es. 50; per togliere, -20)'
      return
    }
    try {
      await withTimeout(addToGoal(goal.id, c))
      onclose()
    } catch (err) {
      error = errorMessage(err)
    }
  }
</script>

<Sheet title="Aggiungi a {goal.name}" {onclose} {error}>
  <form id="goal-add" class="form" novalidate onsubmit={save}>
    <p class="hint">Accantonato finora: <strong class="num">{formatEuro(goal.saved)}</strong>.</p>
    <label class="field">
      <span>Importo (€)</span>
      <!-- svelte-ignore a11y_autofocus -->
      <input class="input num" bind:value={text} use:amountKeys inputmode="decimal" placeholder="0,00" autocomplete="off" autofocus />
      <span class="hint">Per togliere scrivi un importo negativo, es. -20.</span>
    </label>
  </form>
  {#snippet footer()}
    <button type="button" class="btn" onclick={onclose}>Annulla</button>
    <button type="submit" form="goal-add" class="btn btn-primary">Aggiungi</button>
  {/snippet}
</Sheet>
