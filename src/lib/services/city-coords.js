// Utility to map city names to coordinates from city_coords.csv
// Usage: getCityCoords('Tagaytay') => { lat: 14.1032297, lng: 120.9317903 }

export const cityCoords = {
  "Amadeo": { lat: 14.1698511, lng: 120.9217943 },
  "Imus": { lat: 14.4290116, lng: 120.9365911 },
  "General Trias": { lat: 14.3860130, lng: 120.8802597 },
  "Dasmariñas": { lat: 14.3270819, lng: 120.9370871 },
  "Bacoor": { lat: 14.4588160, lng: 120.9595790 },
  "Carmona": { lat: 14.3134763, lng: 121.0573969 },
  "Kawit": { lat: 14.4442564, lng: 120.9035435 },
  "Noveleta": { lat: 14.4278394, lng: 120.8808454 },
  "Silang": { lat: 14.2236240, lng: 120.9741497 },
  "Naic": { lat: 14.3191837, lng: 120.7642540 },
  "Tanza": { lat: 14.4006750, lng: 120.8572845 },
  "Alfonso": { lat: 14.1380464, lng: 120.8554205 },
  "Indang": { lat: 14.1958306, lng: 120.8784148 },
  "Rosario": { lat: 14.4166891, lng: 120.8552629 },
  "Trece Martires": { lat: 14.2811668, lng: 120.8702367 },
  "General Mariano Alvarez": { lat: 14.2954628, lng: 121.0070814 },
  "Cavite City": { lat: 14.4820919, lng: 120.9089190 },
  "Tagaytay": { lat: 14.1032297, lng: 120.9317903 },
  "Mendez": { lat: 14.1300751, lng: 120.9051427 },
  "Ternate": { lat: 14.2863405, lng: 120.7161314 },
  "Maragondon": { lat: 14.2741589, lng: 120.7350728 },
  "Magallanes": { lat: 14.1874692, lng: 120.7573248 }
};

export function getCityCoords(cityName) {
  return cityCoords[cityName] || null;
}
