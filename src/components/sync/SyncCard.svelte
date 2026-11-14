<script lang="ts">
  import Card from '../Card.svelte'
  import DeleteButton from '../DeleteButton.svelte'
  import SyncSetup from './SyncSetup.svelte'
  import BackupsSheet from './BackupsSheet.svelte'
  import PasswordSheet from './PasswordSheet.svelte'
  import ProfilesSheet from './ProfilesSheet.svelte'
  import { sync } from '../../lib/sync/sync.svelte'
  import { formatDateTime } from '../../lib/format'
  import { statusLabel } from '../../lib/sync/labels'

  let sheet = $state<'setup' | 'unlock' | 'backups' | 'password' | 'profiles' | null>(null)
</script>

<Card>
  <h2>Sincronizzazione</h2>
  {#if !sync.meta}
    <p class="muted">
      Allinea i dati tra smartphone e PC tramite il tuo Google Drive, cifrati con una password che conosci solo tu.
    </p>
    <div class="actions">
      <button class="btn btn-primary" onclick={() => (sheet = 'setup')}>Attiva la sincronizzazione</button>
    </div>
  {:else}
    <dl>
      <dt>Account Google</dt>
      <dd>{sync.meta.email || '—'}</dd>
      <dt>Stato</dt>
      <dd class:warn={['needs-auth', 'locked', 'error', 'offline'].includes(sync.status)}>{statusLabel(sync.status)}</dd>
      <dt>Ultima sincronizzazione</dt>
      <dd>{sync.meta.lastSyncAt ? formatDateTime(sync.meta.lastSyncAt) : 'mai'}</dd>
    </dl>
    {#if sync.error}<p class="error-box">{sync.error}</p>{/if}
    <div class="actions">
      {#if sync.status === 'needs-auth'}
        <button class="btn btn-primary" onclick={() => sync.reconnect()}>Riconnetti a Google</button>
      {:else if sync.status === 'locked'}
        <button class="btn btn-primary" onclick={() => (sheet = 'unlock')}>Inserisci la password</button>
      {:else}
        <button class="btn btn-primary" disabled={sync.status === 'syncing'} onclick={() => sync.syncNow()}>
          {sync.status === 'syncing' ? 'Sincronizzazione…' : 'Sincronizza ora'}
        </button>
      {/if}
      <button class="btn" onclick={() => (sheet = 'backups')}>Backup su Drive</button>
      <button class="btn" onclick={() => (sheet = 'password')}>Cambia password</button>
    </div>
    <div class="actions secondary">
      <DeleteButton label="Scollega questo dispositivo" confirmLabel="Conferma: scollega" onconfirm={() => sync.disconnect()} />
    </div>
    <p class="small">Scollegando, i dati restano su questo dispositivo e su Drive; potrai ricollegarlo quando vuoi.</p>
  {/if}
  <button class="btn btn-ghost link" onclick={() => (sheet = 'profiles')}>Account e profili su questo dispositivo ›</button>
</Card>

{#if sheet === 'setup'}
  <SyncSetup onclose={() => (sheet = null)} />
{:else if sheet === 'unlock'}
  <SyncSetup mode="unlock" onclose={() => (sheet = null)} />
{:else if sheet === 'backups'}
  <BackupsSheet onclose={() => (sheet = null)} />
{:else if sheet === 'password'}
  <PasswordSheet onclose={() => (sheet = null)} />
{:else if sheet === 'profiles'}
  <ProfilesSheet onclose={() => (sheet = null)} />
{/if}

<style>
  h2 {
    font-size: var(--text-lg);
    font-weight: 800;
    margin-bottom: var(--space-2);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--space-2) var(--space-4);
    margin: 0 0 var(--space-2);
    font-size: var(--text-sm);
  }

  dt {
    color: var(--color-text-muted);
  }

  dd {
    margin: 0;
    text-align: right;
    word-break: break-word;
  }

  dd.warn {
    color: var(--color-danger);
    font-weight: 600;
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

  .link {
    margin-top: var(--space-3);
    padding: 0;
    min-height: 32px;
  }
</style>
