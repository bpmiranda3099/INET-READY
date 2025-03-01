// Import the necessary Firebase scripts (No ES6 imports allowed!)
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Initialize Firebase (use the exact same config as your app)
firebase.initializeApp({
  apiKey: "AIzaSyDBnH_d4k-LofTrj9a9y0yRbXaQGZzmKqI",
  authDomain: "inet-ready-5a5c1.firebaseapp.com",
  projectId: "inet-ready-5a5c1",
  storageBucket: "inet-ready-5a5c1.appspot.com",
  messagingSenderId: "452680864851",
  appId: "1:452680864851:web:79303713fff1d23a4ae2a6",
  measurementId: "G-JS80BEPX2C"
});

// Retrieve Firebase Messaging instance
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log("[firebase-messaging-sw.js] Received background message:", payload);

  const notificationTitle = payload.notification?.title || "Background Message";
  const notificationOptions = {
    body: payload.notification?.body || "You have a new message.",
    icon: "/app-icon.png"
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Optional: Add additional service worker functionality
self.addEventListener('install', (event) => {
  console.log('Service Worker installed');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activated');
});
