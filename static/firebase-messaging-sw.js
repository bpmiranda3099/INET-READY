// Firebase Messaging Service Worker
// This file must be in the root of your app (in the 'static' folder for SvelteKit)

// Import Firebase scripts - must use compat version for service workers
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Initialize Firebase with your app's config
firebase.initializeApp({
  apiKey: "AIzaSyDBnH_d4k-LofTrj9a9y0yRbXaQGZzmKqI",
  authDomain: "inet-ready-5a5c1.firebaseapp.com",
  projectId: "inet-ready-5a5c1",
  storageBucket: "inet-ready-5a5c1",
  messagingSenderId: "452680864851",
  appId: "1:452680864851:web:79303713fff1d23a4ae2a6",
  measurementId: "G-JS80BEPX2C"
});

// Get Firebase Messaging instance
const messaging = firebase.messaging();

// Cache name for static assets
const CACHE_NAME = 'inet-ready-static-v1';

// Assets to cache (add your app's critical assets here)
const STATIC_ASSETS = [
  '/',
  '/app',
  '/app-icon.png',
  '/favicon.png'
];

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message:', payload);

  // Extract notification data with fallbacks
  const notificationTitle = payload.notification?.title || 'INET-READY Alert';
  const notificationOptions = {
    body: payload.notification?.body || 'New health update available.',
    icon: '/app-icon.png',
    badge: '/favicon.png',
    tag: payload.data?.tag || 'default-tag',
    data: payload.data || {},
    // Add vibration pattern for mobile devices
    vibrate: [100, 50, 100],
    // Add action buttons if needed
    actions: [
      {
        action: 'view',
        title: 'View'
      }
    ],
    // Make sure notification persists in notification tray
    requireInteraction: true,
    // Add a timestamp for the notification (important for ordering)
    timestamp: Date.now()
  };

  // Show notification to user
  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Service worker installation
self.addEventListener('install', (event) => {
  console.log('[firebase-messaging-sw.js] Service Worker installing');
  
  // Cache static assets
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[firebase-messaging-sw.js] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch(error => {
        console.error('[firebase-messaging-sw.js] Cache error:', error);
      })
  );
  
  // Activate immediately
  self.skipWaiting();
});

// Service worker activation (when taking over from previous version)
self.addEventListener('activate', (event) => {
  console.log('[firebase-messaging-sw.js] Service Worker activating');
  
  // Clean up old caches
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[firebase-messaging-sw.js] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Take control of all clients immediately
  return self.clients.claim();
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification clicked:', event.notification.tag);
  
  event.notification.close();
  
  // Add custom action handling if needed
  if (event.action === 'view') {
    console.log('[firebase-messaging-sw.js] "View" action clicked');
  }
  
  // Open or focus the app when notification is clicked
  const urlToOpen = new URL('/app', self.location.origin).href;
  
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then((clientList) => {
      // Check if there's already a window/tab open
      for (const client of clientList) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If no open windows, open new one
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Handle push messages (this is CRITICAL for background notifications)
self.addEventListener('push', (event) => {
  console.log('[firebase-messaging-sw.js] Push event received:', event);
  
  // If the event doesn't contain data, use default message
  if (!event.data) {
    console.log('[firebase-messaging-sw.js] No data in push event, showing default notification');
    
    // Show a default notification
    const title = "INET-READY Weather Update";
    const options = {
      body: "New weather information is available.",
      icon: '/app-icon.png',
      badge: '/favicon.png'
    };
    
    event.waitUntil(
      self.registration.showNotification(title, options)
    );
    
    return;
  }
  
  // Try to parse the data
  try {
    const payload = event.data.json();
    console.log('[firebase-messaging-sw.js] Push event payload:', payload);
    
    // Extract notification
    const notificationTitle = payload.notification?.title || 'INET-READY Alert';
    const notificationOptions = {
      body: payload.notification?.body || 'New update available.',
      icon: '/app-icon.png',
      badge: '/favicon.png',
      data: payload.data || {},
      requireInteraction: true
    };
    
    event.waitUntil(
      self.registration.showNotification(notificationTitle, notificationOptions)
    );
  } catch (error) {
    console.error('[firebase-messaging-sw.js] Error handling push event:', error);
    
    // Show a fallback notification even if there's an error
    event.waitUntil(
      self.registration.showNotification('INET-READY Update', {
        body: 'New information is available.',
        icon: '/app-icon.png'
      })
    );
  }
});

// For testing registration and heartbeat
self.addEventListener('message', (event) => {
  console.log('[firebase-messaging-sw.js] Message received from client:', event.data);
  
  // You can communicate back to the client
  if (event.data && event.data.type === 'PING') {
    // ...existing code...
  }
});