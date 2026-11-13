<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'

  let { title, text }: { title: string; text: string } = $props()
</script>

<ScreenHeader {title} />

<Card>
  <p class="hint">{text}</p>
</Card>

<style>
  .hint {
    color: var(--color-text-muted);
    text-align: center;
    padding: var(--space-5) 0;
  }
</style>
