<script>
    import { onMount, onDestroy } from 'svelte';
    import { saveUserCityPreferences } from '$lib/services/user-preferences-service';
    import { availableCities, fetchLatestWeatherData } from '$lib/services/weather-data-service';

    export let userId;
    export let onComplete = () => {};

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

    async function savePreferences() {
        if (!homeCity) {
            error = "Please select your home city";
            return;
        }
        isSaving = true;
        error = null;
        try {
            await saveUserCityPreferences(userId, {
                homeCity: homeCity,
                preferredCities: selectedCities.map(city =>
                    typeof city === 'object' && city.city ? city.city : city
                )
            });
            onComplete();
        } catch (err) {
            console.error("Error saving city preferences:", err);
            error = "Failed to save your city preferences.";
        } finally {
            isSaving = false;
        }
    }

    function addCity(city) {
        if (city && !selectedCities.includes(city)) {
            selectedCities = [...selectedCities, city];
        }
    }

    function removeCity(index) {
        selectedCities = selectedCities.filter((_, i) => i !== index);
    }

    function skip() {
        onComplete();
    }
</script>

<div class="city-pref-page">
    <!-- App Bar -->
    <div class="app-bar">
        <div class="app-bar-content">
            <small class="app-title">INET-READY</small>
            <h2 class="section-title">City Preferences</h2>
        </div>
    </div>

    <main class="city-pref-main">
        <div class="setup-header">
            <p>Help us provide location-specific heat stress alerts by setting your home city and cities you frequently visit.</p>
        </div>

        {#if error}
            <div class="error-message">
                <p><i class="bi bi-exclamation-triangle"></i> {error}</p>
            </div>
        {/if}

        <div class="setup-content">
            {#if loadingCities}
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>Loading cities from weather monitoring system...</p>
                </div>
            {:else}
                <div class="preference-content">
                    <div class="preference-header">
                        <div class="preference-icon">
                            <i class="bi bi-house-heart"></i>
                        </div>
                        <div class="preference-title">
                            <h3>Home City</h3>
                            <p class="section-description">Select the city in Cavite where you primarily live</p>
                        </div>
                    </div>
                    <div class="select-wrapper">
                        <select 
                            bind:value={homeCity}
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
                </div>
                
                <hr class="preference-divider">
                
                <div class="preference-content">
                    <div class="preference-header">
                        <div class="preference-icon">
                            <i class="bi bi-pin-map"></i>
                        </div>
                        <div class="preference-title">
                            <h3>Preferred Travel Cities</h3>
                            <p class="section-description">Add cities in Cavite you frequently visit or are interested in</p>
                        </div>
                    </div>
                    <div class="select-wrapper">
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
                        <div class="select-icon">
                            <i class="bi bi-chevron-down"></i>
                        </div>
                    </div>
                    
                    <div class="selected-cities">
                        {#if selectedCities.length > 0}
                            <div class="cities-grid">
                                {#each selectedCities as city, index}
                                    <div class="city-card">
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
            {/if}
        </div>
    </main>

    <!-- Bottom Nav Bar for Save Preferences -->
    <div class="city-pref-bottom-nav">
        <button 
            class="save-btn"
            on:click={savePreferences}
            disabled={isSaving || loadingCities || !homeCity}
        >
            {#if isSaving}
                <span class="spinner-small"></span> Saving...
            {:else}
                <i class="bi bi-check-lg"></i> Save Preferences
            {/if}
        </button>
    </div>
</div>

<style>
    .city-pref-page {
        background: #f5f6fa;
        display: flex;
        flex-direction: column;
    }
    .app-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        background-color: #dd815e;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 16px;
        z-index: 1000;
    }
    .app-bar-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .app-title {
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 1px;
        opacity: 0.8;
        margin: 0;
    }
    .section-title {
        font-size: 1.5rem;
        margin: 0;
        font-weight: 600;
    }
    .city-pref-main {
        flex: 1;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .setup-header {
        padding: 6rem 1.5rem 2rem;
        text-align: center;
        background-color: #dd815e;
        color: white;
        width: 100%;
        position: fixed;
        top: 80px;
        left: 0;
        z-index: 1;
    }
    .setup-header h2 {
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .setup-header p {
        position: relative;
        z-index: 1;
        opacity: 0.95;
    }
    .setup-content {
        width: 100%;
        max-width: 550px;
        margin: 0 auto;
        background: white;
        border-radius: 8px;
        margin-top: -32px;
        z-index: 2;
        position: relative;
    }
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
        border-top-color: #dd815e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    .preference-content {
        padding: 1.25rem 1rem;
        position: relative;
    }
    .preference-divider {
        border: 0;
        height: 1px;
        background-color: #eee;
        background-image: linear-gradient(90deg, transparent, #dd815e, transparent);
        margin: 0.5rem 1rem;
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
        flex-shrink: 0;
    }
    .preference-title {
        flex: 1;
    }
    .preference-title h3 {
        margin: 0 0 0.25rem 0;
        color: #333;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .section-description {
        color: #666;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    .select-wrapper {
        position: relative;
        margin-bottom: 1rem;
    }
    .city-select {
        width: 100%;
        padding: 0.85rem 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: white;
        font-size: 1rem;
        appearance: none;
        color: #333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    .city-select:focus {
        border-color: #dd815e;
        box-shadow: 0 0 0 2px rgba(221, 129, 94, 0.2);
        outline: none;
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
        color: #666;
        pointer-events: none;
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
    }
    .city-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        color: #e41e3f;
        font-size: 1.1rem;
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
        font-size: 1.1rem;
        padding: 4px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .remove-btn:hover {
        background-color: rgba(244,67,54,0.1);
        color: #f44336;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        margin-top: 1rem;
        text-align: center;
    }
    .city-pref-bottom-nav {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        background: #fff;
        border-top: 1px solid #eee;
        padding: 1rem 0;
        display: flex;
        justify-content: center;
        z-index: 1001;
        box-shadow: 0 -2px 12px rgba(0,0,0,0.04);
    }
    .save-btn {
        background-color: #dd815e;
        color: #fff;
        border: none;
        padding: 0.85rem 2.2rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: background 0.2s, color 0.2s;
    }
    .save-btn:disabled {
        background: #f5f5f5;
        color: #bbb;
        cursor: not-allowed;
    }
    .save-btn:hover:not(:disabled) {
        background: #e67c4a;
        color: #fff;
    }
    .spinner-small {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(221,129,94,0.2);
        border-top-color: #dd815e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 6px;
        vertical-align: middle;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>