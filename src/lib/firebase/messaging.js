import app from './app';
import { registerServiceWorker, isServiceWorkerActive } from '../services/service-worker';

// Default empty exports for SSR compatibility
let messaging = null;
export let requestFCMToken = async () => null;
export let onMessageListener = () => () => {};

// Only import and initialize Firebase messaging in browser context
if (typeof window !== "undefined") {
  // Dynamically import Firebase messaging
  import('firebase/messaging').then(async (firebaseMessaging) => {
    const { getMessaging, getToken, onMessage, isSupported } = firebaseMessaging;
    
    try {
      // Check if browser supports Firebase Messaging
      if (await isSupported()) {
        // Make sure service worker is registered first
        const isWorkerActive = await isServiceWorkerActive();
        if (!isWorkerActive) {
          console.log("Service worker not active, registering now...");
          await registerServiceWorker();
        }
        
        messaging = getMessaging(app);
        console.log("Firebase Messaging initialized");
        
        // Override the placeholder functions with real implementations
        
        // Request notification permission and FCM token
        requestFCMToken = async () => {
          try {
            // Check if permission is already granted
            const permission = await Notification.requestPermission();
            
            if (permission === "granted") {
              // Get the VAPID key from environment variables
              const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;
              
              // Make sure service worker is active before requesting token
              const isWorkerActive = await isServiceWorkerActive();
              if (!isWorkerActive) {
                console.log("Service worker not active, registering now...");
                await registerServiceWorker();
              }
              
              try {
                console.log("Requesting FCM token with VAPID key...");
                const token = await getToken(messaging, { vapidKey });
                if (token) {
                  console.log("FCM token successfully obtained");
                  return token;
                } else {
                  console.log("No registration token available.");
                  return null;
                }
              } catch (error) {
                console.error("Error getting FCM token:", error);
                
                // More detailed error logging to help diagnose the issue
                if (error.code) {
                  console.error("Error code:", error.code);
                }
                if (error.message) {
                  console.error("Error message:", error.message);
                }
                
                return null;
              }
            } else {
              console.log("Notification permission denied");
              return null;
            }
          } catch (error) {
            console.error("Error requesting FCM token:", error);
            return null;
          }
        };
        
        // Listen for messages while the app is in the foreground
        onMessageListener = (callback) => {
          return onMessage(messaging, (payload) => {
            console.log("Received foreground message:", payload);
            if (callback && typeof callback === 'function') {
              callback(payload);
            }
            return () => {}; // Return unsubscribe function
          });
        };
      }
    } catch (error) {
      console.log("Firebase Messaging not supported:", error);
    }
  }).catch(error => {
    console.error("Error loading Firebase Messaging:", error);
  });
}

export default messaging;
