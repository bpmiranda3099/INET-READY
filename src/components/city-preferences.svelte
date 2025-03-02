<script>
    import { onMount, onDestroy } from 'svelte';
    import { saveUserCityPreferences, getUserCityPreferences } from '$lib/services/user-preferences-service';
    import { availableCities, fetchLatestWeatherData, startWeatherDataUpdates } from '$lib/services/weather-data-service';
    
    export let userId;
    
    let homeCity = '';
    let selectedCities = [];
    let isSaving = false;
    let saved = false;
    let error = null;
    let loadingCities = true;
    let cityList = [];
    let lastUpdated = null;
    
    // Subscribe to the availableCities store
    const unsubscribe = availableCities.subscribe(cities => {
        cityList = cities;
        if (cities.length > 0) {
            loadingCities = false;
        }
    });
    
    onMount(() => {
        // Start periodic updates of weather data (every 15 minutes)
        const stopUpdates = startWeatherDataUpdates(15);
    
        // Load user preferences
        loadUserPreferences();
    
        // Return function to clean up on component destroy
        return () => {
            stopUpdates();
            unsubscribe();
        };
    });
    
    async function loadUserPreferences() {
        try {
            const preferences = await getUserCityPreferences(userId);
            if (preferences) {
                homeCity = preferences.homeCity || '';
                selectedCities = preferences.preferredCities || [];
            }
        } catch (err) {
            console.error("Error loading city preferences:", err);
            error = "Failed to load your city preferences.";
        }
    }
    
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
    
    async function refreshCityList() {
        loadingCities = true;
        error = null;
        
        try {
            const result = await fetchLatestWeatherData();
            lastUpdated = result.lastUpdated;
        } catch (err) {
            console.error("Error refreshing city list:", err);
            error = "Failed to refresh city list.";
        } finally {
            loadingCities = false;
        }
    }
    
    async function savePreferences() {
        if (!homeCity) {
            error = "Please select your home city";
            return;
        }
        
        isSaving = true;
        error = null;
        saved = false;
        
        try {
            await saveUserCityPreferences(userId, {
                homeCity,
                preferredCities: selectedCities
            });
            saved = true;
            setTimeout(() => { saved = false; }, 3000);
        } catch (err) {
            console.error("Error saving city preferences:", err);
            error = "Failed to save your city preferences.";
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="city-preferences">
    <h3>City Preferences</h3>
    
    <div class="data-source-info">
        <span>Data source: Live weather monitoring system</span>
        {#if lastUpdated}
            <span>Last updated: {lastUpdated.toLocaleString()}</span>
        {/if}
        <button 
            class="refresh-button" 
            on:click={refreshCityList}
            disabled={loadingCities}
            aria-label="Refresh city list"
        >
            {loadingCities ? '↻ Refreshing...' : '↻ Refresh'}
        </button>
    </div>
    
    {#if error}
        <div class="error-message">
            <p>{error}</p>
        </div>
    {/if}
    
    {#if saved}
        <div class="success-message">
            <p>Your city preferences have been saved.</p>
        </div>
    {/if}
    
    <div class="preference-section">
        <h4>Home City</h4>
        <p class="section-description">Set your current city of residence in Cavite</p>
        
        <div class="select-container">
            <select 
                bind:value={homeCity}
                disabled={loadingCities || cityList.length === 0}
                class="city-select"
            >
                <option value="">Select your home city</option>
                {#each cityList as city}
                    <option value={city}>{city}</option>
                {/each}
            </select>
            
            {#if loadingCities}
                <div class="loading-indicator">Loading cities...</div>
            {:else if cityList.length === 0}
                <div class="no-cities-message">
                    No cities available. Please try refreshing.
                </div>
            {/if}
        </div>
    </div>
    
    <div class="preference-section">
        <h4>Preferred Cities</h4>
        <p class="section-description">Add cities in Cavite you frequently travel to or are interested in</p>
        
        <div class="select-container">
            <select 
                on:change={e => {
                    const value = e.currentTarget.value;
                    if (value) {
                        addCity(value);
                        e.currentTarget.value = "";
                    }
                }}
                disabled={loadingCities || cityList.filter(city => 
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
            
            {#if cityList.filter(city => city !== homeCity && !selectedCities.includes(city)).length === 0 && cityList.length > 0}
                <p class="city-select-note">All available cities have been added</p>
            {/if}
        </div>
        
        <div class="selected-cities">
            {#if selectedCities.length === 0}
                <p class="empty-message">No preferred cities added yet</p>
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
    
    <div class="actions">
        <button 
            class="save-btn"
            on:click={savePreferences}
            disabled={isSaving || !homeCity || loadingCities}
        >
            {isSaving ? 'Saving...' : 'Save Preferences'}
        </button>
    </div>
</div>

<style>
    .city-preferences {
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .data-source-info {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #666;
    }
    
    .refresh-button {
        background-color: transparent;
        border: 1px solid #ddd;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.85rem;
        color: #4285f4;
        display: inline-flex;
        align-items: center;
        margin-left: auto;
    }
    
    .refresh-button:hover:not(:disabled) {
        background-color: #f5f5f5;
    }
    
    .refresh-button:disabled {
        color: #999;
        cursor: not-allowed;
    }
    
    .loading-indicator {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .no-cities-message {
        padding: 0.5rem;
        color: #d32f2f;
        background-color: #ffebee;
        border-radius: 4px;
        margin-top: 0.5rem;
    }
    
    /* Rest of the existing styles */
    .preference-section {
        margin-bottom: 1.5rem;
    }
    
    .section-description {
        color: #666;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .select-container {
        margin-bottom: 1rem;
    }
    
    .city-select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
        font-size: 1rem;
    }
    
    .city-select:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
    }
    
    .selected-cities {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .selected-city {
        display: inline-flex;
        align-items: center;
        background-color: #e0f2fe;
        border-radius: 16px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem;
    }
    
    .home-city {
        background-color: #dcfce7;
        border: 1px solid #86efac;
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
        margin-top: 1rem;
        display: flex;
        justify-content: flex-end;
    }
    
    .save-btn {
        background-color: #4285f4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
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
    
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    .city-select-note {
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        font-style: italic;
    }
</style>
