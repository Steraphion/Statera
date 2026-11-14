<script lang="ts">
  import type { Snippet } from 'svelte'
  import Icon from './Icon.svelte'

  // back: le schermate aperte da un'altra hanno la freccia indietro (e niente barra in basso sul telefono)
  let { title, back, children }: { title: string; back?: { href: string; label: string }; children?: Snippet } = $props()
</script>

<header class="screen-header" class:sub={!!back}>
  {#if back}
    <a class="back" href={back.href} aria-label="Torna a {back.label}" title="Torna a {back.label}">
      <Icon name="chevron-left" />
    </a>
  {/if}
  <h1>{title}</h1>
  {#if children}
    <div class="actions">{@render children()}</div>
  {/if}
</header>

<style>
  .screen-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-5);
  }

  h1 {
    flex: 1;
    min-width: 0;
    font-size: var(--text-2xl);
    overflow-wrap: anywhere;
  }

  .sub h1 {
    font-size: var(--text-xl);
  }

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .back {
    flex: none;
    display: grid;
    place-items: center;
    width: var(--size-touch);
    height: var(--size-touch);
    border-radius: var(--radius-full);
    background: var(--color-surface);
    color: var(--color-text);
  }
</style>
