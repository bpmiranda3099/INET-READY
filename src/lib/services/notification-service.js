/**
 * Notification Service for managing app notifications
 * Stores notification history in localStorage and integrates with the dashboard
 */

import { writable } from 'svelte/store';

// Create stores for active notifications
export const notifications = writable([]); // For toast notifications
export const dashboardNotifications = writable([]); // For dashboard notifications

// Create stores for push notifications
export const pushNotifications = writable([]);

// Keys for localStorage
const NOTIFICATION_HISTORY_KEY = 'inet-ready-notifications-history';
const REMINDER_TIMESTAMPS_KEY = 'inet-ready-reminder-timestamps';

/**
 * Show a notification (as push notification)
 * @param {string} message - The notification message
 * @param {string} type - The notification type (success, warning, error, info)
 * @param {number} duration - How long to show the toast notification in ms (default 5000ms, set to 0 for persistent)
 * @param {string} title - Optional title for the notification
 * @returns {string} The ID of the notification
 */
export function showNotification(message, type = 'info', duration = 5000, title = '') {
    const notification = {
        id: crypto.randomUUID(),
        message,
        type,
        title: title || getDefaultTitle(type),
        timestamp: new Date().toISOString(),
        showAsToast: false, // Never show as toast
    };

    // Add to notification history
    addToNotificationHistory(notification);

    // Update dashboard notifications store
    dashboardNotifications.update(notifs => [notification, ...notifs]);

    // If notification permission is granted, show as push notification
    if (Notification.permission === 'granted') {
        showPushNotification(notification.title, notification.message);
    }

    return notification.id;
}

/**
 * Show a daily reminder notification that only appears once per day
 * @param {string} reminderId - Unique identifier for this reminder type
 * @param {string} message - The notification message
 * @param {string} title - Title for the notification
 * @param {string} type - The notification type (success, warning, error, info)
 * @returns {string|null} The ID of the notification if sent, null if already sent today
 */
export function showDailyReminderNotification(reminderId, message, title, type = 'warning') {
    // Check if this reminder was already sent today
    if (wasReminderSentToday(reminderId)) {
        console.log(`Daily reminder "${reminderId}" already sent today, skipping`);
        return null;
    }
    
    // Send the notification
    const notificationId = showNotification(message, type, 0, title);
    
    // Record that this reminder was sent today
    recordReminderSent(reminderId);
    
    return notificationId;
}

/**
 * Check if a reminder was already sent today
 * @param {string} reminderId - Unique identifier for the reminder
 * @returns {boolean} True if the reminder was already sent today
 */
function wasReminderSentToday(reminderId) {
    try {
        const timestamps = getReminderTimestamps();
        
        if (!timestamps[reminderId]) {
            return false;
        }
        
        const lastSent = new Date(timestamps[reminderId]);
        const now = new Date();
        
        // Check if the reminder was sent today
        return lastSent.toDateString() === now.toDateString();
    } catch (e) {
        console.error('Error checking reminder timestamp:', e);
        return false;
    }
}

/**
 * Record that a reminder was sent today
 * @param {string} reminderId - Unique identifier for the reminder
 */
function recordReminderSent(reminderId) {
    try {
        const timestamps = getReminderTimestamps();
        
        // Update the timestamp for this reminder
        timestamps[reminderId] = new Date().toISOString();
        
        // Save back to localStorage
        localStorage.setItem(REMINDER_TIMESTAMPS_KEY, JSON.stringify(timestamps));
    } catch (e) {
        console.error('Error recording reminder timestamp:', e);
    }
}

/**
 * Get reminder timestamps from localStorage
 * @returns {Object} Reminder timestamps
 */
function getReminderTimestamps() {
    try {
        const timestamps = localStorage.getItem(REMINDER_TIMESTAMPS_KEY);
        return timestamps ? JSON.parse(timestamps) : {};
    } catch (e) {
        console.error('Error reading reminder timestamps:', e);
        return {};
    }
}

/**
 * Show a push notification
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 * @param {object} options - Additional options for the notification
 */
export function showPushNotification(title, message, options = {}) {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.ready.then(registration => {
            registration.showNotification(title, {
                body: message,
                ...options
            });
        });
    }
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
    const history = getNotificationHistory();
    history.push(notification);
    localStorage.setItem(NOTIFICATION_HISTORY_KEY, JSON.stringify(history));
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