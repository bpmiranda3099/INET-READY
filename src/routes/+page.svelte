<script>
	import { onMount } from 'svelte';
	import { requestFCMToken, testFirestoreConnection } from '$lib/firebase';
	import { goto } from '$app/navigation';

	let fcmError = false;
	let firestoreConnected = false;
	let activeAccordion = null;

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

		// Load Bootstrap from CDN
		loadBootstrap();
	});

	function navigateToApp() {
		goto('/app');
	}

	function loadBootstrap() {
		// Add Bootstrap CSS
		const bootstrapCSS = document.createElement('link');
		bootstrapCSS.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css';
		bootstrapCSS.rel = 'stylesheet';
		bootstrapCSS.integrity = 'sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65';
		bootstrapCSS.crossOrigin = 'anonymous';
		document.head.appendChild(bootstrapCSS);

		// Add Bootstrap JS
		const bootstrapJS = document.createElement('script');
		bootstrapJS.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js';
		bootstrapJS.integrity = 'sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4';
		bootstrapJS.crossOrigin = 'anonymous';
		document.body.appendChild(bootstrapJS);
	}

	function toggleAccordion(index) {
		if (activeAccordion === index) {
			activeAccordion = null;
		} else {
			activeAccordion = index;
		}
	}
</script>

<main class="pb-5">
	<!-- Hero Section with Bootstrap -->
	<section class="hero">
		<div class="hero-content">
			<div class="container">
				<div class="row justify-content-center">
					<div class="col-md-10">
						<i class="bi bi-sun-fill" style="font-size: 15rem; color: #e0b76b; clip-path: inset(0 0 40% 0);"></i>
						<h1 class="display-1 fw-bold mb-4" style="font-size: 5rem; margin-top: -9rem;">INET-READY</h1>
						<p class="subtitle mb-3" style="font-size: 1.25rem;">Your Heat Check for Safe and Informed Travel</p>
						<button class="cta-button btn btn-lg" style="background-color: #dd815e; font-size: 1rem; color: white; margin-top: 1rem;" on:click={navigateToApp}>GET STARTED</button>
					</div>
				</div>
			</div>
		</div>
		<div class="text-center mt-4"></div>
	</section>

	<!-- Features Section Enhanced with Bootstrap -->
	<section class="features py-5 bg-white">
		<div class="container">
			<div class="row text-center mb-5">
				<div class="col">
					<h2 class="display-5 fw-bold" style="font-size: 4rem; margin-bottom: 1rem;">Features</h2>
					<p class="subtitle lead text-black" style="margin: 0rem 0;">Providing a comprehensive solution for monitoring heat related health risks.</p>
				</div>
			</div>
			<div class="row g-4">
				<div class="col-md-6 col-lg-3">
					<div class="feature-card h-100 shadow-m rounded text-center" style="background-color: #70a1a8;">
						<div class="icon mb-3">
							<i class="bi bi-shield-check" style="font-size: 3rem; color: #e0b76b;"></i>
						</div>
						<h3>Health and Safety Guidelines</h3>
						<p class="subtitle lead text-white" style="margin: 1rem 0;">Provides guidelines for managing heat exposure, including prevention, symptoms, and recommendations for vulnerable groups.</p>
					</div>
				</div>
				<div class="col-md-6 col-lg-3">
					<div class="feature-card h-100 shadow-m rounded text-center" style="background-color: #70a1a8;">
						<div class="icon mb-3">
							<i class="bi bi-bell" style="font-size: 3rem; color: #e0b76b;"></i>
						</div>
						<h3>Real-time Alerts</h3>
						<p class="subtitle lead text-white" style="margin: 1rem 0;">Sends real-time notifications when heat index levels are dangerous.</p>
					</div>
				</div>
				<div class="col-md-6 col-lg-3">
					<div class="feature-card h-100 shadow-m rounded text-center" style="background-color: #70a1a8;">
						<div class="icon mb-3">
							<i class="bi bi-thermometer-sun" style="font-size: 3rem; color: #e0b76b;"></i>
						</div>
						<h3>Heat Index Monitoring</h3>
						<p class="subtitle lead text-white" style="margin: 1rem 0;">Gathers and displays real-time weather data to calculate the heat index, informing users of immediate risks.</p>
					</div>
				</div>
				<div class="col-md-6 col-lg-3">
					<div class="feature-card h-100 shadow-m rounded text-center" style="background-color: #70a1a8;">
						<div class="icon mb-3">
							<i class="bi bi-heart-pulse" style="font-size: 3rem; color: #e0b76b;"></i>
						</div>
						<h3>Health Risk Assessment</h3>
						<p class="subtitle lead text-white" style="margin: 1rem 0;">Assesses health risks based on heat index and user data, providing personalized health advisories.</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- FAQ Section -->
	<section class="testimonials py-5">
		<div class="faq-container">
			<div class="faq-title">
				<h2 class="display-5 fw-bold text-center text-white">Frequently Asked Questions</h2>
				<p class="subtitle lead text-muted">Find answers to common questions about INET-READY</p>
			</div>
			
			<div class="accordion subtitle lead" id="faqAccordion" style="max-width: 600px; margin: 0 auto;">
				{#each [
					{ q: "How does INET-READY calculate the heat index?", a: "Using temperature and humidity data with standardized formulas." },
					{ q: "Can I customize my notification preferences?", a: "Yes, you can set custom thresholds and choose alert types." },
					{ q: "Is my health data secure?", a: "Yes, all personal health information is encrypted and stored securely." },
					{ q: "How often is the weather data updated?", a: "Every 15 minutes, with more frequent updates during extreme weather." }
				] as faqs, i}
					<div class="accordion-item mb-3 border rounded shadow-sm">
						<h2 class="accordion-header" id="heading{i}">
							<button 
								class="accordion-header border-0 bg-white w-100 text-start py-3 px-4 d-flex justify-content-between align-items-center"
								type="button" 
								on:click={() => toggleAccordion(i)}
							>
								<span class="fs-5">{faqs.q}</span>
								<span>{activeAccordion === i ? '−' : '+'}</span>
							</button>
						</h2>
						<div class="accordion-collapse collapse {activeAccordion === i ? 'show' : ''}" id="collapse{i}">
							<div class="accordion-body p-4 fs-6">
								{faqs.a}
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Call to Action Section -->
	<section class="get-started py-5  text-center">
		<div class="container">
			<br>
			<br>
			<br>
			<br>
			<br>
			<br>
			<br>
			<h2 class="display-5 fw-bold mb-3">Ready to get started?</h2>
			<button class="cta-button btn btn-lg" style="background-color: #dd815e; font-size: 1rem;" on:click={navigateToApp}>GO TO DASHBOARD</button>
			<br>
			<br>
			<br>
			<br>
			<br>
			<br>
			<br>
		</div>
	</section>
	
	<!-- Footer Section -->
	<footer class="footer">
		<div class="footer-container">
			<div class="footer-brand" style="margin-top: 1rem; margin-left: 1rem;">
				<div class="footer-logo" style="font-size: 2rem;">INET-READY</div>
				<p class="subtitle lead text-muted">Your Heat Check for Safe and Informed Travel</p>
				<div class="social-links">
					<a href="https://github.com/bpmiranda3099/inet-ready-v2" class="social-link text-white"><i class="bi bi-github"></i></a>
				</div>
			</div>
		</div>
		<div class="copyright">
			&copy; {new Date().getFullYear()} INET-READY. All rights reserved.
		</div>
	</footer>
</main>

<!-- Add Bootstrap Icons -->
<svelte:head>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</svelte:head>
