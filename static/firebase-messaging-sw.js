// Import the necessary Firebase scripts (No ES6 imports allowed!)
importScripts('https://www.gstatic.com/firebasejs/11.4.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/11.4.0/firebase-messaging-compat.js');

// Initialize Firebase (replace with your actual config from your Firebase Console)
firebase.initializeApp({
    apiKey: "AIzaSyDBnH_d4k-LofTrj9a9y0yRbXaQGZzmKqI",
    authDomain: "net-ready-5a5c1.firebaseapp.com",
    projectId: "inet-ready-5a5c1",
    storageBucket: "inet-ready-5a5c1.firebasestorage.app",
    messagingSenderId: "452680864851",
    appId: "452680864851:web:79303713fff1d23a4ae2a6",
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
        icon: "/firebase-logo.png"
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});
