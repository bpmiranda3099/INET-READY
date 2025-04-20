// Auto-generated: List of distances between all Cavite city pairs
import { cityCoords } from './city-coords.js';

// Haversine formula to calculate distance between two lat/lng points in kilometers
function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth radius in km
  const toRad = deg => deg * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Generate all unique city pairs and their distances
function computeCityDistances() {
  const cities = Object.keys(cityCoords);
  const distances = [];
  for (let i = 0; i < cities.length; i++) {
    for (let j = i + 1; j < cities.length; j++) {
      const cityA = cities[i];
      const cityB = cities[j];
      const { lat: latA, lng: lngA } = cityCoords[cityA];
      const { lat: latB, lng: lngB } = cityCoords[cityB];
      const distance = haversine(latA, lngA, latB, lngB);
      distances.push({
        cityA,
        cityB,
        distanceKm: Number(distance.toFixed(3))
      });
    }
  }
  return distances;
}

export const cityDistances = computeCityDistances();

export function getCityDistances() {
  return cityDistances;
}
