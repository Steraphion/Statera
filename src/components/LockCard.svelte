<script lang="ts">
  import Card from './Card.svelte'
  import { lock } from '../lib/lock.svelte'
  import { pinProblem, TIMEOUTS } from '../lib/lock'
  import { errorMessage } from '../lib/data/util'
  import { toast } from '../lib/toast.svelte'

  type Mode = '' | 'enable' | 'change' | 'disable' | 'bio'
  let mode = $state<Mode>('')
  let pin = $state('')
  let pin2 = $state('')
  let oldPin = $state('')
  let timeout = $state(60)
  let error = $state('')
  let busy = $state(false)

  const timeoutLabel = $derived(TIMEOUTS.find((t) => t.value === lock.config?.timeout)?.label.toLowerCase() ?? '')

  function open(m: Mode) {
    mode = m
    pin = pin2 = oldPin = ''
    error = ''
  }

  const digits = (s: string) => s.replace(/\D/g, '')

  async function run(fn: () => Promise<unknown>, done: string) {
    error = ''
    busy = true
    try {
      await fn()
      toast.show(done)
      mode = ''
      pin = pin2 = oldPin = ''
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = false
    }
  }

  function checkNew(): boolean {
    const p = pinProblem(pin)
    if (p) {
      error = p
      return false
    }
    if (pin !== pin2) {
      error = 'I due PIN non coincidono'
      return false
    }
    return true
  }

  function submit(e: Event) {
    e.preventDefault()
    if (mode === 'enable') {
      if (!checkNew()) return
      const p = pin
      run(() => lock.enable(p, timeout), 'Blocco attivato')
    } else if (mode === 'change') {
      if (!checkNew()) return
      run(() => lock.changePin(oldPin, pin), 'PIN cambiato')
    } else if (mode === 'disable') {
      run(() => lock.disable(oldPin), 'Blocco disattivato')
    } else if (mode === 'bio') {
      run(() => lock.enableBio(oldPin), 'Impronta attivata')
    }
  }
</script>

<Card>
  <h2>Blocco dell'app</h2>
  {#if !lock.enabled}
    <p class="muted">
      Chiedi un PIN{lock.bioAvailable ? ' (o l\'impronta)' : ''} per aprire Statera, così chi prende in mano il telefono
      o il PC non vede i tuoi movimenti.
    </p>
  {:else}
    <p class="status">
      <strong>Attivo</strong> · si blocca {timeoutLabel}{lock.config?.bio ? ' · impronta attiva' : ''}
    </p>
  {/if}

  {#if mode}
    <form class="form" novalidate onsubmit={submit}>
      {#if mode !== 'enable'}
        <label class="field">
          <span>{mode === 'change' ? 'PIN attuale' : 'PIN'}</span>
          <input class="input num" type="password" inputmode="numeric" autocomplete="off" maxlength="8" bind:value={oldPin} oninput={() => (oldPin = digits(oldPin))} />
        </label>
      {/if}
      {#if mode === 'enable' || mode === 'change'}
        <label class="field">
          <span>{mode === 'change' ? 'Nuovo PIN' : 'PIN (da 4 a 8 cifre)'}</span>
          <input class="input num" type="password" inputmode="numeric" autocomplete="off" maxlength="8" bind:value={pin} oninput={() => (pin = digits(pin))} />
        </label>
        <label class="field">
          <span>Ripeti il PIN</span>
          <input class="input num" type="password" inputmode="numeric" autocomplete="off" maxlength="8" bind:value={pin2} oninput={() => (pin2 = digits(pin2))} />
        </label>
      {/if}
      {#if mode === 'enable'}
        <label class="field">
          <span>Blocca</span>
          <select class="input" bind:value={timeout}>
            {#each TIMEOUTS as t (t.value)}<option value={t.value}>{t.label.toLowerCase()} che lasci l'app</option>{/each}
          </select>
          <span class="hint">All'apertura l'app chiede sempre il PIN.</span>
        </label>
        <p class="note">
          Il PIN non si può recuperare: se lo dimentichi dovrai eliminare i dati da questo dispositivo e ritrovarli da
          Google Drive o da un backup.
        </p>
      {/if}
      {#if error}<p class="error" role="alert">{error}</p>{/if}
      <div class="actions">
        <button type="button" class="btn" onclick={() => (mode = '')}>Annulla</button>
        <button type="submit" class="btn btn-primary" disabled={busy}>
          {mode === 'enable' ? 'Attiva' : mode === 'change' ? 'Cambia PIN' : mode === 'disable' ? 'Disattiva' : 'Continua'}
        </button>
      </div>
    </form>
  {:else if !lock.enabled}
    <button class="btn btn-primary" onclick={() => open('enable')}>Attiva il blocco</button>
  {:else}
    <label class="field">
      <span>Blocca</span>
      <select class="input" value={lock.config?.timeout} onchange={(e) => lock.setTimeout(Number(e.currentTarget.value))}>
        {#each TIMEOUTS as t (t.value)}<option value={t.value}>{t.label.toLowerCase()} che lasci l'app</option>{/each}
      </select>
    </label>
    <div class="actions wrap">
      {#if lock.config?.bio}
        <button class="btn" onclick={() => (lock.disableBio(), toast.show('Impronta disattivata'))}>Non usare l'impronta</button>
      {:else if lock.bioAvailable}
        <button class="btn" onclick={() => open('bio')}>Usa anche l'impronta</button>
      {/if}
      <button class="btn" onclick={() => open('change')}>Cambia PIN</button>
      <button class="btn" onclick={() => open('disable')}>Disattiva</button>
      <button class="btn btn-primary" onclick={() => lock.lockNow()}>Blocca ora</button>
    </div>
  {/if}
  {#if mode === 'bio'}
    <p class="note">Dopo il PIN il telefono ti chiederà l'impronta (o il volto) per collegarla a Statera.</p>
  {/if}
</Card>

<style>
  .muted,
  .note {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
    margin-bottom: var(--space-3);
  }

  .status {
    margin-bottom: var(--space-3);
    font-size: var(--text-sm);
  }

  .error {
    color: var(--color-expense);
    font-size: var(--text-sm);
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2);
  }

  .actions.wrap {
    flex-wrap: wrap;
    justify-content: flex-start;
    margin-top: var(--space-3);
  }
</style>
