/**
 * Notification Service for managing app notifications
 * Stores notification history in localStorage and integrates with the dashboard
 */

import { writable } from 'svelte/store';

// Create stores for active notifications
export const notifications = writable([]); // For toast notifications
export const dashboardNotifications = writable([]); // For dashboard notifications

// Key for localStorage
const NOTIFICATION_HISTORY_KEY = 'inet-ready-notifications-history';

/**
 * Show a notification (appears as toast and in dashboard)
 * @param {string} message - The notification message
 * @param {string} type - The notification type (success, warning, error, info)
 * @param {number} duration - How long to show the toast notification in ms (default 5000ms, set to 0 for persistent)
 * @param {string} title - Optional title for the notification
 * @returns {string} The ID of the notification
 */
export function showNotification(message, type = 'info', duration = 5000, title = '') {
    // Generate a unique ID
    const notificationId = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const notification = {
        id: notificationId,
        message,
        type,
        title: title || getDefaultTitle(type),
        timestamp: new Date(),
        read: false,
        dismissed: false,
        showAsToast: true,
        autoDismiss: duration > 0,
        duration
    };
    
    // Add notification to the toast store
    notifications.update(all => [notification, ...all]);
    
    // Add to dashboard notifications store 
    dashboardNotifications.update(all => [notification, ...all]);
    
    // Add to localStorage history
    addToNotificationHistory(notification);
    
    return notificationId;
}

/**
 * Dismiss a notification from the toast view (but keep it in history)
 * @param {string} id - The ID of the notification to dismiss
 */
export function dismissNotification(id) {
    notifications.update(all => 
        all.map(n => n.id === id ? {...n, dismissed: true, showAsToast: false} : n)
    );
}

/**
 * Add notification to localStorage history
 * @param {Object} notification - The notification to add
 */
function addToNotificationHistory(notification) {
    try {
        // Get existing history from localStorage
        const historyString = localStorage.getItem(NOTIFICATION_HISTORY_KEY);
        const history = historyString ? JSON.parse(historyString) : [];
        
        // Add new notification to history (limit to last 50)
        const updatedHistory = [notification, ...history].slice(0, 50);
        
        // Save back to localStorage
        localStorage.setItem(NOTIFICATION_HISTORY_KEY, JSON.stringify(updatedHistory));
    } catch (e) {
        console.error('Error saving notification history:', e);
    }
}

/**
 * Get default title based on notification type
 * @param {string} type - Notification type
 * @returns {string} Default title
 */
function getDefaultTitle(type) {
    switch(type) {
        case 'success': return 'Success';
        case 'warning': return 'Warning';
        case 'error': return 'Error';
        default: return 'Notification';
    }
}

/**
 * Get notification history from localStorage
 * @returns {Array} The notification history
 */
export function getNotificationHistory() {
    try {
        const history = localStorage.getItem(NOTIFICATION_HISTORY_KEY);
        return history ? JSON.parse(history) : [];
    } catch (e) {
        console.error('Error reading notification history:', e);
        return [];
    }
}

/**
 * Mark a notification as read
 * @param {string} id - The ID of the notification to mark as read
 */
export function markNotificationAsRead(id) {
    try {
        // Get existing history
        const historyString = localStorage.getItem(NOTIFICATION_HISTORY_KEY);
        if (!historyString) return;
        
        // Update the notification in localStorage
        const history = JSON.parse(historyString);
        const updatedHistory = history.map(n => 
            n.id === id ? {...n, read: true} : n
        );
          // Also update it in the dashboard notifications store
        dashboardNotifications.update(all => 
            all.map(n => n.id === id ? {...n, read: true} : n)
        );
        
        localStorage.setItem(NOTIFICATION_HISTORY_KEY, JSON.stringify(updatedHistory));
    } catch (e) {
        console.error('Error marking notification as read:', e);
    }
}

/**
 * Clear all notifications from the dashboard
 */
export function clearAllNotifications() {
    try {
        // Clear the notifications store
        dashboardNotifications.set([]);
        
        // Keep notifications in localStorage but mark them all as read
        const historyString = localStorage.getItem(NOTIFICATION_HISTORY_KEY);
        if (historyString) {
            const history = JSON.parse(historyString);
            const updatedHistory = history.map(n => ({...n, read: true}));
            localStorage.setItem(NOTIFICATION_HISTORY_KEY, JSON.stringify(updatedHistory));
        }
    } catch (e) {
        console.error('Error clearing notifications:', e);
    }
}

/**
 * Load notifications from localStorage into the dashboard store
 */
export function loadNotificationsFromStorage() {
    try {
        const history = getNotificationHistory();
        if (history && history.length > 0) {
            dashboardNotifications.set(history);
        }
    } catch (e) {
        console.error('Error loading notifications from storage:', e);
    }
}

/**
 * Clear all notifications in history
 */
export function clearNotificationHistory() {
    try {
        localStorage.removeItem(NOTIFICATION_HISTORY_KEY);
    } catch (e) {
        console.error('Error clearing notification history:', e);
    }
}