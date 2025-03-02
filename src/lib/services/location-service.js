import { writable } from 'svelte/store';
import { db } from '$lib/firebase';
import { doc, setDoc, collection, serverTimestamp } from 'firebase/firestore';

// Create a store to hold the current location
export const currentLocation = writable(null);

// Options for geolocation
const geoOptions = {
  enableHighAccuracy: true,
  timeout: 10000,
  maximumAge: 30000
};

// Get the user's current position
export async function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
          };
          
          // Update the store
          currentLocation.set(locationData);
          resolve(locationData);
        },
        (error) => {
          console.error("Error getting location:", error);
          reject(error);
        },
        geoOptions
      );
    } else {
      reject(new Error("Geolocation is not supported by this browser."));
    }
  });
}

// Track location in the background and save to Firestore
let watchId = null;

export function startLocationTracking(userId) {
  if (!userId) {
    console.error("User ID is required to track location");
    return;
  }
  
  if ("geolocation" in navigator) {
    // Stop any existing tracking
    stopLocationTracking();
    
    // Start tracking
    watchId = navigator.geolocation.watchPosition(
      async (position) => {
        const locationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date().toISOString(),
          serverTimestamp: serverTimestamp()
        };
        
        // Update the store
        currentLocation.set(locationData);
        
        try {
          // Save to Firestore
          const locationRef = doc(collection(db, `users/${userId}/locations`));
          await setDoc(locationRef, locationData);
          console.log("Location saved to Firestore");
        } catch (error) {
          console.error("Error saving location to Firestore:", error);
        }
      },
      (error) => {
        console.error("Error tracking location:", error);
      },
      geoOptions
    );
    
    return true;
  } else {
    console.error("Geolocation is not supported by this browser.");
    return false;
  }
}

export function stopLocationTracking() {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
    return true;
  }
  return false;
}

// Save a single location point to Firestore
export async function saveLocationToFirestore(userId, location) {
  if (!userId || !location) {
    console.error("User ID and location are required");
    return false;
  }
  
  try {
    const locationRef = doc(collection(db, `users/${userId}/locations`));
    await setDoc(locationRef, {
      ...location,
      serverTimestamp: serverTimestamp()
    });
    console.log("Single location saved to Firestore");
    return true;
  } catch (error) {
    console.error("Error saving location to Firestore:", error);
    return false;
  }
}
