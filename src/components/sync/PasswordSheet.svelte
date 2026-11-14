<script lang="ts">
  import Sheet from '../Sheet.svelte'
  import { sync } from '../../lib/sync/sync.svelte'
  import * as cr from '../../lib/sync/crypto'
  import { errorMessage } from '../../lib/data/util'

  let { onclose }: { onclose: () => void } = $props()

  let useRecovery = $state(false)
  let current = $state('')
  let next = $state('')
  let next2 = $state('')
  let error = $state('')
  let busy = $state(false)
  let done = $state(false)

  async function save() {
    error = cr.passwordProblem(next) ?? (next !== next2 ? 'Le due password non coincidono' : '')
    if (!error && !current) error = useRecovery ? 'Inserisci la chiave di recupero' : 'Inserisci la password attuale'
    if (error) return
    busy = true
    try {
      await sync.changePassword(useRecovery ? { recoveryKey: current } : { password: current }, next)
      done = true
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }
</script>

<Sheet title="Cambia password" {onclose} {error}>
  <form
    novalidate
    class="form"
    onsubmit={(e) => {
      e.preventDefault()
      if (!busy && !done) save()
    }}
  >
    {#if done}
      <p class="ok">✓ Password cambiata. Vale da subito per tutti i dispositivi; quelli già collegati non devono fare nulla.</p>
    {:else}
      <label class="field">
        <span>{useRecovery ? 'Chiave di recupero' : 'Password attuale'}</span>
        <input class="input" type={useRecovery ? 'text' : 'password'} bind:value={current} autocomplete="off" />
      </label>
      <button type="button" class="btn btn-ghost link" onclick={() => ((useRecovery = !useRecovery), (current = ''))}>
        {useRecovery ? 'Uso la password attuale' : 'Non la ricordo: uso la chiave di recupero'}
      </button>
      <label class="field">
        <span>Nuova password</span>
        <input class="input" type="password" bind:value={next} autocomplete="new-password" />
        <span class="hint">Almeno 10 caratteri.</span>
      </label>
      <label class="field">
        <span>Ripeti la nuova password</span>
        <input class="input" type="password" bind:value={next2} autocomplete="new-password" />
      </label>
      {#if busy}<p class="muted">Cifratura in corso…</p>{/if}
    {/if}
    <button type="submit" hidden aria-hidden="true" tabindex="-1"></button>
  </form>
  {#snippet footer()}
    {#if done}
      <button type="button" class="btn btn-primary" onclick={onclose}>Fatto</button>
    {:else}
      <button type="button" class="btn btn-primary" disabled={busy} onclick={save}>Cambia password</button>
    {/if}
  {/snippet}
</Sheet>

<style>
  .link {
    align-self: flex-start;
    padding: 0;
    min-height: var(--size-cat-s);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .ok {
    color: var(--color-income);
    font-weight: 600;
  }
</style>
