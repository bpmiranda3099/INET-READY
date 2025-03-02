import { writable } from 'svelte/store';

// Create stores for geocoded location and loading state
export const locationName = writable(null);
export const geocodingLoading = writable(false);
export const geocodingError = writable(null);

// Cache for geocoding results to avoid excessive API calls
const geocodingCache = new Map();
const CACHE_EXPIRY = 60 * 60 * 1000; // 1 hour in milliseconds

/**
 * Get city and province/state from coordinates using reverse geocoding
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<string>} - Location string in format "City, Province"
 */
export async function getLocationNameFromCoordinates(latitude, longitude) {
  try {
    // Reset error state
    geocodingError.set(null);
    
    // Set loading state
    geocodingLoading.set(true);
    
    // Round coordinates to 4 decimal places for caching
    // This is precise to ~11 meters, which is enough to identify a city
    const roundedLat = parseFloat(latitude.toFixed(4));
    const roundedLng = parseFloat(longitude.toFixed(4));
    const cacheKey = `${roundedLat},${roundedLng}`;
    
    // Check cache first
    const cachedResult = checkCache(cacheKey);
    if (cachedResult) {
      locationName.set(cachedResult);
      geocodingLoading.set(false);
      return cachedResult;
    }
    
    // Use OpenStreetMap Nominatim API for reverse geocoding (free, no API key needed)
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`;
    
    const response = await fetch(url, {
      headers: {
        'Accept-Language': 'en', // Request English results
        'User-Agent': 'INET-READY Health App' // Required by Nominatim policy
      }
    });
    
    if (!response.ok) {
      throw new Error(`Geocoding failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Extract city and province/state/region
    const address = data.address;
    const city = address.city || address.town || address.village || address.hamlet || address.suburb || 'Unknown';
    const province = address.state || address.province || address.region || address.county || '';
    
    // Format the location string
    let locationStr;
    if (province) {
      locationStr = `${city}, ${province}`;
    } else {
      locationStr = city;
    }
    
    // Add country if we couldn't find detailed info
    if (locationStr === 'Unknown' && address.country) {
      locationStr = address.country;
    }
    
    // Cache the result
    cacheResult(cacheKey, locationStr);
    
    // Update the store
    locationName.set(locationStr);
    
    return locationStr;
  } catch (error) {
    console.error('Error geocoding location:', error);
    geocodingError.set('Could not determine your location name');
    locationName.set(null);
    return null;
  } finally {
    geocodingLoading.set(false);
  }
}

/**
 * Alternative implementation using Google Maps API
 * Requires an API key from Google Cloud Console
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<string>} - Location string in format "City, Province"
 */
export async function getLocationNameUsingGoogleMaps(latitude, longitude) {
  try {
    geocodingError.set(null);
    geocodingLoading.set(true);
    
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    
    if (!apiKey) {
      throw new Error('Google Maps API key is required');
    }
    
    const url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${apiKey}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Geocoding failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.status !== 'OK') {
      throw new Error(`Geocoding API error: ${data.status}`);
    }
    
    // Find the locality (city) and administrative_area_level_1 (state/province)
    let city = null;
    let province = null;
    
    for (const result of data.results) {
      for (const component of result.address_components) {
        if (component.types.includes('locality')) {
          city = component.long_name;
        } else if (component.types.includes('administrative_area_level_1')) {
          province = component.long_name;
        }
      }
      
      // If we've found both, break out of the loop
      if (city && province) break;
    }
    
    // Format the location string
    let locationStr = 'Unknown location';
    if (city && province) {
      locationStr = `${city}, ${province}`;
    } else if (city) {
      locationStr = city;
    } else if (province) {
      locationStr = province;
    }
    
    locationName.set(locationStr);
    return locationStr;
  } catch (error) {
    console.error('Error geocoding location with Google Maps:', error);
    geocodingError.set('Could not determine your location name');
    locationName.set(null);
    return null;
  } finally {
    geocodingLoading.set(false);
  }
}

/**
 * Check cache for existing geocoding result
 * @param {string} key - Cache key
 * @returns {string|null} - Cached location string or null if not found/expired
 */
function checkCache(key) {
  if (geocodingCache.has(key)) {
    const cached = geocodingCache.get(key);
    
    if (Date.now() < cached.expiry) {
      return cached.value;
    } else {
      // Expired, remove from cache
      geocodingCache.delete(key);
    }
  }
  return null;
}

/**
 * Cache a geocoding result with expiry
 * @param {string} key - Cache key
 * @param {string} value - Location string
 */
function cacheResult(key, value) {
  geocodingCache.set(key, {
    value,
    expiry: Date.now() + CACHE_EXPIRY
  });
}

/**
 * Clear the geocoding cache
 */
export function clearGeocodingCache() {
  geocodingCache.clear();
}
