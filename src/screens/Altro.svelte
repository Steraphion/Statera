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

  .link-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: 52px;
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
    width: 36px;
    height: 36px;
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
