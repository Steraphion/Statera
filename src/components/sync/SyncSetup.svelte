<script lang="ts">
  import { untrack } from 'svelte'
  import Sheet from '../Sheet.svelte'
  import Segmented from '../Segmented.svelte'
  import { sync, type Connection } from '../../lib/sync/sync.svelte'
  import * as cr from '../../lib/sync/crypto'
  import { errorMessage } from '../../lib/data/util'

  /** 'activate' = attivazione completa; 'unlock' = dispositivo collegato che ha perso la chiave. */
  let { mode = 'activate', onclose }: { mode?: 'activate' | 'unlock'; onclose: () => void } = $props()

  type Step = 'intro' | 'password' | 'recovery' | 'join' | 'done'
  let step = $state<Step>(untrack(() => (mode === 'unlock' ? 'join' : 'intro')))
  let conn = $state<Connection | null>(null)
  let busy = $state('')
  let error = $state('')

  // nuovo
  let pw = $state('')
  let pw2 = $state('')
  let recoveryKey = $state('')
  let saved = $state(false)
  let copied = $state(false)

  // esistente
  let useRecovery = $state(false)
  let secret = $state('')
  let rk = $state('')
  let newPw = $state('')
  let newPw2 = $state('')
  let joinMode = $state<'merge' | 'replace'>('merge')

  async function run(label: string, fn: () => Promise<void>) {
    error = ''
    busy = label
    try {
      await fn()
    } catch (e) {
      error = errorMessage(e)
    } finally {
      busy = ''
    }
  }

  function google() {
    // Chiamata diretta dal tocco: Google apre la sua finestra
    run('Accesso a Google…', async () => {
      conn = await sync.connect()
      step = conn.existing ? 'join' : 'password'
    })
  }

  function choosePassword() {
    error = cr.passwordProblem(pw) ?? (pw !== pw2 ? 'Le due password non coincidono' : '')
    if (error) return
    recoveryKey = cr.generateRecoveryKey()
    step = 'recovery'
  }

  async function copyKey() {
    try {
      await navigator.clipboard.writeText(recoveryKey)
      copied = true
    } catch {
      error = 'Copia non riuscita: scrivi la chiave a mano o scaricala come file'
    }
  }

  function downloadKey() {
    const text = [
      'STATERA — CHIAVE DI RECUPERO',
      '',
      recoveryKey,
      '',
      `Account Google: ${conn?.email ?? ''}`,
      `Creata il: ${new Date().toLocaleString('it-IT')}`,
      '',
      'Serve solo se dimentichi la password di Statera.',
      'Conservala in un posto sicuro e privato (stampata, o in un gestore di password).',
      'Chi ha questa chiave e accesso al tuo account Google può leggere i tuoi dati.',
    ].join('\n')
    const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }))
    const a = document.createElement('a')
    a.href = url
    a.download = 'statera-chiave-di-recupero.txt'
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  }

  function activate() {
    if (!saved) {
      error = 'Conferma di aver conservato la chiave di recupero'
      return
    }
    run('Cifratura e primo caricamento…', async () => {
      await sync.createNew(pw, recoveryKey)
      step = 'done'
    })
  }

  function join() {
    if (useRecovery) {
      if (!cr.isRecoveryKeyShape(rk)) {
        error = 'La chiave di recupero ha 32 caratteri (es. ABCD-EFGH-…)'
        return
      }
      error = cr.passwordProblem(newPw) ?? (newPw !== newPw2 ? 'Le due password non coincidono' : '')
      if (error) return
    } else if (!secret) {
      error = 'Inserisci la password'
      return
    }
    run('Sblocco e sincronizzazione…', async () => {
      if (mode === 'unlock') {
        if (useRecovery) {
          await sync.unlock({ recoveryKey: rk })
          await sync.changePassword({ recoveryKey: rk }, newPw)
        } else await sync.unlock({ password: secret })
      } else {
        await sync.joinExisting(useRecovery ? { recoveryKey: rk, newPassword: newPw } : { password: secret }, joinMode)
      }
      step = 'done'
    })
  }

  /** Azione del pulsante principale del passo corrente (anche con Invio). */
  function primary() {
    if (busy) return
    if (step === 'password') choosePassword()
    else if (step === 'recovery') activate()
    else if (step === 'join') join()
  }

  const title = $derived(mode === 'unlock' ? 'Sblocca la sincronizzazione' : 'Sincronizzazione con Google Drive')
</script>

<Sheet {title} {onclose} {error}>
  <form
    novalidate
    class="form"
    onsubmit={(e) => {
      e.preventDefault()
      primary()
    }}
  >
    {#if step === 'intro'}
      <p>I tuoi dati verranno salvati nella <strong>cartella nascosta di Statera</strong> sul tuo Google Drive:</p>
      <ul>
        <li>cifrati con una <strong>password</strong> che sceglierai tu (Google non può leggerli);</li>
        <li>visibili solo a Statera, che non può vedere nessun altro file del tuo Drive;</li>
        <li>allineati automaticamente su tutti i dispositivi collegati, con un backup al giorno.</li>
      </ul>
      <p class="muted">
        Si aprirà la finestra di Google: scegli il tuo account e consenti l'accesso alla cartella di Statera. Se compare
        l'avviso "Google non ha verificato questa app", tocca <em>Avanzate</em> → <em>Vai a Statera</em>.
      </p>
    {:else if step === 'password'}
      <p>
        Collegato come <strong>{conn?.email}</strong>. Scegli la password che proteggerà i tuoi dati su Drive: ti servirà
        per collegare altri dispositivi.
      </p>
      <label class="field">
        <span>Password</span>
        <input class="input" type="password" bind:value={pw} autocomplete="new-password" />
        <span class="hint">Almeno 10 caratteri. Una frase di più parole va benissimo.</span>
      </label>
      <label class="field">
        <span>Ripeti la password</span>
        <input class="input" type="password" bind:value={pw2} autocomplete="new-password" />
      </label>
    {:else if step === 'recovery'}
      <p>
        Questa è la tua <strong>chiave di recupero</strong>. Se dimentichi la password è l'<strong>unico</strong> modo per
        recuperare i dati: nessuno, nemmeno chi ha creato l'app, può farlo al posto tuo.
      </p>
      <p class="key num" aria-label="Chiave di recupero">{recoveryKey}</p>
      <div class="row">
        <button type="button" class="btn btn-small" onclick={copyKey}>{copied ? 'Copiata ✓' : 'Copia'}</button>
        <button type="button" class="btn btn-small" onclick={downloadKey}>Scarica come file</button>
      </div>
      <p class="muted">Conservala in un posto sicuro e separato dal telefono: stampata, o in un gestore di password.</p>
      <label class="check">
        <input type="checkbox" bind:checked={saved} />
        <span>Ho conservato la chiave di recupero in un posto sicuro</span>
      </label>
    {:else if step === 'join'}
      {#if mode === 'activate'}
        <p>
          Su Drive di <strong>{conn?.email}</strong> c'è già Statera, attivata da un altro dispositivo. Inserisci la
          password scelta allora.
        </p>
      {:else}
        <p>Questo dispositivo è collegato a <strong>{sync.meta?.email}</strong>: inserisci la password di Statera.</p>
      {/if}

      {#if !useRecovery}
        <label class="field">
          <span>Password di Statera</span>
          <input class="input" type="password" bind:value={secret} autocomplete="current-password" />
        </label>
        <button type="button" class="btn btn-ghost link" onclick={() => (useRecovery = true)}>
          Ho dimenticato la password: uso la chiave di recupero
        </button>
      {:else}
        <label class="field">
          <span>Chiave di recupero</span>
          <input class="input num" bind:value={rk} autocomplete="off" placeholder="XXXX-XXXX-XXXX-…" />
        </label>
        <label class="field">
          <span>Nuova password</span>
          <input class="input" type="password" bind:value={newPw} autocomplete="new-password" />
          <span class="hint">Almeno 10 caratteri. Varrà per tutti i dispositivi.</span>
        </label>
        <label class="field">
          <span>Ripeti la nuova password</span>
          <input class="input" type="password" bind:value={newPw2} autocomplete="new-password" />
        </label>
        <button type="button" class="btn btn-ghost link" onclick={() => (useRecovery = false)}>Uso la password</button>
      {/if}

      {#if mode === 'activate' && conn?.localHasData}
        <div class="field">
          <span>Questo dispositivo ha già dei dati. Cosa vuoi farne?</span>
          <Segmented
            label="Dati del dispositivo"
            bind:value={joinMode}
            options={[
              { value: 'merge', label: 'Uniscili a Drive' },
              { value: 'replace', label: 'Usa solo Drive' },
            ]}
          />
          <span class="hint">
            {joinMode === 'merge'
              ? 'I dati dei due lati vengono uniti; conti, carte e categorie con lo stesso nome diventano una cosa sola.'
              : 'I dati di questo dispositivo vengono sostituiti da quelli su Drive. Utile se qui hai solo fatto delle prove.'}
          </span>
        </div>
      {/if}
    {:else if step === 'done'}
      <p class="ok">✓ Sincronizzazione attiva con <strong>{sync.meta?.email}</strong>.</p>
      <p class="muted">
        Statera si sincronizza da sola: all'apertura, quando torni nell'app e pochi secondi dopo ogni modifica. Per
        collegare un altro dispositivo apri Statera su quel dispositivo e attiva la sincronizzazione con lo stesso
        account Google e la stessa password.
      </p>
    {/if}

    {#if busy}<p class="busy" role="status">{busy}</p>{/if}
    <!-- Invio sulla tastiera = pulsante principale -->
    <button type="submit" hidden aria-hidden="true" tabindex="-1"></button>
  </form>

  {#snippet footer()}
    {#if step === 'intro'}
      <button type="button" class="btn btn-primary" disabled={!!busy} onclick={google}>Accedi con Google</button>
    {:else if step === 'password'}
      <button type="button" class="btn btn-primary" onclick={choosePassword}>Continua</button>
    {:else if step === 'recovery'}
      <button type="button" class="btn btn-primary" disabled={!!busy} onclick={activate}>Attiva</button>
    {:else if step === 'join'}
      <button type="button" class="btn btn-primary" disabled={!!busy} onclick={join}>
        {mode === 'unlock' ? 'Sblocca' : 'Collega questo dispositivo'}
      </button>
    {:else}
      <button type="button" class="btn btn-primary" onclick={onclose}>Fatto</button>
    {/if}
  {/snippet}
</Sheet>

<style>
  ul {
    margin: 0;
    padding-left: var(--space-5);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .key {
    padding: var(--space-4);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    font-size: var(--text-lg);
    font-weight: 650;
    letter-spacing: 0.04em;
    text-align: center;
    word-break: break-all;
    user-select: all;
  }

  .row {
    display: flex;
    gap: var(--space-2);
  }

  .check {
    display: flex;
    gap: var(--space-2);
    align-items: flex-start;
    font-weight: 600;
  }

  .check input {
    width: 20px;
    height: 20px;
    flex: none;
    margin-top: 2px;
  }

  .link {
    align-self: flex-start;
    padding: 0;
    min-height: 32px;
    text-align: left;
  }

  .busy {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .ok {
    color: var(--color-income);
    font-weight: 600;
  }
</style>
