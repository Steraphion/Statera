# Sicurezza di Statera

## Come sono protetti i dati
- **Nessun server**: l'app è un insieme di file statici. I dati restano nel browser del dispositivo (IndexedDB) e, solo se l'utente attiva la sincronizzazione, nella cartella nascosta dell'app sul **suo** Google Drive.
- **Cifratura end-to-end** dei dati su Drive: AES-256-GCM con una chiave casuale, a sua volta protetta dalla password dell'utente (PBKDF2-SHA256, 600.000 iterazioni) e da una chiave di recupero. Password e chiave di recupero non lasciano mai il dispositivo; né Google né chi pubblica l'app può leggere i dati.
- **Permesso minimo su Google**: solo `drive.appdata` (la cartella riservata all'app). L'app non può vedere altri file del Drive né altri dati dell'account Google. I file di quella cartella sono accessibili solo a questa app, non a copie dell'app pubblicate da altri.
- **Nessun segreto nel codice**: l'ID client OAuth è pubblico per natura e funziona solo dall'indirizzo autorizzato (`https://steraphion.github.io`). Il client secret non è usato.
- **Content Security Policy** restrittiva: script solo dall'app stessa e dalla libreria di accesso Google; connessioni solo verso Google Drive; nessuno stile o script inline. L'app non si avvia se mostrata dentro un altro sito.
- **Backup esportati** protetti da password (consigliato), con la stessa cifratura.
- **Blocco dell'app** (facoltativo): PIN da 4 a 8 cifre, mai salvato; resta solo un'impronta PBKDF2-SHA256 (210.000 iterazioni, sale casuale). Dopo 5 tentativi sbagliati di fila l'attesa raddoppia a ogni errore (da 30 secondi fino a 15 minuti), anche per l'impronta. L'impronta o il volto usano WebAuthn con l'autenticatore del dispositivo: nessun server, il dato biometrico non arriva mai all'app. La schermata di blocco è una finestra modale che copre anche i pannelli aperti e non si chiude con Esc o il tasto indietro. Il PIN non si recupera: l'unica via è eliminare i dati dal dispositivo (restano su Drive, se la sincronizzazione è attiva).
- **Pubblicazione**: GitHub Actions con permessi minimi e azioni bloccate per impronta (SHA).

## Limiti noti
- Sul dispositivo i dati non sono cifrati con il PIN: il blocco ferma chi prende in mano il telefono o il PC sbloccato, non chi ha accesso tecnico al browser (strumenti per sviluppatori, copia del profilo). Contro questo valgono il blocco schermo e la cifratura del dispositivo.
- Con "Blocca dopo 1/5/15 minuti", l'anteprima delle app recenti può mostrare l'ultima schermata; con "Subito" no.
- Chi controllasse l'account GitHub del progetto potrebbe pubblicare una versione modificata dell'app: l'account deve avere la verifica in due passaggi.
- Chi possiede la chiave di recupero **e** l'accesso all'account Google di un utente può leggerne i dati.

## Segnalazioni
Per segnalare un problema di sicurezza apri una segnalazione nel repository senza includere dati personali o dettagli sfruttabili, e chiedi un contatto privato.
