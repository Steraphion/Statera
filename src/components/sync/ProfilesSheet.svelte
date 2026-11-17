<script lang="ts">
  import Sheet from '../Sheet.svelte'
  import DeleteButton from '../DeleteButton.svelte'
  import { db } from '../../lib/data/db'
  import { sync } from '../../lib/sync/sync.svelte'
  import {
    allProfiles,
    createProfile,
    deleteProfile,
    profileSummary,
    switchTo,
    type Profile,
    type ProfileSummary,
  } from '../../lib/profiles'

  let { onclose }: { onclose: () => void } = $props()

  interface Row {
    p: Profile
    s: ProfileSummary | null
  }

  // Tutti i profili del dispositivo, anche quelli rimasti fuori dall'elenco (v0.36.1), con il loro contenuto
  let rows = $state<Row[] | null>(null)
  let confirmNew = $state(false)

  async function load() {
    const list = await allProfiles(db.name)
    rows = await Promise.all(list.map(async (p) => ({ p, s: await profileSummary(p.db) })))
  }
  void load()

  const current = $derived(rows?.find((r) => r.p.db === db.name) ?? null)
  const others = $derived(rows?.filter((r) => r.p.db !== db.name) ?? [])

  function email(r: Row): string {
    return r.p.email || r.s?.email || ''
  }

  function count(n: number, one: string, many: string) {
    return `${n} ${n === 1 ? one : many}`
  }

  function content(s: ProfileSummary | null): string {
    if (!s || (!s.accounts && !s.movements)) return 'Nessun dato'
    return `${count(s.accounts, 'conto', 'conti')} · ${count(s.movements, 'movimento', 'movimenti')}`
  }

  /** Profilo vuoto e mai collegato: si può togliere dall'elenco. */
  function removable(r: Row): boolean {
    return (!r.s || (!r.s.accounts && !r.s.movements)) && !email(r)
  }

  async function remove(r: Row) {
    await deleteProfile(r.p.db)
    await load()
  }
</script>

<Sheet title="Account su questo dispositivo" {onclose}>
  {#if confirmNew}
    <p class="text">
      Si apre un <strong>profilo vuoto</strong>, con dati separati, per un'altra persona o un altro account Google.
    </p>
    <p class="text">
      I dati di questo profilo restano su questo dispositivo: per tornarci, Altro → Account e profili su questo
      dispositivo.
    </p>
    {#if !sync.meta}
      <p class="note">
        Per salvare su Google Drive i dati di questo profilo non serve un profilo nuovo: usa
        <strong>Attiva la sincronizzazione</strong> in Altro.
      </p>
    {/if}
  {:else}
    <p class="muted">
      Ogni account Google ha i propri dati, separati. Puoi usare Statera con più account sullo stesso dispositivo (ad
      esempio per un'altra persona di casa) e passare dall'uno all'altro.
    </p>

    {#if rows}
      <ul class="list">
        {#if current}
          <li class="row current">
            <span class="main">
              <span class="name">{email(current) || 'Questo profilo (non collegato a Google)'}</span>
              <span class="sub">In uso · {content(current.s)}</span>
            </span>
            <span aria-hidden="true">✓</span>
          </li>
        {/if}
        {#each others as r (r.p.db)}
          <li class="other">
            <button class="row" onclick={() => switchTo(r.p.db)}>
              <span class="main">
                <span class="name">{email(r) || 'Profilo non collegato a Google'}</span>
                <span class="sub">{content(r.s)} · tocca per passare a questo profilo</span>
              </span>
              <span aria-hidden="true">›</span>
            </button>
            {#if removable(r)}
              <div class="remove">
                <DeleteButton label="Rimuovi" confirmLabel="Conferma: rimuovi" onconfirm={() => remove(r)} />
              </div>
            {/if}
          </li>
        {/each}
      </ul>
    {:else}
      <p class="muted">Ricerca dei profili…</p>
    {/if}
  {/if}

  {#snippet footer()}
    {#if confirmNew}
      <button type="button" class="btn btn-primary" onclick={() => switchTo(createProfile())}>Crea profilo vuoto</button>
      <button type="button" class="btn" onclick={() => (confirmNew = false)}>Annulla</button>
    {:else}
      <button type="button" class="btn" onclick={() => (confirmNew = true)}>Nuovo profilo vuoto</button>
    {/if}
  {/snippet}
</Sheet>

<style>
  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
    margin-bottom: var(--space-3);
  }

  .text {
    margin-bottom: var(--space-3);
  }

  .note {
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    font-size: var(--text-sm);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    min-height: var(--size-row);
    padding: 0;
    border: none;
    border-bottom: 1px solid var(--color-border);
    background: none;
    text-align: left;
  }

  .other {
    border-bottom: 1px solid var(--color-border);
  }

  .other .row {
    border-bottom: none;
  }

  .remove {
    display: flex;
    justify-content: flex-end;
    padding-bottom: var(--space-2);
  }

  li:last-child .row,
  li.row:last-child,
  li.other:last-child {
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
