import { getMessaging, getToken, onMessage } from "firebase/messaging";
import app from './app';

let messaging = null;

// Initialize Firebase Messaging if in browser
if (typeof window !== "undefined") {
  messaging = getMessaging(app);
}

// Function to request permission and get FCM token
export const requestFCMToken = async () => {
  try {
    if (!messaging) {
      console.warn("Firebase Messaging is not available in this environment.");
      return null;
    }

    // Request permission for notifications
    const permission = await Notification.requestPermission();
    
    if (permission === "granted") {
      // Get the token
      const token = await getToken(messaging, {
        vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
      });
      
      console.log("FCM Token:", token);
      return token;
    } else {
      console.log("Notification permission denied");
      return null;
    }
  } catch (error) {
    console.error("Error getting FCM token:", error);
    return null;
  }
};

// Handle foreground messages
export const onMessageListener = () => {
  return new Promise((resolve) => {
    if (!messaging) {
      console.warn("Firebase Messaging is not available in this environment.");
      return;
    }
    
    onMessage(messaging, (payload) => {
      resolve(payload);
    });
  });
};

export default messaging;
