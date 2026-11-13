<script lang="ts">
  import Card from './Card.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import * as bk from '../lib/data/backup'
  import { sync } from '../lib/sync/sync.svelte'
  import { formatDateTime } from '../lib/format'

  const last = live(() => bk.lastBackupAt(), null as number | null)
  const hasData = live(async () => (await db.transactions.count()) > 0, false)

  let fileInput: HTMLInputElement
  // $state.raw: il backup letto resta un oggetto semplice, che il database sa salvare
  let pending = $state.raw<{ file: bk.BackupFile; summary: bk.BackupSummary; name: string } | null>(null)
  let message = $state('')
  let error = $state('')

  const DAY = 24 * 60 * 60 * 1000
  const stale = $derived(
    last.ready && hasData.value && (last.value === null || Date.now() - last.value > 30 * DAY),
  )

  async function exportBackup() {
    error = ''
    message = ''
    try {
      const file = await bk.buildBackup(__APP_VERSION__)
      const blob = new Blob([JSON.stringify(file, null, 1)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = bk.backupFileName()
      document.body.appendChild(a)
      a.click()
      a.remove()
      setTimeout(() => URL.revokeObjectURL(url), 10_000)
      await bk.markBackupDone()
      message = 'Backup creato: trovi il file nella cartella Download.'
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    }
  }

  async function pickFile(e: Event) {
    error = ''
    message = ''
    const f = (e.currentTarget as HTMLInputElement).files?.[0]
    ;(e.currentTarget as HTMLInputElement).value = ''
    if (!f) return
    try {
      const file = bk.parseBackup(await f.text())
      pending = { file, summary: bk.summarize(file), name: f.name }
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  async function restore() {
    if (!pending) return
    try {
      if (sync.meta) await sync.restoreSnapshot(pending.file.data)
      else await bk.restoreBackup(pending.file)
      message = 'Dati ripristinati dal backup.'
      pending = null
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    }
  }

  async function wipe() {
    await bk.wipeAll()
    sync.forget()
    message = 'Tutti i dati sono stati eliminati. Le categorie di base sono state ricaricate.'
  }
</script>

<Card>
  <h2>Backup</h2>
  <p class="muted">
    Ultimo backup:
    <strong>{last.value ? formatDateTime(last.value) : 'mai'}</strong>
  </p>
  {#if stale}
    <p class="tip">
      Finché la sincronizzazione non è attiva, i dati esistono solo su questo dispositivo: conviene esportare un backup
      ogni tanto e conservarlo al sicuro.
    </p>
  {/if}
  <div class="actions">
    <button class="btn btn-primary" onclick={exportBackup}>Esporta backup</button>
    <button class="btn" onclick={() => fileInput.click()}>Ripristina da file</button>
    <input
      bind:this={fileInput}
      type="file"
      accept="application/json,.json"
      class="visually-hidden"
      tabindex="-1"
      aria-hidden="true"
      onchange={pickFile}
    />
  </div>
  <p class="small">Il file non è cifrato: chi lo apre può leggere i tuoi movimenti. Conservalo in un posto sicuro.</p>

  {#if pending}
    <div class="confirm">
      <p>
        <strong>{pending.name}</strong><br />
        Creato il {formatDateTime(pending.summary.exportedAt)} · {pending.summary.accounts} conti ·
        {pending.summary.transactions} movimenti · {pending.summary.categories} categorie
      </p>
      <p class="warn">
        {sync.meta
          ? 'Il ripristino sostituisce i dati attuali su questo dispositivo e su tutti quelli sincronizzati.'
          : 'Il ripristino sostituisce tutti i dati attuali di questo dispositivo.'}
      </p>
      <div class="actions">
        <DeleteButton label="Sostituisci i dati" confirmLabel="Conferma sostituzione" onconfirm={restore} />
        <button class="btn" onclick={() => (pending = null)}>Annulla</button>
      </div>
    </div>
  {/if}

  {#if message}<p class="ok" role="status">{message}</p>{/if}
  {#if error}<p class="error-box" role="alert">{error}</p>{/if}
</Card>

<Card>
  <h2>Elimina tutti i dati</h2>
  <p class="muted">
    Cancella conti, carte, movimenti e categorie da questo dispositivo e riparte da zero con le categorie di base. Utile
    dopo aver fatto delle prove. Non si può annullare: se vuoi, prima esporta un backup.
    {#if sync.meta}
      Il dispositivo verrà anche scollegato dalla sincronizzazione; i dati su Google Drive non vengono toccati.
    {/if}
  </p>
  <div class="actions">
    <DeleteButton label="Elimina tutti i dati" onconfirm={wipe} />
  </div>
</Card>

<style>
  h2 {
    font-size: var(--text-md);
    font-weight: 650;
    margin-bottom: var(--space-2);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .muted strong {
    color: var(--color-text);
    font-weight: 600;
  }

  .tip {
    margin-top: var(--space-2);
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-accent-soft);
    font-size: var(--text-sm);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }

  .small {
    margin-top: var(--space-2);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .confirm {
    margin-top: var(--space-4);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
    font-size: var(--text-sm);
  }

  .warn {
    margin-top: var(--space-2);
    color: var(--color-expense);
    font-weight: 600;
  }

  .ok {
    margin-top: var(--space-3);
    font-size: var(--text-sm);
    color: var(--color-income);
  }

  .error-box {
    margin-top: var(--space-3);
  }
</style>
