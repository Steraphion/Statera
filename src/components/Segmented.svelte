<script lang="ts" generics="T extends string">
  let {
    value = $bindable(),
    options,
    label,
    disabled = false,
  }: { value: T; options: { value: T; label: string }[]; label: string; disabled?: boolean } = $props()
</script>

<div class="segmented" role="radiogroup" aria-label={label}>
  {#each options as o (o.value)}
    <button
      type="button"
      role="radio"
      aria-checked={value === o.value}
      class:active={value === o.value}
      {disabled}
      onclick={() => (value = o.value)}
    >
      {o.label}
    </button>
  {/each}
</div>

<style>
  .segmented {
    display: flex;
    padding: 3px;
    gap: 3px;
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
  }

  button {
    flex: 1;
    min-height: 38px;
    border: none;
    border-radius: calc(var(--radius-sm) - 2px);
    background: transparent;
    color: var(--color-text-muted);
    font-weight: 600;
    cursor: pointer;
  }

  button.active {
    background: var(--color-segment-active);
    color: var(--color-text);
    box-shadow: var(--shadow-1);
  }

  button:disabled {
    cursor: default;
  }
</style>
