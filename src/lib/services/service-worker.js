import { writable } from 'svelte/store';

// Create stores for service worker status
export const serviceWorkerSupported = writable(false);
export const serviceWorkerRegistered = writable(false);
export const serviceWorkerError = writable(null);

// Service worker registration path - this points to the existing Firebase messaging SW
const SW_PATH = './././static/firebase-messaging-sw.js';

/**
 * Registers the service worker
 * @returns {Promise<ServiceWorkerRegistration|null>} The service worker registration or null if not supported
 */
export async function registerServiceWorker() {
  // Reset the error state
  serviceWorkerError.set(null);
  
  if ('serviceWorker' in navigator) {
    serviceWorkerSupported.set(true);
    
    try {
      const registration = await navigator.serviceWorker.register(SW_PATH, { 
        scope: '/' 
      });
      
      console.log('Service Worker registered successfully with scope:', registration.scope);
      serviceWorkerRegistered.set(true);
      
      // Set up event handlers for the service worker lifecycle
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        
        if (installingWorker) {
          installingWorker.onstatechange = () => {
            if (installingWorker.state === 'installed') {
              if (navigator.serviceWorker.controller) {
                // At this point, the updated precached content has been fetched,
                // but the previous service worker will still serve the older content
                console.log('New content is available and will be used when all tabs are closed.');
              } else {
                // At this point, everything has been precached.
                console.log('Content is cached for offline use.');
              }
            }
          };
        }
      };
      
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      serviceWorkerError.set(error.message);
      serviceWorkerRegistered.set(false);
      return null;
    }
  } else {
    console.log('Service Workers are not supported in this browser');
    serviceWorkerSupported.set(false);
    serviceWorkerRegistered.set(false);
    return null;
  }
}

/**
 * Unregisters all service workers for the current origin
 * @returns {Promise<boolean>} True if unregistration was successful
 */
export async function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      
      for (const registration of registrations) {
        await registration.unregister();
      }
      
      console.log('Service Workers unregistered successfully');
      serviceWorkerRegistered.set(false);
      return true;
    } catch (error) {
      console.error('Service Worker unregistration failed:', error);
      serviceWorkerError.set(error.message);
      return false;
    }
  }
  return false;
}

/**
 * Checks if a service worker is currently active
 * @returns {Promise<boolean>} True if a service worker is active
 */
export async function isServiceWorkerActive() {
  if (!('serviceWorker' in navigator)) {
    return false;
  }
  
  try {
    const registrations = await navigator.serviceWorker.getRegistrations();
    return registrations.length > 0;
  } catch (error) {
    console.error('Error checking service worker status:', error);
    return false;
  }
}

/**
 * Sends a message to the active service worker
 * @param {object} message The message to send
 * @returns {Promise<any>} The response from the service worker
 */
export async function sendMessageToServiceWorker(message) {
  if (!('serviceWorker' in navigator) || !navigator.serviceWorker.controller) {
    return null;
  }
  
  try {
    // Create a MessageChannel to receive response
    const messageChannel = new MessageChannel();
    
    // Set up promise to wait for response
    const messagePromise = new Promise((resolve) => {
      messageChannel.port1.onmessage = (event) => {
        resolve(event.data);
      };
    });
    
    // Send the message
    navigator.serviceWorker.controller.postMessage(message, [messageChannel.port2]);
    
    // Wait for response with a timeout
    const timeoutPromise = new Promise((resolve) => {
      setTimeout(() => resolve({ error: 'Service worker response timeout' }), 3000);
    });
    
    return Promise.race([messagePromise, timeoutPromise]);
  } catch (error) {
    console.error('Error sending message to service worker:', error);
    return null;
  }
}

// Initialize the service worker when this module is imported
if (typeof window !== 'undefined') {
  // Delay registration to not block the main thread during page load
  window.addEventListener('load', () => {
    setTimeout(() => {
      registerServiceWorker().catch(error => {
        console.error('Failed to register service worker on page load:', error);
      });
    }, 1000);
  });
}
