<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import { formatEuro, formatMonth } from '../lib/format'

  const month = formatMonth(new Date())
</script>

<ScreenHeader title={month} />

<Card>
  <div class="totals">
    <div>
      <span class="label">Entrate</span>
      <span class="num income">{formatEuro(0)}</span>
    </div>
    <div>
      <span class="label">Uscite</span>
      <span class="num expense">{formatEuro(0)}</span>
    </div>
    <div>
      <span class="label">Saldo</span>
      <span class="num">{formatEuro(0)}</span>
    </div>
  </div>
</Card>

<Card>
  <div class="empty">
    <p class="title">Nessun movimento</p>
    <p class="hint">L'inserimento dei movimenti arriva nella Fase 1.3.</p>
  </div>
</Card>

<style>
  .totals {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-3);
    text-align: center;
  }

  .totals div {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .label {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-text-muted);
  }

  .num {
    font-size: var(--text-md);
    font-weight: 600;
  }

  .income {
    color: var(--color-income);
  }

  .expense {
    color: var(--color-expense);
  }

  .empty {
    text-align: center;
    padding: var(--space-5) 0;
  }

  .title {
    font-weight: 600;
  }

  .hint {
    margin-top: var(--space-1);
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }
</style>
