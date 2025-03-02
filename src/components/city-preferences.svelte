<script>
    import { onMount } from 'svelte';
    import { saveUserCityPreferences, getUserCityPreferences } from '$lib/services/user-preferences-service';
    
    export let userId;
    
    let homeCity = '';
    let selectedCities = [];
    let isSaving = false;
    let saved = false;
    let error = null;
    let loadingCities = true;
    let caviteCities = [];
    
    // Function to load cities from CSV
    async function loadCityData() {
        try {
            const response = await fetch('/data/city_coords.csv');
            const csvText = await response.text();
            
            // Parse the CSV
            const rows = csvText.split('\n').slice(1); // Skip header
            const cities = rows
                .filter(row => row.trim().length > 0)
                .map(row => {
                    const [city] = row.split(',');
                    return city.trim();
                });
                
            caviteCities = cities;
            return cities;
        } catch (err) {
            console.error("Error loading city data:", err);
            // Fallback to hardcoded list
            caviteCities = [
                "Amadeo", "Imus", "General Trias", "Dasmariñas", "Bacoor", 
                "Carmona", "Kawit", "Noveleta", "Silang", "Naic",
                "Tanza", "Alfonso", "Indang", "Rosario", "Trece Martires",
                "General Mariano Alvarez", "Cavite City", "Tagaytay", 
                "Mendez", "Ternate", "Maragondon", "Magallanes"
            ];
            return caviteCities;
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
                disabled={loadingCities}
                class="city-select"
            >
                <option value="">Select your home city</option>
                {#each caviteCities as city}
                    <option value={city}>{city}</option>
                {/each}
            </select>
        </div>
    </div>
    
    <div class="preference-section">
        <h4>Preferred Cities</h4>
        <p class="section-description">Add cities in Cavite you frequently travel to or are interested in</p>
        
        <div class="select-container">
            <label for="preferredCitySelect" class="sr-only">Select cities you visit</label>
            <select 
                id="preferredCitySelect"
                on:change={e => {
                    const value = e.currentTarget.value;
                    if (value) {
                        addCity(value);
                        e.currentTarget.value = "";
                    }
                }}
                disabled={loadingCities || caviteCities.filter(city => 
                    city !== homeCity && !selectedCities.includes(city)
                ).length === 0}
                class="city-select"
            >
                <option value="">Add a city you visit</option>
                {#each caviteCities.filter(city => 
                    city !== homeCity && !selectedCities.includes(city)
                ) as city}
                    <option value={city}>{city}</option>
                {/each}
            </select>
            {#if caviteCities.filter(city => city !== homeCity && !selectedCities.includes(city)).length === 0}
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
            disabled={isSaving || !homeCity}
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

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
    
    .city-select-note {
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        font-style: italic;
    }
</style>
