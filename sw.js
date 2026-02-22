const CACHE_NAME = 'presize-cache-v2';
const assetsToCache = [
  '/',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  'https://cdn.tailwindcss.com'
];

// Tahap Install: Menyimpan aset penting ke dalam cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Membuka cache dan menyimpan aset');
        return cache.addAll(assetsToCache);
      })
  );
});

// Tahap Aktifasi: Membersihkan cache lama jika ada update
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Menghapus cache lama');
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Strategi Fetch: Ambil dari cache dulu, jika tidak ada baru ambil dari internet
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});
