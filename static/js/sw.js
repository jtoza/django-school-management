// Service Worker for EduSync School Management
const CACHE_NAME = 'edusync-v1.0.0';
const urlsToCache = [
  '/',
  '/static/dist/css/adminlte.min.css',
  '/static/plugins/fontawesome-free/css/all.min.css',
  '/static/plugins/toastr/toastr.min.css',
  '/static/dist/js/adminlte.min.js',
  '/static/plugins/jquery/jquery.min.js',
  '/static/plugins/bootstrap/js/bootstrap.bundle.min.js',
  '/static/plugins/toastr/toastr.min.js',
  '/static/dist/img/icon-192x192.png',
  '/static/dist/img/icon-512x512.png',
  '/offline/'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip Chrome extensions
  if (event.request.url.startsWith('chrome-extension://')) return;

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request)
          .then(fetchResponse => {
            // Check if we received a valid response
            if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
              return fetchResponse;
            }

            // Clone the response
            const responseToCache = fetchResponse.clone();

            // Add to cache for future visits
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return fetchResponse;
          })
          .catch(error => {
            // If both cache and network fail, show offline page
            console.log('Fetch failed; returning offline page instead.', error);
            
            // For navigation requests, show custom offline page
            if (event.request.mode === 'navigate') {
              return caches.match('/offline/');
            }
            
            // For other requests, you might want to return a fallback
            return new Response('Network error happened', {
              status: 408,
              headers: { 'Content-Type': 'text/plain' },
            });
          });
      })
  );
});

// Handle push notifications (for future use)
self.addEventListener('push', event => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body || 'New notification from EduSync',
    icon: '/static/dist/img/icon-192x192.png',
    badge: '/static/dist/img/icon-72x72.png',
    tag: 'edusync-notification',
    renotify: true,
    actions: [
      {
        action: 'view',
        title: 'View'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'EduSync', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});