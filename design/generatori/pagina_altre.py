#!/usr/bin/env python3
"""Pagina «Altre schermate · Indaco morbido» della tela: scrive le tavole e le voci da aggiungere a canvas.json.
Uso: pagina_altre.py mobile|pc|tutto
Le tavole vanno in $STATERA_CANVAS (o out/project); le voci dell'indice in voci-<parte>.json, nella stessa cartella.
L'indice si aggiorna aggiungendo quelle voci a boards, order e notes (più la pagina e il launch), senza toccare il resto."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import W, OUT
import altre, pc
from altre import THEMES, page_h

PAGE = {'id': 'schermate', 'name': 'Altre schermate · Indaco morbido'}
COL = W + 80          # colonna dei telefoni
PCOL = pc.PW + 80     # colonna dei PC
GAP_ROW = 120 + 260   # spazio tra righe (titolo compreso)

def mobile():
    boards, notes, y = {}, {}, 0
    for ri, (rtitle, screens) in enumerate(altre.MOBILE_ROWS):
        x = 0; maxh = 0
        for key, label, fn, h in screens:
            for theme, t, dark in THEMES:
                name = f'ind-{key}-{theme}.dc.html'
                html = page_h(f'Indaco morbido — {label}, {theme}', t, fn(altre.D, t, dark), h)
                open(os.path.join(OUT, name), 'w').write(html)
                boards[name] = {'x': x, 'y': y, 'w': W, 'h': h, 'title': f'Indaco morbido · {label}, {theme}', 'page': PAGE['id']}
                x += COL; maxh = max(maxh, h)
        notes[f'altT{ri}'] = {'x': 0, 'y': y - 260, 'text': rtitle, 'kind': 'title1', 'maxW': x - 80, 'page': PAGE['id']}
        if ri == 0:
            notes['altNote0'] = {'x': x, 'y': y, 'w': 360, 'size': 'm', 'fill': 'teal', 'page': PAGE['id'], 'text':
                "Conti: i buoni pasto hanno una scheda a «biglietti» (pieni quelli rimasti, tratteggiati gli usati) e gli obiettivi un anello con la percentuale scritta. "
                "Dettaglio conto: saldo progressivo riga per riga; un movimento precedente al saldo iniziale è segnato «non incide». "
                "Cerca evidenzia la parola trovata e mostra il totale dei risultati. Le schermate aperte da un'altra (dettaglio, Cerca, Ricorrenti, Categorie) hanno la freccia indietro e niente barra in basso."}
        if ri == 1:
            notes['altNoteIcone'] = {'x': x, 'y': y, 'w': 360, 'size': 'm', 'fill': 'orange', 'page': PAGE['id'], 'text':
                "Icone delle categorie: per ora quelle degli script. Dove manca (Sport, Bollette, Manutenzione, Auto) c'è l'iniziale nel cerchio colorato: "
                "può restare come ripiego per le categorie create dall'utente. La scelta definitiva va col set di icone (punto 3). "
                "Blocco: i pallini mostrano solo le cifre già scritte, così non si capisce quanto è lungo il PIN."}
        if ri == 3:
            notes['altNoteColori'] = {'x': x, 'y': y, 'w': 360, 'size': 'm', 'fill': 'blue', 'page': PAGE['id'], 'text':
                "Due ruoli di colore nuovi, da confermare nel design system. «Attenzione» (#A86A00, scuro #F2B13C) per budget quasi esaurito e promemoria, sempre con simbolo e testo. "
                "«Pericolo» (#B33736, scuro #F58B84) solo per azioni che cancellano, come Elimina: testo bianco 6,0:1, in scuro testo scuro 8,1:1. "
                "Le conferme a comparsa hanno i colori invertiti rispetto al tema."}
        y += maxh + GAP_ROW
    return boards, notes, y

def pcs(y0):
    boards, notes, y = {}, {}, y0
    for ti, (theme, t, dark) in enumerate(THEMES):
        x = 0; maxh = 0
        for key, label, fn, h in pc.PC_SCREENS:
            name = f'ind-pc-{key}-{theme}.dc.html'
            open(os.path.join(OUT, name), 'w').write(pc.page_pc(f'Indaco morbido PC — {label}, {theme}', t, fn(t, dark), h))
            boards[name] = {'x': x, 'y': y, 'w': pc.PW, 'h': h, 'title': f'PC · {label}, {theme}', 'page': PAGE['id'], 'expand': 'fill'}
            x += PCOL; maxh = max(maxh, h)
        notes[f'altPC{ti}'] = {'x': 0, 'y': y - 260, 'text': f'Versione per PC · tema {theme}', 'kind': 'title1', 'maxW': x - 80, 'page': PAGE['id']}
        if ti == 0:
            notes['altNotePC'] = {'x': x, 'y': y, 'w': 380, 'size': 'm', 'fill': 'teal', 'page': PAGE['id'], 'text':
                "PC: la barra flottante diventa una barra laterale (sezioni, «Nuovo movimento» con la sua scorciatoia, stato della sincronizzazione e profilo). "
                "I moduli si aprono in una finestra centrata, su due colonne. Le scorciatoie sono scritte accanto ai comandi; «?», «Esc» e «Invio» sono proposte nuove. "
                "Conti affianca elenco e dettaglio, con i movimenti in tabella. Le tavole sono fluide: a larghezza di telefono la barra laterale va in cima."}
        y += maxh + GAP_ROW
    return boards, notes, y

def write_voci(part, boards, notes):
    data = {'page': PAGE, 'launch': {'view': 'canvas', 'page': PAGE['id']}, 'boards': boards, 'order': list(boards), 'notes': notes}
    json.dump(data, open(os.path.join(OUT, f'voci-{part}.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'tutto'
    bad = altre.check()
    if bad:
        print('CONTRASTI INSUFFICIENTI'); sys.exit(1)
    mb, mn, y = mobile()
    if part in ('mobile', 'tutto'):
        write_voci('mobile', mb, mn); print('\n'.join(mb))
    if part in ('pc', 'tutto'):
        pb, pn, _ = pcs(y)
        write_voci('pc', pb, pn); print('\n'.join(pb))
