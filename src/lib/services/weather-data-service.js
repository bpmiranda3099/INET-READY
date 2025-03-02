import { db } from '$lib/firebase';
import { collection, doc, getDoc, getDocs, query, orderBy, limit } from 'firebase/firestore';
import { writable } from 'svelte/store';

// Create stores for weather data
export const weatherData = writable({
    cities: [],
    lastUpdated: null,
    isLoading: false,
    error: null
});

// Store for cities list only
export const availableCities = writable([]);

/**
 * Fetch the most recent weather data from Firestore
 */
export async function fetchLatestWeatherData() {
    weatherData.update(state => ({ ...state, isLoading: true, error: null }));
    
    try {
        // Get the most recent date entry
        const datesRef = collection(db, 'hourly_weather_data');
        const datesQuery = query(datesRef, orderBy('timestamp', 'desc'), limit(1));
        const datesSnapshot = await getDocs(datesQuery);
        
        if (datesSnapshot.empty) {
            throw new Error('No weather data available');
        }
        
        const dateDoc = datesSnapshot.docs[0];
        const dateData = dateDoc.data();
        
        // Get all time collections for the most recent date
        const timeCollectionsRef = collection(db, 'hourly_weather_data', dateDoc.id, dateData.last_updated.replace(/:/g, '-'));
        const timeCollectionsSnapshot = await getDocs(timeCollectionsRef);
        
        // Extract city data and exclude _metadata document
        const citiesData = [];
        const cityNames = [];
        
        timeCollectionsSnapshot.forEach(doc => {
            if (doc.id !== '_metadata') {
                const cityData = doc.data();
                citiesData.push(cityData);
                cityNames.push(cityData.city);
            }
        });
        
        // Sort city names alphabetically
        cityNames.sort();
        
        // Update the stores
        weatherData.update(state => ({
            ...state,
            cities: citiesData,
            lastUpdated: dateData.timestamp?.toDate() || new Date(),
            isLoading: false
        }));
        
        availableCities.set(cityNames);
        
        return {
            cities: citiesData,
            cityNames: cityNames,
            lastUpdated: dateData.timestamp?.toDate() || new Date()
        };
    } catch (error) {
        console.error('Error fetching weather data:', error);
        weatherData.update(state => ({ 
            ...state, 
            isLoading: false, 
            error: error.message || 'Failed to fetch weather data' 
        }));
        
        // Return empty fallback data
        return {
            cities: [],
            cityNames: [],
            lastUpdated: null
        };
    }
}

/**
 * Start periodic updates of weather data
 * @param {number} intervalMinutes - How often to refresh data in minutes
 */
export function startWeatherDataUpdates(intervalMinutes = 30) {
    // Fetch immediately
    fetchLatestWeatherData();
    
    // Set up timer for periodic updates
    const intervalId = setInterval(fetchLatestWeatherData, intervalMinutes * 60 * 1000);
    
    // Return function to stop updates
    return () => clearInterval(intervalId);
}

/**
 * Get city data by city name
 * @param {string} cityName - Name of the city
 * @returns {Promise<object|null>} City data or null if not found
 */
export async function getCityData(cityName) {
    try {
        let state = {};
        weatherData.subscribe(value => { state = value; })();
        
        // If weather data is already loaded, search in memory
        if (state.cities.length > 0) {
            const cityData = state.cities.find(city => 
                city.city.toLowerCase() === cityName.toLowerCase()
            );
            
            if (cityData) {
                return cityData;
            }
        }
        
        // If not found or not loaded, fetch latest data
        if (state.cities.length === 0) {
            const data = await fetchLatestWeatherData();
            
            const cityData = data.cities.find(city => 
                city.city.toLowerCase() === cityName.toLowerCase()
            );
            
            return cityData || null;
        }
        
        return null;
    } catch (error) {
        console.error(`Error getting data for city ${cityName}:`, error);
        return null;
    }
}
