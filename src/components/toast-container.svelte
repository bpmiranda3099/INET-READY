<script>
    import { onMount, onDestroy } from 'svelte';
    import { notifications } from '$lib/services/notification-service';
    import ToastNotification from './toast-notification.svelte';

    // Subscribe to the notifications store
    let visibleNotifications = [];
    let unsubscribe;
    
    onMount(() => {
        unsubscribe = notifications.subscribe(notifs => {
            visibleNotifications = notifs.filter(n => !n.dismissed && n.showAsToast);
        });
    });
    
    onDestroy(() => {
        if (unsubscribe) unsubscribe();
    });
</script>

<div class="toast-container">
    {#each visibleNotifications as notification (notification.id)}
        <ToastNotification {notification} />
    {/each}
</div>

<style>
    .toast-container {
        position: fixed;
        top: 60px; /* Positioned below app bar */
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 350px;
        pointer-events: none; /* Allow clicking through container, but not toasts */
    }
    
    /* Mobile responsive layout */
    @media (max-width: 480px) {
        .toast-container {
            right: 0;
            left: 0;
            padding: 0 10px;
            max-width: 100%;
        }
    }
</style>
