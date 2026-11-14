"""Estrae gli elementi delle icone scelte dai tre pacchetti in un JSON compatto (solo forme e attributi geometrici)."""
import os, sys, json, xml.etree.ElementTree as ET
L, T, P, risolte, out = sys.argv[1:6]
R = json.load(open(risolte))
OK_TAGS = {'path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse'}
OK_ATTR = {'d', 'cx', 'cy', 'r', 'rx', 'ry', 'x', 'y', 'width', 'height', 'x1', 'y1', 'x2', 'y2', 'points', 'opacity'}
def nodes(path, skip_bbox=False):
    root = ET.parse(path).getroot()
    res = []
    for el in root.iter():
        tag = el.tag.split('}')[-1]
        if tag not in OK_TAGS: continue
        if skip_bbox and el.get('stroke') == 'none': continue
        res.append([tag, {k: v for k, v in el.attrib.items() if k in OK_ATTR}])
    return res
src = {'lucide': lambda n: os.path.join(L, 'icons', n + '.svg'),
       'tabler': lambda n: os.path.join(T, 'icons', 'outline', n + '.svg'),
       'phosphor': lambda n: os.path.join(P, 'assets', 'duotone', n + '-duotone.svg')}
ver = {s: json.load(open(os.path.join(d, 'package.json')))['version'] for s, d in (('lucide', L), ('tabler', T), ('phosphor', P))}
data = {
 'lucide': {'nome': 'Lucide', 'versione': ver['lucide'], 'licenza': 'ISC', 'viewBox': '0 0 24 24', 'modo': 'tratto', 'icone': {}},
 'tabler': {'nome': 'Tabler Icons', 'versione': ver['tabler'], 'licenza': 'MIT', 'viewBox': '0 0 24 24', 'modo': 'tratto', 'icone': {}},
 'phosphor': {'nome': 'Phosphor (duotone)', 'versione': ver['phosphor'], 'licenza': 'MIT', 'viewBox': '0 0 256 256', 'modo': 'pieno', 'icone': {}},
}
for key, per in R.items():
    for s, name in per.items():
        data[s]['icone'][key] = {'nome': name, 'forme': nodes(src[s](name), skip_bbox=(s == 'tabler'))}
json.dump(data, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
print({s: len(v['icone']) for s, v in data.items()}, os.path.getsize(out))
