"""Shared building blocks for generated pages (blog, security, FAQ).

The icon sprite, floating header, mobile menu, and footer are copied from index.html,
so every generated page stays identical to the homepage chrome. Links are rewritten
for the page's folder depth, so pages work at the domain root and in a subfolder.
"""
import io, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.labora.example"   # placeholder; change with `npm run set-domain -- https://www.yourdomain.com`
INLINE_JS = "<script>document.documentElement.classList.add('js');</script>"

_home = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

def _block(start, end):
    a = _home.index(start)
    return _home[a:_home.index(end, a) + len(end)]

SPRITE = _block('<svg width="0" height="0"', '</svg>\n')
HEADER = _block('<header class="site-header"', '</header>')
MENU = _block('<nav class="mobile-menu"', '</nav>')
FOOTER = _block('<footer class="site-footer">', '</footer>')

# Filled brand marks for social sharing (not part of the outline icon set)
SPRITE = SPRITE.replace('</defs>', '''  <symbol id="b-linkedin" viewBox="0 0 24 24"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45z"/></symbol>
    <symbol id="b-x" viewBox="0 0 24 24"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.67l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64z"/></symbol>
  </defs>''') if '</defs>' in SPRITE else SPRITE

# In-page anchors on the homepage, and site pages linked relatively from the homepage
HOME_ANCHORS = ['#home-collection', '#demo', '#faq', '#product-tour', '#security']
SITE_PAGES = ['blog/', 'security/', 'faq/']

def chrome(prefix, current=None):
    """Header, mobile menu, and footer for a page `prefix` (e.g. "../") below the site root.
    `current` marks the section the page belongs to: "blog", "security", or "faq"."""
    h, m, f = HEADER, MENU, FOOTER
    for frag in HOME_ANCHORS:
        h, m, f = (x.replace(f'href="{frag}"', f'href="{prefix}{frag}"') for x in (h, m, f))
    for pg in SITE_PAGES:
        h, m, f = (x.replace(f'href="{pg}"', f'href="{prefix}{pg}"') for x in (h, m, f))
    h = h.replace('<a class="logo" href="/"', f'<a class="logo" href="{prefix}"')
    f = f.replace('<a class="logo" href="/"', f'<a class="logo" href="{prefix}"')
    if current == "blog":
        # "Resources" leads to the blog hub and is marked as the current section
        h = h.replace('<a class="nav-link" href="/resources/">Resources</a>', f'<a class="nav-link" href="{prefix}blog/" aria-current="page">Resources</a>')
        m = m.replace('<a class="m-link" href="/resources/">Resources</a>', f'<a class="m-link" href="{prefix}blog/" aria-current="page">Resources</a>')
    if current:
        f = f.replace(f'href="{prefix}{current}/"', f'href="{prefix}{current}/" aria-current="page"', 1)
    return h, m, f

OG_ALT = "Labora laboratory management software dashboard"

def head(prefix, title, desc, canonical, og_image, jsonld, css=(), og_type="website", og_alt=OG_ALT, og_size=(1200, 630)):
    links = '\n  '.join(f'<link rel="stylesheet" href="{prefix}assets/css/{c}">' for c in ('styles.min.css', *css))
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0d3a33">
  <meta name="format-detection" content="telephone=no">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Labora">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="{og_size[0]}">
  <meta property="og:image:height" content="{og_size[1]}">
  <meta property="og:image:alt" content="{html.escape(og_alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(desc)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{prefix}assets/img/apple-touch-icon.png">
  <link rel="manifest" href="{prefix}site.webmanifest">
  <link rel="preload" href="{prefix}assets/fonts/figtree-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  {links}
  {INLINE_JS}
  <script type="application/ld+json">
{jsonld}
  </script>
</head>'''

def page(prefix, current, title, desc, canonical, og_image, jsonld, body, css=(), js=(), og_type="website", og_alt=OG_ALT):
    h, m, f = chrome(prefix, current)
    scripts = '\n'.join(f'<script src="{prefix}assets/js/{s}" defer></script>' for s in ('main.min.js', *js))
    return f'''{head(prefix, title, desc, canonical, og_image, jsonld, css, og_type, og_alt)}
<body>
<a class="skip-link" href="#main">Skip to content</a>
{SPRITE}
{h}

{m}

<main id="main" class="{current}-main">
{body}
</main>

{f}

{scripts}
</body>
</html>
'''

def write(rel_path, content):
    p = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="").write(content)
