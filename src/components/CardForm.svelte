<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from './Sheet.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import * as repo from '../lib/data/repo'
  import type { Account, Card } from '../lib/data/types'

  let { card, accounts, onclose }: { card?: Card; accounts: Account[]; onclose: () => void } = $props()

  // Valori di partenza del modulo (letti una volta all'apertura)
  const orig = untrack(() => card)
  const firstAccountId = untrack(() => accounts[0]?.id ?? '')

  let name = $state(orig?.name ?? '')
  let accountId = $state(orig?.accountId ?? firstAccountId)
  let error = $state('')
  let busy = $state(false)

  async function run(action: () => Promise<unknown>) {
    error = ''
    busy = true
    try {
      await action()
      onclose()
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    } finally {
      busy = false
    }
  }

  function save(e: SubmitEvent) {
    e.preventDefault()
    const input = { name, accountId }
    run(() => (card ? repo.updateCard(card.id, input) : repo.createCard(input)))
  }
</script>

<Sheet title={card ? 'Modifica carta' : 'Nuova carta'} {onclose}>
  {#if accounts.length === 0}
    <p class="empty-note">
      Per aggiungere una carta di debito crea prima un conto di tipo "Conto corrente".
    </p>
  {:else}
    <form id="card-form" class="form" onsubmit={save}>
      <label class="field">
        <span>Nome</span>
        <input class="input" bind:value={name} placeholder="Es. Bancomat" maxlength="40" required />
        <span class="hint">Solo un nome per riconoscerla: il numero della carta non viene mai salvato.</span>
      </label>

      <label class="field">
        <span>Conto collegato</span>
        <select class="input" bind:value={accountId}>
          {#each accounts as a (a.id)}
            <option value={a.id}>{a.name}</option>
          {/each}
        </select>
        <span class="hint">Le spese con questa carta scalano subito da questo conto.</span>
      </label>

      {#if error}
        <p class="error-box" role="alert">{error}</p>
      {/if}
    </form>
  {/if}

  {#snippet footer()}
    {#if card}
      <DeleteButton onconfirm={() => run(() => repo.deleteCard(card.id))} />
      <button type="button" class="btn" onclick={() => run(() => repo.setCardArchived(card.id, !card.archived))}>
        {card.archived ? 'Ripristina' : 'Archivia'}
      </button>
    {/if}
    {#if accounts.length > 0}
      <button type="submit" form="card-form" class="btn btn-primary" disabled={busy}>Salva</button>
    {/if}
  {/snippet}
</Sheet>
