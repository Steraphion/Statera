<script lang="ts">
  import Card from './Card.svelte'
  import DeleteButton from './DeleteButton.svelte'
  import ImportSheet from './ImportSheet.svelte'
  import { db } from '../lib/data/db'
  import { live } from '../lib/data/live.svelte'
  import * as bk from '../lib/data/backup'
  import { sync } from '../lib/sync/sync.svelte'
  import { snapshotOf } from '../lib/sync/merge'
  import { formatDateTime } from '../lib/format'
  import { passwordProblem } from '../lib/sync/crypto'
  import { errorMessage } from '../lib/data/util'

  const last = live(() => bk.lastBackupAt(), null as number | null)
  const hasData = live(async () => (await db.transactions.count()) > 0, false)

  let fileInput: HTMLInputElement
  // $state.raw: il backup letto resta un oggetto semplice, che il database sa salvare
  let pending = $state.raw<{ file: bk.BackupFile; summary: bk.BackupSummary; name: string } | null>(null)
  let locked = $state.raw<{ file: bk.EncryptedBackupFile; name: string } | null>(null)
  let message = $state('')
  let error = $state('')
  let busy = $state(false)

  // Esportazione
  let exporting = $state(false)
  let protect = $state(true)
  let pw = $state('')
  let pw2 = $state('')
  let openPw = $state('')

  const DAY = 24 * 60 * 60 * 1000
  const stale = $derived(
    last.ready && hasData.value && (last.value === null || Date.now() - last.value > 30 * DAY),
  )

  function download(content: string, name: string) {
    const url = URL.createObjectURL(new Blob([content], { type: 'application/json' }))
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  }

  async function exportBackup() {
    error = ''
    message = ''
    if (protect) {
      error = passwordProblem(pw) ?? (pw !== pw2 ? 'Le due password non coincidono' : '')
      if (error) return
    }
    busy = true
    try {
      const file = await bk.buildBackup(__APP_VERSION__)
      const content = protect ? JSON.stringify(await bk.encryptBackup(file, pw)) : JSON.stringify(file, null, 1)
      download(content, bk.backupFileName(new Date(), protect))
      await bk.markBackupDone()
      message = protect
        ? 'Backup protetto creato: trovi il file nella cartella Download. Senza la sua password non si può aprire.'
        : 'Backup creato: trovi il file nella cartella Download. Il file non è protetto: conservalo in un posto sicuro.'
      exporting = false
      pw = pw2 = ''
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }

  async function pickFile(e: Event) {
    error = ''
    message = ''
    pending = locked = null
    const f = (e.currentTarget as HTMLInputElement).files?.[0]
    ;(e.currentTarget as HTMLInputElement).value = ''
    if (!f) return
    try {
      const read = bk.readBackupFile(await f.text())
      if ('encrypted' in read) locked = { file: read.encrypted, name: f.name }
      else pending = { file: read.plain, summary: bk.summarize(read.plain), name: f.name }
    } catch (err) {
      error = errorMessage(err)
    }
  }

  async function unlockFile() {
    if (!locked) return
    error = ''
    busy = true
    try {
      const file = await bk.decryptBackup(locked.file, openPw)
      pending = { file, summary: bk.summarize(file), name: locked.name }
      locked = null
      openPw = ''
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }

  async function restore() {
    if (!pending) return
    try {
      if (sync.meta) await sync.restoreSnapshot(snapshotOf(pending.file.data))
      else await bk.restoreBackup(pending.file)
      message = 'Dati ripristinati dal backup.'
      pending = null
    } catch (e) {
      error = errorMessage(e)
    }
  }

  async function wipe() {
    await bk.wipeAll()
    sync.forget()
    message = 'Tutti i dati sono stati eliminati. Le categorie di base sono state ricaricate.'
  }
  let importing = $state(false)
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
    <button class="btn btn-primary" onclick={() => ((exporting = !exporting), (error = ''), (message = ''))}>
      Esporta backup
    </button>
    <button class="btn" onclick={() => fileInput.click()}>Ripristina da file</button>
    <button class="btn" onclick={() => (importing = true)}>Importa da CSV</button>
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

  {#if exporting}
    <form
      novalidate
      class="form export"
      onsubmit={(e) => {
        e.preventDefault()
        exportBackup()
      }}
    >
      <label class="check">
        <input type="checkbox" bind:checked={protect} />
        <span>Proteggi il file con una password (consigliato)</span>
      </label>
      {#if protect}
        <label class="field">
          <span>Password del backup</span>
          <input class="input" type="password" bind:value={pw} autocomplete="new-password" />
          <span class="hint">Almeno 10 caratteri. Puoi usare la stessa password di Statera.</span>
        </label>
        <label class="field">
          <span>Ripeti la password</span>
          <input class="input" type="password" bind:value={pw2} autocomplete="new-password" />
        </label>
      {:else}
        <p class="warn">Senza password chiunque trovi il file può leggere tutti i tuoi movimenti.</p>
      {/if}
      <div class="actions">
        <button type="submit" class="btn btn-primary" disabled={busy}>{busy ? 'Cifratura…' : 'Scarica il backup'}</button>
        <button type="button" class="btn" onclick={() => (exporting = false)}>Annulla</button>
      </div>
    </form>
  {/if}

  {#if locked}
    <form
      novalidate
      class="form confirm"
      onsubmit={(e) => {
        e.preventDefault()
        unlockFile()
      }}
    >
      <p><strong>{locked.name}</strong><br />Backup protetto da password, creato il {formatDateTime(locked.file.exportedAt)}.</p>
      <label class="field">
        <span>Password del backup</span>
        <input class="input" type="password" bind:value={openPw} autocomplete="current-password" />
      </label>
      <div class="actions">
        <button type="submit" class="btn btn-primary" disabled={busy}>{busy ? 'Apertura…' : 'Apri'}</button>
        <button type="button" class="btn" onclick={() => (locked = null)}>Annulla</button>
      </div>
    </form>
  {/if}

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

{#if importing}
  <ImportSheet onclose={() => (importing = false)} />
{/if}

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

  .export {
    margin-top: var(--space-4);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
  }

  .check {
    display: flex;
    gap: var(--space-2);
    align-items: flex-start;
    font-weight: 600;
    font-size: var(--text-sm);
  }

  .check input {
    width: 20px;
    height: 20px;
    flex: none;
  }


  .confirm {
    margin-top: var(--space-4);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-border);
    font-size: var(--text-sm);
  }

  .warn {
    margin-top: var(--space-2);
    color: var(--color-danger);
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
