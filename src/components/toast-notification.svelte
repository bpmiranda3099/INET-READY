<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { fly, fade } from 'svelte/transition';
    import { dismissNotification } from '$lib/services/notification-service';

    export let notification;
    
    const dispatch = createEventDispatcher();
    let progressInterval;
    let progress = 100;
    let progressStep;

    // Get appropriate icon based on notification type
    $: iconClass = getIconClass(notification.type);
    
    // Handle automatic dismissal
    onMount(() => {
        if (notification.autoDismiss && notification.duration > 0) {
            const duration = notification.duration;
            const startTime = Date.now();
            progressStep = 100 / (duration / 10); // Update every 10ms
            
            progressInterval = setInterval(() => {
                const elapsed = Date.now() - startTime;
                progress = Math.max(0, 100 - (elapsed / duration) * 100);
                
                if (progress <= 0) {
                    clearInterval(progressInterval);
                    handleDismiss();
                }
            }, 10);
        }
        
        return () => {
            if (progressInterval) clearInterval(progressInterval);
        };
    });
    
    function handleDismiss() {
        if (progressInterval) clearInterval(progressInterval);
        dismissNotification(notification.id);
    }
    
    // Pause progress when hovering
    function handleMouseEnter() {
        if (progressInterval) clearInterval(progressInterval);
    }
    
    // Resume progress when leaving
    function handleMouseLeave() {
        if (notification.autoDismiss && notification.duration > 0) {
            const remainingTime = (progress / 100) * notification.duration;
            progressStep = progress / (remainingTime / 10);
            
            progressInterval = setInterval(() => {
                progress = Math.max(0, progress - progressStep);
                
                if (progress <= 0) {
                    clearInterval(progressInterval);
                    handleDismiss();
                }
            }, 10);
        }
    }
    
    function getIconClass(type) {
        switch(type) {
            case 'success': return 'bi-check-circle-fill';
            case 'warning': return 'bi-exclamation-triangle-fill';
            case 'error': return 'bi-exclamation-circle-fill';
            case 'info': 
            default: return 'bi-info-circle-fill';
        }
    }
</script>

<div 
    class="toast-notification {notification.type}" 
    transition:fly={{ y: -20, duration: 300 }}
    on:mouseenter={handleMouseEnter}
    on:mouseleave={handleMouseLeave}
>
    <div class="toast-header">
        <div class="toast-icon"><i class="bi {iconClass}"></i></div>
        <div class="toast-title">{notification.title || 'Notification'}</div>
        <button class="toast-close" on:click={handleDismiss}>
            <i class="bi bi-x"></i>
        </button>
    </div>
    <div class="toast-body">
        {notification.message}
    </div>
    {#if notification.autoDismiss && notification.duration > 0}
        <div class="toast-progress">
            <div class="toast-progress-bar" style="width: {progress}%"></div>
        </div>
    {/if}
</div>

<style>
    .toast-notification {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        width: 100%;
        overflow: hidden;
        pointer-events: all;
        position: relative;
        border-left: 4px solid #dd815e;
    }
    
    .toast-notification.success {
        border-left-color: #48c774;
    }
    
    .toast-notification.warning {
        border-left-color: #ffdd57;
    }
    
    .toast-notification.error {
        border-left-color: #f44336;
    }
    
    .toast-notification.info {
        border-left-color: #dd815e; /* Using your app's orange theme */
    }
    
    .toast-header {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        background-color: rgba(0, 0, 0, 0.02);
    }
    
    .toast-icon {
        margin-right: 8px;
        font-size: 1.1rem;
    }
    
    .toast-notification.success .toast-icon {
        color: #48c774;
    }
    
    .toast-notification.warning .toast-icon {
        color: #ffdd57;
    }
    
    .toast-notification.error .toast-icon {
        color: #f44336;
    }
    
    .toast-notification.info .toast-icon {
        color: #dd815e;
    }
    
    .toast-title {
        flex: 1;
        font-weight: 600;
    }
    
    .toast-close {
        background: transparent;
        border: none;
        cursor: pointer;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        color: #666;
        font-size: 1.2rem;
        padding: 0;
        transition: all 0.2s;
    }
    
    .toast-close:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
    
    .toast-body {
        padding: 12px 16px;
        color: #444;
    }
    
    .toast-progress {
        height: 4px;
        background: rgba(0, 0, 0, 0.08);
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
    }
    
    .toast-progress-bar {
        height: 100%;
        transition: width 0.1s linear;
    }
    
    .toast-notification.success .toast-progress-bar {
        background-color: #48c774;
    }
    
    .toast-notification.warning .toast-progress-bar {
        background-color: #ffdd57;
    }
    
    .toast-notification.error .toast-progress-bar {
        background-color: #f44336;
    }
    
    .toast-notification.info .toast-progress-bar {
        background-color: #dd815e;
    }
</style>
