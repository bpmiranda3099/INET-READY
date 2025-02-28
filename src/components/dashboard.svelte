<script>
    import { onMount } from 'svelte';
    import { logoutUser, onMessageListener } from '$lib/firebase';
    
    export let user;
    
    let notifications = [];
    let loading = false;
    
    onMount(() => {
        // Subscribe to foreground messages
        const unsubscribe = onMessageListener((payload) => {
            console.log('Received foreground message:', payload);
            const notification = {
                title: payload.notification?.title || 'New Message',
                body: payload.notification?.body || 'You received a new notification',
                timestamp: new Date().toISOString()
            };
            
            notifications = [notification, ...notifications];
        });
        
        return unsubscribe;
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
    
    <div class="content">
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
        
        <div class="card">
            <h3>Account</h3>
            <div class="account-info">
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>User ID:</strong> {user.uid}</p>
                <p><strong>Email Verified:</strong> {user.emailVerified ? 'Yes' : 'No'}</p>
                <p><strong>Account Created:</strong> {user.metadata?.creationTime ? new Date(user.metadata.creationTime).toLocaleString() : 'Unknown'}</p>
            </div>
        </div>
    </div>
</div>
