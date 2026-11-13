<script lang="ts">
  import Sheet from '../Sheet.svelte'
  import DeleteButton from '../DeleteButton.svelte'
  import { sync } from '../../lib/sync/sync.svelte'
  import type { DriveFile } from '../../lib/sync/google'
  import { errorMessage } from '../../lib/data/util'
  import { formatDay } from '../../lib/format'

  let { onclose }: { onclose: () => void } = $props()

  let list = $state<DriveFile[] | null>(null)
  let error = $state('')
  let done = $state('')

  $effect(() => {
    sync
      .backups()
      .then((b) => (list = b))
      .catch((e) => (error = errorMessage(e)))
  })

  function dayOf(f: DriveFile): string {
    return f.name.match(/(\d{4}-\d{2}-\d{2})/)?.[1] ?? ''
  }

  async function restore(f: DriveFile) {
    error = ''
    try {
      await sync.restore(f.id)
      done = `Dati riportati al ${formatDay(dayOf(f))}.`
    } catch (e) {
      error = errorMessage(e)
    }
  }
</script>

<Sheet title="Backup su Drive" {onclose} {error}>
  <p class="muted">
    Statera salva sul tuo Drive un backup cifrato al giorno e tiene gli ultimi 30. Ripristinarne uno riporta i dati a
    quel giorno su <strong>tutti</strong> i dispositivi collegati.
  </p>
  {#if done}
    <p class="ok" role="status">✓ {done}</p>
  {:else if list === null && !error}
    <p class="empty-note">Caricamento…</p>
  {:else if list && list.length === 0}
    <p class="empty-note">Ancora nessun backup: il primo viene creato con la prossima sincronizzazione.</p>
  {:else if list}
    <ul class="list">
      {#each list as f (f.id)}
        <li class="row">
          <span class="main">
            <span class="name">{formatDay(dayOf(f))}</span>
            <span class="sub num">{dayOf(f)}</span>
          </span>
          <DeleteButton label="Ripristina" confirmLabel="Conferma ripristino" onconfirm={() => restore(f)} />
        </li>
      {/each}
    </ul>
  {/if}
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
    min-height: 56px;
    border-bottom: 1px solid var(--color-border);
  }

  .row:last-child {
    border-bottom: none;
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 600;
  }

  .sub {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .ok {
    color: var(--color-income);
    font-weight: 600;
  }
</style>
