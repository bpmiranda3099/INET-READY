<script>
	import { injectSpeedInsights } from '@vercel/speed-insights/sveltekit';
	import '../styles/styles.css';
	import ToastContainer from '../components/toast-container.svelte';
	import { onMount } from 'svelte';
	import { loadNotificationsFromStorage } from '$lib/services/notification-service';
	import { showPropellerAds } from '$lib/services/ads-service';

	injectSpeedInsights();

	let showPropAds;

	// Subscribe to the propeller ads store
	const unsubscribePropAds = showPropellerAds.subscribe((value) => {
		showPropAds = value;
	});

	onMount(() => {
		// Load saved notifications from localStorage on app start
		loadNotificationsFromStorage();

		return () => {
			unsubscribePropAds();
		};
	});
</script>

<svelte:head>
	<meta
		name="viewport"
		content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
	/>
	<meta name="google-adsense-account" content="ca-pub-5128336241212748" />
	<link
		rel="stylesheet"
		href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
	/>
	<script
		async
		src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5128336241212748"
		crossorigin="anonymous"
	></script>
	
	{#if showPropAds}
		<script
			src="https://fpyf8.com/88/tag.min.js"
			data-zone="148051"
			async
			data-cfasync="false"
		></script>
	{/if}
	
</svelte:head>

<main>
	<slot />
</main>

<ToastContainer />
