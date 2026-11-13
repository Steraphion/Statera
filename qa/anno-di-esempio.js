// Inserisce un anno di movimenti di esempio direttamente nel database dell'app (solo per prove)
async () => {
  const db = await new Promise(r => { const q = indexedDB.open(localStorage.getItem('statera.profiloAttivo') || 'statera-locale'); q.onsuccess = () => r(q.result) })
  const get = (s) => new Promise(r => { const q = db.transaction(s).objectStore(s).getAll(); q.onsuccess = () => r(q.result) })
  const cats = await get('categories'); const accs = await get('accounts')
  const conto = accs.find(a => a.type === 'conto_corrente'); const buoni = accs.find(a => a.type === 'buoni_pasto')
  const cid = (name) => cats.find(c => c.name === name).id
  const now = Date.now(); const out = []
  let n = 0
  const add = (date, type, amount, cat, desc, acc = conto) => out.push({ id: 'fake-' + (++n), createdAt: now, updatedAt: now, deletedAt: null, type, date, categoryId: cat ? cid(cat) : null, description: desc, notes: '', toAccountId: null, accountIds: [acc.id], parts: [{ accountId: acc.id, cardId: null, amount, vouchers: null, voucherValue: null }] })
  for (let i = 11; i >= 0; i--) {
    const d = new Date(2026, 10 - i, 1); const m = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    add(`${m}-01`, 'entrata', 165000, 'Stipendio', 'Stipendio')
    add(`${m}-03`, 'uscita', 55000, 'Affitto/mutuo', 'Affitto')
    add(`${m}-08`, 'uscita', 6000 + (i * 731) % 5000, 'Bollette', 'Luce e gas')
    add(`${m}-10`, 'uscita', 18000 + (i * 1913) % 9000, 'Spesa alimentare', 'Spesa settimana')
    add(`${m}-17`, 'uscita', 9000 + (i * 977) % 6000, 'Spesa alimentare', 'Spesa')
    add(`${m}-12`, 'uscita', 4000 + (i * 1301) % 3000, 'Carburante', 'Benzina')
    add(`${m}-15`, 'uscita', 2500 + (i * 503) % 4000, 'Svago', 'Cinema e uscite')
    if (i % 3 === 0) add(`${m}-20`, 'uscita', 12000, 'Abbigliamento', 'Vestiti')
    if (i === 4) add(`${m}-05`, 'uscita', 60000, 'Viaggi', 'Weekend')
    if (i % 4 === 1) add(`${m}-25`, 'entrata', 8000, 'Rimborsi', 'Rimborso spese')
  }
  await new Promise(r => { const t = db.transaction('transactions', 'readwrite'); for (const x of out) t.objectStore('transactions').put(x); t.oncomplete = r })
  db.close()
  return out.length
}
