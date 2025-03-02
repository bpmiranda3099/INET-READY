<script>
    import { onMount } from 'svelte';
    import { logoutUser, onMessageListener, hasMedicalRecord, requestFCMToken, getMedicalData } from '$lib/firebase';
    import { getCurrentPosition, currentLocation } from '$lib/services/location-service';
    import { 
        getLocationNameFromCoordinates,
        locationName,
        geocodingLoading,
        geocodingError
    } from '$lib/services/geocoding-service';
    import { 
        registerServiceWorker, 
        serviceWorkerSupported, 
        serviceWorkerRegistered, 
        serviceWorkerError 
    } from '../lib/services/service-worker';
    import { getUserCityPreferences } from '$lib/services/user-preferences-service';
    
    // Components
    import MedicalProfile from './medicalprofile.svelte';
    import MedicalForm from './medicalform.svelte';
    import PermissionsPanel from './permissions-panel.svelte';
    import CityPreferences from './city-preferences.svelte';
    import CityPreferencesSetup from './city-preferences-setup.svelte';
    import TravelHealthCards from './travel-health-cards.svelte';
    
    export let user;
    
    // State variables
    let notifications = [];
    let loading = false;
    let showMedicalForm = false;
    let medicalRecordExists = false;
    let activeTab = 'notifications';
    
    // City preferences state
    let hasCityPreferences = false;
    let showCityPreferencesSetup = false;
    let checkingCityPreferences = true;
    let homeCity = '';
    let preferredCities = [];
    
    // Permission states
    let notificationPermission = null;
    let locationPermission = null;
    let showPermissionsPanel = false;
    let fcmToken = null;
    
    // Location state
    let locationData = null;
    let locationError = null;
    let fetchingLocation = false;
    let currentLocationName = null;
    let fetchingLocationName = false;
    let locationNameError = null;
    
    // Service Worker state
    let swSupported;
    let swRegistered;
    let swError;
    
    // Subscribe to service worker states
    const unsubscribeSW1 = serviceWorkerSupported.subscribe(value => swSupported = value);
    const unsubscribeSW2 = serviceWorkerRegistered.subscribe(value => swRegistered = value);
    const unsubscribeSW3 = serviceWorkerError.subscribe(value => swError = value);
    
    // Subscribe to location updates
    const unsubscribeLocation = currentLocation.subscribe(value => {
        if (value) {
            locationData = value;
            // Get the location name when coordinates change
            getLocationNameFromCoordinates(value.latitude, value.longitude);
        }
    });
    
    // Subscribe to location name updates
    const unsubscribeLocationName = locationName.subscribe(value => {
        currentLocationName = value;
    });
    
    // Subscribe to geocoding loading state
    const unsubscribeGeocodingLoading = geocodingLoading.subscribe(value => {
        fetchingLocationName = value;
    });
    
    // Subscribe to geocoding error state
    const unsubscribeGeocodingError = geocodingError.subscribe(value => {
        locationNameError = value;
    });
    
    let unsubscribeMessages;
    onMount(() => {
        (async () => {
            // Check existing permissions
            notificationPermission = Notification.permission;
            
            // Check for geolocation permission state
            if ("permissions" in navigator) {
                try {
                    const status = await navigator.permissions.query({ name: 'geolocation' });
                    locationPermission = status.state;
                    // Listen for changes to permission state
                    status.onchange = () => {
                        locationPermission = status.state;
                    };
                    
                    // If location permission is granted, get current position
                    if (locationPermission === 'granted') {
                        getLocation();
                    }
                } catch (error) {
                    console.error("Error checking geolocation permission:", error);
                }
            }
            
            // Register service worker if not already registered
            if (!swRegistered) {
                try {
                    await registerServiceWorker();
                    console.log("Service worker registration status:", swRegistered);
                } catch (error) {
                    console.error("Error registering service worker:", error);
                }
            }
            
            // Check if user has city preferences
            try {
                const cityPreferences = await getUserCityPreferences(user.uid);
                if (cityPreferences && cityPreferences.homeCity) {
                    hasCityPreferences = true;
                    homeCity = cityPreferences.homeCity;
                    
                    // Ensure preferredCities is an array of strings
                    if (Array.isArray(cityPreferences.preferredCities)) {
                        preferredCities = cityPreferences.preferredCities.map(city => 
                            typeof city === 'object' && city !== null && city.city 
                                ? city.city 
                                : typeof city === 'string' 
                                    ? city 
                                    : ''
                        ).filter(city => city !== ''); // Remove any empty items
                    }
                    
                    console.log("Loaded preferences:", { homeCity, preferredCities });
                } else {
                    hasCityPreferences = false;
                }
                
                // Show city preferences setup if user doesn't have them yet
                // But only after permissions panel is handled
                showCityPreferencesSetup = !hasCityPreferences;
            } catch (error) {
                console.error("Error checking city preferences:", error);
            } finally {
                checkingCityPreferences = false;
            }
            
            // Determine if we should show the permissions panel
            showPermissionsPanel = notificationPermission !== 'granted' || 
                                locationPermission !== 'granted';
            
            // If notifications already granted, get FCM token
            if (notificationPermission === 'granted') {
                fcmToken = await requestFCMToken();
                if (fcmToken) {
                    // Here you would typically save the token to the user's profile
                    console.log("FCM token available:", fcmToken);
                }
            }
            
            // Subscribe to foreground messages
            const unsubscribeMessages = onMessageListener();
            
            // Check if user has medical record
            if (user && user.uid) {
                hasMedicalRecord(user.uid).then(result => {
                    medicalRecordExists = result;
                });
            }
        })();
        let unsubscribeMessages = onMessageListener();
        return () => {
            if (unsubscribeMessages) unsubscribeMessages();
            unsubscribeLocation();
            unsubscribeSW1();
            unsubscribeSW2();
            unsubscribeSW3();
            unsubscribeLocationName();
            unsubscribeGeocodingLoading();
            unsubscribeGeocodingError();
        };
    });
    
    function handleCityPreferencesComplete() {
        showCityPreferencesSetup = false;
        hasCityPreferences = true;
    }
    
    async function getLocation() {
        fetchingLocation = true;
        locationError = null;
        
        try {
            locationData = await getCurrentPosition();
            
            // Get the location name after getting coordinates
            if (locationData) {
                await getLocationNameFromCoordinates(locationData.latitude, locationData.longitude);
            }
        } catch (error) {
            console.error("Error fetching location:", error);
            locationError = error.message || "Could not retrieve your location";
        } finally {
            fetchingLocation = false;
        }
    }
    
    async function handleLogout() {
        loading = true;
        try {
            await logoutUser();
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            loading = false;
        }
    }
    
    function handleMedicalFormCompleted() {
        showMedicalForm = false;
        medicalRecordExists = true;
    }
    
    async function requestNotificationPermission() {
        try {
            const permission = await Notification.requestPermission();
            notificationPermission = permission;
            
            if (permission === 'granted') {
                // Ensure service worker is registered before requesting FCM token
                if (!swRegistered) {
                    await registerServiceWorker();
                }
                
                fcmToken = await requestFCMToken();
                if (fcmToken) {
                    // Save FCM token to user profile
                    console.log("FCM token received:", fcmToken);
                    // Implementation to save token to user profile would go here
                }
            }
        } catch (error) {
            console.error("Error requesting notification permission:", error);
        }
        
        // Update permissions panel visibility
        showPermissionsPanel = notificationPermission !== 'granted' || 
                              locationPermission !== 'granted';
    }
    
    function requestLocationPermission() {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log("Latitude:", position.coords.latitude);
                    console.log("Longitude:", position.coords.longitude);
                    
                    // Update location data
                    locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    
                    // Update permission state
                    navigator.permissions.query({ name: 'geolocation' }).then(status => {
                        locationPermission = status.state;
                        
                        // Update permissions panel visibility
                        showPermissionsPanel = notificationPermission !== 'granted' || 
                                              locationPermission !== 'granted';
                    });
                    
                    // Here you would store the location information
                    // Implementation to save location to user profile would go here
                },
                (error) => {
                    console.error("Error getting location:", error);
                    locationError = error.message || "Could not retrieve your location";
                },
                { enableHighAccuracy: true }
            );
        } else {
            console.log("Geolocation is not supported by this browser.");
        }
    }
    
    function handlePermissionsComplete() {
        showPermissionsPanel = false;
    }
</script>

<div class="dashboard">
    <div class="header">
        <h1>Dashboard</h1>
        <button on:click={handleLogout} class="logout-btn" disabled={loading}>
            {loading ? 'Logging out...' : 'Logout'}
        </button>
    </div>
    
    <div class="welcome">
        <h2>Welcome, {user.email}!</h2>
        <p>You are now connected to INET-READY.</p>
        
        <!-- Display location coordinates and location name -->
        {#if locationData}
            <div class="location-info">
                <p>
                    <span class="location-icon">📍</span> 
                    {#if currentLocationName}
                        <span class="location-name">{currentLocationName}</span>
                    {:else if fetchingLocationName}
                        <span class="location-name loading">Determining location name...</span>
                    {:else if locationNameError}
                        <span class="location-name error">{locationNameError}</span>
                    {/if}
                    <span class="coordinates">
                        {locationData.latitude.toFixed(6)}°, {locationData.longitude.toFixed(6)}°
                    </span>
                    <button on:click={getLocation} class="refresh-btn" disabled={fetchingLocation}>
                        {#if fetchingLocation}
                            Updating...
                        {:else}
                            ↻
                        {/if}
                    </button>
                </p>
            </div>
        {:else if locationPermission === 'granted' && !locationData}
            <div class="location-info loading">
                <p>
                    <span class="location-icon">📍</span> 
                    {fetchingLocation ? 'Getting your location...' : 'Location data not available.'}
                    <button on:click={getLocation} class="refresh-btn" disabled={fetchingLocation}>
                        {fetchingLocation ? 'Loading...' : 'Get Location'}
                    </button>
                </p>
            </div>
        {:else if locationError}
            <div class="location-info error">
                <p>
                    <span class="location-icon">⚠️</span> 
                    {locationError}
                    <button on:click={requestLocationPermission} class="refresh-btn">
                        Try Again
                    </button>
                </p>
            </div>
        {/if}
    </div>
    
    <!-- Permissions Panel -->
    {#if showPermissionsPanel}
        <PermissionsPanel 
            {notificationPermission} 
            {locationPermission}
            onRequestNotification={requestNotificationPermission}
            onRequestLocation={requestLocationPermission}
            onComplete={handlePermissionsComplete}
        />
    {/if}
    
    <!-- City Preferences Setup -->
    {#if !showPermissionsPanel && showCityPreferencesSetup && !checkingCityPreferences}
        <CityPreferencesSetup 
            userId={user.uid}
            onComplete={handleCityPreferencesComplete}
        />
    {/if}
    
    <!-- Service Worker Status (for debugging, can be removed in production) -->
    {#if swError}
        <div class="sw-error">
            <p>⚠️ Service Worker Error: {swError}</p>
        </div>
    {/if}
    
    <!-- Travel Health Cards - Only show if user has city preferences -->
    {#if hasCityPreferences && preferredCities.length > 0}
        <div class="travel-health-advice-section">
            <h3>Travel Health Advice</h3>
            <TravelHealthCards 
                userId={user.uid}
                homeCity={homeCity}
                preferredCities={preferredCities}
                useCurrentLocation={true}
                currentLocation={currentLocationName}
            />
        </div>
    {/if}
    
    <!-- Tab navigation -->
    <div class="dashboard-tabs">
        <button 
            class="tab-btn" 
            class:active={activeTab === 'notifications'}
            on:click={() => activeTab = 'notifications'}
        >
            Notifications
        </button>
        <button 
            class="tab-btn" 
            class:active={activeTab === 'account'}
            on:click={() => activeTab = 'account'}
        >
            Account
        </button>
        <button 
            class="tab-btn" 
            class:active={activeTab === 'medical'}
            on:click={() => activeTab = 'medical'}
        >
            Medical Profile
        </button>
        <button 
            class="tab-btn" 
            class:active={activeTab === 'settings'}
            on:click={() => activeTab = 'settings'}
        >
            Settings
        </button>
    </div>
    
    <!-- Tab content -->
    {#if activeTab === 'notifications'}
        <div class="tab-content">
            <div class="card">
                <h3>Notifications</h3>
                {#if notifications.length === 0}
                    <p class="empty-state">No notifications yet</p>
                {:else}
                    <div class="notifications-list">
                        {#each notifications as notification}
                            <div class="notification">
                                <h4>{notification.title}</h4>
                                <p>{notification.body}</p>
                                <small>{new Date(notification.timestamp).toLocaleString()}</small>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    {:else if activeTab === 'account'}
        <div class="tab-content">
            <div class="card">
                <h3>Account Information</h3>
                <div class="account-info">
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>User ID:</strong> {user.uid}</p>
                    <p><strong>Email Verified:</strong> {user.emailVerified ? 'Yes' : 'No'}</p>
                    <p><strong>Account Created:</strong> {user.metadata?.creationTime ? new Date(user.metadata.creationTime).toLocaleString() : 'Unknown'}</p>
                </div>
                
                <!-- Permissions Status -->
                <div class="permissions-status">
                    <h4>App Permissions</h4>
                    <p>
                        <strong>Notifications:</strong> 
                        <span class={notificationPermission === 'granted' ? 'granted' : 'not-granted'}>
                            {notificationPermission === 'granted' ? 'Enabled' : 'Disabled'}
                        </span>
                        {#if notificationPermission !== 'granted'}
                            <button on:click={requestNotificationPermission}>Enable</button>
                        {/if}
                    </p>
                    <p>
                        <strong>Location:</strong> 
                        <span class={locationPermission === 'granted' ? 'granted' : 'not-granted'}>
                            {locationPermission === 'granted' ? 'Enabled' : 'Disabled'}
                        </span>
                        {#if locationPermission !== 'granted'}
                            <button on:click={requestLocationPermission}>Enable</button>
                        {/if}
                    </p>
                    <p>
                        <strong>Service Worker:</strong> 
                        <span class={swRegistered ? 'granted' : 'not-granted'}>
                            {swRegistered ? 'Active' : 'Inactive'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    {:else if activeTab === 'medical'}
        <div class="tab-content">
            {#if showMedicalForm}
                <MedicalForm 
                    userId={user.uid} 
                    isEditing={medicalRecordExists} 
                    on:completed={handleMedicalFormCompleted} 
                    on:cancel={() => showMedicalForm = false}
                />
            {:else}
                <MedicalProfile userId={user.uid} />
            {/if}
        </div>
    {:else if activeTab === 'settings'}
        <div class="tab-content">
            <div class="settings-container">
                <CityPreferences userId={user.uid} />
            </div>
        </div>
    {/if}
</div>

<style>
    /* Add styling for permission indicators */
    .permissions-status .granted {
        color: green;
        font-weight: bold;
    }
    
    .permissions-status .not-granted {
        color: #888;
    }
    
    .permissions-status button {
        margin-left: 1rem;
        font-size: 0.8rem;
        padding: 0.2rem 0.5rem;
    }
    
    /* Styling for location display */
    .location-info {
        background: #f8faff;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #4285f4;
        display: flex;
        align-items: center;
    }
    
    .location-info.error {
        background: #fff8f8;
        border-left-color: #f44242;
    }
    
    .location-info.loading {
        background: #f8f9fa;
        border-left-color: #888;
    }
    
    .location-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .location-name {
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .location-name.loading {
        color: #888;
        font-style: italic;
    }
    
    .location-name.error {
        color: #f44242;
        font-style: italic;
    }
    
    .coordinates {
        font-family: monospace;
        font-weight: bold;
        color: #333;
    }
    
    .refresh-btn {
        background: transparent;
        border: none;
        color: #4285f4;
        cursor: pointer;
        font-size: 1rem;
        margin-left: 0.5rem;
        padding: 0.2rem 0.5rem;
        border-radius: 50%;
        transition: all 0.2s;
    }
    
    .refresh-btn:hover {
        background: rgba(66, 133, 244, 0.1);
    }
    
    .refresh-btn:disabled {
        color: #888;
        cursor: not-allowed;
    }
    
    /* Service worker error message */
    .sw-error {
        background: #fff8f8;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #f44242;
    }

    /* Add styling for settings tab */
    .settings-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }

    /* Add styling for travel health advice section */
    .travel-health-advice-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .travel-health-advice-section h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #333;
    }
</style>
