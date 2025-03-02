<script>
    import { onMount } from 'svelte';
    import { logoutUser, onMessageListener, hasMedicalRecord, requestFCMToken } from '$lib/firebase';
    // Fix component import capitalization to match the actual file names
    import MedicalProfile from './medicalprofile.svelte';
    import MedicalForm from './medicalform.svelte';
    import PermissionsPanel from './permissions-panel.svelte';
    
    export let user;
    
    let notifications = [];
    let loading = false;
    let showMedicalForm = false;
    let medicalRecordExists = false;
    let activeTab = 'notifications';
    
    // Permission states
    let notificationPermission = null;
    let locationPermission = null;
    let showPermissionsPanel = false;
    let fcmToken = null;
    
    onMount(async () => {
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
            } catch (error) {
                console.error("Error checking geolocation permission:", error);
            }
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
        const unsubscribe = onMessageListener();
        
        // Check if user has medical record
        if (user && user.uid) {
            hasMedicalRecord(user.uid).then(result => {
                medicalRecordExists = result;
            });
        }
        
        unsubscribe();
    });
    
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
</style>
