<script>
    import { onMount, onDestroy } from 'svelte';
    import { saveUserCityPreferences } from '$lib/services/user-preferences-service';
    import { availableCities, fetchLatestWeatherData, startWeatherDataUpdates } from '$lib/services/weather-data-service';
    
    export let userId;
    export let onComplete = () => {}; // Callback when setup is completed
    
    let homeCity = '';
    let selectedCities = [];
    let isSaving = false;
    let error = null;
    let loadingCities = true;
    let cityList = [];
    
    // Subscribe to the availableCities store
    const unsubscribe = availableCities.subscribe(cities => {
        cityList = cities;
        if (cities.length > 0) {
            loadingCities = false;
        }
    });
    
    onMount(async () => {
        // Fetch weather data to get city list
        try {
            await fetchLatestWeatherData();
        } catch (err) {
            console.error("Error loading city data:", err);
            error = "Failed to load cities. You can still set preferences later.";
        }
    });
    
    onDestroy(() => {
        unsubscribe();
    });
    
    function addCity(city) {
        if (city && !selectedCities.includes(city)) {
            selectedCities = [...selectedCities, city];
        }
    }
    
    function removeCity(index) {
        selectedCities = selectedCities.filter((_, i) => i !== index);
    }
    
    async function savePreferences() {
        if (!homeCity) {
            error = "Please select your home city";
            return;
        }
        
        isSaving = true;
        error = null;
        
        try {
            await saveUserCityPreferences(userId, {
                homeCity,
                preferredCities: selectedCities
            });
            onComplete();
        } catch (err) {
            console.error("Error saving city preferences:", err);
            error = "Failed to save your city preferences.";
        } finally {
            isSaving = false;
        }
    }
    
    function skip() {
        onComplete();
    }
</script>

<div class="setup-container">
    <div class="setup-card">
        <div class="setup-header">
            <h2>Set Your City Preferences</h2>
            <p>Help us provide location-specific heat stress alerts by setting your home city and cities you frequently visit.</p>
        </div>
        
        {#if error}
            <div class="error-message">
                <p>{error}</p>
            </div>
        {/if}
        
        <div class="setup-content">
            {#if loadingCities}
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>Loading cities from weather monitoring system...</p>
                </div>
            {:else}
                <div class="setup-section">
                    <h3>Where do you live?</h3>
                    <select 
                        bind:value={homeCity}
                        class="city-select"
                    >
                        <option value="">Select your home city</option>
                        {#each cityList as city}
                            <option value={city}>{city}</option>
                        {/each}
                    </select>
                </div>
                
                <div class="setup-section">
                    <h3>Cities you visit regularly (optional)</h3>
                    <div class="city-select-container">
                        <select 
                            on:change={e => {
                                const value = e.currentTarget.value;
                                if (value) {
                                    addCity(value);
                                    e.currentTarget.value = "";
                                }
                            }}
                            disabled={cityList.filter(city => 
                                city !== homeCity && !selectedCities.includes(city)
                            ).length === 0}
                            class="city-select"
                        >
                            <option value="">Add a city you visit</option>
                            {#each cityList.filter(city => 
                                city !== homeCity && !selectedCities.includes(city)
                            ) as city}
                                <option value={city}>{city}</option>
                            {/each}
                        </select>
                    </div>
                    
                    <div class="selected-cities">
                        {#if selectedCities.length === 0}
                            <p class="empty-message">No preferred cities added</p>
                        {:else}
                            {#each selectedCities as city, index}
                                <div class="selected-city">
                                    <span>{city}</span>
                                    <button 
                                        class="remove-btn"
                                        on:click={() => removeCity(index)}
                                        aria-label="Remove preferred city"
                                    >
                                        ×
                                    </button>
                                </div>
                            {/each}
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
        
        <div class="actions">
            <button 
                class="skip-btn"
                on:click={skip}
            >
                Set Later
            </button>
            <button 
                class="save-btn"
                on:click={savePreferences}
                disabled={isSaving || loadingCities || !homeCity}
            >
                {isSaving ? 'Saving...' : 'Save Preferences'}
            </button>
        </div>
    </div>
</div>

<style>
    .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(0,0,0,0.1);
        border-top-color: #4285f4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    
    /* Keep existing styles */
    .setup-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .setup-card {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: 90%;
        max-width: 500px;
        padding: 1.5rem;
    }
    
    .setup-header {
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .setup-header h2 {
        margin-bottom: 0.5rem;
        color: #333;
    }
    
    .setup-header p {
        color: #666;
    }
    
    .setup-section {
        margin-bottom: 1.5rem;
    }
    
    .setup-section h3 {
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        color: #444;
    }
    
    .city-select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .city-select:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
    }
    
    .selected-cities {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .selected-city {
        display: inline-flex;
        align-items: center;
        background-color: #e0f2fe;
        border-radius: 16px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem;
    }
    
    .remove-btn {
        background: none;
        border: none;
        color: #888;
        cursor: pointer;
        font-size: 1.2rem;
        margin-left: 0.3rem;
        padding: 0 0.2rem;
    }
    
    .remove-btn:hover {
        color: #f44336;
    }
    
    .empty-message {
        color: #888;
        font-style: italic;
        font-size: 0.9rem;
    }
    
    .actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .save-btn {
        background-color: #4285f4;
        color: white;
        border: none;
        padding: 0.5rem 1.25rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .save-btn:hover:not(:disabled) {
        background-color: #3367d6;
    }
    
    .save-btn:disabled {
        background-color: #b0c0d9;
        cursor: not-allowed;
    }
    
    .skip-btn {
        background-color: transparent;
        color: #666;
        border: 1px solid #ddd;
        padding: 0.5rem 1.25rem;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .skip-btn:hover {
        background-color: #f5f5f5;
    }
    
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
</style>
