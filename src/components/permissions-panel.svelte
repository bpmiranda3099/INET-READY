<script>
    export let notificationPermission;
    export let locationPermission;
    export let onRequestNotification;
    export let onRequestLocation;
    export let onComplete;
    
    let showNotificationRequest = notificationPermission !== 'granted';
    let showLocationRequest = locationPermission !== 'granted';
    let dismissed = false;
</script>

{#if !dismissed}
<div class="permissions-panel">
    <div class="permissions-content">
        <h3>Enhance Your Experience</h3>
        <p class="intro">INET-READY provides personalized health alerts based on your location and weather conditions. To get the full experience, please enable these features:</p>
        
        {#if showNotificationRequest}
            <div class="permission-item">
                <div class="permission-icon">📱</div>
                <div class="permission-details">
                    <h4>Push Notifications</h4>
                    <p>Receive important health alerts and weather updates relevant to your well-being.</p>
                    <button on:click={onRequestNotification} class="primary-btn">
                        Enable Notifications
                    </button>
                </div>
            </div>
        {/if}
        
        {#if showLocationRequest}
            <div class="permission-item">
                <div class="permission-icon">📍</div>
                <div class="permission-details">
                    <h4>Location Access</h4>
                    <p>Get personalized health recommendations based on local weather and environmental conditions.</p>
                    <button on:click={onRequestLocation} class="primary-btn">
                        Enable Location
                    </button>
                </div>
            </div>
        {/if}
        
        <div class="permissions-actions">
            <button on:click={() => { dismissed = true; onComplete(); }} class="dismiss-btn">
                Maybe Later
            </button>
        </div>
    </div>
</div>
{/if}

<style>
    .permissions-panel {
        background-color: #f8f9fa;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 1rem 0 2rem;
        padding: 1.5rem;
        border-left: 4px solid #4285f4;
    }
    
    .permissions-content {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .intro {
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    
    .permission-item {
        display: flex;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    .permission-icon {
        font-size: 2rem;
        margin-right: 1rem;
        display: flex;
        align-items: center;
    }
    
    .permission-details {
        flex: 1;
    }
    
    .permission-details h4 {
        margin: 0 0 0.5rem;
    }
    
    .permission-details p {
        margin: 0 0 1rem;
        color: #666;
    }
    
    .primary-btn {
        background-color: #4285f4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    
    .primary-btn:hover {
        background-color: #3367d6;
    }
    
    .permissions-actions {
        text-align: right;
        margin-top: 1rem;
    }
    
    .dismiss-btn {
        background: transparent;
        border: none;
        color: #777;
        cursor: pointer;
        text-decoration: underline;
    }
    
    .dismiss-btn:hover {
        color: #555;
    }
</style>
