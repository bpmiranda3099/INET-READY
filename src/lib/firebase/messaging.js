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
              // Get the VAPID key 
              // Option 1: Use the environment variable properly
              const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;
              
              // Option 2 (fallback): Use the actual Base64 VAPID key directly from Firebase Console
              // If the env variable isn't available, use a fallback key
              // You can get this key from Firebase Console -> Project Settings -> Cloud Messaging -> Web Push certificates
              const fallbackVapidKey = "BH8kgEvLl8BMqiLFpV_PeSsRMplLVzrwZft_-VE7qUZL9opz41bXD_3-f13jIdKJ35XPNCBkYeUGtQ5E2jU0PyA";
              
              const effectiveVapidKey = vapidKey || fallbackVapidKey;
              
              try {
                console.log("Attempting to get FCM token with VAPID key");
                const token = await getToken(messaging, { vapidKey: effectiveVapidKey });
                if (token) {
                  console.log("FCM Token successfully obtained:", token);
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
