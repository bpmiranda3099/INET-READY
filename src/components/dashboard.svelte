<script>
    import { onMount } from 'svelte';
    import { logoutUser, onMessageListener, hasMedicalRecord } from '$lib/firebase';
    // Fix component import capitalization to match the actual file names
    import MedicalProfile from './medicalprofile.svelte';
    import MedicalForm from './medicalform.svelte';
    
    export let user;
    
    let notifications = [];
    let loading = false;
    let showMedicalForm = false;
    let medicalRecordExists = false;
    let activeTab = 'notifications';
    
    onMount(() => {
        // Subscribe to foreground messages
        const unsubscribe = onMessageListener();
        
        // Check if user has medical record
        if (user && user.uid) {
            hasMedicalRecord(user.uid).then(result => {
                medicalRecordExists = result;
            });
        }
        
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
    
    function handleMedicalFormCompleted() {
        showMedicalForm = false;
        medicalRecordExists = true;
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
    .dashboard-tabs {
        display: flex;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: var(--spacing-lg);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .tab-btn {
        padding: var(--spacing-sm) var(--spacing-md);
        background: none;
        border: none;
        border-bottom: 3px solid transparent;
        cursor: pointer;
        font-weight: 500;
        color: var(--text-light);
        transition: all 0.3s;
        white-space: nowrap;
    }
    
    .tab-btn.active {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
    }
    
    .tab-btn:hover:not(.active) {
        color: var(--text-color);
        border-bottom-color: var(--border-color);
    }
    
    .tab-content {
        margin-bottom: var(--spacing-xl);
    }
</style>
