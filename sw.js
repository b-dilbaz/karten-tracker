// Service Worker: App startet auch offline, Preise werden bei Verbindung frisch geholt.
const CACHE = 'karten-tracker-v1';
const SHELL = ['./', 'index.html', 'config.js', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png',
  'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // Datenbank-Anfragen (Supabase) und Kartenbilder nie abfangen
  if (url.hostname.endsWith('supabase.co') || url.hostname === 'assets.tcgdex.net') return;
  const sameOrigin = url.origin === self.location.origin;
  // Seite, Einstellungen und Preiskatalog: erst Netz, sonst Cache
  if (sameOrigin) {
    e.respondWith(fetch(e.request).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return r;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('index.html'))));
    return;
  }
  // Bibliothek vom CDN: erst Cache
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
