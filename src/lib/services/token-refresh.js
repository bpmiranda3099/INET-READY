import { getMessaging, getToken, onMessage } from 'firebase/messaging';
import { getFirestore, doc, updateDoc, setDoc, getDoc} from 'firebase/firestore';
import { onAuthStateChanged } from 'firebase/auth';
import auth from '../firebase/auth';
import app from '../firebase/app';
import { isServiceWorkerActive, registerServiceWorker } from './service-worker';

// Default VAPID key from environment
const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;

/**
 * Set up token refresh listeners and periodic checks
 * Call this function when your app initializes
 */
export async function setupTokenRefreshService() {
  // Only run in browser context
  if (typeof window === 'undefined') return;
  
  try {
    // Make sure service worker is active
    const swActive = await isServiceWorkerActive();
    if (!swActive) {
      await registerServiceWorker();
    }
    
    // Check if notifications are supported and permission is granted
    if (!('Notification' in window)) return;
    if (Notification.permission !== 'granted') return;
    
    const messaging = getMessaging(app);
    
    // Listen for token changes
    onMessage(messaging, () => {
      getToken(messaging, { vapidKey })
        .then(refreshedToken => {
          console.log('Token refreshed automatically');
          updateTokenInFirestore(refreshedToken);
        })
        .catch(err => {
          console.error('Unable to refresh token', err);
        });
    });
    
    // Update token for current user if logged in
    onAuthStateChanged(auth, user => {
      if (user) {
        getToken(messaging, { vapidKey })
          .then(currentToken => {
            if (currentToken) {
              updateTokenInFirestore(currentToken, user.uid);
              
              // Subscribe to the daily_weather_insights topic
              subscribeToTopic(currentToken, 'daily_weather_insights')
                .then(() => console.log('Subscribed to daily_weather_insights topic'))
                .catch(error => console.error('Failed to subscribe to topic:', error));
            }
          })
          .catch(console.error);
      }
    });
    
    // Set up periodic token validation
    setInterval(validateStoredTokens, 24 * 60 * 60 * 1000); // Once per day
    
  } catch (error) {
    console.error('Error setting up token refresh service:', error);
  }
}

/**
 * Subscribe a token to an FCM topic
 */
async function subscribeToTopic(token, topic) {
  try {
    // Use a proxy server or Firebase Function to call the FCM API
    // This is needed because FCM API requires server authentication
    const subscribeEndpoint = import.meta.env.VITE_FCM_SUBSCRIBE_ENDPOINT;
    
    if (!subscribeEndpoint) {
      console.error('No FCM subscription endpoint configured');
      return false;
    }
    
    const response = await fetch(subscribeEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token,
        topic
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to subscribe to topic: ${response.statusText}`);
    }
    
    return true;
  } catch (error) {
    console.error('Error subscribing to topic:', error);
    return false;
  }
}

/**
 * Update a user's FCM token in Firestore
 */
async function updateTokenInFirestore(token, uid = null) {
  try {
    const db = getFirestore();

    // If no UID provided, use current user
    if (!uid) {
      const currentUser = auth.currentUser;
      if (!currentUser) return;
      uid = currentUser.uid;
    }

    // Try to get the user's home city from preferences (userPreferences collection)
    let homeCity = null;
    try {
      const userPrefsRef = doc(db, 'userPreferences', uid);
      const userPrefsSnap = await getDoc(userPrefsRef);
      if (userPrefsSnap.exists() && userPrefsSnap.data().cityPreferences?.homeCity) {
        homeCity = userPrefsSnap.data().cityPreferences.homeCity;
      }
    } catch {
      // Ignore, fallback to null
    }

    // Update the user document with the new token and required fields
    await setDoc(doc(db, 'users', uid), {
      fcmToken: token,
      tokenUpdatedAt: new Date(),
      notification_enabled: true,
      ...(homeCity ? { location: { city: homeCity } } : {})
    }, { merge: true });

    // Also add to a separate tokens collection for easy querying
    await setDoc(doc(db, 'fcm_tokens', token), {
      token,
      userId: uid,
      createdAt: new Date(),
      lastValidated: new Date(),
      isValid: true,
      platform: 'web',
      subscribedTopics: ['daily_weather_insights'] // Default subscription
    });

  } catch (error) {
    console.error('Error updating token in Firestore:', error);
  }
}

// Other functions remain unchanged

// Initialize if in browser context
if (typeof window !== 'undefined') {
    // Delay initialization to not block the main thread during page load
    window.addEventListener('load', () => {
        setTimeout(() => {
            setupTokenRefreshService().catch(error => {
                console.error('Failed to set up token refresh service:', error);
            });
        }, 3000);
    });
}
function validateStoredTokens() {
    throw new Error('Function not implemented.');
}

