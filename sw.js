// Service worker de Mi Canastita: guarda la app para que abra sin internet
const CACHE = 'canastita-v10';
const APP = ['./', './index.html', './manifest.webmanifest', './icons/app-192.png', './icons/app-512.png',
             './icons/app-adaptable-192.png', './icons/app-adaptable-512.png', './icons/app-apple-180.png', './icons/app-icono.svg'];

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
    // Siempre pide la versión más nueva al servidor (sin la caché del navegador) para que las mejoras lleguen al abrir la app
    e.respondWith(fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { const c = r.clone(); if (r.ok) caches.open(CACHE).then(x => x.put('./index.html', c)); return r; })
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
