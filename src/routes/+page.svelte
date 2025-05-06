<script>
let cardContentHover = false;
let cardContentHover2 = false;
let cardContentHover3 = false;
let cardContentHover4 = false;
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

  <nav class="navbar navbar-expand-lg shadow-sm py-3 fixed-top" style="background:#dd815e; z-index:1050;">
	<div class="container-fluid">
	<a class="navbar-brand d-flex align-items-center gap-2" href="/" style="color:#fff;">
	  <img id="navbar-appicon" src="/app-icon.png" alt="INET-READY" width="36" height="36" style="border-radius:8px; transition:transform 0.3s cubic-bezier(0.4,0,0.2,1);" />
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
  /* Make navbar fixed and add body padding for content below */
  body {
	padding-top: 74px !important;
  }
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
	border-bottom: none;
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
<h1 class="hero-title-transform" style="color:#dd815e; font-size:2.7rem; font-weight:700;">
  Travel <span id="safer-smarter" class="safer-smarter">Safer.</span>
  <br> Your Heat-Health Companion
</h1>
<script>
  import { onMount } from 'svelte';
  let intervalId;
  let showingSmarter = false;
  onMount(() => {
	const el = document.getElementById('safer-smarter');
	if (!el) return;
	intervalId = setInterval(() => {
	  showingSmarter = !showingSmarter;
	  el.classList.add('fade-out');
	  setTimeout(() => {
		el.textContent = showingSmarter ? 'Smarter.' : 'Safer.';
		el.classList.remove('fade-out');
	  }, 400);
	}, 2200);
	return () => clearInterval(intervalId);
  });
// App icon scroll animation: clockwise on scroll down, counterclockwise on scroll up
let lastScrollY = 0;
let appIconRotation = 0;
onMount(() => {
  // Wait for DOM to be ready to ensure the app icon is present
  let rafId;
  function setupScrollHandler() {
	const appIcon = document.getElementById('navbar-appicon');
	if (!appIcon) {
	  rafId = requestAnimationFrame(setupScrollHandler);
	  return;
	}
	function handleScroll() {
	  const currentY = window.scrollY;
	  const delta = currentY - lastScrollY;
	  appIconRotation += delta * 0.6;
	  appIcon.style.transform = `rotate(${appIconRotation}deg)`;
	  lastScrollY = currentY;
	}
	window.addEventListener('scroll', handleScroll);
	// Clean up
	return () => {
	  window.removeEventListener('scroll', handleScroll);
	  if (rafId) cancelAnimationFrame(rafId);
	};
  }
  return setupScrollHandler();
});
</script>
<style>
  .hero-title-transform .safer-smarter {
	display: inline-block;
	transition: opacity 0.4s cubic-bezier(0.4,0,0.2,1);
  }
  .hero-title-transform .safer-smarter.fade-out {
	opacity: 0;
	transition: opacity 0.4s cubic-bezier(0.4,0,0.2,1);
  }
</style>
<p class="subtitle mb-4" style="font-size:1.25rem; color:#555; max-width:600px; margin:0 auto; font-family:'Segoe UI', Arial, sans-serif; line-height:1.5;">INET-READY keeps you safe and healthy on the go with real-time heat alerts, personalized health insights, and secure medical data—all in one easy-to-use platform.</p>
	  <button class="btn px-5 py-3 cta-button" style="background:#dd815e; color:#fff; border-radius:50px; font-weight:700; font-size:1.2rem;" on:click={navigateToApp}>Get Started</button>
	</div>
  </section>

  <!-- BENEFITS/FEATURES SECTION -->
  <section id="features" class="features py-5" style="background:#f5f5f7;">
  <div class="container">
  <h2 class="mb-4 text-center" style="color:#dd815e; font-weight:700; font-size:2.5rem;">How INET-READY Helps You</h2>
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
  <section style="background:#fff;">
	<div class="responsive-container-block outer-container" style="background:#fff;">
	  <div class="responsive-container-block inner-container">
		<p class="text-blk section-head-text" style="color:#dd815e;">Meet Our Developers</p>
		<p class="text-blk section-subhead-text">The INET-READY team brings together expertise in project management, frontend, backend, QA, and research to deliver a safer travel experience.</p>
		<div class="responsive-container-block" style="justify-content:center; gap:2rem; flex-wrap:wrap;">
		  <!-- Alyssa Mae Abac -->
		  <div class="card dev-card">
	  <div class="img-wrapper portrait-header">
		<img src="https://scontent.fmnl9-4.fna.fbcdn.net/v/t39.30808-1/495262217_3787895071428231_6510113284719315269_n.jpg?stp=cp6_dst-jpg_s200x200_tt6&_nc_cat=105&ccb=1-7&_nc_sid=1d2534&_nc_eui2=AeG8Km6yYzmTR-eYef0uKi_NwpI2en4CDivCkjZ6fgIOK90THDhrfB1cqcQgLxlxLd5W1BNj3sNFkYLKT-H3nbx8&_nc_ohc=ewMcjaW4PcoQ7kNvwHqSDjG&_nc_oc=AdnxAoZbNA6-Gx0bBL4YfKecD9Bo3UHWAKeN779qCiDUyazM1EOLptFenG7AGqdkds0&_nc_zt=24&_nc_ht=scontent.fmnl9-4.fna&_nc_gid=14i2lCz7n3wr0SheVfVz5Q&oh=00_AfLsbQ8ZrLrDilE-WP4EGNloBGSwph9NGOVzlkfj9k30AQ&oe=681FEA1B" alt="Alyssa Mae Abac" />
		<div class="vignette">
		  <div class="portrait-text">
			<span class="name">Alyssa Mae Abac</span>
		  </div>
		</div>
	  </div>
  <div class="card-content">
	<span class="position">Project Management, Public Relations, Documentation</span>
  </div>
		  </div>
		  <!-- Nicole Wyne Fernandez -->
		  <div class="card dev-card">
	  <div class="img-wrapper portrait-header">
		<img src="https://scontent.fmnl9-4.fna.fbcdn.net/v/t39.30808-1/343387404_534020152265878_7710459416092706346_n.jpg?stp=dst-jpg_s200x200_tt6&_nc_cat=105&ccb=1-7&_nc_sid=e99d92&_nc_eui2=AeGHReVsdDpVrzDuEALqsl3GDmtPlx8QAJMOa0-XHxAAk5ptVLRH1IJSzZl7L90-X8CpbimKEwgnga5o3WDmtAsX&_nc_ohc=eSoLWwaD-cEQ7kNvwF4Uqpz&_nc_oc=AdnGa6AlUfNxtxtBodPpW5LgXhPvdNVptUjF6MzdDXxGGwE_A97jMZ860T2_lREp_XM&_nc_zt=24&_nc_ht=scontent.fmnl9-4.fna&_nc_gid=Ox-UkQkT3nckhc85WaOaig&oh=00_AfKvBAV6Z-mqVKeyPy1OMKcIzqqFzCbhEXXEAM-TZ8KbSw&oe=68200EA2" alt="Nicole Wyne Fernandez" />
		<div class="vignette">
		  <div class="portrait-text">
			<span class="name">Nicole Wyne Fernandez</span>
		  </div>
		</div>
	  </div>
  <div class="card-content">
	<span class="position">Frontend Development</span>
  </div>
		  </div>
		  <!-- Brandon Miranda -->
		  <div class="card dev-card">
	  <div class="img-wrapper portrait-header">
		<img src="https://scontent.fmnl9-2.fna.fbcdn.net/v/t39.30808-6/316940975_6344569778905754_4439269053930394859_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeG6qP_3LvpoeIoYqIP4EVasalvDEyl0enRqW8MTKXR6dJjX2pD9M320EZlcSminQeVGK1R1MoysNVrUNRU-eFSq&_nc_ohc=1CQxN8M3wMoQ7kNvwGkEVyb&_nc_oc=Adm_vwz2RbsGISielkR3eMaKbDEWw-CDlHI9P3Xx12jzHxHUl1IhDb-pUiz9recTSjs&_nc_zt=23&_nc_ht=scontent.fmnl9-2.fna&_nc_gid=7ClNm47ZT_PpzEgB2iXAdA&oh=00_AfLdpyxMYErRuIzqIa6dDHJzp8vObfhAKLlqKlbjl5dltQ&oe=682004B8" alt="Brandon Miranda" />
		<div class="vignette">
		  <div class="portrait-text">
			<span class="name">Brandon Miranda</span>
		  </div>
		</div>
	  </div>
  <div class="card-content">
	<span class="position">Backend Development</span>
  </div>
		  </div>
		  <!-- Alexander Asinas -->
		  <div class="card dev-card">
	  <div class="img-wrapper portrait-header">
		<img src="https://scontent.fmnl9-6.fna.fbcdn.net/v/t39.30808-6/349663129_1607290049762067_877432076550208488_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeHzWneW3mDNJWjQM6Ehjp2efgywZQhDLah-DLBlCEMtqB6fvWBJVzwRR4BfTXbU-f7kbnUOoZnnEXqTXxuvHC7A&_nc_ohc=n3Try9-fbokQ7kNvwHFbxGk&_nc_oc=AdlKdPRhwW66n6jT5ZJ2nmHyJYMzqoRCs0pjLUi8ky3Fa0cjwckWYGzPgV2yopcb5Mk&_nc_zt=23&_nc_ht=scontent.fmnl9-6.fna&_nc_gid=fIPMYiL-XtJuzPJaOynQoQ&oh=00_AfKoJuyJKwn5lxaPbbG9Nm42WOU7EzeCZVJdg38PxAwuGw&oe=68200068" alt="Alexander Asinas" />
		<div class="vignette">
		  <div class="portrait-text">
			<span class="name">Alexander Asinas</span>
		  </div>
		</div>
	  </div>
  <div class="card-content">
	<span class="position">QA/QC, Research, System Analyst</span>
  </div>
		  </div>
		</div>
	  </div>
	</div>
	<style>
	  .responsive-container-block.outer-container { background: #fff; }
	  .section-head-text { color: #dd815e; font-size: 2.5rem; font-weight: 700; }
	  .section-subhead-text { color: #555; font-size: 1.1rem; margin-bottom: 2.5rem; }
  .dev-card {
	width: 100%;
	min-width: 220px;
	max-width: 320px;
	min-height: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: flex-start;
	background: #dd815e;
	border-radius: 16px;
	box-shadow: 0 4px 24px rgba(221,129,94,0.13);
	margin-bottom: 1.5rem;
	padding: 0;
	text-align: center;
	color: #fff;
	overflow: hidden;
	border: none;
  }
  .card-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: auto;
	padding: 10px 0 10px 0;
	min-height: 0;
  }
  .name {
	color: #dd815e;
	font-size: 2.1rem;
	font-weight: 800;
	margin: 10px 0 4px 0;
	text-align: center;
	line-height: 1.1;
	letter-spacing: 0.01em;
  }
  .position {
	color: #fff;
	font-weight: 600;
	font-size: 1.08rem;
	margin-bottom: 8px;
	text-align: center;
	display: block;
	transition: opacity 0.2s;
  }

  .img-wrapper.portrait-header {
	width: 100%;
	aspect-ratio: 1.6/1;
	min-height: 0;
	height: auto;
	margin: 0;
	border-radius: 0;
	overflow: hidden;
	background: #f5f5f7;
	position: relative;
	display: flex;
	align-items: flex-end;
	justify-content: center;
	box-shadow: none;
	max-width: 100%;
  }
  .img-wrapper.portrait-header img {
	width: 100%;
	height: 100%;
	min-height: 180px;
	max-height: 260px;
	object-fit: cover;
	display: block;
	position: relative;
	left: 0;
	top: 0;
	z-index: 1;
	border-radius: 0;
  }
  .vignette {
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	height: 65%;
	z-index: 2;
	background: linear-gradient(
	  to top,
	  rgba(0,0,0,0.68) 0%,
	  rgba(0,0,0,0.38) 40%,
	  rgba(0,0,0,0.10) 85%,
	  rgba(0,0,0,0.00) 100%
	);
	display: flex;
	align-items: flex-end;
	justify-content: center;
	border-radius: 0;
	pointer-events: none;
  }
  .portrait-text {
	width: 100%;
	padding: 18px 0 12px 0;
	text-align: center;
	color: #fff;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: flex-end;
	gap: 2px;
	font-family: inherit;
	font-weight: 600;
	font-size: 1.08rem;
	letter-spacing: 0.01em;
	pointer-events: none;
  }
  .portrait-text .name {
	font-size: 2.1rem;
	font-weight: 800;
	color: #fff;
	margin-bottom: 2px;
	text-shadow: 0 2px 8px rgba(0,0,0,0.18);
	line-height: 1.1;
	letter-spacing: 0.01em;
  }
  .portrait-text .position {
	font-size: 1.01rem;
	font-weight: 500;
	color: #fff;
	opacity: 0.93;
	text-shadow: 0 2px 8px rgba(0,0,0,0.18);
  }
	@media (max-width: 1200px) { .dev-card { width: 90vw; min-width: 260px; max-width: 340px; } }
	@media (max-width: 500px) { .outer-container { padding: 2rem; } .dev-card { width: 100%; min-width: 220px; max-width: 100%; } }
	</style>
  </section>

  <!-- ABOUT SECTION -->
  <section id="about" class="py-5" style="background:#dd815e; color:#fff;">
   <div class="container">
	 <div class="row align-items-center flex-column-reverse flex-md-row">
	   <div class="col-md-6 text-center text-md-start">
		 <h3 style="color:#fff; font-weight:700; font-size:1.7rem;">About INET-READY</h3>
		 <p style="font-size:1.1rem; color:#fff;">INET-READY is a modern, privacy-focused platform for travelers. We combine real-time weather, health risk insights, and secure data management to help you travel smarter and safer—whether for business or leisure.</p>
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
			<span class="fw-bold align-items-center d-flex footer-title" style="color:#fff; font-size:1.6rem; height:45px; line-height:36px;">INET-READY</span>
		  </div>
		</div>
	<!-- Contact Column -->
	<div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start footer-col-uniform">
	  <div class="fw-bold mb-2 footer-uniform-text" style="color:#fff;">Contact</div>
	  <div class="d-flex align-items-center mb-2 footer-uniform-text" style="gap:0.5rem;">
		<i class="bi bi-github" style="color:#fff; font-size:1.3rem;"></i>
		<a href="https://github.com/bpmiranda3099/inet-ready-v2" target="_blank" rel="noopener" class="text-decoration-none" style="color:#fff;">GitHub</a>
	  </div>
	  <div class="d-flex align-items-center mb-2 footer-uniform-text" style="gap:0.5rem;">
		<i class="bi bi-envelope-fill" style="color:#fff; font-size:1.3rem;"></i>
		<a href="mailto:info@inet-ready.com" class="text-decoration-none" style="color:#fff;">Email</a>
	  </div>
	  <div class="d-flex align-items-center mb-2 footer-uniform-text" style="gap:0.5rem;">
		<i class="bi bi-phone" style="color:#fff; font-size:1.3rem;"></i>
		<a href="https://inet-ready-v2.vercel.app" target="_blank" rel="noopener" class="text-decoration-none" style="color:#fff;">App</a>
	  </div>
	</div>
		<!-- Support Column -->
		<div class="col-12 col-md-3 text-center text-md-start mb-3 mb-md-0 d-flex flex-column align-items-center align-items-md-start footer-col-uniform">
		  <div class="fw-bold mb-2 footer-uniform-text" style="color:#fff;">Support</div>
		  <a href="/terms" class="text-decoration-none mb-1 footer-uniform-text" style="color:#fff;">Terms</a>
		  <a href="/privacy" class="text-decoration-none mb-1 footer-uniform-text" style="color:#fff;">Privacy</a>
		  <a href="/data-deletion" class="text-decoration-none mb-1 footer-uniform-text" style="color:#fff;">Data Deletion</a>
		</div>
	  </div>
  <hr style="border-color:rgba(255,255,255,0.2); margin:2rem 0 1rem 0;" />
  <div class="text-center small footer-copyright" style="color:#fff; font-size:0.98rem;">© 2025 INET-READY. All rights reserved.</div>
	</div>
  </footer>
 </main>

  <style>
  /* Footer uniform font size for all except INET-READY title and copyright */
  /* Powered by row responsive styles */
  @media (max-width: 600px) {
	.footer-poweredby-row {
	  flex-direction: row !important;
	  flex-wrap: wrap;
	  justify-content: center !important;
	  align-items: center !important;
	  gap: 0 !important;
	  width: 100%;
	  margin: 0 auto;
	}
	.poweredby-col {
	  flex: 1 1 33%;
	  min-width: 0;
	  max-width: 33%;
	  justify-content: center !important;
	  align-items: center !important;
	  display: flex !important;
	  margin-bottom: 0.2rem;
	  margin-top: 0.2rem;
	  padding: 0 2px;
	}
	.poweredby-label {
	  font-size: 0.82rem !important;
	  white-space: nowrap;
	}
	.powered-by-label {
	  font-size: 0.92rem !important;
	}
	.footer-col-uniform .footer-uniform-text img.tech-logo {
	  width: 20px !important;
	  height: 20px !important;
	}
  }
  .footer-col-uniform .footer-uniform-text,
  .footer-col-uniform .footer-uniform-text a,
  .footer-col-uniform .footer-uniform-text span {
	font-size: 1rem !important;
	font-weight: 400 !important;
	line-height: 1.5 !important;
  }
  .footer-col-uniform .fw-bold.footer-uniform-text {
	font-weight: 600 !important;
  }
  .footer-col-uniform .footer-uniform-text {
	margin-bottom: 0.35rem;
  }
  .footer-col-uniform .footer-uniform-text[style*="font-size"] {
	font-size: 1rem !important;
  }
  /* Keep INET-READY title and copyright distinct */
  .footer-title {
	font-size: 1.6rem !important;
	font-weight: 700 !important;
  }
  .footer-copyright {
	font-size: 0.98rem !important;
  }
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
