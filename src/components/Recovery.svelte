<script lang="ts">
  import { startup } from '../lib/startup.svelte'

  let { message, onretry }: { message: string; onretry?: () => void } = $props()
</script>

<div class="recovery" role="alert">
  <img src="./favicon.svg" alt="" width="48" height="48" />
  <h1>Statera non riesce ad aprirsi</h1>
  <p class="msg">{message}</p>
  <ol>
    <li>Chiudi Statera anche dall'elenco delle app recenti.</li>
    <li>Se usi Statera anche in una scheda di Chrome, chiudi quella scheda.</li>
    <li>
      Se non basta: Impostazioni del telefono → App → <strong>Chrome</strong> → Arresto forzato (Statera funziona
      dentro Chrome). Poi riapri Statera.
    </li>
  </ol>
  <p class="safe">I tuoi dati restano salvati sul dispositivo: questa schermata non li cancella.</p>
  <div class="actions">
    <button class="btn btn-primary" onclick={() => (onretry ? onretry() : startup.run())}>Riprova</button>
    <button class="btn" onclick={() => location.reload()}>Ricarica l'app</button>
  </div>
  <p class="version">Versione {__APP_VERSION__}</p>
</div>

<style>
  .recovery {
    max-width: 480px;
    margin: 10vh auto 0;
    padding: var(--space-5);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  h1 {
    font-size: var(--text-lg);
  }

  .msg {
    padding: var(--space-3);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    font-family: var(--font-num);
    font-size: var(--text-sm);
    word-break: break-word;
  }

  ol {
    margin: 0;
    padding-left: var(--space-5);
    font-size: var(--text-sm);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .safe {
    font-size: var(--text-sm);
    color: var(--color-income);
  }

  .actions {
    display: flex;
    gap: var(--space-2);
  }

  .version {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
