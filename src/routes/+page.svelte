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
				const reg = await navigator.serviceWorker.register('/firebase-messaging-sw.js'); // Ensure correct path
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

<main>
  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg shadow-sm py-3" style="background:#dd815e;">
	<div class="container-fluid">
	  <a class="navbar-brand d-flex align-items-center gap-2" href="#" style="color:#fff;">
		<img src="/app-icon.png" alt="INET-READY" width="36" height="36" style="border-radius:8px;" />
		<span class="fw-bold" style="color:#fff; letter-spacing:1px;">INET-READY</span>
	  </a>
	  <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" style="border-color:#fff;">
		<span class="navbar-toggler-icon" style="filter:invert(1);"></span>
	  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
	<ul class="navbar-nav ms-auto mb-2 mb-lg-0">
	  <li class="nav-item">
		<a class="nav-link active" aria-current="page" href="#features" style="color:#fff;">Features</a>
	  </li>
	  <li class="nav-item">
		<a class="nav-link" href="#about" style="color:#fff;">About</a>
	  </li>
	  <li class="nav-item">
		<a class="nav-link" href="#contact" style="color:#fff;">Contact</a>
	  </li>
	  <li class="nav-item dropdown">
		<a class="nav-link dropdown-toggle" href="#" id="navbarLegalDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false" style="color:#fff;">
		  Legal
		</a>
		<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarLegalDropdown">
		  <li><a class="dropdown-item" href="/terms">Terms of Service</a></li>
		  <li><a class="dropdown-item" href="/privacy">Privacy Policy</a></li>
		  <li><a class="dropdown-item" href="/data-deletion">Data Deletion</a></li>
		</ul>
	  </li>
	  <li class="nav-item">
		<button class="btn ms-2 px-4" style="background:#fff; color:#dd815e; border:none; border-radius:50px; font-weight:600;" on:click={navigateToApp}>Get Started</button>
	  </li>
	</ul>
  </div>
	</div>
  </nav>

  <!-- HERO SECTION -->
  <section class="hero d-flex align-items-center justify-content-center text-center px-3" style="background:#fff; min-height:60vh;">
	<div class="hero-content w-100">
	  <h1 style="color:#dd815e; font-size:2.5rem; font-weight:700;">Your Heat Check for Safe and Informed Travel</h1>
	  <p class="subtitle mb-4" style="font-size:1.2rem; color:#555;">Stay safe, healthy, and ready for your next adventure with real-time heat index, health insights, and secure medical data.</p>
	  <button class="btn px-4 py-2" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:600; font-size:1.1rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- FEATURES SECTION -->
  <section id="features" class="features py-5" style="background:#f5f5f7;">
	<div class="container">
	  <h2 class="mb-5 text-center" style="color:#dd815e; font-weight:700;">Why Choose INET-READY?</h2>
	  <div class="row g-4 feature-cards justify-content-center">
		<div class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#ff6933; font-size:2.2rem;"><i class="bi bi-thermometer-sun"></i></div>
			<h5 class="fw-bold mb-2">Real-Time Heat Index</h5>
			<p>Get up-to-date heat index forecasts for your city, powered by OpenMeteo and geospatial data.</p>
		  </div>
		</div>
		<div class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#4285F4; font-size:2.2rem;"><i class="bi bi-heart-pulse"></i></div>
			<h5 class="fw-bold mb-2">Personalized Health Insights</h5>
			<p>Receive tailored health risk insights and travel advice based on your medical profile and location.</p>
		  </div>
		</div>
		<div class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#dd815e; font-size:2.2rem;"><i class="bi bi-shield-lock"></i></div>
			<h5 class="fw-bold mb-2">Privacy & Security</h5>
			<p>Your medical data is encrypted and securely managed—privacy is our top priority.</p>
		  </div>
		</div>
	  </div>
	</div>
  </section>

  <!-- ABOUT SECTION -->
  <section id="about" class="py-5">
	<div class="container">
	  <div class="row align-items-center flex-column-reverse flex-md-row">
		<div class="col-md-6 text-center text-md-start">
		  <h3 style="color:#dd815e; font-weight:700;">About INET-READY</h3>
		  <p style="font-size:1.1rem; color:#555;">INET-READY is a modern, privacy-focused platform for travelers. We combine real-time weather, health risk insights, and secure data management to help you travel smarter and safer—whether for business or leisure.</p>
		  <ul class="list-unstyled mt-3" style="color:#4285F4;">
			<li><i class="bi bi-check-circle-fill me-2"></i> Trusted by travelers and families</li>
			<li><i class="bi bi-check-circle-fill me-2"></i> Powered by SvelteKit, Firebase, and Mapbox</li>
			<li><i class="bi bi-check-circle-fill me-2"></i> No technical skills required—just sign up and go!</li>
		  </ul>
		</div>
		<div class="col-md-6 mb-4 mb-md-0 text-center">
		  <img src="/app-icon.png" alt="INET-READY Logo" class="img-fluid rounded shadow-sm" style="max-width:180px; background:#fff;" />
		</div>
	  </div>
	</div>
  </section>

  <!-- CALL TO ACTION -->
  <section class="get-started py-5" style="background:#fff;">
	<div class="container text-center">
	  <h2 style="color:#dd815e; font-weight:700;">Ready to travel safer?</h2>
	  <p class="mb-4" style="font-size:1.1rem; color:#555;">Create your free account and get instant access to personalized travel health tools and notifications.</p>
	  <button class="btn px-4 py-2" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:600; font-size:1.1rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- CONTACT/FOOTER -->
  <footer id="contact" class="border-0 py-4 mt-5" style="background:#dd815e;">
	<div class="container d-flex flex-column flex-md-row justify-content-between align-items-center gap-3">
	  <div class="d-flex align-items-center gap-2">
		<img src="/app-icon.png" alt="INET-READY" width="32" height="32" style="border-radius:8px;" />
		<span class="fw-bold" style="color:#fff;">INET-READY</span>
	  </div>
	  <div class="small" style="color:#fff;">&copy; {new Date().getFullYear()} INET-READY. All rights reserved.</div>
	  <div class="d-flex flex-wrap align-items-center gap-3">
		<a href="/terms" class="text-decoration-none" style="color:#fff;">Terms</a>
		<a href="/privacy" class="text-decoration-none" style="color:#fff;">Privacy</a>
		<a href="/data-deletion" class="text-decoration-none" style="color:#fff;">Data Deletion</a>
		<a href="https://inet-ready-v2.vercel.app" class="text-decoration-none" style="color:#fff;">Live Demo</a>
		<a href="mailto:info@inet-ready.com" class="text-decoration-none" style="color:#fff;">Contact</a>
	  </div>
	</div>
  </footer>
</main>

