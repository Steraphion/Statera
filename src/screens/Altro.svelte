<script lang="ts">
  import Card from '../components/Card.svelte'
  import ScreenHeader from '../components/ScreenHeader.svelte'
  import DataCard from '../components/DataCard.svelte'
  import SyncCard from '../components/sync/SyncCard.svelte'
  import LockCard from '../components/LockCard.svelte'
  import { device } from '../lib/device.svelte'
  import { sync } from '../lib/sync/sync.svelte'
  import { statusLabel } from '../lib/sync/labels'
</script>

<ScreenHeader title="Altro" />

<SyncCard />

<LockCard />

<Card>
  <h2>Gestione</h2>
  <a class="link-row" href="#/categorie">
    <span>Categorie</span>
    <span aria-hidden="true">›</span>
  </a>
  <a class="link-row" href="#/ricorrenti">
    <span>Movimenti ricorrenti</span>
    <span aria-hidden="true">›</span>
  </a>
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
  <dl>
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
    <dd>{statusLabel(sync.status)}</dd>
  </dl>
</Card>

<DataCard />

<Card>
  <h2>Informazioni</h2>
  <dl>
    <dt>Versione</dt>
    <dd class="num">{__APP_VERSION__}</dd>
    <dt>Connessioni esterne</dt>
    <dd>{sync.meta ? 'Solo Google (accesso e Drive)' : 'Nessuna'}</dd>
  </dl>
  <a class="link-row privacy" href="./privacy.html" target="_blank" rel="noopener">
    <span>Informativa sulla privacy</span>
    <span aria-hidden="true">›</span>
  </a>
  <a class="link-row" href="./licenze.html" target="_blank" rel="noopener">
    <span>Licenze del carattere e delle icone</span>
    <span aria-hidden="true">›</span>
  </a>
</Card>

<style>
  h2 {
    font-size: var(--text-md);
    font-weight: 650;
    margin-bottom: var(--space-2);
  }

  .link-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 44px;
    color: var(--color-text);
    text-decoration: none;
    font-weight: 500;
  }

  .privacy {
    margin-top: var(--space-2);
    font-size: var(--text-sm);
  }

  .muted {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .install {
    margin-top: var(--space-3);
  }

  dl {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--space-2) var(--space-4);
    margin: 0;
    font-size: var(--text-sm);
  }

  dt {
    color: var(--color-text-muted);
  }

  dd {
    margin: 0;
    text-align: right;
  }
</style>
