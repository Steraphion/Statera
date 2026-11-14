<script lang="ts">
  import type { Snippet } from 'svelte'

  let { children }: { children: Snippet } = $props()
</script>

<section class="card">
  {@render children()}
</section>

<style>
  /* Scheda (design system: Scheda): superficie, angoli grandi, niente bordo né ombra */
  .card {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-4) var(--space-5);
  }

  .card + :global(.card) {
    margin-top: var(--space-4);
  }
</style>
