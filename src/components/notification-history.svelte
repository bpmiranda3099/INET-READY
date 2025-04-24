<script>
    import { onMount } from 'svelte';
    import { getNotificationHistory, clearNotificationHistory } from '$lib/services/notification-service';
    
    export let maxItems = 50;
    
    let notifications = [];
    let expandedNotifications = {};
    
    onMount(() => {
        loadNotifications();
    });
    
    function loadNotifications() {
        notifications = getNotificationHistory().slice(0, maxItems);
    }
    
    function clearHistory() {
        clearNotificationHistory();
        notifications = [];
    }
    
    function toggleExpanded(id) {
        expandedNotifications[id] = !expandedNotifications[id];
        expandedNotifications = {...expandedNotifications};
    }
    
    function formatDate(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
    
    function getIconClass(type) {
        switch(type) {
            case 'success': return 'bi-check-circle-fill';
            case 'error': return 'bi-exclamation-circle-fill';
            case 'warning': return 'bi-exclamation-triangle-fill';
            case 'info': 
            default: return 'bi-info-circle-fill';
        }
    }
</script>

<div class="notification-history">
    <div class="notification-history-header">
        <h3>Notification History</h3>
        {#if notifications.length > 0}
            <button class="clear-btn" on:click={clearHistory}>
                <i class="bi bi-trash"></i>
                Clear History
            </button>
        {/if}
    </div>
    
    {#if notifications.length === 0}
        <div class="empty-state">
            <i class="bi bi-bell-slash"></i>
            <p>No notifications</p>
        </div>
    {:else}
        <ul class="notification-list">
            {#each notifications as notification}
                <li class="notification-item {notification.type}">
                    <div class="notification-header" on:click={() => toggleExpanded(notification.id)}>
                        <div class="notification-icon">
                            <i class="bi {getIconClass(notification.type)}"></i>
                        </div>
                        <div class="notification-title">
                            {notification.title || 'Notification'}
                        </div>
                        <div class="notification-time">
                            {formatDate(notification.timestamp)}
                        </div>
                        <div class="notification-expand">
                            <i class="bi {expandedNotifications[notification.id] ? 'bi-chevron-up' : 'bi-chevron-down'}"></i>
                        </div>
                    </div>
                    {#if expandedNotifications[notification.id]}
                        <div class="notification-content">
                            <p>{notification.message}</p>
                        </div>
                    {/if}
                </li>
            {/each}
        </ul>
    {/if}
</div>

<style>
    .notification-history {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        overflow: hidden;
    }
    
    .notification-history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background-color: #f8f8f8;
        border-bottom: 1px solid #eee;
    }
    
    .notification-history-header h3 {
        margin: 0;
        color: #333;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .clear-btn {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        background-color: transparent;
        color: #666;
        border: none;
        font-size: 0.9rem;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .clear-btn:hover {
        background-color: rgba(244, 67, 54, 0.1);
        color: #f44336;
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 1rem;
        color: #999;
    }
    
    .empty-state i {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        opacity: 0.6;
    }
    
    .empty-state p {
        font-size: 1rem;
        margin: 0;
    }
    
    .notification-list {
        list-style: none;
        padding: 0;
        margin: 0;
        max-height: 400px;
        overflow-y: auto;
        flex-wrap: nowrap;
    }
    
    .notification-item {
        border-bottom: 1px solid #eee;
    }
    
    .notification-item:last-child {
        border-bottom: none;
    }
    
    .notification-header {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .notification-header:hover {
        background-color: #f9f9f9;
    }
    
    .notification-icon {
        margin-right: 0.75rem;
        display: flex;
        align-items: center;
    }
    
    .notification-item.success .notification-icon {
        color: #48c774;
    }
    
    .notification-item.error .notification-icon {
        color: #f44336;
    }
    
    .notification-item.warning .notification-icon {
        color: #ffdd57;
    }
    
    .notification-item.info .notification-icon {
        color: #dd815e; /* Using app's orange theme */
    }
    
    .notification-title {
        flex: 1;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .notification-time {
        font-size: 0.75rem;
        color: #777;
        margin-right: 0.75rem;
        white-space: nowrap;
    }
    
    .notification-expand {
        color: #999;
        font-size: 0.75rem;
    }
    
    .notification-content {
        padding: 0 1rem 0.75rem 2.75rem;
        font-size: 0.9rem;
        color: #555;
        line-height: 1.4;
    }
    
    .notification-content p {
        margin: 0;
    }
    
    /* Left border styling for notification items */
    .notification-item {
        position: relative;
    }
    
    .notification-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
    }
    
    .notification-item.success::before {
        background-color: #48c774;
    }
    
    .notification-item.error::before {
        background-color: #f44336;
    }
    
    .notification-item.warning::before {
        background-color: #ffdd57;
    }
    
    .notification-item.info::before {
        background-color: #dd815e; /* Using app's orange theme */
    }
</style>
