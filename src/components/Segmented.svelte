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
  /* Segmentato (design system): pillola, scelta in colore principale */
  .segmented {
    display: flex;
    padding: var(--space-1);
    gap: var(--space-1);
    border-radius: var(--radius-full);
    background: var(--color-surface-2);
  }

  button {
    flex: 1;
    min-height: var(--size-btn-s);
    padding: 0 var(--space-3);
    border: none;
    border-radius: var(--radius-full);
    background: transparent;
    color: var(--color-text-muted);
    font-weight: 700;
    cursor: pointer;
    transition: background-color var(--duration-base) var(--ease-standard);
  }

  button.active {
    background: var(--color-primary);
    color: var(--color-on-primary);
    font-weight: 800;
  }

  button:disabled {
    cursor: default;
  }
</style>
