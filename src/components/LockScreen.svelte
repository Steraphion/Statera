<script lang="ts">
  import { onMount, tick } from 'svelte'
  import DeleteButton from './DeleteButton.svelte'
  import { db } from '../lib/data/db'
  import { lock } from '../lib/lock.svelte'
  import { listProfiles, DEFAULT_DB } from '../lib/profiles'

  let pin = $state('')
  let error = $state('')
  let busy = $state(false)
  let forgot = $state(false)
  let input: HTMLInputElement | undefined = $state()
  let dlg: HTMLDialogElement | undefined = $state()

  const length = $derived(lock.config?.length ?? 6)

  async function submit() {
    if (busy || !pin) return
    busy = true
    error = await lock.unlock(pin)
    busy = false
    if (error) {
      pin = ''
      await tick()
      input?.focus()
    }
  }

  async function bio() {
    error = ''
    const msg = await lock.unlockBio()
    if (msg) error = msg
  }

  async function reset() {
    db.close()
    const names = [...new Set([DEFAULT_DB, ...listProfiles().map((p) => p.db)])]
    await lock.resetDevice(names)
  }

  onMount(() => {
    // Finestra modale: sta sopra ogni altro pannello aperto (anche lui modale) e rende inattivo il resto
    if (!dlg?.open) dlg?.showModal()
    input?.focus()
    // Con l'impronta attiva la si propone subito (se il browser lo consente senza un tocco)
    if (lock.config?.bio && lock.autoBio) void lock.unlockBio().then((msg) => msg && msg !== 'Impronta non disponibile: usa il PIN' && (error = msg))
  })
</script>

<dialog
  bind:this={dlg}
  class="lock"
  aria-labelledby="lock-title"
  oncancel={(e) => e.preventDefault()}
  onclose={() => {
    // Chiusa con il tasto indietro o Esc mentre è ancora bloccata: si riapre subito
    if (lock.locked) dlg?.showModal()
  }}
>
  <div class="box">
    <img src="./favicon.svg" alt="" width="56" height="56" />
    <h1 id="lock-title">Statera è bloccata</h1>
    {#if !forgot}
      <form
        novalidate
        onsubmit={(e) => {
          e.preventDefault()
          submit()
        }}
      >
        <label class="field">
          <span>PIN</span>
          <input
            bind:this={input}
            class="input pin num"
            type="password"
            inputmode="numeric"
            autocomplete="off"
            maxlength="8"
            bind:value={pin}
            oninput={() => {
              error = ''
              pin = pin.replace(/\D/g, '')
              if (pin.length === length) submit()
            }}
          />
        </label>
        {#if error}<p class="error" role="alert">{error}</p>{/if}
        <button type="submit" class="btn btn-primary" disabled={busy || !pin}>Sblocca</button>
      </form>
      {#if lock.config?.bio}
        <button class="btn" onclick={bio}>Usa l'impronta</button>
      {/if}
      <button class="btn btn-ghost btn-small" onclick={() => (forgot = true)}>Ho dimenticato il PIN</button>
    {:else}
      <div class="forgot">
        <p>
          Per sicurezza il PIN non si può recuperare. Puoi togliere il blocco solo
          <strong>eliminando i dati di Statera da questo dispositivo</strong>.
        </p>
        <p>
          Se usi la sincronizzazione, i dati restano su Google Drive: dopo, collega di nuovo l'account con la tua
          password e li ritrovi. Altrimenti potrai ripristinarli solo da un backup esportato.
        </p>
        <DeleteButton
          label="Elimina i dati di questo dispositivo"
          confirmLabel="Conferma: elimina i dati"
          onconfirm={reset}
        />
        <button class="btn" onclick={() => (forgot = false)}>Torna al PIN</button>
      </div>
    {/if}
  </div>
</dialog>

<style>
  .lock {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    max-width: none;
    max-height: none;
    margin: 0;
    border: 0;
    display: grid;
    place-items: center;
    padding: var(--space-4);
    background: var(--color-bg);
    color: var(--color-text);
    overflow-y: auto;
  }

  .lock::backdrop {
    background: var(--color-bg);
  }

  .box {
    width: 100%;
    max-width: 340px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    text-align: center;
  }

  img {
    align-self: center;
    border-radius: var(--radius-md);
  }

  h1 {
    font-size: var(--text-xl);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .field {
    text-align: left;
  }

  .pin {
    min-height: 56px;
    font-size: var(--text-xl);
    letter-spacing: 0.4em;
    text-align: center;
  }

  .error {
    color: var(--color-danger);
    font-size: var(--text-sm);
  }

  .forgot {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    text-align: left;
    font-size: var(--text-sm);
  }
</style>
