<script>    import { onMount, onDestroy } from 'svelte';
    import { saveUserCityPreferences, getUserCityPreferences } from '$lib/services/user-preferences-service';
    import { availableCities, fetchLatestWeatherData, startWeatherDataUpdates } from '$lib/services/weather-data-service';
    import { showNotification } from '$lib/services/notification-service';
    import ToastContainer from './toast-container.svelte';
    
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
                // Ensure homeCity is a string
                homeCity = typeof preferences.homeCity === 'string' 
                    ? preferences.homeCity 
                    : '';
                
                // Ensure preferredCities is an array of strings
                if (Array.isArray(preferences.preferredCities)) {
                    // Convert any objects to strings if needed
                    selectedCities = preferences.preferredCities.map(city => 
                        typeof city === 'object' && city !== null && city.city 
                            ? city.city 
                            : typeof city === 'string' 
                                ? city 
                                : ''
                    ).filter(city => city !== ''); // Remove any empty items
                } else {
                    selectedCities = [];
                }
                
                console.log("Loaded preferences:", { homeCity, selectedCities });
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
       
    async function savePreferences() {
        if (!homeCity) {
            // Show toast notification instead of setting error
            showNotification(
                "Please select your home city",
                'warning',
                5000,
                'Missing Information'
            );
            return;
        }
        
        isSaving = true;
        error = null;
        saved = false;
        
        try {
            const preferences = await getUserCityPreferences(userId);
            const homeCityChanged = preferences?.homeCity !== homeCity;
            const citiesChanged = JSON.stringify(preferences?.preferredCities) !== JSON.stringify(selectedCities);
            
            // Only save if there are actual changes
            if (!homeCityChanged && !citiesChanged) {
                isSaving = false;
                return;
            }
            
            await saveUserCityPreferences(userId, {
                homeCity,
                preferredCities: selectedCities
            });

            let notificationMessage = 'City preferences saved successfully.';
            if (homeCityChanged && citiesChanged) {
                notificationMessage = 'Both home city and preferred cities updated successfully.';
            } else if (homeCityChanged) {
                notificationMessage = 'Home city updated successfully.';
            } else if (citiesChanged) {
                notificationMessage = 'Preferred cities updated successfully.';
            } 

            showNotification(
                notificationMessage,
                'success'
            );

            saved = true;
            setTimeout(() => saved = false, 3000);
        } catch (err) {
            showNotification(
                "Failed to save your city preferences. Please try again.",
                'error'
            );
            
            error = "Failed to save your city preferences. Please try again.";
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="city-preferences section-container">
      <!-- Toast notifications will be used instead of these static messages -->
    
    <!-- Home City Section -->
    <div class="preference-content">
        <div class="preference-header">
            <div class="preference-icon">
                <i class="bi bi-house-heart"></i>
            </div>
            <div class="preference-title">
                <h4>Home City</h4>
                <p class="section-description">Set your current city of residence in Cavite</p>
            </div>
        </div>
        
        <div class="select-container">
            <div class="select-wrapper">
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
                <div class="select-icon">
                    <i class="bi bi-chevron-down"></i>
                </div>
            </div>
            
            {#if loadingCities}
                <div class="loading-indicator">
                    <div class="loading-spinner-small"></div>
                    Loading cities...
                </div>
            {:else if cityList.length === 0}
                <div class="no-cities-message">
                    <i class="bi bi-exclamation-triangle"></i>
                    No cities available. Please try refreshing.
                </div>
            {/if}
        </div>
    </div>
    
    <!-- Horizontal rule divider -->
    <hr class="preference-divider">
    
    <!-- Preferred Cities Section -->
    <div class="preference-content">
        <div class="preference-header">
            <div class="preference-icon">
                <i class="bi bi-pin-map"></i>
            </div>
            <div class="preference-title">
                <h4>Preferred Cities</h4>
                <p class="section-description">Add cities you frequently travel to or are interested in</p>
            </div>
        </div>
        
        <div class="select-container">
            <div class="select-wrapper">
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
                <div class="select-icon">
                    <i class="bi bi-chevron-down"></i>
                </div>
            </div>
            
            {#if cityList.filter(city => city !== homeCity && !selectedCities.includes(city)).length === 0 && cityList.length > 0}
                <p class="city-select-note"><i class="bi bi-info-circle"></i> All available cities have been added</p>
            {/if}
        </div>
        
        <div class="selected-cities">
            {#if selectedCities.length === 0}
                <div class="empty-state">
                    <div class="empty-icon">🏙️</div>
                    <p class="empty-message">No preferred cities added yet</p>
                    <p class="empty-hint">Add cities you frequently visit to receive travel health insights</p>
                </div>
            {:else}
                <div class="cities-grid">
                    {#each selectedCities as city, index}                    <div class="city-card">
                            <div class="city-icon"><i class="bi bi-geo-alt-fill"></i></div>
                            <div class="city-info">
                                <span class="city-name">{city}</span>
                            </div>
                            <button 
                                class="remove-btn"
                                on:click={() => removeCity(index)}
                                aria-label="Remove preferred city"
                            >
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    {/each}
                </div>
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

<style>    .city-preferences {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .preferences-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
      .preference-content {
        padding: 1rem 0.75rem 0rem 0.75rem;
        position: relative;
    }
    
    .preference-divider {
        border: 0;
        height: 1px;
        background-color: #eee;
        background-image: linear-gradient(90deg, transparent, #dd815e, transparent);
        margin: 1rem 0;
    }
    
    .preference-header {
        display: flex;
        margin-bottom: 1.25rem;
        align-items: center;
    }
    
    .preference-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: rgba(221, 129, 94, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        color: #dd815e;
        font-size: 1.4rem;
    }
    
    .preference-title h4 {
        margin: 0 0 0.25rem 0;
        color: #333;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .section-description {
        color: #666;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .select-container {
        margin-bottom: 1.25rem;
    }
    
    .select-wrapper {
        position: relative;
    }
    
    .city-select {
        width: 100%;
        padding: 0.85rem 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: white;
        font-size: 1rem;
        appearance: none;
        color: #333;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .city-select:focus {
        outline: none;
        border-color: #dd815e;
        box-shadow: 0 0 0 3px rgba(221, 129, 94, 0.15);
    }
    
    .city-select:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
        color: #999;
    }
    
    .select-icon {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #888;
        pointer-events: none;
    }
    
    .loading-spinner-small {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(221, 129, 94, 0.3);
        border-top-color: #dd815e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-indicator {
        display: flex;
        align-items: center;
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .no-cities-message {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        color: #d32f2f;
        background-color: #ffebee;
        border-radius: 4px;
        margin-top: 0.5rem;
    }
    
    .selected-cities {
        margin-top: 1rem;
    }
    
    .cities-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0.75rem;
    }
    
    .city-card {
        display: flex;
        align-items: center;
        background-color: #f0f7ff;
        border-left: 3px solid #dd815e;
        border-radius: 8px;
        padding: 0.8rem;
        position: relative;
        transition: all 0.2s;
    }
    
    .city-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }    .city-icon {
        color: #e41e3f;
        font-size: 1.2rem;
        margin-right: 0.75rem;
    }
    
    .city-info {
        flex: 1;
    }
    
    .city-name {
        font-weight: 500;
        color: #333;
    }
    
    .remove-btn {
        background: none;
        border: none;
        color: #999;
        cursor: pointer;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    .remove-btn:hover {
        background-color: rgba(244, 67, 54, 0.1);
        color: #f44336;
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem;
        text-align: center;
        background-color: #f9f9f9;
        border-radius: 8px;
        border: 1px dashed #ddd;
    }
    
    .empty-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        color: #999;
    }
    
    .empty-message {
        color: #555;
        font-weight: 500;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .empty-hint {
        color: #888;
        font-size: 0.85rem;
        line-height: 1.4;
        max-width: 250px;
    }
    
    .actions {
        margin-top: 1rem;
        display: flex;
        justify-content: flex-end;
    }
      .save-btn {
        background-color: #dd815e;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: all 0.2s;
        margin-bottom: 1rem;
        margin-right: 1rem;
    }
    
    .save-btn:hover:not(:disabled) {
        background-color: #c26744;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .save-btn:disabled {
        background-color: #e5aa95;
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
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        font-style: italic;
    }
</style>
