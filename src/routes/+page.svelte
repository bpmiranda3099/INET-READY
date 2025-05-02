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
		<span class="fw-bold" style="color:#fff;">INET-READY</span>
		<span class="d-none d-md-inline" style="color:#fff;">: Your Heat Check for Safe and Informed Travel</span>
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
	  <li class="nav-item">
		<a class="nav-link" href="/terms" style="color:#fff;">Terms of Service</a>
	  </li>
	  <li class="nav-item">
		<a class="nav-link" href="/privacy" style="color:#fff;">Privacy Policy</a>
	  </li>
	  <li class="nav-item">
		<a class="nav-link" href="/data-deletion" style="color:#fff;">Data Deletion</a>
	  </li>
	  <li class="nav-item">
		<button class="btn ms-2 px-4" style="background:#fff; color:#dd815e; border:none; border-radius:50px; font-weight:600;" on:click={navigateToApp}>Get Started</button>
	  </li>
	</ul>
  </div>
	</div>
  </nav>

  <!-- HERO SECTION -->
  <section class="hero d-flex align-items-center justify-content-center text-center px-3" style="background:#fff; min-height:70vh;">
	<div class="hero-content w-100">
<video src="https://cdnl.iconscout.com/lottie/premium/thumb/avoid-direct-sun-animation-download-in-lottie-json-gif-static-svg-file-formats--cooling-air-herself-fan-waving-heat-stroke-danger-pack-people-animations-9123129.mp4" autoplay loop muted playsinline style="max-width:600px; width:100%; height:auto; border:none; background:transparent; box-shadow:none;"></video>
	  <h1 style="color:#dd815e; font-size:2.7rem; font-weight:700;">Travel Safer. Travel Smarter. <br> Your Heat-Health Companion</h1>
<p class="subtitle mb-4" style="font-size:1.25rem; color:#555; max-width:600px; margin:0 auto; font-family:'Segoe UI', Arial, sans-serif; line-height:1.5;">INET-READY helps you stay safe and healthy on every journey with real-time heat index alerts, personalized health insights, and secure medical data management—all in one easy-to-use platform.</p>
	  <button class="btn px-5 py-3 cta-button" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:700; font-size:1.2rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- BENEFITS/FEATURES SECTION -->
  <section id="features" class="features py-5" style="background:#f5f5f7;">
	<div class="container">
	  <h2 class="mb-4 text-center" style="color:#dd815e; font-weight:700;">How INET-READY Helps You</h2>
	  <ul class="list-unstyled row g-4 feature-cards justify-content-center mb-5" style="padding:0;">
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#ff6933; font-size:2.2rem;"><i class="bi bi-thermometer-sun"></i></div>
			<h5 class="fw-bold mb-2">Real-Time Heat Index</h5>
			<p>Get up-to-date heat index forecasts for your city, powered by OpenMeteo and geospatial data.</p>
		  </div>
		</li>
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#4285F4; font-size:2.2rem;"><i class="bi bi-heart-pulse"></i></div>
			<h5 class="fw-bold mb-2">Personalized Health Insights</h5>
			<p>Receive tailored health risk insights and travel advice based on your medical profile and location.</p>
		  </div>
		</li>
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#dd815e; font-size:2.2rem;"><i class="bi bi-shield-lock"></i></div>
			<h5 class="fw-bold mb-2">Privacy & Security</h5>
			<p>Your medical data is encrypted and securely managed—privacy is our top priority.</p>
		  </div>
		</li>
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#1976d2; font-size:2.2rem;"><i class="bi bi-bell-fill"></i></div>
			<h5 class="fw-bold mb-2">Instant Notifications</h5>
			<p>Receive timely alerts about heat risks and health reminders wherever you are.</p>
		  </div>
		</li>
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#ff6933; font-size:2.2rem;"><i class="bi bi-geo-alt-fill"></i></div>
			<h5 class="fw-bold mb-2">Location-Based Advice</h5>
			<p>Get personalized travel health tips based on your current or planned destinations.</p>
		  </div>
		</li>
		<li class="col-12 col-md-4">
		  <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
			<div class="icon mb-3" style="color:#4285F4; font-size:2.2rem;"><i class="bi bi-cloud-arrow-down"></i></div>
			<h5 class="fw-bold mb-2">Easy Data Access</h5>
			<p>Securely store and access your medical info and travel preferences anytime, anywhere.</p>
		  </div>
		</li>
	  </ul>

	</div>
  </section>
  <!-- SOCIAL PROOF SECTION -->
  <section class="py-5" style="background:#fff;">
	<div class="container">
	  <h2 class="mb-4 text-center" style="color:#dd815e; font-weight:700;">What Our Users Say</h2>
	  <div class="row justify-content-center g-4">
		<div class="col-12 col-md-4">
		  <div class="bg-white rounded shadow-sm p-4 h-100 text-center">
			<div class="mb-3"><i class="bi bi-chat-quote" style="font-size:2rem; color:#4285F4;"></i></div>
			<blockquote class="blockquote mb-2" style="font-size:1.1rem;">“INET-READY gave me peace of mind on my trip. The heat alerts and health tips were spot on!”</blockquote>
			<footer class="blockquote-footer">Anna, Frequent Traveler</footer>
		  </div>
		</div>
		<div class="col-12 col-md-4">
		  <div class="bg-white rounded shadow-sm p-4 h-100 text-center">
			<div class="mb-3"><i class="bi bi-chat-quote" style="font-size:2rem; color:#dd815e;"></i></div>
			<blockquote class="blockquote mb-2" style="font-size:1.1rem;">“I love how easy it is to keep my medical info safe and get travel advice for my family.”</blockquote>
			<footer class="blockquote-footer">Miguel, Parent</footer>
		  </div>
		</div>
		<div class="col-12 col-md-4">
		  <div class="bg-white rounded shadow-sm p-4 h-100 text-center">
			<div class="mb-3"><i class="bi bi-chat-quote" style="font-size:2rem; color:#ff6933;"></i></div>
			<blockquote class="blockquote mb-2" style="font-size:1.1rem;">“The notifications are super helpful. I feel safer traveling for work now.”</blockquote>
			<footer class="blockquote-footer">Sarah, Business Traveler</footer>
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
			<li><i class="bi bi-check-circle-fill me-2"></i> Powered by SvelteKit, Firebase, Mapbox, and OpenMeteo</li>
			<li><i class="bi bi-check-circle-fill me-2"></i> No technical skills required—just sign up and go!</li>
		  </ul>
		</div>
		<div class="col-md-6 mb-4 mb-md-0 text-center">
<img src="/app-icon.png" alt="INET-READY Logo" class="img-fluid rounded" style="max-width:180px; background:transparent; border:none;" />
		</div>
	  </div>
	</div>
  </section>

  <!-- CALL TO ACTION -->
  <section class="get-started py-5" style="background:#fff;">
	<div class="container text-center">
	  <h2 style="color:#dd815e; font-weight:700;">Ready to travel safer?</h2>
	  <p class="mb-4" style="font-size:1.1rem; color:#555;">Create your free account and get instant access to personalized travel health tools and notifications.</p>
	  <button class="btn px-5 py-3 cta-button" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:700; font-size:1.2rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- CONTACT/FOOTER -->
  <footer id="contact" class="border-0 py-5 mt-5" style="background:#dd815e;">
	<div class="container">
	  <div class="row gy-4">
		<!-- Brand/Logo Section -->
		<div class="col-12 col-md-4 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start">
		  <div class="d-flex align-items-center gap-2 mb-2 mb-md-0">
			<img src="/app-icon.png" alt="INET-READY" width="36" height="36" style="border-radius:8px; background:transparent;" />
			<span class="fw-bold" style="color:#fff; font-size:1.2rem;">INET-READY</span>
		  </div>
		</div>
		<!-- Links Section -->
		<div class="col-12 col-md-4 text-center mb-3 mb-md-0 d-flex flex-column align-items-center justify-content-center">
		  <div class="row w-100">
			<div class="col-12 d-flex flex-column flex-md-row justify-content-center align-items-center gap-2 gap-md-3">
			  <a href="/terms" class="text-decoration-none" style="color:#fff;">Terms</a>
			  <a href="/privacy" class="text-decoration-none" style="color:#fff;">Privacy</a>
			  <a href="/data-deletion" class="text-decoration-none" style="color:#fff;">Data Deletion</a>
			</div>
			<div class="col-12 d-flex flex-column flex-md-row justify-content-center align-items-center gap-2 gap-md-3 mt-2 mt-md-3">
			  <a href="https://inet-ready-v2.vercel.app" class="text-decoration-none" style="color:#fff;">Live Demo</a>
			  <a href="mailto:info@inet-ready.com" class="text-decoration-none" style="color:#fff;">Contact</a>
			</div>
			<div class="col-12 d-flex flex-row justify-content-center align-items-center gap-3 mt-3">
			  <!-- Social Links -->
			  <a href="https://github.com/bpmiranda3099/inet-ready-v2" target="_blank" rel="noopener" title="GitHub" aria-label="GitHub" style="color:#fff; font-size:1.5rem;"><i class="bi bi-github"></i></a>
			  <a href="mailto:support@inet-ready.com" target="_blank" rel="noopener" title="Email" aria-label="Email" style="color:#fff; font-size:1.5rem;"><i class="bi bi-envelope-fill"></i></a>
			  <a href="https://inet-ready-v2.vercel.app" target="_blank" rel="noopener" title="Website" aria-label="Website" style="color:#fff; font-size:1.5rem;"><i class="bi bi-globe2"></i></a>
			</div>
		  </div>
		</div>
		<!-- Powered By Section -->
		<div class="col-12 col-md-4 text-center text-md-end d-flex flex-column align-items-center align-items-md-end">
		  <div class="mb-2" style="color:#fff; font-weight:600; letter-spacing:1px; font-size:1.1rem;">Powered by:</div>
		  <div class="d-flex justify-content-center justify-content-md-end align-items-center gap-2 flex-wrap">
			<img src="/open-meteo-icon.png" alt="OpenMeteo" class="tech-logo white-logo" style="border-radius:12px; background:transparent;" height="36" />
			<img src="/mapbox-icon.png" alt="Mapbox" class="tech-logo white-logo" style="border-radius:12px; background:transparent;" height="36" />
			<img src="/svelte-icon.png" alt="Svelte" class="tech-logo white-logo" style="border-radius:12px; background:transparent;" height="36" />
			<img src="/firebase-icon.png" alt="Firebase" class="tech-logo white-logo" style="border-radius:12px; background:transparent;" height="36" />
			<img src="/aptible-icon.png" alt="Aptible" class="tech-logo white-logo" style="border-radius:12px; background:transparent;" height="36" />
		  </div>
		</div>
	  </div>
	  <hr style="border-color:rgba(255,255,255,0.2); margin:2rem 0 1rem 0;" />
	  <div class="text-center small" style="color:#fff;">© 2025 INET-READY. All rights reserved.</div>
	</div>
  </footer>
 </main>

<style>
.tech-logo {
  height: 60px;
  width: auto;
  object-fit: contain;
}
.white-logo {
  filter: brightness(0) invert(1) !important;
}
</style>

