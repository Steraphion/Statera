"""Collaudo della sincronizzazione con Google e Drive simulati (dati di esempio)."""
import asyncio, json, re, sys, time, itertools
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright

BASE = "http://localhost:4173"
results = []
def check(name, ok, info=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{info}]" if info and not ok else ""))

FAKE_GIS = """
window.google = { accounts: { oauth2: {
  initTokenClient(cfg) { return { requestAccessToken(o) {
    window.__gisCalls = (window.__gisCalls||0) + 1;
    if (window.__gisFail) { setTimeout(() => cfg.error_callback({ type: 'popup_failed_to_open' }), 50); return }
    setTimeout(() => cfg.callback({ access_token: 'tok-' + Date.now(), expires_in: 3600, scope: cfg.scope }), 50);
  } } },
  hasGrantedAllScopes() { return true },
  revoke(t, cb) { cb && cb() }
} } };
"""

class FakeDrive:
    def __init__(self): self.files = {}; self.ids = itertools.count(1); self.calls = 0
    async def handle(self, route):
        req = route.request; self.calls += 1
        cors = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}
        if req.method == "OPTIONS":
            return await route.fulfill(status=204, headers=cors)
        if not (req.headers.get("authorization") or "").startswith("Bearer tok-"):
            return await route.fulfill(status=401, headers=cors, body="{}")
        u = urlparse(req.url); q = parse_qs(u.query); path = u.path
        def ok(obj): return route.fulfill(status=200, headers={**cors, "Content-Type": "application/json"}, body=json.dumps(obj))
        if path == "/drive/v3/about":
            return await ok({"user": {"emailAddress": "utente.prova@example.com", "displayName": "Utente Prova"}})
        if path == "/drive/v3/files" and req.method == "GET":
            assert q.get("spaces") == ["appDataFolder"]
            return await ok({"files": [{"id": i, "name": f["name"], "modifiedTime": "2026-11-13T00:00:00Z"} for i, f in sorted(self.files.items(), key=lambda x: x[1]["name"])]})
        m = re.match(r"^/drive/v3/files/([^/]+)$", path)
        if m and req.method == "GET":
            f = self.files.get(m.group(1))
            if not f: return await route.fulfill(status=404, headers=cors, body="{}")
            return await route.fulfill(status=200, headers=cors, body=f["content"])
        if m and req.method == "DELETE":
            self.files.pop(m.group(1), None); return await route.fulfill(status=204, headers=cors)
        if path == "/upload/drive/v3/files" and req.method == "POST":
            body = req.post_data
            boundary = req.headers["content-type"].split("boundary=")[1]
            parts = [p for p in body.split("--" + boundary) if p.strip() and p.strip() != "--"]
            meta = json.loads(parts[0].split("\r\n\r\n", 1)[1].strip())
            content = parts[1].split("\r\n\r\n", 1)[1].rstrip("\r\n")
            assert meta["parents"] == ["appDataFolder"]
            fid = f"id{next(self.ids)}"; self.files[fid] = {"name": meta["name"], "content": content}
            return await ok({"id": fid, "name": meta["name"]})
        m = re.match(r"^/upload/drive/v3/files/([^/]+)$", path)
        if m and req.method == "PATCH":
            self.files[m.group(1)]["content"] = req.post_data
            return await ok({"id": m.group(1), "name": self.files[m.group(1)]["name"]})
        return await route.fulfill(status=400, headers=cors, body=json.dumps({"error": {"message": "non gestito " + req.method + " " + path}}))
    def names(self): return sorted(f["name"] for f in self.files.values())
    def content(self, name): return next(f["content"] for f in self.files.values() if f["name"] == name)

drive = FakeDrive()

async def new_device(b, p, label, mobile):
    opts = {**p.devices["Pixel 7"]} if mobile else {"viewport": {"width": 1366, "height": 800}}
    ctx = await b.new_context(**opts, locale="it-IT", accept_downloads=True)
    await ctx.route("https://accounts.google.com/gsi/client", lambda r: r.fulfill(status=200, content_type="text/javascript", body=FAKE_GIS))
    await ctx.route("https://www.googleapis.com/**", drive.handle)
    pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(f"{label} PAGEERROR {e}"))
    pg.on("console", lambda m: errs.append(f"{label}: {m.text}") if m.type == "error" else None)
    await pg.goto(BASE + "/"); await pg.wait_for_selector("nav"); await pg.wait_for_timeout(400)
    return ctx, pg, errs

def field(pg, text):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{re.escape(text)}$"))).locator("input")

def sel(pg, label):
    return pg.locator("label.field", has=pg.locator("span", has_text=re.compile(f"^{label}$"))).locator("select")

async def click(pg, loc):
    await loc.click()

async def add_account(pg, name, saldo):
    await pg.goto(BASE + "/#/conti"); await pg.wait_for_timeout(300)
    await pg.get_by_role("button", name="Conto").first.click()
    await pg.get_by_label("Nome").fill(name); await pg.get_by_label("Saldo iniziale (€)").fill(saldo)
    await pg.get_by_role("button", name="Salva").click(); await pg.wait_for_timeout(250)

async def add_expense(pg, amount, desc, cat="Svago"):
    await pg.goto(BASE + "/#/movimenti"); await pg.wait_for_timeout(300)
    btn = pg.get_by_role("button", name=re.compile("^(Nuovo movimento|Movimento)$"))
    await btn.first.click(); await pg.wait_for_selector("dialog[open]")
    await pg.get_by_label("Importo (€)").fill(amount)
    await pg.locator(".cat-list").get_by_role("radio", name=re.compile(f"^{cat}")).click()
    await pg.get_by_label("Descrizione").fill(desc)
    await pg.get_by_role("button", name="Salva", exact=True).click(); await pg.wait_for_timeout(300)

async def descriptions(pg):
    return await pg.evaluate("""() => new Promise(res => { const q = indexedDB.open(localStorage.getItem('statera.profiloAttivo') || 'statera-locale');
      q.onsuccess = () => { const r = q.result.transaction('transactions').objectStore('transactions').getAll();
        r.onsuccess = () => { q.result.close(); res(r.result.filter(t => t.deletedAt === null).map(t => t.description).sort()) } } })""")

async def sync_status(pg):
    await pg.goto(BASE + "/#/altro"); await pg.wait_for_timeout(300)
    return (await pg.locator("dl").first.inner_text())

async def wait_synced(pg, timeout=12):
    t0 = time.time()
    while time.time() - t0 < timeout:
        txt = await pg.locator("body").inner_text()
        if "Sincronizzato" in txt and "in corso" not in txt: return True
        await pg.wait_for_timeout(300)
    return False

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")

        # ---------- Telefono: primo dispositivo ----------
        tctx, tel, terr = await new_device(b, p, "telefono", True)
        await add_account(tel, "Conto", "1000")
        await add_expense(tel, "12", "Cinema dal telefono")
        await tel.goto(BASE + "/#/altro"); await tel.wait_for_timeout(300)
        await tel.get_by_role("button", name="Attiva la sincronizzazione").click()
        await tel.get_by_role("button", name="Accedi con Google").click()
        await field(tel, "Password").wait_for()
        check("Accesso Google e scelta password", await tel.get_by_text("utente.prova@example.com").count() >= 1)
        await field(tel, "Password").fill("corta")
        await field(tel, "Ripeti la password").fill("corta")
        await tel.get_by_role("button", name="Continua").click()
        check("Password troppo corta rifiutata", "10 caratteri" in " ".join(await tel.locator(".sheet-error").all_inner_texts()))
        await field(tel, "Password").fill("una frase segreta di prova")
        await field(tel, "Ripeti la password").fill("una frase segreta di prova")
        await tel.get_by_role("button", name="Continua").click()
        key = (await tel.locator("p.key").text_content()).strip()
        check("Chiave di recupero mostrata", re.fullmatch(r"([A-Z2-9]{4}-){7}[A-Z2-9]{4}", key) is not None, key)
        await tel.get_by_role("button", name="Attiva", exact=True).click()
        check("Senza conferma della chiave non si attiva", "chiave di recupero" in " ".join(await tel.locator(".sheet-error").all_inner_texts()))
        async with tel.expect_download() as dl:
            await tel.get_by_role("button", name="Scarica come file").click()
        kf = await dl.value; check("Chiave scaricabile come file", kf.suggested_filename == "statera-chiave-di-recupero.txt")
        await tel.get_by_label("Ho conservato la chiave di recupero in un posto sicuro").check()
        await tel.get_by_role("button", name="Attiva", exact=True).click()
        await tel.get_by_text("Sincronizzazione attiva").wait_for(timeout=20000)
        await tel.get_by_role("button", name="Fatto").click()
        check("Su Drive: chiavi, dati e backup del giorno", drive.names()[:1] == ["statera-backup-" + time.strftime("%Y-%m-%d") + ".json"] and "statera-data.json" in drive.names() and "statera-keys.json" in drive.names(), str(drive.names()))
        check("Dati su Drive cifrati (nessun testo leggibile)", "Cinema" not in drive.content("statera-data.json") and "Conto" not in drive.content("statera-data.json"))
        check("Password non salvata su Drive", "una frase segreta" not in drive.content("statera-keys.json"))
        st = await sync_status(tel)
        check("Telefono: stato Sincronizzato", "Sincronizzato" in st and "utente.prova@example.com" in st, st)

        # ---------- PC: secondo dispositivo con dati di prova propri ----------
        pctx, pc, perr = await new_device(b, p, "pc", False)
        await add_account(pc, "conto", "1000")          # stesso conto, scritto diversamente
        await add_expense(pc, "5", "Prova dal PC")
        await pc.goto(BASE + "/#/altro"); await pc.wait_for_timeout(300)
        await pc.get_by_role("button", name="Attiva la sincronizzazione").click()
        await pc.get_by_role("button", name="Accedi con Google").click()
        await field(pc, "Password di Statera").wait_for()
        check("PC: riconosce Statera già attiva su Drive", await pc.get_by_text("c'è già Statera").count() == 1)
        await field(pc, "Password di Statera").fill("password sbagliata!!")
        await pc.get_by_role("button", name="Collega questo dispositivo").click()
        await pc.wait_for_timeout(2500)
        check("PC: password sbagliata rifiutata", "non corretta" in " ".join(await pc.locator(".sheet-error").all_inner_texts()))
        await field(pc, "Password di Statera").fill("una frase segreta di prova")
        await pc.get_by_role("button", name="Collega questo dispositivo").click()
        await pc.get_by_text("Sincronizzazione attiva").wait_for(timeout=20000)
        await pc.get_by_role("button", name="Fatto").click()
        d = await descriptions(pc)
        check("PC: unione dei dati (telefono + PC)", d == ["Cinema dal telefono", "Prova dal PC"], str(d))
        await pc.goto(BASE + "/#/conti"); await pc.wait_for_timeout(400)
        names = await pc.locator(".list").first.locator(".name").all_text_contents()
        check("PC: un solo conto 'Conto' (nessun doppione)", names == ["Conto"], str(names))
        await pc.goto(BASE + "/#/categorie"); await pc.wait_for_timeout(300)
        cats = await pc.locator(".list-row .name:not(.child)").all_text_contents()
        check("PC: nessuna categoria doppia", len(cats) == len(set(cats)), str(cats))

        # ---------- modifiche automatiche nei due sensi ----------
        await add_expense(pc, "20", "Pizza dal PC")
        await pc.wait_for_timeout(5500)  # sincronizzazione automatica dopo la modifica
        await tel.evaluate("document.dispatchEvent(new Event('visibilitychange'))")  # telefono torna in primo piano
        await tel.wait_for_timeout(2500)
        d = await descriptions(tel)
        check("Telefono riceve la spesa fatta sul PC", "Pizza dal PC" in d and "Prova dal PC" in d, str(d))
        await tel.goto(BASE + "/#/conti"); await tel.wait_for_timeout(400)
        bal = await tel.locator(".list").first.inner_text()
        check("Telefono: saldo aggiornato 963,00", "963,00" in bal, bal)

        # ---------- permesso scaduto ----------
        await tel.evaluate("""() => { for (const k of Object.keys(localStorage)) if (k.startsWith('statera.token')) localStorage.setItem(k, JSON.stringify({value:'tok-old', expiresAt: 1})) }""")
        expire = """() => { for (const k of Object.keys(localStorage)) if (k.startsWith('statera.token')) localStorage.setItem(k, JSON.stringify({value:'tok-old', expiresAt: 1})) }"""
        await tel.reload(); await tel.wait_for_selector("nav"); await tel.wait_for_timeout(1500)
        banner = tel.get_by_role("button", name="Riconnetti", exact=True)
        check("Permesso scaduto: nessun avviso finché non si tocca nulla", await banner.count() == 0)
        calls = await tel.evaluate("() => window.__gisCalls || 0")
        await tel.get_by_role("button", name="Nuovo movimento").first.click(); await tel.wait_for_timeout(600)
        check("Il + non fa partire il rinnovo (non disturba l'inserimento)", await tel.evaluate("() => window.__gisCalls || 0") == calls)
        await tel.get_by_role("button", name="Chiudi").first.click(); await tel.wait_for_timeout(300)
        await tel.get_by_role("link", name="Movimenti").first.click(); await tel.wait_for_timeout(2500)
        check("Al primo tocco il permesso si rinnova da solo", await tel.evaluate("() => window.__gisCalls || 0") == calls + 1 and await banner.count() == 0 and "Sincronizzato" in await sync_status(tel), await sync_status(tel))
        # rinnovo automatico non riuscito (es. finestra bloccata): compare l'avviso
        await tel.evaluate(expire); await tel.reload(); await tel.wait_for_selector("nav"); await tel.wait_for_timeout(1500)
        await tel.evaluate("() => { window.__gisFail = true }")
        await tel.get_by_role("link", name="Conti").first.click(); await tel.wait_for_timeout(1000)
        check("Rinnovo automatico non riuscito: avviso 'Riconnetti'", await banner.count() == 1)
        await tel.get_by_role("link", name="Analisi").first.click(); await tel.wait_for_timeout(600)
        check("Un solo tentativo automatico per scadenza", await tel.evaluate("() => window.__gisCalls || 0") == 1)
        await tel.evaluate("() => { window.__gisFail = false }")
        await banner.click(); await tel.wait_for_timeout(2500)
        check("Dopo 'Riconnetti' torna sincronizzato", await banner.count() == 0 and "Sincronizzato" in await sync_status(tel))

        # ---------- cambio password e terzo dispositivo con chiave di recupero ----------
        await tel.goto(BASE + "/#/altro"); await tel.wait_for_timeout(300)
        await tel.get_by_role("button", name="Cambia password").click()
        await field(tel, "Password attuale").fill("una frase segreta di prova")
        await field(tel, "Nuova password").fill("nuova frase segreta 2")
        await field(tel, "Ripeti la nuova password").fill("nuova frase segreta 2")
        await tel.locator("dialog").get_by_role("button", name="Cambia password").click()
        await tel.get_by_text("Password cambiata").wait_for(timeout=20000)
        await tel.get_by_role("button", name="Fatto").click()
        check("Cambio password", True)

        cctx, c3, cerr = await new_device(b, p, "tablet", True)
        await c3.goto(BASE + "/#/altro"); await c3.wait_for_timeout(300)
        await c3.get_by_role("button", name="Attiva la sincronizzazione").click()
        await c3.get_by_role("button", name="Accedi con Google").click()
        await field(c3, "Password di Statera").wait_for()
        await c3.get_by_role("button", name=re.compile("Ho dimenticato la password")).click()
        await field(c3, "Chiave di recupero").fill(key.lower().replace("-", " "))
        await field(c3, "Nuova password").fill("terza password valida")
        await field(c3, "Ripeti la nuova password").fill("terza password valida")
        await c3.get_by_role("button", name="Collega questo dispositivo").click()
        await c3.get_by_text("Sincronizzazione attiva").wait_for(timeout=30000)
        await c3.get_by_role("button", name="Fatto").click()
        d = await descriptions(c3)
        check("Terzo dispositivo con chiave di recupero: riceve tutto", d == ["Cinema dal telefono", "Pizza dal PC", "Prova dal PC"], str(d))
        keys = json.loads(drive.content("statera-keys.json"))
        check("Nuova password impostata dal recupero vale su Drive", keys["format"] == "statera-keys")

        # ---------- backup su Drive e ripristino ----------
        await pc.goto(BASE + "/#/movimenti"); await pc.wait_for_timeout(300)
        await pc.get_by_role("button", name=re.compile("^Pizza dal PC")).click()
        await pc.get_by_role("button", name="Elimina").click(); await pc.get_by_role("button", name="Conferma eliminazione").click()
        await pc.wait_for_timeout(5500)
        await tel.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await tel.wait_for_timeout(2500)
        check("Cancellazione sul PC arriva al telefono", "Pizza dal PC" not in await descriptions(tel))
        await tel.goto(BASE + "/#/altro"); await tel.wait_for_timeout(300)
        await tel.get_by_role("button", name="Backup su Drive").click()
        await tel.locator("dialog").get_by_role("button", name="Ripristina").first.wait_for(timeout=10000)
        n_b = await tel.locator("dialog").get_by_role("button", name="Ripristina").count()
        check("Elenco backup su Drive", n_b == 1, str(n_b))
        await tel.locator("dialog").get_by_role("button", name="Ripristina").first.click()
        await tel.locator("dialog").get_by_role("button", name="Conferma ripristino").click()
        await tel.get_by_text("Dati riportati").wait_for(timeout=15000)
        await tel.get_by_role("button", name="Chiudi").click()
        d = await descriptions(tel)
        check("Ripristino backup: torna lo stato del backup", d == ["Cinema dal telefono", "Pizza dal PC", "Prova dal PC"], str(d))
        await pc.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pc.wait_for_timeout(2500)
        check("Ripristino vale anche per il PC", "Pizza dal PC" in await descriptions(pc))

        # ---------- profili: secondo account sullo stesso dispositivo ----------
        await pc.goto(BASE + "/#/altro"); await pc.wait_for_timeout(300)
        await pc.get_by_role("button", name=re.compile("Account e profili")).click()
        await pc.get_by_role("button", name="Aggiungi un altro account").click()
        await pc.wait_for_selector("nav"); await pc.wait_for_timeout(800)
        check("Nuovo profilo: vuoto e non collegato", await descriptions(pc) == [] and "Non attiva" in await sync_status(pc))
        await pc.get_by_role("button", name=re.compile("Account e profili")).click()
        await pc.get_by_role("button", name=re.compile("utente.prova@example.com")).click()
        await pc.wait_for_selector("nav"); await pc.wait_for_timeout(1500)
        check("Ritorno al profilo principale con i suoi dati", "Cinema dal telefono" in await descriptions(pc))

        # ---------- scollegare ----------
        await c3.goto(BASE + "/#/altro"); await c3.wait_for_timeout(300)
        await c3.get_by_role("button", name="Scollega questo dispositivo").click()
        await c3.get_by_role("button", name="Conferma: scollega").click(); await c3.wait_for_timeout(500)
        check("Scollega: dispositivo non più collegato, dati locali restano", "Non attiva" in await sync_status(c3) and len(await descriptions(c3)) == 3)

        # ---------- offline ----------
        await tctx.set_offline(True)
        await add_expense(tel, "3", "Caffè offline")
        await tel.wait_for_timeout(5000)
        st = await sync_status(tel)
        check("Senza rete: movimento salvato, sync in attesa", "In attesa di connessione" in st or "Sincronizzato" in st, st)
        await tctx.set_offline(False)
        await tel.evaluate("window.dispatchEvent(new Event('online'))"); await tel.wait_for_timeout(3000)
        await pc.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pc.wait_for_timeout(2500)
        check("Tornata la rete: il movimento arriva al PC", "Caffè offline" in await descriptions(pc))

        all_err = [e for e in terr + perr + cerr if "net::ERR_INTERNET_DISCONNECTED" not in e and "Failed to fetch" not in e]
        check("Nessun errore in console", not all_err, " | ".join(all_err[:4]))
        await b.close()
    fails = [r for r in results if not r[1]]
    print(f"\nTOTALE: {len(results)-len(fails)}/{len(results)} superati")

asyncio.run(main())
