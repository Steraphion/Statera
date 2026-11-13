<script lang="ts">
  import { today } from '../lib/data/util'

  // Campo data con scorciatoie "Ieri" e "Oggi"
  let { value = $bindable(), label = 'Data' }: { value: string; label?: string } = $props()

  function yesterday(): string {
    const d = new Date()
    d.setDate(d.getDate() - 1)
    return today(d)
  }
</script>

<div class="field">
  <span class="head">
    <label for="date-field">{label}</label>
    <span class="quick">
      <button type="button" class:on={value === yesterday()} onclick={() => (value = yesterday())}>Ieri</button>
      <button type="button" class:on={value === today()} onclick={() => (value = today())}>Oggi</button>
    </span>
  </span>
  <input id="date-field" class="input" type="date" bind:value required />
</div>

<style>
  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
  }

  label {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-text-muted);
  }

  .quick {
    display: flex;
    gap: var(--space-1);
  }

  button {
    border: none;
    background: none;
    padding: 0 var(--space-1);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-accent);
    cursor: pointer;
  }

  button.on {
    color: var(--color-text-muted);
    text-decoration: underline;
  }
</style>
