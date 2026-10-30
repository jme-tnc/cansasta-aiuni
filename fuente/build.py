"""Arma la carpeta pwa/ a partir de app.html: index.html completo, manifest, service worker e íconos."""
import json, re, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent      # carpeta fuente/
OUT = ROOT.parent                          # la app se genera en la raíz del repositorio
(OUT / "icons").mkdir(parents=True, exist_ok=True)

BASKET = """
<path d="M150 262 C150 120 362 120 362 262" fill="none" stroke="#EFA383" stroke-width="24" stroke-linecap="round"/>
<circle cx="198" cy="252" r="44" fill="#BDE8D4"/>
<circle cx="306" cy="246" r="48" fill="#FFE39A"/>
<path d="M300 200 q16 -26 40 -22 q-10 26 -40 22z" fill="#8FD3B4"/>
<path d="M118 300 L394 300 L362 424 Q357 442 338 442 L174 442 Q155 442 150 424 Z" fill="#FFF3E6"/>
<g stroke="#F4C3A6" stroke-width="10" stroke-linecap="round">
<line x1="138" y1="340" x2="374" y2="340"/><line x1="148" y1="380" x2="364" y2="380"/><line x1="160" y1="418" x2="352" y2="418"/>
<line x1="200" y1="306" x2="208" y2="436"/><line x1="256" y1="306" x2="256" y2="436"/><line x1="312" y1="306" x2="304" y2="436"/>
</g>
<rect x="96" y="268" width="320" height="50" rx="25" fill="#EFA383"/>
<g transform="translate(256 150)">
<path d="M0 0 C-30 -40 -78 -30 -70 6 C-64 34 -24 22 0 0Z" fill="#EE86A8"/>
<path d="M0 0 C30 -40 78 -30 70 6 C64 34 24 22 0 0Z" fill="#EE86A8"/>
<path d="M-6 6 L-30 58 L-12 52 L-2 66 Z M6 6 L30 58 L12 52 L2 66 Z" fill="#E7769B"/>
<circle r="15" fill="#F7A9C2"/>
</g>"""

def icon_svg(scale=1.0, rounded=True):
    bg = '<rect width="512" height="512" rx="112" fill="#FBD6E1"/>' if rounded else '<rect width="512" height="512" fill="#FBD6E1"/>'
    dots = '<circle cx="256" cy="282" r="200" fill="#FFFFFF" opacity=".55"/>'
    t = f'translate({256*(1-scale)} {256*(1-scale)+10*scale}) scale({scale})'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{bg}<g transform="{t}">{dots}{BASKET}</g></svg>'

(OUT / "icons" / "favicon.svg").write_text(icon_svg(0.92))

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for name, size, svg in [
        ("icon-192.png", 192, icon_svg(0.92)),
        ("icon-512.png", 512, icon_svg(0.92)),
        ("apple-touch-icon.png", 180, icon_svg(0.86, rounded=False)),
        ("maskable-512.png", 512, icon_svg(0.70, rounded=False)),
    ]:
        pg.set_viewport_size({"width": size, "height": size})
        pg.set_content(f'<html><body style="margin:0;background:transparent">'
                       f'<div style="width:{size}px;height:{size}px">{svg.replace("<svg ", f"<svg width={size} height={size} ")}</div></body></html>')
        pg.screenshot(path=str(OUT / "icons" / name), omit_background=True)
    b.close()

manifest = {
    "name": "Mi Canastita – Lista de compras",
    "short_name": "Mi Canastita",
    "description": "Lista de compras simple con íconos que cambian según el producto.",
    "lang": "es-PE",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#FFF6F8",
    "theme_color": "#FBD6E1",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

SW = """// Service worker de Mi Canastita: guarda la app para que abra sin internet
const CACHE = 'canastita-v2';
const APP = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png',
             './icons/icon-512.png', './icons/apple-touch-icon.png', './icons/favicon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(APP)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put('./index.html', c)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  if (url.origin === location.origin || url.host.endsWith('fonts.googleapis.com') || url.host.endsWith('fonts.gstatic.com')) {
    e.respondWith(caches.match(req).then(hit => {
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); } return r; })
        .catch(() => hit);
      return hit || net;
    }));
  }
});
"""
(OUT / "sw.js").write_text(SW)

src = (ROOT / "app.html").read_text()
src = re.sub(r"<title>.*?</title>\s*", "", src, count=1)
src = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', "", src, count=1)

HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Mi Canastita</title>
<meta name="description" content="Lista de compras simple con íconos que cambian según el producto.">
<meta name="theme-color" content="#FBD6E1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#4A2E3E" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Mi Canastita">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
"""
head_part, body_part = src.split("</style>", 1)
SWREG = """<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });
}
</script>
"""
html = HEAD + head_part + "</style>\n</head>\n<body>\n" + body_part + SWREG + "</body>\n</html>\n"
(OUT / "index.html").write_text(html)
print("ok", [str(x.relative_to(OUT)) for x in sorted(OUT.rglob("*")) if x.is_file()])
