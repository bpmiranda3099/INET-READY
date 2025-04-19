<script>
  import { onMount } from 'svelte';
  import { requestFCMToken } from '$lib/firebase/messaging';
  import { registerServiceWorker, isServiceWorkerActive } from '$lib/services/service-worker';
  import { getMessaging, getToken } from 'firebase/messaging';
  import { getFunctions, httpsCallable } from 'firebase/functions';
  import app from '$lib/firebase/app';
  
  let notificationPermission = 'unknown';
  let fcmToken = null;
  let swStatus = { active: false, scope: null };
  let isLoading = false;
  let testResult = null;
  let vapidKey = process.env.VITE_FIREBASE_VAPID_KEY;
  
  onMount(async () => {
    if ('Notification' in window) {
      notificationPermission = Notification.permission;
      
      if (notificationPermission === 'granted') {
        await checkServiceWorker();
        fcmToken = await getOrRequestToken();
      }
    } else {
      notificationPermission = 'unsupported';
    }
  });
  
  async function checkServiceWorker() {
    isLoading = true;
    try {
      const regs = await navigator.serviceWorker.getRegistrations();
      const fcmSW = regs.find(reg => reg.scope.includes(window.location.origin));
      
      if (fcmSW) {
        swStatus.active = !!fcmSW.active;
        swStatus.scope = fcmSW.scope;
      } else {
        // Try to register the service worker
        await registerServiceWorker();
        const active = await isServiceWorkerActive();
        swStatus.active = active;
      }
    } catch (error) {
      console.error("Error checking service worker:", error);
    } finally {
      isLoading = false;
    }
  }
  
  async function getOrRequestToken() {
    try {
      // Ensure service worker is registered first
      if (!swStatus.active) {
        await registerServiceWorker();
      }
      
      // Get FCM token using Firebase Messaging
      const messaging = getMessaging(app);
      const currentToken = await getToken(messaging, {
        vapidKey: vapidKey,
        serviceWorkerRegistration: await navigator.serviceWorker.ready
      });
      
      if (currentToken) {
        console.log('Current FCM token:', currentToken);
        return currentToken;
      } else {
        console.log('No FCM token available. Requesting new token...');
        const newToken = await requestFCMToken();
        return newToken;
      }
    } catch (error) {
      console.error("Error getting FCM token:", error);
      return null;
    }
  }
  
  async function requestPermission() {
    isLoading = true;
    
    try {
      const permission = await Notification.requestPermission();
      notificationPermission = permission;
      
      if (permission === 'granted') {
        await checkServiceWorker();
        fcmToken = await getOrRequestToken();
      }
    } catch (error) {
      console.error("Error requesting permission:", error);
      testResult = { success: false, message: error.message };
    } finally {
      isLoading = false;
    }
  }
  
  async function sendTestNotification() {
    isLoading = true;
    testResult = null;
    
    try {
      // Create a test notification directly in the browser
      new Notification("Test Notification", {
        body: "This is a test notification sent directly from the browser",
        icon: "/app-icon.png",
        badge: "/favicon.png"
      });
      
      testResult = { success: true, message: "Local test notification sent!" };
    } catch (error) {
      console.error("Error sending test notification:", error);
      testResult = { success: false, message: error.message };
    } finally {
      isLoading = false;
    }
  }
  
  async function sendServerNotification() {
    isLoading = true;
    testResult = null;
    
    try {
      if (!fcmToken) {
        throw new Error("No FCM token available");
      }
      
      // Use Firebase Functions to send a notification
      const functions = getFunctions(app);
      const sendTestNotification = httpsCallable(functions, 'sendTestNotification');
      
      // Call the function
      const result = await sendTestNotification({ token: fcmToken });
      console.log("Function result:", result.data);
      
      testResult = { 
        success: true, 
        message: "Server notification sent! It may take a moment to arrive."
      };
    } catch (error) {
      console.error("Error sending server notification:", error);
      testResult = { 
        success: false, 
        message: `Error: ${error.message}. This may be because your cloud function isn't deployed yet.`
      };
    } finally {
      isLoading = false;
    }
  }
  
  async function reregisterServiceWorker() {
    isLoading = true;
    testResult = null;
    
    try {
      // Unregister existing service workers
      const regs = await navigator.serviceWorker.getRegistrations();
      for (let reg of regs) {
        await reg.unregister();
        console.log("Unregistered service worker:", reg.scope);
      }
      
      // Register new service worker
      const reg = await navigator.serviceWorker.register('/firebase-messaging-sw.js', { scope: '/' }); // Ensure correct path
      console.log("Registered new service worker:", reg.scope);
      
      // Update status
      swStatus.active = !!reg.active;
      swStatus.scope = reg.scope;
      
      testResult = { 
        success: true, 
        message: "Service worker re-registered successfully"
      };
      
      // Request new token after a brief delay
      setTimeout(async () => {
        fcmToken = await getOrRequestToken();
      }, 1000);
      
    } catch (error) {
      console.error("Error re-registering service worker:", error);
      testResult = { success: false, message: error.message };
    } finally {
      isLoading = false;
    }
  }
  
  function copyToken() {
    if (fcmToken) {
      navigator.clipboard.writeText(fcmToken);
      testResult = { success: true, message: "Token copied to clipboard!" };
    }
  }
</script>

<div class="container my-4">
  <h1>Push Notification Tester</h1>
  
  <div class="card mb-4">
    <div class="card-body">
      <h3>Notification Status</h3>
      
      <div class="mb-3">
        <strong>Permission Status:</strong> 
        <span class={
          notificationPermission === 'granted' ? 'text-success' : 
          notificationPermission === 'denied' ? 'text-danger' : 'text-warning'
        }>
          {notificationPermission}
        </span>
      </div>
      
      <div class="mb-3">
        <strong>Service Worker:</strong> 
        <span class={swStatus.active ? 'text-success' : 'text-danger'}>
          {swStatus.active ? 'Active' : 'Inactive'}
        </span>
        {#if swStatus.scope}
          <small class="text-muted ms-2">({swStatus.scope})</small>
        {/if}
      </div>
      
      <div class="mb-3">
        <strong>FCM Token:</strong> 
        {#if fcmToken}
          <span class="text-success">Available</span>
          <button class="btn btn-sm btn-outline-secondary ms-2" on:click={copyToken}>
            Copy
          </button>
          <div class="mt-2">
            <small class="text-muted" style="word-break: break-all;">
              {fcmToken}
            </small>
          </div>
        {:else}
          <span class="text-danger">Not available</span>
        {/if}
      </div>
      
      <div class="d-grid gap-2 d-sm-block">
        {#if notificationPermission !== 'granted'}
          <button 
            class="btn btn-primary me-2" 
            on:click={requestPermission} 
            disabled={isLoading || notificationPermission === 'denied'}>
            {isLoading ? 'Processing...' : 'Request Permission'}
          </button>
        {:else}
          <button 
            class="btn btn-primary me-2" 
            on:click={sendTestNotification} 
            disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send Browser Notification'}
          </button>
          
          <button 
            class="btn btn-info me-2" 
            on:click={sendServerNotification} 
            disabled={isLoading || !fcmToken}>
            {isLoading ? 'Sending...' : 'Send Server Notification'}
          </button>
        {/if}
        
        <button 
          class="btn btn-outline-secondary" 
          on:click={reregisterServiceWorker} 
          disabled={isLoading}>
          Re-register Service Worker
        </button>
      </div>
    </div>
  </div>
  
  {#if testResult}
    <div class="alert {testResult.success ? 'alert-success' : 'alert-danger'}">
      {testResult.message}
    </div>
  {/if}
  
  <div class="card">
    <div class="card-body">
      <h3>Troubleshooting Steps</h3>
      
      <ol>
        <li>Check if the service worker is properly registered and active</li>
        <li>Ensure notifications are enabled in your browser settings</li>
        <li>Verify that your site has the correct VAPID key</li>
        <li>Make sure the FCM token is saved in your database</li>
        <li>Test with both direct browser notifications and server-sent notifications</li>
        <li>Check browser console for any errors</li>
        <li>Try using a different browser to rule out browser-specific issues</li>
      </ol>
      
      <p><strong>Note:</strong> Some browsers and operating systems may block background notifications due to battery optimization settings or focus modes.</p>
    </div>
  </div>
</div>

