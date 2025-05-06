<script>
	import { onMount } from 'svelte';
	import { requestFCMToken, testFirestoreConnection } from '$lib/firebase';
	// @ts-ignore
	import { goto } from '$app/navigation';

	let fcmError = false;
	let firestoreConnected = false;
	let activeAccordion = null;

// For navbar collapse toggle
let navbarCollapse;
function toggleNavbar() {
  if (navbarCollapse) {
	// Use Bootstrap's Collapse API if available (ignore TS error)
	// @ts-ignore
	const collapse = window.bootstrap?.Collapse || window.Collapse;
	if (typeof collapse === 'function') {
	  // @ts-ignore
	  let bsCollapse = collapse.getInstance(navbarCollapse);
	  if (!bsCollapse) {
		// @ts-ignore
		bsCollapse = new collapse(navbarCollapse, {toggle: false});
	  }
	  bsCollapse.toggle();
	} else {
	  // Fallback: toggle class manually
	  navbarCollapse.classList.toggle('show');
	}
  }
}

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
	  <a class="navbar-brand d-flex align-items-center gap-2" href="/" style="color:#fff;">
		<img src="/app-icon.png" alt="INET-READY" width="36" height="36" style="border-radius:8px;" />
		<span class="fw-bold align-items-center d-flex" style="color:#fff; height:45px; line-height:36px; font-size:1.6rem;">INET-READY</span>
		<span class="d-none d-md-inline align-items-center d-flex" style="color:#fff; height:36px; line-height:36px;"> Your Heat Check for Safe and Informed Travel</span>
	  </a>
	  <button class="navbar-toggler" type="button" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" style="border-color:#fff;" on:click={toggleNavbar}>
		<span class="navbar-toggler-icon" style="filter:invert(1);"></span>
	  </button>
	  <div class="collapse navbar-collapse" id="navbarNav" bind:this={navbarCollapse}>
		<ul class="navbar-nav ms-auto mb-2 mb-lg-0">
		  <li class="nav-item">
			<a class="nav-link active" aria-current="page" href="#features" style="color:#fff;">Features</a>
		  </li>
		  <li class="nav-item">
			<a class="nav-link" href="#about" style="color:#fff;">About</a>
		  </li>
		  <!-- Contact Dropdown -->
	  <li class="nav-item dropdown hover-dropdown">
		<a class="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false" style="color:#fff;" tabindex="0">
		  Contact
		</a>
			<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarContactDropdown">
			  <li><a class="dropdown-item d-flex align-items-center gap-2" href="https://github.com/bpmiranda3099/inet-ready-v2" target="_blank" rel="noopener"><i class="bi bi-github"></i> GitHub</a></li>
			  <li><a class="dropdown-item d-flex align-items-center gap-2" href="mailto:info@inet-ready.com"><i class="bi bi-envelope-fill"></i> Email</a></li>
			  <li><a class="dropdown-item d-flex align-items-center gap-2" href="https://inet-ready-v2.vercel.app" target="_blank" rel="noopener"><i class="bi bi-phone"></i> App</a></li>
			</ul>
		  </li>
		  <!-- Support Dropdown -->
	  <li class="nav-item dropdown hover-dropdown">
		<a class="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false" style="color:#fff;" tabindex="0">
		  Support
		</a>
			<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarSupportDropdown">
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
  <style>
  /* Dropdown on hover for desktop */
  @media (min-width: 992px) {
  .hover-dropdown:hover > .dropdown-menu {
	display: block;
	margin-top: 0;
  }
  .hover-dropdown > .dropdown-toggle:active {
	pointer-events: none;
  }
  .navbar-nav .nav-link, .navbar-nav .dropdown-toggle {
	position: relative;
	transition: color 0.2s;
  }
  .navbar-nav .nav-link:hover, .navbar-nav .dropdown-toggle:hover {
	text-decoration: none;
  }
  .navbar-nav .nav-link::after, .navbar-nav .dropdown-toggle::after {
	content: '';
	display: block;
	width: 0;
	height: 1.5px; /* Thinner underline for all links */
	background: transparent;
	transition: width 0.2s, background 0.2s;
	position: absolute;
	left: 0;
	bottom: 0.2em;
  }
  .navbar-nav .nav-link:hover::after, .navbar-nav .dropdown-toggle:hover::after {
	width: 100%;
	background: #fff;
	height: 1.5px; /* Ensure hover underline is also thin */
  }
  /* Hide dropdown arrow for Contact and Support */
  .navbar-nav .dropdown-toggle::after {
	display: none !important;
  }
  }
  @media (max-width: 991.98px) {
	.navbar-collapse {
	  background: #dd815e;
	  padding: 1rem 0.5rem 0.5rem;
	}
	.navbar-nav .nav-item {
	  border-bottom: 1px solid rgba(255,255,255,0.08);
	}
	.navbar-nav .nav-link, .navbar-nav .dropdown-toggle {
	  color: #fff !important;
	  font-size: 1.1rem;
	  padding: 0.75rem 1.5rem;
	}
	.navbar-nav .dropdown-menu {
	  background: #fff;
	  border-radius: 0 0 8px 8px;
	  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
	}
	.navbar-nav .dropdown-item {
	  color: #dd815e;
	  font-weight: 500;
	}
	.navbar-toggler {
	  border: none;
	}
  }
  </style>
  <style>
	/* Dropdown on hover for desktop */
	@media (min-width: 992px) {
	  .hover-dropdown:hover > .dropdown-menu {
		display: block;
		margin-top: 0;
	  }
	  .hover-dropdown > .dropdown-toggle:active {
		pointer-events: none;
	  }
	}
  </style>

  <!-- HERO SECTION -->
  <section class="hero d-flex align-items-center justify-content-center text-center px-3" style="background:#fff; min-height:70vh;">
	<div class="hero-content w-100">
<video src="https://cdnl.iconscout.com/lottie/premium/thumb/avoid-direct-sun-animation-download-in-lottie-json-gif-static-svg-file-formats--cooling-air-herself-fan-waving-heat-stroke-danger-pack-people-animations-9123129.mp4" autoplay loop muted playsinline style="max-width:600px; width:100%; height:auto; border:none; background:transparent; box-shadow:none;"></video>
	  <h1 style="color:#dd815e; font-size:2.7rem; font-weight:700;">Travel Safer. Travel Smarter. <br> Your Heat-Health Companion</h1>
<p class="subtitle mb-4" style="font-size:1.25rem; color:#555; max-width:600px; margin:0 auto; font-family:'Segoe UI', Arial, sans-serif; line-height:1.5;">INET-READY keeps you safe and healthy on the go with real-time heat alerts, personalized health insights, and secure medical data—all in one easy-to-use platform.</p>
	  <button class="btn px-5 py-3 cta-button" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:700; font-size:1.2rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- BENEFITS/FEATURES SECTION -->
  <section id="features" class="features py-5" style="background:#f5f5f7;">
  <div class="container">
	<h2 class="mb-4 text-center" style="color:#dd815e; font-weight:700;">How INET-READY Helps You</h2>
	<div id="featureCarousel" class="carousel slide" data-bs-ride="carousel" data-bs-interval="5000">
	  <div class="carousel-inner">
		<div class="carousel-item active">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-thermometer-sun"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Real-Time Heat Index</h5>
			  <p class="w-100" style="word-break:break-word;">Get up-to-date heat index forecasts for your city, powered by OpenMeteo and geospatial data.</p>
			</div>
		  </div>
		</div>
		<div class="carousel-item">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-heart-pulse-fill"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Personalized Health Insights</h5>
			  <p class="w-100" style="word-break:break-word;">Receive tailored health risk insights and travel advice based on your medical profile and location.</p>
			</div>
		  </div>
		</div>
		<div class="carousel-item">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-shield-lock-fill"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Privacy & Security</h5>
			  <p class="w-100" style="word-break:break-word;">Your medical data is encrypted and securely managed—privacy is our top priority.</p>
			</div>
		  </div>
		</div>
		<div class="carousel-item">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-bell-fill"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Instant Notifications</h5>
			  <p class="w-100" style="word-break:break-word;">Receive timely alerts about heat risks and health reminders wherever you are.</p>
			</div>
		  </div>
		</div>
		<div class="carousel-item">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-geo-alt-fill"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Location-Based Advice</h5>
			  <p class="w-100" style="word-break:break-word;">Get personalized travel health tips based on your current or planned destinations.</p>
			</div>
		  </div>
		</div>
		<div class="carousel-item">
		  <div class="d-flex justify-content-center">
			<div class="feature-card inet-orange d-flex flex-column justify-content-center align-items-center text-center p-4 rounded position-relative" style="min-width:300px; max-width:400px; width:100%; margin:0 1rem; min-height:320px;">
			  <div class="feature-icon-topright"><i class="bi bi-cloud-arrow-down-fill"></i></div>
			  <h5 class="fw-bold mb-2 w-100" style="word-break:break-word;">Easy Data Access</h5>
			  <p class="w-100" style="word-break:break-word;">Securely store and access your medical info and travel preferences anytime, anywhere.</p>
			</div>
		  </div>
		</div>
	  </div>
	  <button class="carousel-control-prev" type="button" data-bs-target="#featureCarousel" data-bs-slide="prev">
		<span class="carousel-control-prev-icon" aria-hidden="true"></span>
		<span class="visually-hidden">Previous</span>
	  </button>
	  <button class="carousel-control-next" type="button" data-bs-target="#featureCarousel" data-bs-slide="next">
		<span class="carousel-control-next-icon" aria-hidden="true"></span>
		<span class="visually-hidden">Next</span>
	  </button>
	</div>
  </div>
  </section>

  <!-- MEET OUR DEVELOPERS SECTION (Swiper Format) -->
  <section class="py-5" style="background:#fff;">
	<div class="responsive-container-block outer-container" style="background:#fff;">
	  <div class="responsive-container-block inner-container">
		<p class="text-blk section-head-text" style="color:#dd815e;">Meet Our Developers</p>
		<p class="text-blk section-subhead-text">The INET-READY team brings together expertise in project management, frontend, backend, QA, and research to deliver a safer travel experience.</p>
		<div class="responsive-container-block" style="justify-content:center; gap:2rem; flex-wrap:wrap;">
		  <!-- Alyssa Mae Abac -->
		  <div class="card dev-card">
			<div class="img-wrapper">
			  <svg width="100%" height="100%" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
				<circle cx="60" cy="60" r="60" fill="#f5f5f7"/>
				<text x="50%" y="54%" text-anchor="middle" fill="#bbb" font-size="38" font-family="Arial, sans-serif" dy=".3em">AM</text>
			  </svg>
			</div>
			<div class="card-content">
			  <p class="text-blk name" style="color:#dd815e;">Alyssa Mae Abac</p>
			  <p class="text-blk position" style="color:#dd815e;">Project Management, Public Relations, Documentation</p>
			  <p class="text-blk testimonial">Leads the project, manages communication, and keeps documentation organized.</p>
			</div>
		  </div>
		  <!-- Nicole Wyne Fernandez -->
		  <div class="card dev-card">
			<div class="img-wrapper">
			  <svg width="100%" height="100%" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
				<circle cx="60" cy="60" r="60" fill="#f5f5f7"/>
				<text x="50%" y="54%" text-anchor="middle" fill="#bbb" font-size="38" font-family="Arial, sans-serif" dy=".3em">NF</text>
			  </svg>
			</div>
			<div class="card-content">
			  <p class="text-blk name" style="color:#dd815e;">Nicole Wyne Fernandez</p>
			  <p class="text-blk position" style="color:#dd815e;">Frontend Development</p>
			  <p class="text-blk testimonial">Designs and builds user-friendly interfaces with intuitive navigation.</p>
			</div>
		  </div>
		  <!-- Brandon Miranda -->
		  <div class="card dev-card">
			<div class="img-wrapper">
			  <svg width="100%" height="100%" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
				<circle cx="60" cy="60" r="60" fill="#f5f5f7"/>
				<text x="50%" y="54%" text-anchor="middle" fill="#bbb" font-size="38" font-family="Arial, sans-serif" dy=".3em">BM</text>
			  </svg>
			</div>
			<div class="card-content">
			  <p class="text-blk name" style="color:#dd815e;">Brandon Miranda</p>
			  <p class="text-blk position" style="color:#dd815e;">Backend Development</p>
			  <p class="text-blk testimonial">Develops and optimizes backend systems, APIs, and databases.</p>
			</div>
		  </div>
		  <!-- Alexander Asinas -->
		  <div class="card dev-card">
			<div class="img-wrapper">
			  <svg width="100%" height="100%" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
				<circle cx="60" cy="60" r="60" fill="#f5f5f7"/>
				<text x="50%" y="54%" text-anchor="middle" fill="#bbb" font-size="38" font-family="Arial, sans-serif" dy=".3em">AA</text>
			  </svg>
			</div>
			<div class="card-content">
			  <p class="text-blk name" style="color:#dd815e;">Alexander Asinas</p>
			  <p class="text-blk position" style="color:#dd815e;">QA/QC, Research, System Analyst</p>
			  <p class="text-blk testimonial">Ensures quality, researches, and bridges business and technical needs.</p>
			</div>
		  </div>
		</div>
	  </div>
	</div>
	<style>
	  .responsive-container-block.outer-container { background: #fff; }
	  .section-head-text { color: #dd815e; font-size: 2.5rem; font-weight: 700; }
	  .section-subhead-text { color: #555; font-size: 1.1rem; margin-bottom: 2.5rem; }
	  .dev-card { width: 320px; min-width: 320px; max-width: 320px; min-height: 420px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(221,129,94,0.13); margin-bottom: 1.5rem; padding: 30px 25px 40px 25px; }
	  .name { color: #dd815e; font-size: 1.2rem; font-weight: 700; }
	  .position { color: #dd815e; font-weight: 600; }
	  .testimonial { color: #555; font-size: 1rem; }
	  .img-wrapper { width: 120px; height: 120px; margin: 0 auto 18px auto; border-radius: 50%; overflow: hidden; background: #f5f5f7; display: flex; align-items: center; justify-content: center; }
	  .img-wrapper svg { width: 100%; height: 100%; display: block; }
	  @media (max-width: 1200px) { .dev-card { width: 300px; min-width: 300px; max-width: 300px; } }
	  @media (max-width: 1024px) { .dev-card { width: 90vw; min-width: 260px; max-width: 340px; } }
	  @media (max-width: 500px) { .outer-container { padding: 0 10px; } .dev-card { width: 100%; min-width: 220px; max-width: 100%; } }
	</style>
  </section>

  <!-- ABOUT SECTION -->
  <section id="about" class="py-5">
	<div class="container">
	  <div class="row align-items-center flex-column-reverse flex-md-row">
		<div class="col-md-6 text-center text-md-start">
		  <h3 style="color:#dd815e; font-weight:700;">About INET-READY</h3>
		  <p style="font-size:1.1rem; color:#555;">INET-READY is a modern, privacy-focused platform for travelers. We combine real-time weather, health risk insights, and secure data management to help you travel smarter and safer—whether for business or leisure.</p>
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
  <footer id="contact" class="border-0 py-4 mt-5" style="background:#dd815e;">
	<div class="container">
	  <div class="row gy-4">
		<!-- Title Column -->
		<div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start">
		  <div class="d-flex align-items-center gap-2 mb-2 mb-md-0">
			<img src="/app-icon.png" alt="INET-READY" width="36" height="36" style="border-radius:8px; background:transparent;" />
			<span class="fw-bold align-items-center d-flex" style="color:#fff; font-size:1.6rem; height:45px; line-height:36px;">INET-READY</span>
		  </div>
		</div>
	<!-- Contact Column -->
	<div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start">
	  <div class="fw-bold mb-2" style="color:#fff;">Contact</div>
	  <div class="d-flex align-items-center mb-2" style="gap:0.5rem;">
		<i class="bi bi-github" style="color:#fff; font-size:1.3rem;"></i>
		<a href="https://github.com/bpmiranda3099/inet-ready-v2" target="_blank" rel="noopener" class="text-decoration-none" style="color:#fff;">GitHub</a>
	  </div>
	  <div class="d-flex align-items-center mb-2" style="gap:0.5rem;">
		<i class="bi bi-envelope-fill" style="color:#fff; font-size:1.3rem;"></i>
		<a href="mailto:info@inet-ready.com" class="text-decoration-none" style="color:#fff;">Email</a>
	  </div>
	  <div class="d-flex align-items-center mb-2" style="gap:0.5rem;">
		<i class="bi bi-phone" style="color:#fff; font-size:1.3rem;"></i>
		<a href="https://inet-ready-v2.vercel.app" target="_blank" rel="noopener" class="text-decoration-none" style="color:#fff;">App</a>
	  </div>
	</div>
		<!-- Support Column -->
		<div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start">
		  <div class="fw-bold mb-2" style="color:#fff;">Support</div>
		  <a href="/terms" class="text-decoration-none mb-1" style="color:#fff;">Terms</a>
		  <a href="/privacy" class="text-decoration-none mb-1" style="color:#fff;">Privacy</a>
		  <a href="/data-deletion" class="text-decoration-none mb-1" style="color:#fff;">Data Deletion</a>
		</div>
	<!-- Powered By Column -->
  <div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start">
	<div class="mb-2 fw-bold" style="color:#fff; letter-spacing:1px; font-size:1.1rem;">Powered by</div>
	<div class="d-flex flex-column align-items-start gap-2">
	  <div class="d-flex align-items-center" style="gap:0.5rem;">
		<img src="/open-meteo-icon.png" alt="OpenMeteo" class="tech-logo white-logo" style="border-radius:12px; background:transparent; width:24px; height:24px; object-fit:contain;" />
		<span style="color:#fff; font-size:1rem;">OpenMeteo</span>
	  </div>
	  <div class="d-flex align-items-center" style="gap:0.5rem;">
		<img src="/mapbox-icon.png" alt="Mapbox" class="tech-logo white-logo" style="border-radius:12px; background:transparent; width:24px; height:24px; object-fit:contain;" />
		<span style="color:#fff; font-size:1rem;">Mapbox</span>
	  </div>
	  <div class="d-flex align-items-center" style="gap:0.5rem;">
		<img src="/svelte-icon.png" alt="Svelte" class="tech-logo white-logo" style="border-radius:12px; background:transparent; width:24px; height:24px; object-fit:contain;" />
		<span style="color:#fff; font-size:1rem;">SvelteKit</span>
	  </div>
	  <div class="d-flex align-items-center" style="gap:0.5rem;">
		<img src="/firebase-icon.png" alt="Firebase" class="tech-logo white-logo" style="border-radius:12px; background:transparent; width:24px; height:24px; object-fit:contain;" />
		<span style="color:#fff; font-size:1rem;">Firebase</span>
	  </div>
	  <div class="d-flex align-items-center" style="gap:0.5rem;">
		<img src="/aptible-icon.png" alt="Aptible" class="tech-logo white-logo" style="border-radius:12px; background:transparent; width:24px; height:24px; object-fit:contain;" />
		<span style="color:#fff; font-size:1rem;">Aptible</span>
	  </div>
	</div>
  </div>
	  </div>
	  <hr style="border-color:rgba(255,255,255,0.2); margin:2rem 0 1rem 0;" />
	  <div class="text-center small" style="color:#fff;">© 2025 INET-READY. All rights reserved.</div>
	</div>
  </footer>
 </main>

  <style>
  .inet-orange {
	background: #dd815e !important;
	color: #fff !important;
	box-shadow: 0 2px 8px rgba(221,129,94,0.10);
  }
  .feature-card h5,
  .feature-card p {
	color: #fff !important;
  }
.tech-logo {
  height: 60px;
  width: auto;
  object-fit: contain;
}
.white-logo {
  filter: brightness(0) invert(1) !important;
}
.feature-icon-topright{
	font-size: 3rem;
	color: #fff;
}
</style>
