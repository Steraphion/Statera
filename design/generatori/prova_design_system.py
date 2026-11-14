#!/usr/bin/env python3
"""Controllo locale del design system: una pagina per anteprima, in tema chiaro e scuro.
Uso: prova_design_system.py <uscita di design_system.py>
Scrive <uscita>/prova/<Componente>-light.html e -dark.html, con tokens.css e bundle.css come nella pagina.
Per le immagini, ad esempio:
  google-chrome --headless=new --window-size=1000,800 --screenshot=X.png --allow-file-access-from-files file://…/X.html"""
import os, sys

out = sys.argv[1]; P = os.path.join(out, 'project')
d = os.path.join(out, 'prova'); os.makedirs(d, exist_ok=True)
for c in sorted(os.listdir(os.path.join(P, 'components'))):
    f = os.path.join(P, 'components', c, 'preview.html')
    if not os.path.exists(f): continue
    body = open(f).read()
    for th in ('light', 'dark'):
        open(os.path.join(d, f'{c}-{th}.html'), 'w').write(
            f'<!doctype html><html data-theme="{th}"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="../project/tokens.css"><link rel="stylesheet" href="../project/components/bundle.css">'
            f'<style>body{{margin:0;background:var(--color-bg)}}</style></head><body>{body}</body></html>')
    print(c)
