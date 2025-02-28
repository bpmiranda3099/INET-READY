<script>
	import { onMount } from 'svelte';
	import { requestFCMToken, testFirestoreConnection } from '$lib/firebase';
	import { goto } from '$app/navigation';

	onMount(async () => {
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker
				.register('/firebase-messaging-sw.js')
				.then((reg) => console.log('Service Worker Registered:', reg))
				.catch((err) => console.error('Service Worker Registration Failed:', err));
		}

		await requestFCMToken();
		
		// Test Firestore connection
		await testFirestoreConnection();
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
