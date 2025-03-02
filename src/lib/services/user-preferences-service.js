import { db } from '$lib/firebase';
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';

/**
 * Save user city preferences to Firestore
 * @param {string} userId - The user ID
 * @param {object} preferences - User preferences object
 * @param {string} preferences.homeCity - User's home city
 * @param {Array<string>} preferences.preferredCities - User's preferred cities to travel
 */
export async function saveUserCityPreferences(userId, preferences) {
    try {
        const userPrefsRef = doc(db, 'userPreferences', userId);
        const userPrefsDoc = await getDoc(userPrefsRef);
        
        // Try to add coordinates for each city
        const prefsWithCoords = await addCityCoordinates(preferences);
        
        if (userPrefsDoc.exists()) {
            // Update existing document
            await updateDoc(userPrefsRef, {
                cityPreferences: prefsWithCoords,
                updatedAt: new Date()
            });
        } else {
            // Create new document
            await setDoc(userPrefsRef, {
                cityPreferences: prefsWithCoords,
                createdAt: new Date(),
                updatedAt: new Date()
            });
        }
        
        return true;
    } catch (error) {
        console.error('Error saving user city preferences:', error);
        throw error;
    }
}

/**
 * Get user city preferences from Firestore
 * @param {string} userId - The user ID
 * @returns {Promise<object|null>} User city preferences or null if not found
 */
export async function getUserCityPreferences(userId) {
    try {
        const userPrefsRef = doc(db, 'userPreferences', userId);
        const userPrefsDoc = await getDoc(userPrefsRef);
        
        if (userPrefsDoc.exists() && userPrefsDoc.data().cityPreferences) {
            return userPrefsDoc.data().cityPreferences;
        }
        
        return null;
    } catch (error) {
        console.error('Error getting user city preferences:', error);
        throw error;
    }
}

/**
 * Add coordinates to city preferences if available
 * @param {object} preferences - City preferences object
 * @returns {Promise<object>} - Preferences with coordinates added
 */
async function addCityCoordinates(preferences) {
    try {
        // Try to load city coordinates from CSV file
        const response = await fetch('/data/city_coords.csv');
        const csvText = await response.text();
        
        // Simple CSV parsing
        const rows = csvText.split('\n').slice(1); // Skip header
        const cityCoords = {};
        
        rows.forEach(row => {
            if (row.trim()) {
                const [city, lat, lng] = row.split(',');
                cityCoords[city.trim()] = {
                    latitude: parseFloat(lat),
                    longitude: parseFloat(lng)
                };
            }
        });
        
        // Add coordinates to home city
        const result = { 
            homeCity: preferences.homeCity,
            preferredCities: [...preferences.preferredCities]
        };
        
        if (preferences.homeCity && cityCoords[preferences.homeCity]) {
            result.homeCityCoordinates = cityCoords[preferences.homeCity];
        }
        
        // Add coordinates for preferred cities
        if (preferences.preferredCities && preferences.preferredCities.length) {
            result.preferredCityCoordinates = {};
            preferences.preferredCities.forEach(city => {
                if (cityCoords[city]) {
                    result.preferredCityCoordinates[city] = cityCoords[city];
                }
            });
        }
        
        return result;
    } catch (error) {
        console.warn('Error adding city coordinates:', error);
        // Return original preferences if there was an error
        return preferences;
    }
}
