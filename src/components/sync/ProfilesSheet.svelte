<script lang="ts">
  import Sheet from '../Sheet.svelte'
  import { db } from '../../lib/data/db'
  import { activeProfile, createProfile, listProfiles, switchTo } from '../../lib/profiles'

  let { onclose }: { onclose: () => void } = $props()

  const current = activeProfile()
  const others = listProfiles().filter((p) => p.db !== db.name)
</script>

<Sheet title="Account su questo dispositivo" {onclose}>
  <p class="muted">
    Ogni account Google ha i propri dati, separati. Puoi usare Statera con più account sullo stesso dispositivo (ad
    esempio per un'altra persona di casa) e passare dall'uno all'altro.
  </p>

  <ul class="list">
    <li class="row current">
      <span class="main">
        <span class="name">{current.email || 'Questo profilo (non collegato a Google)'}</span>
        <span class="sub">In uso</span>
      </span>
      <span aria-hidden="true">✓</span>
    </li>
    {#each others as p (p.db)}
      <li>
        <button class="row" onclick={() => switchTo(p.db)}>
          <span class="main">
            <span class="name">{p.email || 'Profilo non collegato'}</span>
            <span class="sub">Tocca per passare a questo account</span>
          </span>
          <span aria-hidden="true">›</span>
        </button>
      </li>
    {/each}
  </ul>

  {#snippet footer()}
    <button type="button" class="btn" onclick={() => switchTo(createProfile())}>Aggiungi un altro account</button>
  {/snippet}
</Sheet>

<style>
  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
    margin-bottom: var(--space-3);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    min-height: 56px;
    padding: 0;
    border: none;
    border-bottom: 1px solid var(--color-border);
    background: none;
    text-align: left;
  }

  li:last-child .row,
  li.row:last-child {
    border-bottom: none;
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 600;
    word-break: break-word;
  }

  .sub {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
