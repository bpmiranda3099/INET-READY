import app from './app';

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
        messaging = getMessaging(app);
        console.log("Firebase Messaging initialized");
        
        // Override the placeholder functions with real implementations
        
        // Request notification permission and FCM token
        requestFCMToken = async () => {
          try {
            // Check if permission is already granted
            const permission = await Notification.requestPermission();
            
            if (permission === "granted") {
              // Replace with your actual VAPID key from Firebase Console
              // Project Settings -> Cloud Messaging -> Web Push Certificates
              const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;
              
              try {
                const token = await getToken(messaging, { vapidKey });
                if (token) {
                  console.log("FCM Token:", token);
                  return token;
                } else {
                  console.log("No registration token available.");
                  return null;
                }
              } catch (error) {
                console.error("Error getting FCM token:", error);
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
            callback(payload);
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
