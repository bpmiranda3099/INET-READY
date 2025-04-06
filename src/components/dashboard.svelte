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
    let activeTab = 'dashboard'; // Changed default to dashboard
    
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

    // Function to get the section title based on active tab
    function getSectionTitle(tab) {
        switch (tab) {
            case 'dashboard':
                return 'Dashboard';
            case 'notifications':
                return 'Notifications';
            case 'account':
                return 'Account';
            case 'medical':
                return 'Medical Profile';
            case 'settings':
                return 'Settings';
            default:
                return 'Dashboard';
        }
    }
</script>

<div class="dashboard">
    <!-- App Bar -->
    <div class="app-bar">
        <div class="app-bar-content">
            <small class="app-title">INET-READY</small>
            <h2 class="section-title">{getSectionTitle(activeTab)}</h2>
        </div>
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
    
    <!-- Main Content Area -->
    <div class="content-area">
        {#if activeTab === 'dashboard'}
            <div class="dashboard-section">
                <!-- Remove the heading since it's now in the app bar -->
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
            </div>
        {:else if activeTab === 'notifications'}
            <div class="notifications-section">
                <!-- Remove the heading since it's now in the app bar -->
                <div class="card">
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
            <div class="account-section">
                <!-- Remove the heading since it's now in the app bar -->
                <div class="card">
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
                    
                    <!-- Logout Button -->
                    <div class="logout-container">
                        <button on:click={handleLogout} class="logout-btn" disabled={loading}>
                            {loading ? 'Logging out...' : 'Logout'}
                        </button>
                    </div>
                </div>
            </div>
        {:else if activeTab === 'medical'}
            <div class="medical-section">
                <!-- Remove the heading since it's now in the app bar -->
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
            <div class="settings-section">
                <!-- Remove the heading since it's now in the app bar -->
                <div class="settings-container">
                    <CityPreferences userId={user.uid} />
                </div>
            </div>
        {/if}
    </div>
    
    <!-- Bottom Navigation Bar -->
    <div class="bottom-nav">
        <button 
            class="nav-item" 
            class:active={activeTab === 'dashboard'}
            on:click={() => activeTab = 'dashboard'}
        >
            <i class="bi bi-house"></i>
            <span>Dashboard</span>
        </button>
        <button 
            class="nav-item" 
            class:active={activeTab === 'notifications'}
            on:click={() => activeTab = 'notifications'}
        >
            <i class="bi bi-bell"></i>
            <span>Notifications</span>
        </button>
        <button 
            class="nav-item" 
            class:active={activeTab === 'account'}
            on:click={() => activeTab = 'account'}
        >
            <i class="bi bi-person"></i>
            <span>Account</span>
        </button>
        <button 
            class="nav-item" 
            class:active={activeTab === 'medical'}
            on:click={() => activeTab = 'medical'}
        >
            <i class="bi bi-heart-pulse"></i>
            <span>Medical</span>
        </button>
        <button 
            class="nav-item" 
            class:active={activeTab === 'settings'}
            on:click={() => activeTab = 'settings'}
        >
            <i class="bi bi-gear"></i>
            <span>Settings</span>
        </button>
    </div>
</div>

<style>
    .dashboard {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        padding-bottom: 70px; /* Space for bottom nav */
        padding-top: 80px; /* Space for app bar */
        position: relative;
    }
    
    /* App bar styles */
    .app-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        background-color: #dd815e; /* Orange main color */
        color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        display: flex;
        align-items: center;
        padding: 0 1rem;
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
    
    .content-area {
        flex: 1;
        padding: 1rem;
        padding-bottom: 2rem;
        overflow-y: auto;
    }
    
    /* Bottom navigation styles */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: white;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-around;
        z-index: 1000;
    }
    
    .nav-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 0;
        background: none;
        border: none;
        color: #666;
        font-size: 0.75rem;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .nav-item i {
        font-size: 1.25rem;
        margin-bottom: 0.25rem;
    }
    
    .nav-item.active {
        color: white;
        background-color: #dd815e; /* Orange main color */
    }
    
    .nav-item:not(.active):hover {
        color: #dd815e; /* Orange hover color */
    }
    
    /* Card styles */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Section styling */
    .dashboard-section, 
    .notifications-section, 
    .account-section, 
    .medical-section, 
    .settings-section {
        padding-bottom: 1rem;
    }
    
    /* Logout button styling */
    .logout-container {
        margin-top: 1.5rem;
        display: flex;
        justify-content: center;
    }

    .logout-btn {
        background-color: #dd815e; /* Orange main color */
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.2s;
        width: auto;
        min-height: 40px;
    }
    
    .logout-btn:hover {
        background-color: #c26744;
    }
    
    .logout-btn:disabled {
        background-color: #e5aa95;
        cursor: not-allowed;
    }
    
    /* Permission indicators */
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
        background: #dd815e;
        color: white;
        border: none;
        border-radius: 4px;
    }
    
    /* Notifications styling */
    .notifications-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        max-height: 70vh;
        overflow-y: auto;
    }
    
    .notification {
        padding: 0.75rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #dd815e;
    }
    
    .notification h4 {
        margin: 0 0 0.5rem 0;
    }
    
    .notification p {
        margin: 0 0 0.5rem 0;
    }
    
    .notification small {
        color: #888;
    }
    
    .empty-state {
        color: #888;
        text-align: center;
        padding: 2rem 0;
        font-style: italic;
    }
    
    /* Location display styling */
    .location-info {
        background: #f8faff;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #dd815e;
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
        color: #dd815e;
        cursor: pointer;
        font-size: 1rem;
        margin-left: 0.5rem;
        padding: 0.2rem 0.5rem;
        border-radius: 50%;
        transition: all 0.2s;
    }
    
    .refresh-btn:hover {
        background: rgba(221, 129, 94, 0.1);
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

    /* Settings container styling */
    .settings-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }

    /* Travel health advice section */
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
    
    @media (min-width: 768px) {
        .bottom-nav {
            height: 80px;
        }
        
        .nav-item {
            font-size: 0.85rem;
        }
        
        .nav-item i {
            font-size: 1.5rem;
        }
        
        .dashboard {
            padding-bottom: 80px;
        }
        
        .app-title {
            font-size: 0.8rem;
        }
        
        .section-title {
            font-size: 1.7rem;
        }
    }
</style>
