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
        
        // Add weather data for cities
        const enhancedPreferences = await enhanceWithCityData(preferences);
        
        if (userPrefsDoc.exists()) {
            // Update existing document
            await updateDoc(userPrefsRef, {
                cityPreferences: enhancedPreferences,
                updatedAt: new Date()
            });
        } else {
            // Create new document
            await setDoc(userPrefsRef, {
                cityPreferences: enhancedPreferences,
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
        const enhancedPreferences = {
            homeCity: preferences.homeCity,
            homeCityData: homeCityData || null,
            preferredCities: []
        };

        // Fetch city data for each preferred city
        for (const city of preferences.preferredCities) {
            const cityData = await getCityData(city);
            enhancedPreferences.preferredCities.push({
                city: city,
                cityData: cityData || null
            });
        }

        return enhancedPreferences;
    } catch (error) {
        console.warn('Error enhancing city data:', error);
        // Return original preferences if there was an error
        return preferences;
    }
}
function enhanceWithCityData(preferences) {
    throw new Error('Function not implemented.');
}

