<script lang="ts">
  import Card from '../components/Card.svelte'
  import Icon from '../components/Icon.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import DataCard from '../components/DataCard.svelte'
  import SyncCard from '../components/sync/SyncCard.svelte'
  import LockCard from '../components/LockCard.svelte'
  import { device } from '../lib/device.svelte'
  import { sync } from '../lib/sync/sync.svelte'
  import { statusLabel } from '../lib/sync/labels'
  import Segmented from '../components/Segmented.svelte'
  import PalettePicker from '../components/PalettePicker.svelte'
  import { theme } from '../lib/theme.svelte'
  import type { ThemePref } from '../lib/theme'
  import { columns } from '../lib/columns.svelte'
  import { ui } from '../lib/ui.svelte'

  let themePref = $state<ThemePref>(theme.pref)
  $effect(() => {
    if (themePref !== theme.pref) theme.set(themePref)
  })
</script>

<ScreenHeader title="Altro" />

<SyncCard />

<LockCard />

<Card>
  <h2>Gestione</h2>
  <a class="link-row" href="#/categorie">
    <span class="ic" aria-hidden="true"><Icon name="tag" size={18} /></span>
    <span class="grow">Categorie</span>
    <Icon name="chevron-right" size={18} />
  </a>
  <a class="link-row" href="#/ricorrenti">
    <span class="ic" aria-hidden="true"><Icon name="repeat" size={18} /></span>
    <span class="grow">Movimenti ricorrenti</span>
    <Icon name="chevron-right" size={18} />
  </a>
  {#if columns.pc}
    <button class="link-row" onclick={() => (ui.shortcuts = true)}>
      <span class="ic" aria-hidden="true"><Icon name="keyboard" size={18} /></span>
      <span class="grow">Scorciatoie da tastiera</span>
      <kbd>?</kbd>
    </button>
  {/if}
</Card>

<Card>
  <h2>Aspetto</h2>
  <p class="muted theme-hint">Le scelte valgono per questo dispositivo.</p>
  <h3 class="sub-h">Tema</h3>
  <p class="muted theme-hint">Chiaro o scuro; "Automatico" segue l'impostazione del telefono o del PC.</p>
  <Segmented
    label="Tema"
    bind:value={themePref}
    options={[
      { value: 'auto', label: 'Automatico' },
      { value: 'light', label: 'Chiaro' },
      { value: 'dark', label: 'Scuro' },
    ]}
  />
  <h3 class="sub-h">Colori</h3>
  <p class="muted theme-hint">Ogni palette ha la sua versione chiara e scura. I colori di conti e categorie restano gli stessi.</p>
  <PalettePicker />
</Card>

<Card>
  <h2>Installazione</h2>
  {#if device.installed}
    <p class="muted">Statera è installata come app su questo dispositivo.</p>
  {:else if device.canInstall}
    <p class="muted">Installa Statera per aprirla come un'app, anche offline.</p>
    <button class="btn btn-primary install" onclick={() => device.install()}>Installa Statera</button>
  {:else}
    <p class="muted">
      Per installarla usa il menu del browser: su Android "Aggiungi a schermata Home" o
      "Installa app", su PC l'icona di installazione nella barra degli indirizzi.
    </p>
  {/if}
</Card>

<Card>
  <h2>I tuoi dati</h2>
  <dl class="facts">
    <dt>Dove sono salvati</dt>
    <dd>{sync.meta ? 'Su questo dispositivo e, cifrati, sul tuo Google Drive' : 'Solo su questo dispositivo'}</dd>
    <dt>Protezione dalla pulizia automatica</dt>
    <dd>
      {#if device.persistent === null}
        Non disponibile in questo browser
      {:else if device.persistent}
        Attiva
      {:else}
        Non concessa (lo diventa di solito dopo l'installazione)
      {/if}
    </dd>
    <dt>Sincronizzazione</dt>
    <dd>{statusLabel(sync.status, sync)}</dd>
  </dl>
</Card>

<DataCard />

<Card>
  <h2>Informazioni</h2>
  <dl class="facts">
    <dt>Versione</dt>
    <dd class="num">{__APP_VERSION__}</dd>
    <dt>Connessioni esterne</dt>
    <dd>{sync.meta ? 'Solo Google (accesso e Drive)' : 'Nessuna'}</dd>
  </dl>
  <a class="link-row privacy" href="./privacy.html" target="_blank" rel="noopener">
    <span class="ic" aria-hidden="true"><Icon name="shield-check" size={18} /></span>
    <span class="grow">Informativa sulla privacy</span>
    <Icon name="chevron-right" size={18} />
  </a>
  <a class="link-row" href="./licenze.html" target="_blank" rel="noopener">
    <span class="ic" aria-hidden="true"><Icon name="file-text" size={18} /></span>
    <span class="grow">Licenze del carattere e delle icone</span>
    <Icon name="chevron-right" size={18} />
  </a>
</Card>

<style>
  h2 {
    font-size: var(--text-lg);
    margin-bottom: var(--space-2);
  }

  button.link-row {
    width: 100%;
    padding: 0;
    border: 0;
    background: none;
    font: inherit;
    text-align: left;
    cursor: pointer;
  }

  .link-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-field);
    color: var(--color-text);
    text-decoration: none;
    font-weight: 700;
  }

  .link-row :global(svg:last-child) {
    color: var(--color-text-muted);
  }

  .grow {
    flex: 1;
  }

  .ic {
    display: grid;
    place-items: center;
    width: var(--size-btn-s);
    height: var(--size-btn-s);
    border-radius: var(--radius-full);
    background: var(--color-accent-soft);
    color: var(--color-accent);
  }

  .privacy {
    margin-top: var(--space-2);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .install {
    margin-top: var(--space-3);
  }

  .theme-hint {
    margin-bottom: var(--space-3);
  }

  .sub-h {
    margin: var(--space-5) 0 var(--space-1);
    font-size: var(--text-md);
    font-weight: 800;
  }
</style>
