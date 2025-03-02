<script>
    import { onMount } from 'svelte';
    import { saveUserCityPreferences, getUserCityPreferences } from '$lib/services/user-preferences-service';
    
    export let userId;
    
    let homeCity = '';
    let cityInput = '';
    let selectedCities = [];
    let suggestedCities = [];
    let isSaving = false;
    let saved = false;
    let error = null;
    let cityData = [];
    let loadingCities = true;
    
    // Cavite cities list
    const caviteCities = [
        "Amadeo", "Imus", "General Trias", "Dasmariñas", "Bacoor", 
        "Carmona", "Kawit", "Noveleta", "Silang", "Naic",
        "Tanza", "Alfonso", "Indang", "Rosario", "Trece Martires",
        "General Mariano Alvarez", "Cavite City", "Tagaytay", 
        "Mendez", "Ternate", "Maragondon", "Magallanes"
    ];
    
    // Function to load cities with their coordinates from CSV
    async function loadCityData() {
        try {
            const response = await fetch('/data/city_coords.csv');
            const csvText = await response.text();
            
            // Simple CSV parsing
            const rows = csvText.split('\n').slice(1); // Skip header
            
            const parsedData = rows
                .filter(row => row.trim().length > 0)
                .map(row => {
                    const [city, lat, lng] = row.split(',');
                    return {
                        name: city.trim(),
                        latitude: parseFloat(lat),
                        longitude: parseFloat(lng)
                    };
                });
                
            cityData = parsedData;
            return parsedData;
        } catch (err) {
            console.error("Error loading city data:", err);
            // Fallback to just names if CSV loading fails
            return caviteCities.map(city => ({ name: city }));
        } finally {
            loadingCities = false;
        }
    }
    
    onMount(async () => {
        // Load cities data
        await loadCityData();
        
        // Load user preferences
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
    });
    
    function handleCityInput() {
        if (!cityInput.trim()) {
            suggestedCities = [];
            return;
        }
        
        const input = cityInput.toLowerCase();
        
        // Use city data if available, otherwise fallback to just city names
        if (cityData.length > 0) {
            suggestedCities = cityData
                .filter(city => 
                    city.name.toLowerCase().includes(input) && 
                    !selectedCities.includes(city.name) &&
                    city.name.toLowerCase() !== homeCity.toLowerCase())
                .map(city => city.name)
                .slice(0, 8); // Show more suggestions for better UX
        } else {
            suggestedCities = caviteCities
                .filter(city => 
                    city.toLowerCase().includes(input) && 
                    !selectedCities.includes(city) &&
                    city.toLowerCase() !== homeCity.toLowerCase())
                .slice(0, 8);
        }
    }
    
    function selectCity(city) {
        if (!selectedCities.includes(city)) {
            selectedCities = [...selectedCities, city];
            cityInput = '';
            suggestedCities = [];
        }
    }
    
    function removeCity(index) {
        selectedCities = selectedCities.filter((_, i) => i !== index);
    }
    
    function selectHomeCity(city) {
        homeCity = city;
        cityInput = '';
        suggestedCities = [];
    }
    
    async function savePreferences() {
        isSaving = true;
        error = null;
        saved = false;
        
        try {
            await saveUserCityPreferences(userId, {
                homeCity,
                preferredCities: selectedCities
            });
            saved = true;
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
        
        <div class="city-input-container">
            <input 
                type="text"
                placeholder={loadingCities ? "Loading cities..." : "Start typing your home city..."}
                bind:value={cityInput}
                on:input={handleCityInput}
                disabled={loadingCities}
                class="city-input"
            />
            
            {#if suggestedCities.length > 0}
                <div class="suggestions-dropdown">
                    {#each suggestedCities as city}
                        <div 
                            class="suggestion-item"
                            role="button"
                            tabindex="0"
                            on:click={() => selectHomeCity(city)}
                            on:keydown={(e) => e.key === 'Enter' && selectHomeCity(city)}
                        >
                            {city}
                        </div>
                    {/each}
                </div>
            {:else if cityInput && cityInput.length > 0 && !loadingCities}
                <div class="suggestions-dropdown">
                    <div class="suggestion-item no-results">No matching cities found</div>
                </div>
            {/if}
        </div>
        
        {#if homeCity}
            <div class="selected-city home-city">
                <span>{homeCity}</span>
                <button 
                    class="remove-btn"
                    on:click={() => { homeCity = ''; }}
                    aria-label="Remove home city"
                >
                    ×
                </button>
            </div>
        {/if}
    </div>
    
    <div class="preference-section">
        <h4>Preferred Cities</h4>
        <p class="section-description">Add cities in Cavite you frequently travel to or are interested in</p>
        
        <div class="city-input-container">
            <input 
                type="text"
                placeholder={loadingCities ? "Loading cities..." : "Search for a city to add..."}
                bind:value={cityInput}
                on:input={handleCityInput}
                disabled={loadingCities}
                class="city-input"
            />
            
            {#if suggestedCities.length > 0}
                <div class="suggestions-dropdown">
                    {#each suggestedCities as city}
                        <div 
                            class="suggestion-item"
                            role="button"
                            tabindex="0"
                            on:click={() => selectCity(city)}
                            on:keydown={(e) => e.key === 'Enter' && selectCity(city)}
                        >
                            {city}
                        </div>
                    {/each}
                </div>
            {:else if cityInput && cityInput.length > 0 && !loadingCities}
                <div class="suggestions-dropdown">
                    <div class="suggestion-item no-results">No matching cities found</div>
                </div>
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
            disabled={isSaving}
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
    
    .preference-section {
        margin-bottom: 1.5rem;
    }
    
    .section-description {
        color: #666;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .city-input-container {
        position: relative;
        margin-bottom: 1rem;
    }
    
    .city-input {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
    }
    
    .suggestions-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 0 0 4px 4px;
        z-index: 10;
        max-height: 200px;
        overflow-y: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .suggestion-item {
        padding: 0.5rem;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    
    .suggestion-item:hover {
        background-color: #f5f5f5;
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
    
    .save-btn:hover {
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
    
    .suggestion-item.no-results {
        font-style: italic;
        color: #888;
        cursor: default;
    }
    
    .suggestion-item.no-results:hover {
        background-color: white;
    }
    
    .city-input:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
    }
</style>
