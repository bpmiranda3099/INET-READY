<script>
  import '../styles/styles.css';
  import ToastContainer from '../components/toast-container.svelte';
  import { onMount } from 'svelte';
  import { loadNotificationsFromStorage } from '$lib/services/notification-service';
  
  onMount(() => {
    // Load saved notifications from localStorage on app start
    loadNotificationsFromStorage();
  });
</script>

<svelte:head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
</svelte:head>

<main>
  <slot />
</main>

<ToastContainer />
