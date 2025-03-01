<script>
	import { onMount } from 'svelte';
	import { requestFCMToken, testFirestoreConnection } from '$lib/firebase';
	import { goto } from '$app/navigation';

	let fcmError = false;
	let firestoreConnected = false;

	onMount(async () => {
		// Register service worker
		if ('serviceWorker' in navigator) {
			try {
				const reg = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
				console.log('Service Worker Registered:', reg);
			} catch (err) {
				console.error('Service Worker Registration Failed:', err);
			}
		}

		// Request FCM token (with error handling)
		try {
			const token = await requestFCMToken();
			fcmError = !token;
		} catch (error) {
			console.error("FCM token request failed:", error);
			fcmError = true;
		}
		
		// Test Firestore connection
		try {
			firestoreConnected = await testFirestoreConnection();
		} catch (error) {
			console.error("Firestore connection test failed:", error);
		}
	});

	function navigateToApp() {
		goto('/app');
	}
</script>

<main>
	<section class="hero">
		<div class="hero-content">
			<h1>Welcome to INET-READY</h1>
			<p class="subtitle">The all-in-one platform for secure network monitoring and notifications</p>
			<button class="cta-button" on:click={navigateToApp}>Get Started</button>
		</div>
	</section>

	<section class="features">
		<h2>Key Features</h2>
		<div class="feature-cards">
			<div class="feature-card">
				<div class="icon">📊</div>
				<h3>Real-time Monitoring</h3>
				<p>Monitor your network performance with instant updates and alerts</p>
			</div>
			<div class="feature-card">
				<div class="icon">🔒</div>
				<h3>Secure Authentication</h3>
				<p>Enterprise-grade security to keep your network data safe</p>
			</div>
			<div class="feature-card">
				<div class="icon">📱</div>
				<h3>Push Notifications</h3>
				<p>Stay informed with real-time alerts directly to your device</p>
			</div>
		</div>
	</section>

	<section class="get-started">
		<h2>Ready to get started?</h2>
		<p>Create an account or login to access your dashboard</p>
		<button class="secondary-button" on:click={navigateToApp}>Go to Dashboard</button>
	</section>
</main>
