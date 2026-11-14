<script lang="ts">
  import type { Snippet } from 'svelte'

  let { title, children }: { title: string; children?: Snippet } = $props()
</script>

<header class="screen-header">
  <h1>{title}</h1>
  {#if children}
    <div class="actions">{@render children()}</div>
  {/if}
</header>

<style>
  .screen-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }

  h1 {
    font-size: var(--text-2xl);
  }
</style>
