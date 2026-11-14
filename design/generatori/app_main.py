"""Lettura dei sorgenti dell'app (checkout del ramo main) per il design system.

Niente valori copiati a mano: token da src/styles/tokens.css, icone da src/lib/icons.ts,
logo da src/lib/logo.ts e icona/simbolo*.svg (tutti e due generati da scripts/icona-app.mjs),
carattere e licenza da src/assets/fonts/.
"""
import json, os, re


class App:
    def __init__(self, root):
        self.root = root
        self.version = json.load(open(self.p('package.json')))['version']
        self.tokens_light, self.tokens_dark = self._tokens()
        self.icons, self.cat_icons, self.cat_labels, self.cat_groups = self._icons()
        self.logo_size, self.logo_radius, self.logo = self._logo()
        self.simbolo = open(self.p('icona/simbolo.svg')).read().strip()
        self.simbolo_piccolo = open(self.p('icona/simbolo-piccolo.svg')).read().strip()
        self.font = self.p('src/assets/fonts/PlusJakartaSans-latin.woff2')
        self.font_license = self.p('src/assets/fonts/OFL.txt')

    def p(self, rel):
        return os.path.join(self.root, rel)

    # ------------------------------------------------------------ token
    def _tokens(self):
        css = re.sub(r'/\*.*?\*/', '', open(self.p('src/styles/tokens.css')).read(), flags=re.S)
        blocks = {}
        for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
            sel = sel.strip()
            decl = dict((k, v.strip()) for k, v in re.findall(r'--([A-Za-z0-9-]+)\s*:\s*([^;]+);', body))
            blocks[sel] = decl
        light = blocks[':root']
        dark = next(v for k, v in blocks.items() if 'data-theme' in k and 'dark' in k)
        return light, dark

    def value(self, name, theme='light'):
        """Valore di un token nel tema, con i var() risolti (per i contrasti)."""
        v = (self.tokens_dark.get(name) if theme == 'dark' else None) or self.tokens_light.get(name)
        m = re.fullmatch(r'var\(--([A-Za-z0-9-]+)\)', v or '')
        return self.value(m.group(1), theme) if m else v

    # ------------------------------------------------------------ icone
    def _icons(self):
        src = open(self.p('src/lib/icons.ts')).read()
        icons = {}
        body = src[src.index('export const ICONS = {'):src.index('\n}', src.index('export const ICONS = {'))]
        for name, nodes in re.findall(r"^  '([a-z0-9-]+)': (\[.*\]),?$", body, flags=re.M):
            icons[name] = json.loads(nodes)

        def obj(start):
            i = src.index(start); j = src.index('\n}', i)
            return src[src.index('{', i + len(start) - 1):j + 2]
        cat_icons = dict(re.findall(r"^\s+'?([a-z_]+)'?: '([a-z0-9-]+)'", obj('export const CATEGORY_ICONS = {'), flags=re.M))
        cat_labels = dict(re.findall(r"^\s+'?([a-z_]+)'?: '([^']+)'", obj('export const CATEGORY_ICON_LABELS'), flags=re.M))
        g0 = src.index('export const CATEGORY_ICON_GROUPS'); g1 = src.index('\n]', g0)
        groups_src = src[src.index('= [', g0) + 2:g1 + 2]
        groups = json.loads(groups_src.replace("'", '"'))
        return icons, cat_icons, cat_labels, groups

    def icon(self, name, size=20, sw=2):
        """Icona Lucide come la disegna il componente Icon dell'app."""
        inner = ''.join('<' + t + ''.join(f' {k}="{v}"' for k, v in a.items()) + '/>' for t, a in self.icons[name])
        return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')

    # ------------------------------------------------------------ logo
    def _logo(self):
        src = open(self.p('src/lib/logo.ts')).read()
        size = int(re.search(r'LOGO_SIZE = (\d+)', src).group(1))
        radius = int(re.search(r'LOGO_RADIUS = (\d+)', src).group(1))
        data = json.loads(src[src.index('= {', src.index('export const LOGO:')) + 2:].strip())
        return size, radius, data

    def logo_svg(self, px, cls='st-logo'):
        """Logo come il componente Logo: riquadro e simbolo coi colori dai token (classi in bundle.css)."""
        v = self.logo['piccolo' if px <= 32 else 'grande']
        nodes = ''.join('<' + t + ''.join(f' {k}="{a[k]}"' for k in a) + '/>' for t, a in v['nodes'])
        n = self.logo_size
        return (f'<svg class="{cls}" width="{px}" height="{px}" viewBox="0 0 {n} {n}" aria-hidden="true" focusable="false">'
                f'<rect class="st-logo__tile" width="{n}" height="{n}" rx="{self.logo_radius}"/>'
                f'<g class="st-logo__glyph" transform="{v["transform"]}">{nodes}</g></svg>')
