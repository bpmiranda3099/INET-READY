import { writable } from 'svelte/store';

// Check if propellerAds are disabled in localStorage
const getInitialPropellerAdsState = () => {
    if (typeof localStorage === 'undefined') return true;
    const savedValue = localStorage.getItem('inet-ready-show-propeller-ads');
    return savedValue === null ? true : savedValue === 'true';
};

// Create a writable store with the initial value from localStorage
export const showPropellerAds = writable(getInitialPropellerAdsState());

// Subscribe to changes and save to localStorage
showPropellerAds.subscribe(value => {
    if (typeof localStorage !== 'undefined') {
        localStorage.setItem('inet-ready-show-propeller-ads', value.toString());
    }
});

// Function to toggle propeller ads visibility
export function togglePropellerAds() {
    showPropellerAds.update(value => !value);
}
