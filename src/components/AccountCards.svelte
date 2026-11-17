<script lang="ts">
  import Icon from './Icon.svelte'
  import CardForm from './CardForm.svelte'
  import { cardEligible, cardsOf } from '../lib/data/balances'
  import type { Account, Card } from '../lib/data/types'

  /**
   * Carte di debito di un conto, nel suo dettaglio: si aprono per modificarle e se ne aggiungono altre.
   * Le carte prepagate sono conti a sé: non ne hanno di nuove, ma tengono quelle collegate quando erano «Altro».
   */
  let { account, cards, accounts }: { account: Account; cards: Card[]; accounts: Account[] } = $props()

  const mine = $derived(cardsOf(account, cards))
  const eligible = $derived(accounts.filter((a) => a.id === account.id || (cardEligible(a) && !a.archived)))
  let sheet = $state<{ card?: Card } | null>(null)
</script>

{#if cardEligible(account) || mine.length > 0}
  <div class="cards" role="group" aria-label="Carte collegate a {account.name}">
    {#each mine as c (c.id)}
      <button class="btn btn-soft btn-small chip" onclick={() => (sheet = { card: c })} aria-label="Carta {c.name}{c.archived ? ', archiviata' : ''}: modifica">
        <Icon name="credit-card" size={16} />
        {c.name}{c.archived ? ' · archiviata' : ''}
      </button>
    {/each}
    {#if cardEligible(account) && !account.archived}
      <button class="btn btn-ghost btn-small" onclick={() => (sheet = {})}>
        <Icon name="plus" size={16} />
        {mine.length ? 'Carta' : 'Aggiungi una carta'}
      </button>
    {/if}
  </div>
{/if}

{#if sheet}
  <CardForm card={sheet.card} accounts={eligible} accountId={account.id} onclose={() => (sheet = null)} />
{/if}

<style>
  .cards {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
  }
</style>
