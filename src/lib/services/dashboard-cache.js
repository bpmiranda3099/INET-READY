// Utility for secure dashboard caching (non-sensitive data only)
const DASHBOARD_CACHE_KEY = 'inet-ready-dashboard-cache-v1';

export function saveDashboardCache(data) {
    // Only cache non-sensitive fields!
    const safeData = {
        homeCity: data.homeCity,
        preferredCities: data.preferredCities,
        lastUpdated: data.lastUpdated,
        // Add more non-sensitive fields as needed
    };
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(safeData));
}

export function loadDashboardCache() {
    try {
        const raw = localStorage.getItem(DASHBOARD_CACHE_KEY);
        if (!raw) return null;
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

export function clearDashboardCache() {
    localStorage.removeItem(DASHBOARD_CACHE_KEY);
}
