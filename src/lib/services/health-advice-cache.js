import { db } from '$lib/firebase';
import { doc, getDoc, setDoc, collection, query, where, getDocs } from 'firebase/firestore';
import { generateTravelHealthAdvice } from './gemini-service';
import { getCityData } from './weather-data-service';

/**
 * Cache key for localStorage to store the last advice fetched time
 */
const LAST_ADVICE_FETCH_KEY = 'inet-ready-last-advice-fetch';

/**
 * Get health advice for travel between cities, using cached data if available and not expired
 * @param {Object} params The parameters for getting health advice
 * @param {string} params.userId User ID
 * @param {string} params.fromCity The origin city
 * @param {string} params.toCity The destination city
 * @param {Object} params.medicalData User's medical data
 * @returns {Promise<Object>} The health advice object
 */
export async function getHealthAdvice({ userId, fromCity, toCity, medicalData }) {
  try {
    // Check if we can use cached advice
    const cachedAdvice = await getCachedHealthAdvice({ userId, fromCity, toCity });
    
    // Use cached advice if it's not expired (less than 1 hour old)
    if (cachedAdvice && !isAdviceExpired(cachedAdvice.timestamp)) {
      console.log("Using cached health advice");
      return cachedAdvice;
    }
    
    // Get weather data for both cities
    const [fromCityWeather, toCityWeather] = await Promise.all([
      getCityData(fromCity),
      getCityData(toCity)
    ]);
    
    const weatherData = {
      fromCity: fromCityWeather,
      toCity: toCityWeather
    };
    
    // Generate new advice
    console.log("Generating new health advice");
    const adviceText = await generateTravelHealthAdvice({ 
      fromCity, 
      toCity, 
      medicalData, 
      weatherData 
    });
    
    // Cache the new advice
    const advice = {
      userId,
      fromCity,
      toCity,
      adviceText,
      timestamp: new Date(),
      weatherData
    };
    
    await cacheHealthAdvice(advice);
    
    // Update local cache timestamp
    localStorage.setItem(LAST_ADVICE_FETCH_KEY, new Date().toISOString());
    
    return advice;
  } catch (error) {
    console.error("Error getting health advice:", error);
    throw error;
  }
}

/**
 * Get cached health advice from Firestore
 * @param {Object} params Parameters
 * @param {string} params.userId User ID
 * @param {string} params.fromCity Origin city
 * @param {string} params.toCity Destination city
 * @returns {Promise<Object|null>} Cached advice or null if not found
 */
async function getCachedHealthAdvice({ userId, fromCity, toCity }) {
  try {
    // Create a unique ID for this advice combination
    const adviceId = `${userId}_${fromCity}_${toCity}`.replace(/\s+/g, '_');
    const adviceRef = doc(db, 'healthAdvice', adviceId);
    const adviceDoc = await getDoc(adviceRef);
    
    if (adviceDoc.exists()) {
      const data = adviceDoc.data();
      // Convert Firestore timestamp to JS Date
      return {
        ...data,
        timestamp: data.timestamp?.toDate() || new Date()
      };
    }
    
    return null;
  } catch (error) {
    console.error("Error getting cached health advice:", error);
    return null;
  }
}

/**
 * Cache health advice in Firestore
 * @param {Object} advice The advice object to cache
 */
async function cacheHealthAdvice(advice) {
  try {
    const { userId, fromCity, toCity } = advice;
    
    // Create a unique ID for this advice combination
    const adviceId = `${userId}_${fromCity}_${toCity}`.replace(/\s+/g, '_');
    const adviceRef = doc(db, 'healthAdvice', adviceId);
    
    await setDoc(adviceRef, {
      ...advice,
      lastUpdated: new Date()
    });
    
    return true;
  } catch (error) {
    console.error("Error caching health advice:", error);
    return false;
  }
}

/**
 * Check if advice is expired (older than 1 hour)
 * @param {Date} timestamp The timestamp to check
 * @returns {boolean} True if expired, false otherwise
 */
function isAdviceExpired(timestamp) {
  if (!timestamp) return true;
  
  const now = new Date();
  const oneHour = 60 * 60 * 1000; // 1 hour in milliseconds
  
  return (now.getTime() - new Date(timestamp).getTime()) > oneHour;
}

/**
 * Get all cached health advice for a user
 * @param {string} userId User ID
 * @returns {Promise<Array>} Array of advice objects
 */
export async function getUserHealthAdvice(userId) {
  try {
    // Query Firestore for all advice for this user
    const healthAdviceRef = collection(db, 'healthAdvice');
    const q = query(healthAdviceRef, where("userId", "==", userId));
    const querySnapshot = await getDocs(q);
    
    const advice = [];
    querySnapshot.forEach((doc) => {
      const data = doc.data();
      advice.push({
        ...data,
        timestamp: data.timestamp?.toDate() || new Date()
      });
    });
    
    return advice;
  } catch (error) {
    console.error("Error fetching user health advice:", error);
    return [];
  }
}

/**
 * Clear all cached health advice for testing
 * @param {string} userId User ID
 */
export async function clearHealthAdviceCache(userId) {
    try {
        const healthAdviceRef = collection(db, 'healthAdvice');
        const q = query(healthAdviceRef, where("userId", "==", userId));
        const querySnapshot = await getDocs(q);
        
        const deletePromises = [];
        querySnapshot.forEach((document) => {
            deletePromises.push(deleteDoc(document.ref));
        });
        
        await Promise.all(deletePromises);
        localStorage.removeItem(LAST_ADVICE_FETCH_KEY);
        
        return true;
    } catch (error) {
        console.error("Error clearing health advice cache:", error);
        return false;
    }
}

async function deleteDoc(ref) {
    try {
        await ref.delete();
    } catch (error) {
        console.error("Error deleting document:", error);
        throw error;
    }
}
function deleteDoc(ref) {
    throw new Error('Function not implemented.');
}

