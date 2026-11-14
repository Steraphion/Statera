"""Controlla quali nomi di icona esistono nei tre set (cartelle passate come argomenti)."""
import os, sys, json
L, T, P = sys.argv[1:4]
have = {'lucide': set(f[:-4] for f in os.listdir(os.path.join(L, 'icons')) if f.endswith('.svg')),
        'tabler': set(f[:-4] for f in os.listdir(os.path.join(T, 'icons', 'outline')) if f.endswith('.svg')),
        'phosphor': set(f[:-12] for f in os.listdir(os.path.join(P, 'assets', 'duotone')) if f.endswith('-duotone.svg'))}
# chiave: (lucide, tabler, phosphor) con alternative separate da |
WANT = json.load(open(sys.argv[4]))
out, miss = {}, []
for key, cands in WANT.items():
    out[key] = {}
    for s, c in zip(('lucide', 'tabler', 'phosphor'), cands):
        hit = next((n for n in c.split('|') if n in have[s]), None)
        if hit: out[key][s] = hit
        else: miss.append((key, s, c))
json.dump(out, open(sys.argv[5], 'w'), indent=1)
print('mancanti:', miss)
