<script>
	import { onMount } from 'svelte';
	import { logoutUser, onMessageListener, requestFCMToken } from '$lib/firebase';
	import { getCurrentPosition, currentLocation } from '$lib/services/location-service';
	import {
		getLocationNameFromCoordinates,
		locationName,
		geocodingLoading,
		geocodingError
	} from '$lib/services/geocoding-service';
	import {
		registerServiceWorker,
		serviceWorkerSupported,
		serviceWorkerRegistered,
		serviceWorkerError
	} from '../lib/services/service-worker';
	import { getUserCityPreferences } from '$lib/services/user-preferences-service';
	import {
		getNotificationHistory,
		markNotificationAsRead,
		clearNotificationHistory,
		showNotification
	} from '$lib/services/notification-service';
	import {
		hasMedicalRecord,
		getMedicalData,
		deleteMedicalData
	} from '$lib/services/medical-api.js';
	import { syncCityInsightsToDashboard } from '$lib/services/city-insight-sync';
	import {
		saveDashboardCache,
		loadDashboardCache,
		clearDashboardCache
	} from '$lib/services/dashboard-cache';
	import { signInWithGoogle, signInWithFacebook } from '$lib/firebase/auth';
	import { setupTokenRefreshService } from '$lib/services/token-refresh.js';

	onMount(() => {
		setupTokenRefreshService();
	});

	// Components
	import MedicalProfile from './medicalprofile.svelte';
	import MedicalForm from './medicalform.svelte';
	import PermissionsPanel from './permissions-panel.svelte';
	import CityPreferences from './city-preferences.svelte';
	import CityPreferencesSetup from './city-preferences-setup.svelte';
	import TravelHealthCards from './travel-health-cards.svelte';

	export let user; // State variables
	let notifications = [];
	let loading = false;
	let showMedicalForm = false;
	let medicalRecordExists = false;
	let medicalData = null; // Add state variable for medical data
	let loadingMedicalData = false; // Track loading state for medical data
	let activeTab = 'dashboard'; // Changed default to dashboard
	let showWelcomeMessage = true; // Control whether to show welcome message on startup
	let showAds = true; // Control whether to show ads
	let unreadNotifications = 0;
	let deletingMedicalData = false;
	let deleteError = null;
	let showDeleteConfirm = false;
	let deleteSuccess = false;
	let dashboardRefreshKey = 0;

	// City preferences state
	let hasCityPreferences = false;
	let showCityPreferencesSetup = false;
	let checkingCityPreferences = true;
	let homeCity = '';
	let preferredCities = [];
	let loadingCities = false;
	let lastUpdated = null;

	// Permission states
	let notificationPermission = null;
	let locationPermission = null;
	let showPermissionsPanel = false;
	let fcmToken = null;

	// Location state
	let locationData = null;
	let locationError = null;
	let fetchingLocation = false;
	let currentLocationName = null;
	let fetchingLocationName = false;
	let locationNameError = null;

	// Service Worker state
	let swSupported;
	let swRegistered;
	let swError;

	// Subscribe to service worker states
	const unsubscribeSW1 = serviceWorkerSupported.subscribe((value) => (swSupported = value));
	const unsubscribeSW2 = serviceWorkerRegistered.subscribe((value) => (swRegistered = value));
	const unsubscribeSW3 = serviceWorkerError.subscribe((value) => (swError = value));

	// Subscribe to location updates
	const unsubscribeLocation = currentLocation.subscribe((value) => {
		if (value) {
			locationData = value;
			// Get the location name when coordinates change
			getLocationNameFromCoordinates(value.latitude, value.longitude);
		}
	});

	// Subscribe to location name updates
	const unsubscribeLocationName = locationName.subscribe((value) => {
		currentLocationName = value;
	});

	// Subscribe to geocoding loading state
	const unsubscribeGeocodingLoading = geocodingLoading.subscribe((value) => {
		fetchingLocationName = value;
	});

	// Subscribe to geocoding error state
	const unsubscribeGeocodingError = geocodingError.subscribe((value) => {
		locationNameError = value;
	});

	let unsubscribeMessages;
	onMount(() => {
		// Try to load cached dashboard state
		const cached = loadDashboardCache();
		if (cached) {
			homeCity = cached.homeCity || '';
			preferredCities = cached.preferredCities || [];
			notifications = cached.notifications || [];
			lastUpdated = cached.lastUpdated || null;
			if (cached.showAds !== undefined) {
				showAds = cached.showAds;
			}
		}
		// Check if welcome message is disabled in local storage
		const hideWelcome = localStorage.getItem('inet-ready-hide-welcome');
		if (hideWelcome === 'true') {
			showWelcomeMessage = false;
		}

		// Check if ads are disabled in local storage
		const hideAds = localStorage.getItem('inet-ready-hide-ads');
		if (hideAds === 'true') {
			showAds = false;
		}

		// Load notifications from localStorage
		notifications = getNotificationHistory();
		unreadNotifications = notifications.filter((n) => !n.read).length;

		(async () => {
			// Check existing permissions
			notificationPermission = Notification.permission;

			// Check for geolocation permission state
			if ('permissions' in navigator) {
				try {
					const status = await navigator.permissions.query({ name: 'geolocation' });
					locationPermission = status.state;
					// Listen for changes to permission state
					status.onchange = () => {
						locationPermission = status.state;
					};

					// If location permission is granted, get current position
					if (locationPermission === 'granted') {
						getLocation();
					}
				} catch (error) {
					console.error('Error checking geolocation permission:', error);
				}
			}

			// Register service worker if not already registered
			if (!swRegistered) {
				try {
					await registerServiceWorker();
					console.log('Service worker registration status:', swRegistered);
				} catch (error) {
					console.error('Error registering service worker:', error);
				}
			}

			// Check if user has city preferences
			try {
				const cityPreferences = await getUserCityPreferences(user.uid);
				if (cityPreferences && cityPreferences.homeCity) {
					hasCityPreferences = true;
					homeCity = cityPreferences.homeCity;

					// Ensure preferredCities is an array of strings
					if (Array.isArray(cityPreferences.preferredCities)) {
						preferredCities = cityPreferences.preferredCities
							.map((city) =>
								typeof city === 'object' && city !== null && city.city
									? city.city
									: typeof city === 'string'
										? city
										: ''
							)
							.filter((city) => city !== ''); // Remove any empty items
					}

					console.log('Loaded preferences:', { homeCity, preferredCities });
				} else {
					hasCityPreferences = false;
				}

				// Show city preferences setup if user doesn't have them yet
				// But only after permissions panel is handled
				showCityPreferencesSetup = !hasCityPreferences;
			} catch (error) {
				console.error('Error checking city preferences:', error);
			} finally {
				checkingCityPreferences = false;
			}

			// Determine if we should show the permissions panel
			showPermissionsPanel =
				notificationPermission !== 'granted' || locationPermission !== 'granted';

			// If notifications already granted, get FCM token
			if (notificationPermission === 'granted') {
				fcmToken = await requestFCMToken();
				if (fcmToken) {
					// Here you would typically save the token to the user's profile
					console.log('FCM token available:', fcmToken);
				}
			}

			// Subscribe to foreground messages and store them in dashboard notification history
			unsubscribeMessages = onMessageListener((payload) => {
				const notification = payload.notification || {};
				const data = payload.data || {};
				const title = notification.title || data.title || 'INET-READY Alert';
				const message = notification.body || data.body || 'You have a new alert.';
				const type = data.type || 'info';
				showNotification(message, type, 0, title);
			});

			// Check if user has medical record
			medicalRecordExists = await hasMedicalRecord();

			// After loading city preferences, sync city insights to dashboard
			if (hasCityPreferences && homeCity) {
				await syncCityInsightsToDashboard(homeCity);
			}
		})();
		let unsubscribeMessages = onMessageListener();
		return () => {
			if (unsubscribeMessages) unsubscribeMessages();
			unsubscribeLocation();
			unsubscribeSW1();
			unsubscribeSW2();
			unsubscribeSW3();
			unsubscribeLocationName();
			unsubscribeGeocodingLoading();
			unsubscribeGeocodingError();
		};
	});
	// Save dashboard cache whenever relevant data changes
	$: saveDashboardCache({
		homeCity,
		preferredCities,
		notifications,
		lastUpdated,
		showAds
	});

	function handleCityPreferencesComplete() {
		showCityPreferencesSetup = false;
		hasCityPreferences = true;
	}

	async function getLocation() {
		fetchingLocation = true;
		locationError = null;

		try {
			locationData = await getCurrentPosition();

			// Get the location name after getting coordinates
			if (locationData) {
				await getLocationNameFromCoordinates(locationData.latitude, locationData.longitude);
			}
		} catch (error) {
			console.error('Error fetching location:', error);
			locationError = error.message || 'Could not retrieve your location';
		} finally {
			fetchingLocation = false;
		}
	}

	async function handleLogout() {
		loading = true;
		try {
			clearDashboardCache();
			await logoutUser();
		} catch (err) {
			console.error('Logout error:', err);
		} finally {
			loading = false;
		}
	}

	function handleMedicalFormCompleted() {
		showMedicalForm = false;
		medicalRecordExists = true;
	} // Function to load user's medical data and open the form
	async function openMedicalForm() {
		loadingMedicalData = true;
		try {
			const data = await getMedicalData();
			if (data) {
				// Ensure all required nested objects exist in the data
				if (!data.fluid_intake) {
					data.fluid_intake = {};
				}
				if (!data.fluid_intake.other) {
					data.fluid_intake.other = { has_other: false, name: '', cups: 0 };
				}
				if (!data.medical_conditions) {
					data.medical_conditions = {};
				}
				if (!data.medical_conditions.other) {
					data.medical_conditions.other = { has_other: false, description: '' };
				}
				if (!data.medications) {
					data.medications = {};
				}
				if (!data.medications.other) {
					data.medications.other = { has_other: false, description: '' };
				}

				// Convert fluid intake amounts from ml (in DB) to cups (for form)
				// The standard ML_PER_CUP value used in the form
				const ML_PER_CUP = 237;

				// Process standard drink types
				const drinkTypes = [
					'water',
					'electrolyte_drinks',
					'coconut_water',
					'fruit_juice',
					'iced_tea',
					'soda',
					'milk_tea',
					'coffee',
					'herbal_tea'
				];

				// Convert ml values to cups for form display
				for (const drinkType of drinkTypes) {
					const dbField = drinkType + '_amount'; // Field in database (e.g., water_amount)
					const formField = drinkType + '_cups'; // Field expected by form (e.g., water_cups)

					// If the DB field exists, convert to cups
					if (data.fluid_intake[dbField] !== undefined) {
						data.fluid_intake[formField] =
							Math.round((data.fluid_intake[dbField] / ML_PER_CUP) * 10) / 10;
					} else {
						// Ensure the form field exists with default value
						data.fluid_intake[formField] = 0;
					}
				}

				// Process "other" fluid if it exists
				if (data.fluid_intake.other_fluid && data.fluid_intake.other_fluid_amount) {
					data.fluid_intake.other = {
						has_other: true,
						name: data.fluid_intake.other_fluid,
						cups: Math.round((data.fluid_intake.other_fluid_amount / ML_PER_CUP) * 10) / 10
					};
				}

				// Fix activity_duration if it's a string format
				if (data.activity && typeof data.activity.activity_duration === 'string') {
					// Convert string format from database to the object format expected by the form
					let durationValue = 30; // Default to 30 minutes

					switch (data.activity.activity_duration) {
						case 'less_than_30_mins':
							durationValue = 20;
							break;
						case '30_to_60_mins':
							durationValue = 45;
							break;
						case '1_to_2_hours':
							durationValue = 90;
							break;
						case 'more_than_2_hours':
							durationValue = 150;
							break;
					}

					// Replace the string with an object having value and unit properties
					data.activity.activity_duration = {
						value: durationValue,
						unit: 'minutes'
					};
				}

				medicalData = data;
				showMedicalForm = true;
			} else {
				medicalData = null;
				showMedicalForm = true;
			}
		} catch (err) {
			console.error('Error loading medical data:', err);
			medicalData = null;
			showMedicalForm = true;
		} finally {
			loadingMedicalData = false;
		}
	}

	async function requestNotificationPermission() {
		try {
			const permission = await Notification.requestPermission();
			notificationPermission = permission;

			if (permission === 'granted') {
				// Ensure service worker is registered before requesting FCM token
				if (!swRegistered) {
					await registerServiceWorker();
				}

				fcmToken = await requestFCMToken();
				if (fcmToken) {
					// Save FCM token to user profile
					console.log('FCM token received:', fcmToken);
					// Implementation to save token to user profile would go here
				}
			}
		} catch (error) {
			console.error('Error requesting notification permission:', error);
		}

		// Update permissions panel visibility
		showPermissionsPanel = notificationPermission !== 'granted' || locationPermission !== 'granted';
	}

	function requestLocationPermission() {
		if ('geolocation' in navigator) {
			navigator.geolocation.getCurrentPosition(
				(position) => {
					console.log('Latitude:', position.coords.latitude);
					console.log('Longitude:', position.coords.longitude);

					// Update location data
					locationData = {
						latitude: position.coords.latitude,
						longitude: position.coords.longitude,
						accuracy: position.coords.accuracy,
						timestamp: new Date().toISOString()
					};

					// Update permission state
					navigator.permissions.query({ name: 'geolocation' }).then((status) => {
						locationPermission = status.state;

						// Update permissions panel visibility
						showPermissionsPanel =
							notificationPermission !== 'granted' || locationPermission !== 'granted';
					});

					// Here you would store the location information
					// Implementation to save location to user profile would go here
				},
				(error) => {
					console.error('Error getting location:', error);
					locationError = error.message || 'Could not retrieve your location';
				},
				{ enableHighAccuracy: true }
			);
		} else {
			console.log('Geolocation is not supported by this browser.');
		}
	}

	function handlePermissionsComplete() {
		showPermissionsPanel = false;
	}

	// Function to toggle welcome message visibility preference
	function toggleWelcomeMessage() {
		showWelcomeMessage = !showWelcomeMessage;
		localStorage.setItem('inet-ready-hide-welcome', showWelcomeMessage ? 'false' : 'true');
	}

	// Function to toggle ads visibility preference
	function toggleAdsVisibility() {
		showAds = !showAds;
		localStorage.setItem('inet-ready-hide-ads', showAds ? 'false' : 'true');
	}

	// Function to refresh the city list data
	async function refreshCityList() {
		loadingCities = true;

		try {
			// Import the function directly where we need it
			const { fetchLatestWeatherData } = await import('$lib/services/weather-data-service');
			const result = await fetchLatestWeatherData();
			lastUpdated = result.lastUpdated;
		} catch (err) {
			console.error('Error refreshing city list:', err);
		} finally {
			loadingCities = false;
		}
	} // Function to get the section title based on active tab
	function getSectionTitle(tab) {
		switch (tab) {
			case 'dashboard':
				return 'Dashboard';
			case 'notifications':
				return 'Notifications';
			case 'account':
				return 'Account';
			case 'medical':
				return 'Medical Profile';
			case 'settings':
				return 'Settings';
			default:
				return 'Dashboard';
		}
	}

	// Function to get the icon for a notification type
	function getNotificationIcon(type) {
		switch (type) {
			case 'success':
				return 'bi-check-circle-fill';
			case 'warning':
				return 'bi-exclamation-triangle-fill';
			case 'error':
				return 'bi-exclamation-circle-fill';
			case 'info':
				return 'bi-info-circle-fill';
			default:
				return 'bi-bell-fill';
		}
	}

	// New function to categorize notifications
	function categorizeNotifications(notifications) {
		const categories = {
			system: {
				name: 'System Notifications',
				description: 'App updates, version changes, policy updates, feature introductions',
				icon: 'bi-gear-fill',
				color: '#3498db', // Blue
				notifications: []
			},
			emergency: {
				name: 'Emergency Notifications',
				description: 'Heat index fluctuations and other urgent alerts',
				icon: 'bi-exclamation-triangle-fill',
				color: '#e74c3c', // Red
				notifications: []
			},
			reminder: {
				name: 'Reminder Notifications',
				description: 'Regular reminders and checkup notifications',
				icon: 'bi-clock-fill',
				color: '#f39c12', // Amber
				notifications: []
			},
			settings: {
				name: 'Settings Notifications',
				description: 'Changes to your preferences and settings',
				icon: 'bi-sliders',
				color: '#2ecc71', // Green
				notifications: []
			}
		};

		// Loop through notifications and categorize them
		notifications.forEach((notification) => {
			// Categorize by keywords in notification title and message
			let category = 'system'; // Default category

			const text = (notification.title + ' ' + notification.message).toLowerCase();

			if (
				text.includes('heat index') ||
				text.includes('emergency') ||
				text.includes('urgent') ||
				text.includes('alert') ||
				text.includes('warning')
			) {
				category = 'emergency';
			} else if (
				text.includes('remind') ||
				text.includes("don't forget") ||
				text.includes('scheduled')
			) {
				category = 'reminder';
			} else if (
				text.includes('setting') ||
				text.includes('preference') ||
				text.includes('profile') ||
				text.includes('account')
			) {
				category = 'settings';
			} else if (
				text.includes('update') ||
				text.includes('version') ||
				text.includes('new feature') ||
				text.includes('policy') ||
				text.includes('terms')
			) {
				category = 'system';
			}

			// Add to appropriate category
			categories[category].notifications.push(notification);
		});

		return categories;
	}

	// Get categorized notifications
	$: categorizedNotifications = categorizeNotifications(notifications);

	// Add this function to handle delete
	async function handleDeleteMedicalData() {
		deleteError = null;
		deletingMedicalData = true;
		try {
			await deleteMedicalData();
			deleteSuccess = true;
			medicalRecordExists = false;
			showDeleteConfirm = false;
			// Reload the page after a short delay to show the success message
			setTimeout(() => {
				location.reload();
			}, 2500);
		} catch (err) {
			deleteError = err?.message || 'Failed to delete medical data.';
		} finally {
			deletingMedicalData = false;
		}
	}

	async function handleLinkGoogle() {
		try {
			const { user: authUser, error } = await signInWithGoogle();
			if (error) {
				showNotification(error.message || 'Failed to link Google account', 'error');
			} else {
				showNotification('Successfully linked Google account', 'success');
			}
		} catch (err) {
			showNotification('Failed to link Google account', 'error');
		}
	}

	async function handleLinkFacebook() {
		try {
			const { user: authUser, error } = await signInWithFacebook();
			if (error) {
				showNotification(error.message || 'Failed to link Facebook account', 'error');
			} else {
				showNotification('Successfully linked Facebook account', 'success');
			}
		} catch (err) {
			showNotification('Failed to link Facebook account', 'error');
		}
	}

	function redactEmail(email) {
		if (!email) return '';
		const [name, domain] = email.split('@');
		if (name.length <= 2) {
			return name[0] + '***@' + domain;
		}
		return name[0] + '***' + name[name.length - 1] + '@' + domain;
	}

	function redactUid(uid) {
		if (!uid) return '';
		if (uid.length <= 4) return uid[0] + '***' + uid[uid.length - 1];
		return uid.slice(0, 2) + '***' + uid.slice(-2);
	}

	let logoRotating = false;
	let previousTab = activeTab;

	$: if (activeTab !== previousTab) {
		previousTab = activeTab;
		logoRotating = true;
		setTimeout(() => (logoRotating = false), 600); // match animation duration
	}
</script>

<div class="dashboard {showAds ? 'show-ads' : ''}">
	<!-- AdSense Banner -->
	{#if showAds}
		<div class="ad-container">
			<script
				async
				src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5128336241212748"
				crossorigin="anonymous"
			>
			</script>
			<ins
				class="adsbygoogle"
				style="display:block"
				data-ad-format="autorelaxed"
				data-ad-client="ca-pub-5128336241212748"
				data-ad-slot="7178650811"
			>
			</ins>
			<script>
				(adsbygoogle = window.adsbygoogle || []).push({});
			</script>
		</div>
	{/if}
	<!-- App Bar -->
	<div class="app-bar">
		<div class="app-bar-content">
			<div class="app-bar-main">
				<img
					src="/app-icon.png"
					alt="INET-READY"
					class="app-logo {logoRotating ? 'rotating' : ''}"
					on:animationend={() => (logoRotating = false)}
				/>
				<div class="app-titles">
					<small class="app-title">INET-READY</small>
					<h2 class="section-title">
						{activeTab === 'medical' && showMedicalForm
							? 'Update Medical Profile'
							: getSectionTitle(activeTab)}
					</h2>
				</div>
			</div>
		</div>
		<!-- Edit Medical Profile Button (only shows when on medical tab and not already editing) -->
		{#if activeTab === 'medical' && !showMedicalForm}
			<button class="edit-icon-btn" on:click={openMedicalForm} aria-label="Edit medical profile">
				<i class="bi bi-pencil-square"></i>
			</button>
		{/if}
		<!-- Logout Button (only shows when on account tab) -->
		{#if activeTab === 'account'}
			<button class="edit-icon-btn" on:click={handleLogout} aria-label="Logout" disabled={loading}>
				<i class="bi bi-box-arrow-right"></i>
			</button>
		{/if}
		<!-- Clear All Notifications Button (only shows when on notifications tab and notifications exist) -->
		{#if activeTab === 'notifications' && notifications.length > 0}
			<button
				class="edit-icon-btn"
				on:click={() => {
					clearNotificationHistory();
					notifications = [];
					unreadNotifications = 0;
				}}
				aria-label="Clear all notifications"
			>
				<i class="bi bi-trash"></i>
			</button>
		{/if}
	</div>

	<!-- Permissions Panel -->
	{#if showPermissionsPanel}
		<PermissionsPanel
			{notificationPermission}
			{locationPermission}
			onRequestNotification={requestNotificationPermission}
			onRequestLocation={requestLocationPermission}
			onComplete={handlePermissionsComplete}
		/>
	{/if}

	<!-- City Preferences Setup -->
	{#if !showPermissionsPanel && showCityPreferencesSetup && !checkingCityPreferences}
		<CityPreferencesSetup userId={user?.uid} onComplete={handleCityPreferencesComplete} />
	{/if}

	<!-- Service Worker Status (for debugging, can be removed in production) -->
	{#if swError}
		<div class="sw-error">
			<p>⚠️ Service Worker Error: {swError}</p>
		</div>
	{/if}

	<!-- Main Content Area -->
	<div class="content-area">
		{#if activeTab === 'dashboard'}
			{#key dashboardRefreshKey}
				<div class="dashboard-section">
					<!-- Travel Health Cards - Only show if user has city preferences -->
					{#if hasCityPreferences && preferredCities.length > 0}
						<TravelHealthCards
							{homeCity}
							{preferredCities}
							useCurrentLocation={true}
							currentLocation={currentLocationName}
						/>
					{/if}
				</div>
			{/key}
		{:else if activeTab === 'notifications'}
			<div class="notifications-section">
				{#if notifications.length === 0}
					<div class="card">
						<div class="empty-state">
							<div class="empty-icon"><i class="bi bi-bell"></i></div>
							<p class="empty-hint">Notifications will appear here when we have updates for you</p>
						</div>
					</div>
				{:else}
					<!-- Categorized Notification Sections -->
					{#each Object.keys(categorizedNotifications) as categoryKey}
						{@const category = categorizedNotifications[categoryKey]}
						{#if category.notifications.length > 0}
							<div class="section-container notification-category">
								<div
									class="section-header"
									style="background-color: {category.color}; color: white; margin-bottom: 8px;"
								>
									<h3>
										<i class="bi {category.icon}"></i>
										{category.name}
									</h3>
									<div
										class="category-count"
										style="background-color: rgba(255, 255, 255, 0.3); color: white;"
									>
										<span>{category.notifications.length}</span>
									</div>
								</div>
								<div class="section-body">
									<div class="condition-cards notifications-list">
										{#each category.notifications as notification}
											<!-- svelte-ignore a11y-click-events-have-key-events -->
											<div
												class="notification-card {notification.read ? 'read' : 'unread'}"
												style="border-left: 4px solid {category.color};"
												on:click={() => {
													if (!notification.read) {
														markNotificationAsRead(notification.id);
														notification.read = true;
														unreadNotifications = Math.max(0, unreadNotifications - 1);
														notifications = notifications; // trigger reactivity
													}
												}}
											>
												<div class="notification-icon" style="color: {category.color};">
													<i class="bi {getNotificationIcon(notification.type)}"></i>
													{#if !notification.read}
														<div class="unread-indicator"></div>
													{/if}
												</div>
												<div class="notification-content">
													<h4 class="notification-title">{notification.title || 'Notification'}</h4>
													<p class="notification-message">{notification.message}</p>
													<small class="notification-time"
														>{new Date(notification.timestamp).toLocaleString()}</small
													>
												</div>
											</div>
										{/each}
									</div>
								</div>
							</div>
						{/if}
					{/each}
				{/if}
			</div>{:else if activeTab === 'account'}
			<div class="account-section">
				<!-- Account Information -->
				<div class="section-container">
					<div class="section-header">
						<h3>Account Information</h3>
					</div>
					<div class="section-body">
						<div class="preference-content">
							<!-- Email Info -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-envelope"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Email Address</span>
									<span class="setting-description">{redactEmail(user.email)}</span>
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- User ID Info -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-person-badge"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">User ID</span>
									<span class="setting-description">{redactUid(user.uid)}</span>
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- Email Verification Status -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-patch-check"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Email Verification</span>
									<span class="setting-description">
										{#if user.emailVerified}
											<span class="status-badge verified">Verified</span>
										{:else}
											<span class="status-badge unverified">Not Verified</span>
										{/if}
									</span>
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- Linked Accounts -->
							<!--
                            {#if !user.providerData.some(provider => provider.providerId === 'facebook.com')}
                            <div class="account-header">
                                <div class="preference-icon">
                                    <i class="bi bi-facebook"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Facebook Account</span>
                                    <span class="setting-description">Link your Facebook account</span>
                                </div>
                                <div class="setting-action">
                                    <button class="enable-btn facebook" on:click={handleLinkFacebook}>
                                        Link Account
                                    </button>
                                </div>
                            </div>
                            <hr class="preference-divider" />
                            {/if}
                            -->
							{#if !user.providerData.some((provider) => provider.providerId === 'google.com')}
								<div class="account-header">
									<div class="preference-icon">
										<i class="bi bi-google"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Google Account</span>
										<span class="setting-description">Link your Google account</span>
									</div>
									<div class="setting-action">
										<button class="enable-btn google" on:click={handleLinkGoogle}>
											Link Account
										</button>
									</div>
								</div>
								<hr class="preference-divider" />
							{/if}
							<!-- Account Created Date -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-calendar-date"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Account Created</span>
									<span class="setting-description">
										{user.metadata?.creationTime
											? new Date(user.metadata.creationTime).toLocaleString(undefined, {
													year: 'numeric',
													month: 'long',
													day: 'numeric',
													hour: '2-digit',
													minute: '2-digit'
												})
											: 'Unknown'}
									</span>
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- Delete Medical Data Option -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-trash"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Delete Medical Data</span>
									<span class="setting-description"
										>Permanently remove your medical profile from our system.</span
									>
								</div>
								<div class="setting-action">
									<button
										class="enable-btn danger"
										on:click={() => (showDeleteConfirm = true)}
										disabled={deletingMedicalData}
									>
										Delete
									</button>
								</div>
							</div>
							{#if showDeleteConfirm}
								<div class="modal-overlay">
									<div class="modal-dialog section-container">
										<div class="section-header danger-header">
											<h3><i class="bi bi-trash"></i> Confirm Deletion</h3>
										</div>
										<div class="section-body">
											<p style="margin: 16px 0px">
												Are you sure you want to permanently delete your medical data? This action
												cannot be undone.
											</p>
											{#if deleteError}
												<div class="error">{deleteError}</div>
											{/if}
											<div class="modal-actions">
												<button
													class="enable-btn danger"
													on:click={() => {
														console.log('Delete clicked');
														handleDeleteMedicalData();
													}}
													disabled={deletingMedicalData}
												>
													{deletingMedicalData ? 'Deleting...' : 'Yes, Delete'}
												</button>
												<button
													class="enable-btn"
													on:click={() => {
														console.log('Cancel clicked');
														showDeleteConfirm = false;
														deleteError = null;
													}}
													disabled={deletingMedicalData}
												>
													Cancel
												</button>
											</div>
										</div>
									</div>
								</div>
							{/if}
							{#if deleteSuccess}
								<div class="success-message">Your medical data has been deleted.</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Location Information -->
				<div class="section-container">
					<div class="section-header">
						<h3>Location Information</h3>
					</div>
					<div class="section-body">
						<div class="preference-content">
							{#if locationData}
								<!-- Current Location -->
								<div class="account-header">
									<div class="preference-icon">
										<i class="bi bi-geo-alt"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Current Location</span>
										<span class="setting-description">
											{#if currentLocationName}
												{currentLocationName}
											{:else if fetchingLocationName}
												<span class="loading-text">Determining location name...</span>
											{:else if locationNameError}
												<span class="error-text">{locationNameError}</span>
											{:else}
												Unknown location
											{/if}
										</span>
									</div>
									<div class="setting-action">
										<button
											on:click={getLocation}
											class="refresh-btn"
											disabled={fetchingLocation}
											aria-label="Refresh location"
										>
											{#if fetchingLocation}
												<div class="button-spinner"></div>
											{:else}
												<i class="bi bi-arrow-clockwise"></i>
											{/if}
										</button>
									</div>
								</div>
								<hr class="preference-divider" />
								<!-- Coordinates -->
								<!--
                                <div class="account-header">
                                    <div class="preference-icon">
                                        <i class="bi bi-pin-map-fill"></i>
                                    </div>
                                    <div class="preference-title">
                                        <span class="setting-label">Coordinates</span>
                                        <span class="setting-description coordinates-text">
                                            {locationData.latitude.toFixed(6)}°, {locationData.longitude.toFixed(6)}°
                                        </span>
                                    </div>
                                </div>
                                <hr class="preference-divider" />
                                -->
								<!-- Last Updated -->
								<div class="account-header">
									<div class="preference-icon">
										<i class="bi bi-clock-history"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Last Updated</span>
										<span class="setting-description">
											{new Date(locationData.timestamp).toLocaleString(undefined, {
												year: 'numeric',
												month: 'long',
												day: 'numeric',
												hour: '2-digit',
												minute: '2-digit'
											})}
										</span>
									</div>
								</div>
							{:else if locationPermission === 'granted' && !locationData}
								<div class="account-header">
									<div class="preference-icon">
										<i class="bi bi-geo-alt"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Location Data</span>
										<span class="setting-description">
											{fetchingLocation
												? 'Getting your location...'
												: 'Location data not available.'}
										</span>
									</div>
									<div class="setting-action">
										<button on:click={getLocation} class="enable-btn" disabled={fetchingLocation}>
											{fetchingLocation ? 'Loading...' : 'Get Location'}
										</button>
									</div>
								</div>
							{:else if locationError}
								<div class="account-header">
									<div class="preference-icon error-icon">
										<i class="bi bi-exclamation-triangle"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Error</span>
										<span class="setting-description error-text">
											{locationError}
										</span>
									</div>
									<div class="setting-action">
										<button on:click={getLocation} class="enable-btn"> Try Again </button>
									</div>
								</div>
							{:else}
								<div class="paccount-header">
									<div class="preference-icon">
										<i class="bi bi-shield-lock"></i>
									</div>
									<div class="preference-title">
										<span class="setting-label">Location Services</span>
										<span class="setting-description"> Location services not enabled </span>
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- App Permissions -->
				<div class="section-container">
					<div class="section-header">
						<h3>App Permissions</h3>
					</div>
					<div class="section-body">
						<div class="preference-content">
							<!-- Notifications Permission -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-bell"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Notifications</span>
									<span class="setting-description">
										Allow the app to send you important health alerts
									</span>
								</div>
								<div class="setting-action">
									{#if notificationPermission === 'granted'}
										<span class="status-badge verified">Enabled</span>
									{:else}
										<button on:click={requestNotificationPermission} class="enable-btn">
											Enable
										</button>
									{/if}
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- Location Permission -->
							<div class="account-header">
								<div class="preference-icon">
									<i class="bi bi-geo-alt"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Location Services</span>
									<span class="setting-description">
										Access your location to provide localized health advice
									</span>
								</div>
								<div class="setting-action">
									{#if locationPermission === 'granted'}
										<span class="status-badge verified">Enabled</span>
									{:else}
										<button on:click={requestLocationPermission} class="enable-btn">
											Enable
										</button>
									{/if}
								</div>
							</div>
							<hr class="preference-divider" />
							<!-- Service Worker Status -->
							<!--
                            <div class="account-header">
                                <div class="preference-icon">
                                    <i class="bi bi-hdd-network"></i>
                                </div>
                                <div class="preference-title">
                                    <span class="setting-label">Background Services</span>
                                    <span class="setting-description">
                                        Enable background processing to receive push notifications
                                    </span>
                                </div>
                                <div class="setting-action">
                                    {#if swRegistered}
                                        <span class="status-badge verified">Active</span>
                                    {:else}
                                        <span class="status-badge unverified">Inactive</span>
                                    {/if}
                                </div>
                            </div>
                            -->
						</div>
					</div>
				</div>
			</div>
		{:else if activeTab === 'medical'}
			<div class="medical-section">
				<!-- Main section keeps app bar header, no additional container header -->
				{#if showMedicalForm}
					<MedicalForm
						initialData={medicalData}
						isEditing={medicalRecordExists}
						on:completed={handleMedicalFormCompleted}
						on:cancel={() => (showMedicalForm = false)}
					/>
				{:else}
					<MedicalProfile />
				{/if}
			</div>{:else if activeTab === 'settings'}
			<div class="settings-section">
				<!-- Display Preferences Container -->
				<div class="section-container">
					<div class="section-header">
						<h3>Display Preferences</h3>
					</div>
					<div class="section-body">
						<div class="preference-content">
							<div class="preference-header">
								<div class="preference-icon">
									<i class="bi bi-chat-square-text"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Show Welcome Message</span>
									<span class="setting-description"
										>Display the welcome message each time you open the application</span
									>
								</div>
								<div class="setting-action">
									<label class="switch">
										<input
											type="checkbox"
											checked={showWelcomeMessage}
											on:change={toggleWelcomeMessage}
										/>
										<span class="slider round"></span>
									</label>
								</div>
							</div>
							<hr class="preference-divider" />
							<div class="preference-header">
								<div class="preference-icon">
									<i class="bi bi-badge-ad"></i>
								</div>
								<div class="preference-title">
									<span class="setting-label">Show Advertisements</span>
									<span class="setting-description">Display advertisements in the application</span>
								</div>
								<div class="setting-action">
									<label class="switch">
										<input type="checkbox" checked={showAds} on:change={toggleAdsVisibility} />
										<span class="slider round"></span>
									</label>
								</div>
							</div>
						</div>
					</div>
				</div>
				<!-- City Preferences Container -->
				<div class="section-container">
					<div class="section-header">
						<h3>City Preferences</h3>
					</div>
					<div class="section-body city-preferences-wrapper">
						<CityPreferences userId={user?.uid} />
					</div>
				</div>
			</div>
		{/if}
	</div>
	<!-- Bottom Navigation Bar -->
	<div class="bottom-nav">
		<button
			class="nav-item"
			class:active={activeTab === 'dashboard'}
			on:click={() => {
				if (activeTab !== 'dashboard') {
					window.location.reload();
				}
			}}
			on:touchend={() => {
				if (activeTab !== 'dashboard') {
					window.location.reload();
				}
			}}
		>
			<i class="bi {activeTab === 'dashboard' ? 'bi-house-fill' : 'bi-house'}"></i>
			<span class:hide-label={activeTab === 'dashboard'}>Dashboard</span>
		</button>
		<button
			class="nav-item"
			class:active={activeTab === 'medical'}
			on:click={() => (activeTab = 'medical')}
		>
			<i class="bi {activeTab === 'medical' ? 'bi-heart-pulse-fill' : 'bi-heart-pulse'}"></i>
			<span class:hide-label={activeTab === 'medical'}>Medical</span>
		</button>
		<button
			class="nav-item"
			class:active={activeTab === 'notifications'}
			on:click={() => {
				activeTab = 'notifications';
				if (showMedicalForm) showMedicalForm = false;
			}}
		>
			<i class="bi {activeTab === 'notifications' ? 'bi-bell-fill' : 'bi-bell'}"></i>
			<span class:hide-label={activeTab === 'notifications'}>Notifications</span>
		</button>
		<button
			class="nav-item"
			class:active={activeTab === 'settings'}
			on:click={() => {
				activeTab = 'settings';
				if (showMedicalForm) showMedicalForm = false;
			}}
		>
			<i class="bi {activeTab === 'settings' ? 'bi-gear-fill' : 'bi-gear'}"></i>
			<span class:hide-label={activeTab === 'settings'}>Settings</span>
		</button>
		<button
			class="nav-item"
			class:active={activeTab === 'account'}
			on:click={() => {
				activeTab = 'account';
				if (showMedicalForm) showMedicalForm = false;
			}}
		>
			<i class="bi {activeTab === 'account' ? 'bi-person-fill' : 'bi-person'}"></i>
			<span class:hide-label={activeTab === 'account'}>Account</span>
		</button>
	</div>
</div>

<style>
	.dashboard {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		padding-bottom: 70px; /* Space for bottom nav */
		padding-top: 80px; /* Space for app bar */
		position: relative;
	}
	/* Ad container styles */
	.ad-container {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		background-color: #f8f9fa;
		padding: 8px 0;
		text-align: center;
		z-index: 1001; /* Higher than app bar */
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	/* App bar styles */
	.app-bar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 80px;
		background-color: #dd815e; /* Orange main color */
		color: white;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 16px;
		z-index: 1000;
	}

	/* Adjust app bar position when ads are shown */
	:global(.dashboard.show-ads .app-bar) {
		top: 90px; /* Adjusted top position */
	}

	/* Adjust content area padding when ads are shown */
	:global(.dashboard.show-ads) {
		padding-top: 170px; /* 80px (app bar) + 90px (ad container) */
	}

	/* Edit icon button in app bar */
	.edit-icon-btn {
		background: transparent;
		color: white;
		border: none;
		border-radius: 50%;
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition:
			background-color 0.2s,
			transform 0.2s;
	}

	.edit-icon-btn:hover {
		background: transparent;
		transform: scale(1.05);
	}

	.edit-icon-btn i {
		font-size: 1.8rem;
		box-shadow: transparent;
		z-index: 1000;
		display: flex;
		align-items: center;
		padding: 0 1rem;
	}

	.app-bar-content {
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.app-bar-main {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.app-title {
		text-transform: uppercase;
		font-size: 0.7rem;
		letter-spacing: 1px;
		opacity: 0.8;
		margin: 0;
	}

	.app-titles {
		display: flex;
		flex-direction: column;
	}

	.app-logo {
		width: 35px;
		height: 35px;
		object-fit: contain;
		transition: transform 0.2s;
	}
	.app-logo.rotating {
		animation: rotate-logo 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
	}
	@keyframes rotate-logo {
		0% {
			transform: rotate(0deg);
		}
		80% {
			transform: rotate(360deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.section-title {
		font-size: 1.5rem;
		margin: 0;
		font-weight: 600;
	}

	.content-area {
		flex: 1;
		padding-bottom: 2rem;
		overflow-y: auto;
	}

	/* Bottom navigation styles */
	.bottom-nav {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 70px;
		background-color: white;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		display: flex;
		align-items: center;
		justify-content: space-around;
		z-index: 1000;
	}

	.nav-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.5rem 0;
		background: none;
		border: none;
		color: #666;
		font-size: 0.75rem;
		cursor: pointer;
		position: relative;
		transition:
			background 0.2s,
			color 0.2s;
	}

	.nav-item i {
		font-size: 1.25rem;
		margin-bottom: 0.25rem;
		transition:
			font-size 0.3s cubic-bezier(0.4, 0, 0.2, 1),
			color 0.2s;
	}

	.nav-item.active {
		color: white;
		background-color: #dd815e; /* Orange main color */
		border-radius: 16px;
	}
	.nav-item.active i {
		font-size: 2.4rem;
		color: white;
		transition:
			font-size 0.35s cubic-bezier(0.4, 0, 0.2, 1),
			color 0.2s;
		position: relative;
	}

	.nav-item i::after {
		content: '';
		display: block;
		position: absolute;
		left: 50%;
		transform: translateX(-50%) scaleX(0);
		transform-origin: left;
		bottom: -6px;
		width: 32px;
		height: 4px;
		background: white;
		border-radius: 2px;
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
		transition:
			transform 0.7s cubic-bezier(0.4, 0, 0.2, 1),
			opacity 0.2s;
		opacity: 0;
		pointer-events: none;
	}

	.nav-item.active i::after {
		transform: translateX(-50%) scaleX(1);
		opacity: 1;
	}

	.nav-item:not(.active):hover {
		color: #dd815e; /* Orange hover color */
	}

	.nav-item span {
		display: inline-block;
		transition:
			opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1),
			max-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
			margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		opacity: 1;
		max-width: 100px;
		margin-left: 0;
		white-space: nowrap;
		overflow: hidden;
	}
	.nav-item .hide-label {
		opacity: 0;
		max-width: 0;
		margin-left: 0;
		pointer-events: none;
	}
	/* Card styles */
	.card {
		background: white;
		padding: 1.5rem;
		border-radius: 8px;
		margin-bottom: 1rem;
	}

	/* Section styling */
	.notifications-section,
	.account-section,
	.medical-section,
	.settings-section {
		padding-top: 1rem;
		padding-bottom: 1rem;
	}

	/* New Notification category styles */
	.notification-category {
		margin-bottom: 16px;
	}

	.notification-category .section-header {
		padding: 12px 16px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: #f8f9fa;
		border-radius: 8px 8px 0 0;
		border-bottom: 1px solid #e9ecef;
	}

	.notification-category .section-header h3 {
		margin: 0;
		font-size: 1.2rem;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.category-count {
		background-color: #f0f0f0;
		border-radius: 16px;
		padding: 2px 10px;
		font-size: 0.85rem;
		font-weight: 600;
		color: #666;
	}

	.notification-card {
		display: flex;
		padding: 12px 16px;
		background-color: white;
		margin-bottom: 8px;
		border-radius: 6px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		cursor: pointer;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
		position: relative;
	}

	.notification-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
	}

	.notification-card.read {
		opacity: 0.75;
	}

	.notification-icon {
		margin-right: 12px;
		font-size: 1.2rem;
		position: relative;
		min-width: 24px;
		display: flex;
		align-items: flex-start;
		justify-content: center;
	}

	.unread-indicator {
		position: absolute;
		top: -4px;
		right: -4px;
		width: 8px;
		height: 8px;
		background-color: #e74c3c;
		border-radius: 50%;
	}

	.notification-content {
		flex: 1;
	}

	.notification-title {
		margin: 0 0 4px 0;
		font-size: 0.95rem;
		font-weight: 600;
		color: #333;
	}

	.notification-message {
		margin: 0 0 8px 0;
		font-size: 0.9rem;
		color: #555;
		line-height: 1.4;
	}

	.notification-time {
		font-size: 0.75rem;
		color: #777;
	}

	/* Account section containers with health card-style headers */
	.section-container {
		background: white;
		border-radius: 16px;
		overflow: hidden;
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
		margin-bottom: 1.5rem;
	}

	.section-header {
		background: #dd815e;
		color: white;
		padding: 1rem;
		position: relative;
		overflow: hidden;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.section-header::after {
		content: '';
		position: absolute;
		top: -20px;
		right: -20px;
		width: 120px;
		height: 120px;
		background: rgba(255, 255, 255, 0.08);
		border-radius: 50%;
		pointer-events: none;
		z-index: 0;
	}

	.section-header h3 {
		margin: 0;
		font-size: 1.2rem;
		font-weight: 600;
		letter-spacing: 0.3px;
		position: relative;
		z-index: 1;
	}

	.data-source-info {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
		color: white;
		z-index: 1;
		text-align: right;
	}

	.refresh-button {
		background-color: transparent;
		border: 0px transparent;
		padding: 0.2rem 0.5rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.85rem;
		color: white;
		display: inline-flex;
		align-items: center;
	}

	.refresh-button:hover:not(:disabled) {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.refresh-button:disabled {
		color: rgba(255, 255, 255, 0.5);
		cursor: not-allowed;
	}

	.open-meteo-icon {
		height: 20px;
		width: auto;
		opacity: 0.9;
		filter: brightness(0) invert(1);
		vertical-align: middle;
		margin-left: 4px;
		transition: opacity 0.2s ease;
	}

	.open-meteo-link:hover .open-meteo-icon {
		opacity: 1;
	}

	.section-body {
	}

	.logout-section {
		display: flex;
		justify-content: center;
		padding: 1rem;
	}

	.city-preferences-wrapper {
		padding: 0; /* Remove padding since the city preferences component already has its own padding */
	}

	.logout-section {
		display: flex;
		justify-content: center;
		padding: 1rem;
	}

	/* Logout button styling */
	.logout-container {
		margin-top: 1.5rem;
		display: flex;
		justify-content: center;
	}

	.logout-btn {
		background-color: #dd815e; /* Orange main color */
		color: white;
		border: none;
		padding: 0.75rem 2rem;
		border-radius: 8px;
		cursor: pointer;
		font-weight: bold;
		transition: background-color 0.2s;
		width: auto;
		min-height: 40px;
	}

	.logout-btn:hover {
		background-color: #c26744;
	}

	.logout-btn:disabled {
		background-color: #e5aa95;
		cursor: not-allowed;
	}

	/* Permission indicators */
	.permissions-status .granted {
		color: green;
		font-weight: bold;
	}

	.permissions-status .not-granted {
		color: #888;
	}

	.permissions-status button {
		margin-left: 1rem;
		font-size: 0.8rem;
		padding: 0.2rem 0.5rem;
		background: #dd815e;
		color: white;
		border: none;
		border-radius: 4px;
	}

	/* Notifications styling */
	.notifications-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		max-height: 70vh;
		overflow-y: auto;
		flex-wrap: nowrap;
	}

	.notification {
		padding: 0.75rem;
		border-radius: 8px;
		background-color: #f8f9fa;
		border-left: 4px solid #dd815e;
	}

	.notification h4 {
		margin: 0 0 0.5rem 0;
	}

	.notification p {
		margin: 0 0 0.5rem 0;
	}

	.notification small {
		color: #888;
	}

	.empty-state {
		color: #888;
		text-align: center;
		padding: 2rem 0;
		font-style: italic;
	}

	/* Location display styling */
	.location-info {
		background: #f8faff;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		margin: 1rem 0;
		border-left: 3px solid #dd815e;
		display: flex;
		align-items: center;
	}

	.location-info.error {
		background: #fff8f8;
		border-left-color: #f44242;
	}

	.location-info.loading {
		background: #f8f9fa;
		border-left-color: #888;
	}

	.location-icon {
		font-size: 1.2rem;
		margin-right: 0.5rem;
	}

	.location-name {
		font-weight: bold;
		margin-right: 0.5rem;
	}

	.location-name.loading {
		color: #888;
		font-style: italic;
	}

	.location-name.error {
		color: #f44242;
		font-style: italic;
	}

	.coordinates {
		font-family: monospace;
		font-weight: bold;
		color: #333;
	}

	.refresh-btn {
		background: transparent;
		border: none;
		color: #dd815e;
		cursor: pointer;
		font-size: 1rem;
		margin-left: 0.5rem;
		padding: 0.2rem 0.5rem;
		border-radius: 50%;
		transition: all 0.2s;
	}

	.refresh-btn:hover {
		background: rgba(221, 129, 94, 0.1);
	}

	.refresh-btn:disabled {
		color: #888;
		cursor: not-allowed;
	}

	/* Service worker error message */
	.sw-error {
		background: #fff8f8;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		margin: 1rem 0;
		border-left: 3px solid #f44242;
	}

	/* Settings container styling */
	.settings-container {
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	} /* Settings styles */
	.settings-group {
		padding: 1rem;
		border-bottom: 1px solid #eee;
	}

	.settings-group h4 {
		margin-top: 0;
		margin-bottom: 1rem;
		color: #333;
	}

	.setting-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.5rem 0;
	}
	/* New horizontal preference content styling */
	.preference-content {
		margin-bottom: 1rem;
	}

	.preference-header {
		display: flex;
		align-items: center;
		padding: 1rem 0.75rem 0rem 0.75rem;
		position: relative;
	}

	.preference-icon {
		width: 48px;
		height: 48px;
		border-radius: 50%;
		background: rgba(221, 129, 94, 0.15);
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 1rem;
		color: #dd815e;
		font-size: 1.4rem;
		flex-shrink: 0;
	}
	.preference-title {
		flex: 1;
	}

	.setting-info {
		flex: 1;
	}

	.setting-label {
		display: block;
		font-weight: 600;
		font-size: 1.1rem;
		color: #333;
		margin-bottom: 0.25rem;
	}

	.setting-description {
		display: block;
		font-size: 0.9rem;
		color: #666;
		line-height: 1.4;
	}

	.setting-action {
		margin-left: 1rem;
	}

	/* Toggle Switch */
	.switch {
		position: relative;
		display: inline-block;
		width: 50px;
		height: 24px;
		margin-left: 1rem;
	}

	.switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: #ccc;
		transition: 0.4s;
	}

	.slider:before {
		position: absolute;
		content: '';
		height: 16px;
		width: 16px;
		left: 4px;
		bottom: 4px;
		background-color: white;
		transition: 0.4s;
	}

	input:checked + .slider {
		background-color: #dd815e;
	}

	input:focus + .slider {
		box-shadow: 0 0 1px #dd815e;
	}

	input:checked + .slider:before {
		transform: translateX(26px);
	}

	.slider.round {
		border-radius: 24px;
	}

	.slider.round:before {
		border-radius: 50%;
	}

	/* Travel health advice section */
	.travel-health-advice-section {
		margin: 1.5rem 0;
		padding: 1rem;
		background-color: white;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.travel-health-advice-section h3 {
		margin-top: 0;
		margin-bottom: 1rem;
		color: #333;
	}

	@media (min-width: 768px) {
		.bottom-nav {
			height: 80px;
		}

		.nav-item {
			font-size: 0.85rem;
		}

		.nav-item i {
			font-size: 1.5rem;
		}

		.dashboard {
			padding-bottom: 80px;
		}

		.app-title {
			font-size: 0.8rem;
		}

		.section-title {
			font-size: 1.7rem;
		}
	}

	.status-badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.8rem;
		font-weight: 500;
	}

	.status-badge.verified {
		background-color: rgba(76, 175, 80, 0.15);
		color: #2e7d32;
	}

	.status-badge.unverified {
		background-color: rgba(244, 67, 54, 0.15);
		color: #c62828;
	}

	.enable-btn {
		background-color: #dd815e;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.enable-btn:hover {
		background-color: #c26744;
		transform: translateY(-1px);
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
	}

	.enable-btn:active {
		transform: translateY(0);
	}

	/* New Notification category styles */
	.notification-category {
		margin-bottom: 16px;
	}

	.notification-category .section-header {
		padding: 12px 16px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: #f8f9fa;
		border-radius: 8px 8px 0 0;
		border-bottom: 1px solid #e9ecef;
	}

	.notification-category .section-header h3 {
		margin: 0;
		font-size: 1.2rem;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.category-count {
		background-color: #f0f0f0;
		border-radius: 16px;
		padding: 2px 10px;
		font-size: 0.85rem;
		font-weight: 600;
		color: #666;
	}

	.notification-card {
		display: flex;
		padding: 12px 16px;
		background-color: white;
		margin-bottom: 8px;
		border-radius: 6px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		cursor: pointer;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
		position: relative;
	}

	.notification-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
	}

	.notification-card.read {
		opacity: 0.75;
	}

	.notification-icon {
		margin-right: 12px;
		font-size: 1.2rem;
		position: relative;
		min-width: 24px;
		display: flex;
		align-items: flex-start;
		justify-content: center;
	}

	.unread-indicator {
		position: absolute;
		top: -4px;
		right: -4px;
		width: 8px;
		height: 8px;
		background-color: #e74c3c;
		border-radius: 50%;
	}

	.notification-content {
		flex: 1;
	}

	.notification-title {
		margin: 0 0 4px 0;
		font-size: 0.95rem;
		font-weight: 600;
		color: #333;
	}

	.notification-message {
		margin: 0 0 8px 0;
		font-size: 0.9rem;
		color: #555;
		line-height: 1.4;
	}

	.notification-time {
		font-size: 0.75rem;
		color: #777;
	}

	.notifications-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.enable-btn.danger {
		background-color: #e74c3c;
	}
	.enable-btn.danger:hover {
		background-color: #c0392b;
	}
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.3);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 3000; /* Increased to ensure it's above all other content */
		pointer-events: all;
	}
	.modal-dialog {
		background: white;
		border-radius: 12px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
		max-width: 350px;
		width: 100%;
		text-align: center;
		z-index: 3100;
		pointer-events: auto;
	}
	.modal-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		margin-top: 1.5rem;
		margin-bottom: 1rem;
		margin-left: 1rem;
		margin-right: 1rem;
		justify-content: center;
		flex-direction: column;
	}
	.success-message {
		background: #e8f5e9;
		color: #2e7d32;
		padding: 0.75rem 1rem;
		border-radius: 6px;
		margin: 1rem 0;
		text-align: center;
		font-weight: 500;
	}
	.refresh-btn {
		background-color: #dd815e;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.refresh-btn:hover {
		background-color: #c26744;
		transform: translateY(-1px);
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
	}

	.refresh-btn:active {
		transform: translateY(0);
	}
	.danger-header {
		background: #e74c3c;
		color: white;
	}
	.preference-divider {
		border: 0;
		height: 1px;
		background-color: #eee;
		background-image: linear-gradient(90deg, transparent, #ccc, transparent);
		margin: 0.5rem 0 0.5rem 0;
	}
	.account-header {
		display: flex;
		align-items: center;
		padding: 0.75rem 0.5rem 0.5rem;
		position: relative;
	}
	.enable-btn.facebook {
		background-color: #1877f2;
	}

	.enable-btn.facebook:hover {
		background-color: #1464cf;
	}

	.enable-btn.google {
		background-color: #dc3545;
	}

	.enable-btn.google:hover {
		background-color: #bb2d3b;
	}
</style>
