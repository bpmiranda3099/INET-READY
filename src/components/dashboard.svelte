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
    let showWelcomeMessage = true; // Control whether to show welcome message on startup
    
    // City preferences state
    let hasCityPreferences = false;
    let showCityPreferencesSetup = false;
    let checkingCityPreferences = true;
    let homeCity = '';
    let preferredCities = [];
    let loadingCities = false;
    let lastUpdated = null;
    
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
    
    let unsubscribeMessages;    onMount(() => {
        // Check if welcome message is disabled in local storage
        const hideWelcome = localStorage.getItem('inet-ready-hide-welcome');
        if (hideWelcome === 'true') {
            showWelcomeMessage = false;
        }
        
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

    // Function to toggle welcome message visibility preference
    function toggleWelcomeMessage() {
        showWelcomeMessage = !showWelcomeMessage;
        localStorage.setItem('inet-ready-hide-welcome', showWelcomeMessage ? 'false' : 'true');
    }

    // Function to refresh the city list data
    async function refreshCityList() {
        loadingCities = true;
        
        try {
            // Import the function directly where we need it
            const { fetchLatestWeatherData } = await import('$lib/services/weather-data-service');
            const result = await fetchLatestWeatherData();
            lastUpdated = result.lastUpdated;
        } catch (err) {
            console.error("Error refreshing city list:", err);
        } finally {
            loadingCities = false;
        }
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
                  <!-- Travel Health Cards - Only show if user has city preferences -->
                {#if hasCityPreferences && preferredCities.length > 0}
                    <TravelHealthCards 
                        userId={user.uid}
                        homeCity={homeCity}
                        preferredCities={preferredCities}
                        useCurrentLocation={true}
                        currentLocation={currentLocationName}
                    />
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
            </div>        {:else if activeTab === 'account'}
            <div class="account-section">
                <!-- Account Information -->
                <div class="section-container">
                    <div class="section-header">
                        <h3>Account Information</h3>
                    </div>
                    <div class="section-body">
                        <div class="preference-content">
                            <!-- Email Info -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-envelope"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Email Address</span>
                                    <span class="setting-description">{user.email}</span>
                                </div>
                            </div>
                            
                            <!-- User ID Info -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-person-badge"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">User ID</span>
                                    <span class="setting-description">{user.uid}</span>
                                </div>
                            </div>
                            
                            <!-- Email Verification Status -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-patch-check"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Email Verification</span>
                                    <span class="setting-description">
                                        {#if user.emailVerified}
                                            <span class="status-badge verified">Verified</span>
                                        {:else}
                                            <span class="status-badge unverified">Not Verified</span>
                                        {/if}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Account Created Date -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-calendar-date"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Account Created</span>
                                    <span class="setting-description">{user.metadata?.creationTime ? new Date(user.metadata.creationTime).toLocaleString() : 'Unknown'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Location Information -->
                <div class="section-container">
                    <div class="section-header">
                        <h3>Location Information</h3>
                    </div>
                    <div class="section-body">
                        <div class="preference-content">
                            {#if locationData}
                                <!-- Current Location -->
                                <div class="preference-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-geo-alt"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Current Location</span>
                                        <span class="setting-description">
                                            {#if currentLocationName}
                                                {currentLocationName}
                                            {:else if fetchingLocationName}
                                                <span class="loading-text">Determining location name...</span>
                                            {:else if locationNameError}
                                                <span class="error-text">{locationNameError}</span>
                                            {:else}
                                                Unknown location
                                            {/if}
                                        </span>
                                    </div>
                                    <div class="setting-action">
                                        <button on:click={getLocation} class="icon-button" disabled={fetchingLocation} aria-label="Refresh location">
                                            {#if fetchingLocation}
                                                <div class="button-spinner"></div>
                                            {:else}
                                                <i class="bi bi-arrow-clockwise"></i>
                                            {/if}
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- Coordinates -->
                                <div class="preference-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-pin-map-fill"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Coordinates</span>
                                        <span class="setting-description coordinates-text">
                                            {locationData.latitude.toFixed(6)}°, {locationData.longitude.toFixed(6)}°
                                        </span>
                                    </div>
                                </div>
                                
                                <!-- Last Updated -->
                                <div class="preference-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-clock-history"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Last Updated</span>
                                        <span class="setting-description">
                                            {new Date(locationData.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                            {:else if locationPermission === 'granted' && !locationData}
                                <div class="preference-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-geo-alt"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Location Data</span>
                                        <span class="setting-description">
                                            {fetchingLocation ? 'Getting your location...' : 'Location data not available.'}
                                        </span>
                                    </div>                                    <div class="setting-action">
                                        <button on:click={getLocation} class="enable-btn" disabled={fetchingLocation}>
                                            {fetchingLocation ? 'Loading...' : 'Get Location'}
                                        </button>
                                    </div>
                                </div>
                            {:else if locationError}
                                <div class="preference-header">
                                    <div class="preference-icon error-icon">
                                        <i class="bi bi-exclamation-triangle"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Error</span>
                                        <span class="setting-description error-text">
                                            {locationError}
                                        </span>
                                    </div>                                    <div class="setting-action">
                                        <button on:click={getLocation} class="enable-btn">
                                            Try Again
                                        </button>
                                    </div>
                                </div>
                            {:else}                                <div class="preference-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-shield-lock"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Location Services</span>
                                        <span class="setting-description">
                                            Location services not enabled
                                        </span>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
                
                <!-- App Permissions -->
                <div class="section-container">
                    <div class="section-header">
                        <h3>App Permissions</h3>
                    </div>
                    <div class="section-body">
                        <div class="preference-content">
                            <!-- Notifications Permission -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-bell"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Notifications</span>
                                    <span class="setting-description">
                                        Allow the app to send you important health alerts
                                    </span>
                                </div>
                                <div class="setting-action">
                                    {#if notificationPermission === 'granted'}
                                        <span class="status-badge verified">Enabled</span>
                                    {:else}                                        <button on:click={requestNotificationPermission} class="enable-btn">
                                            Enable
                                        </button>
                                    {/if}
                                </div>
                            </div>
                            
                            <!-- Location Permission -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-geo-alt"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Location Services</span>
                                    <span class="setting-description">
                                        Access your location to provide localized health advice
                                    </span>
                                </div>
                                <div class="setting-action">
                                    {#if locationPermission === 'granted'}
                                        <span class="status-badge verified">Enabled</span>
                                    {:else}                                        <button on:click={requestLocationPermission} class="enable-btn">
                                            Enable
                                        </button>
                                    {/if}
                                </div>
                            </div>
                            
                            <!-- Service Worker Status -->
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-hdd-network"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Background Services</span>
                                    <span class="setting-description">
                                        Enable background processing to receive push notifications
                                    </span>
                                </div>
                                <div class="setting-action">
                                    {#if swRegistered}
                                        <span class="status-badge verified">Active</span>
                                    {:else}
                                        <span class="status-badge unverified">Inactive</span>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Logout Button -->
                <div class="section-container">
                    <div class="section-body logout-section">
                        <button on:click={handleLogout} class="logout-btn" disabled={loading}>
                            {loading ? 'Logging out...' : 'Logout'}
                        </button>
                    </div>
                </div>
            </div>        {:else if activeTab === 'medical'}
            <div class="medical-section">
                <!-- Main section keeps app bar header, no additional container header -->
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
            </div>{:else if activeTab === 'settings'}
            <div class="settings-section">
                <!-- Display Preferences Container -->
                <div class="section-container">
                    <div class="section-header">
                        <h3>Display Preferences</h3>
                    </div>                    <div class="section-body">                <div class="preference-content">
                            <div class="preference-header">
                                <div class="preference-icon">
                                    <i class="bi bi-chat-square-text"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Show Welcome Message</span>
                                    <span class="setting-description">Display the welcome message each time you open the application</span>
                                </div>
                                <div class="setting-action">
                                    <label class="switch">
                                        <input 
                                            type="checkbox" 
                                            checked={showWelcomeMessage} 
                                            on:change={toggleWelcomeMessage}
                                        >
                                        <span class="slider round"></span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                  <!-- City Preferences Container -->
                <div class="section-container">
                    <div class="section-header">
                        <h3>City Preferences</h3>                        
                        <div class="data-source-info">
                            <span>Powered by: <a href="https://open-meteo.com/" class="open-meteo-link"><img src="/open-meteo-icon.png" alt="Open-Meteo" class="open-meteo-icon"></a></span>
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
                    </div>                    <div class="section-body city-preferences-wrapper">
                        <CityPreferences userId={user.uid} />
                    </div>
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
    .notifications-section, 
    .account-section, 
    .medical-section, 
    .settings-section {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Account section containers with health card-style headers */
    .section-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        background: #dd815e;
        color: white;
        padding: 1rem;
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    
    .section-header h3 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
    }
    
    .data-source-info {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
        color: white;
        z-index: 1;
        text-align: right;
    }
    
    .refresh-button {
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.85rem;
        color: white;
        display: inline-flex;
        align-items: center;
    }
    
    .refresh-button:hover:not(:disabled) {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .refresh-button:disabled {
        color: rgba(255, 255, 255, 0.5);
        cursor: not-allowed;
    }
    
    .open-meteo-icon {
        height: 20px;
        width: auto;
        opacity: 0.9;
        filter: brightness(0) invert(1);
        vertical-align: middle;
        margin-left: 4px;
        transition: opacity 0.2s ease;
    }
    
    .open-meteo-link:hover .open-meteo-icon {
        opacity: 1;
    }
    
    .section-body {
        padding: 1.5rem;
    }
    
    .logout-section {
        display: flex;
        justify-content: center;
        padding: 1rem;
    }
    
    .city-preferences-wrapper {
        padding: 0; /* Remove padding since the city preferences component already has its own padding */
    }
    
    .logout-section {
        display: flex;
        justify-content: center;
        padding: 1rem;
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
    }    /* Settings styles */
    .settings-group {
        padding: 1rem;
        border-bottom: 1px solid #eee;
    }
    
    .settings-group h4 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #333;
    }
    
    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
    }
      /* New horizontal preference content styling */
    .preference-content {
        margin-bottom: 1rem;
    }
    
    .preference-header {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        position: relative;
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
    
    .setting-info {
        flex: 1;
    }
    
    .setting-label {
        display: block;
        font-weight: 600;
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 0.25rem;
    }
    
    .setting-description {
        display: block;
        font-size: 0.9rem;
        color: #666;
        line-height: 1.4;
    }
    
    .setting-action {
        margin-left: 1rem;
    }
    
    /* Toggle Switch */
    .switch {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 24px;
        margin-left: 1rem;
    }
    
    .switch input { 
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
    }
    
    .slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
    }
    
    input:checked + .slider {
        background-color: #dd815e;
    }
    
    input:focus + .slider {
        box-shadow: 0 0 1px #dd815e;
    }
    
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    
    .slider.round {
        border-radius: 24px;
    }
    
    .slider.round:before {
        border-radius: 50%;
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

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-badge.verified {
        background-color: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
    }
    
    .status-badge.unverified {
        background-color: rgba(244, 67, 54, 0.15);
        color: #c62828;
    }

    .enable-btn {
        background-color: #dd815e;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .enable-btn:hover {
        background-color: #c26744;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .enable-btn:active {
        transform: translateY(0);
    }
</style>
