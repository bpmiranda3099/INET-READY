import { db } from '$lib/firebase';
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';
import { getCityData } from './weather-data-service';

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
        
        // We need to maintain the simple format for display but also store enhanced data
        // This approach separates the display values from the enhanced data
        const preferencesToSave = {
            homeCity: preferences.homeCity,
            preferredCities: preferences.preferredCities,
            // Store enhanced data in a separate field so it doesn't interfere with the original format
            enhancedData: await enhanceWithCityData(preferences)
        };
        
        if (userPrefsDoc.exists()) {
            // Update existing document
            await updateDoc(userPrefsRef, {
                cityPreferences: preferencesToSave,
                updatedAt: new Date()
            });
        } else {
            // Create new document
            await setDoc(userPrefsRef, {
                cityPreferences: preferencesToSave,
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
async function enhanceWithCityData(preferences) {
    try {
        // Fetch city data for home city
        const homeCityData = await getCityData(preferences.homeCity);
        
        const result = {
            homeCityData: homeCityData || null,
            preferredCitiesData: {}
        };

        // Fetch city data for each preferred city
        for (const city of preferences.preferredCities) {
            const cityData = await getCityData(city);
            if (cityData) {
                result.preferredCitiesData[city] = cityData;
            }
        }

        return result;
    } catch (error) {
        console.warn('Error enhancing city data:', error);
        // Return empty enhanced data if there was an error
        return { homeCityData: null, preferredCitiesData: {} };
    }
}

