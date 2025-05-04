<script>
	import { onMount, onDestroy, afterUpdate } from 'svelte';
	import {
		availableCities,
		getCityData,
		getHeatIndexPredictions
	} from '$lib/services/weather-data-service';
	import { spring } from 'svelte/motion';
	import MapBackground from './map-background.svelte';
	import { getCityCoords } from '$lib/services/city-coords';
	import { getInetReadyStatus } from '$lib/services/inet-ready-advice';
	import { getMedicalData } from '$lib/services/medical-api';
	import { v4 as uuidv4 } from 'uuid';
	import Chatbot from './chatbot.svelte';
	import { getCurrentUser } from '.././lib/firebase/auth';
	import {
		saveTravelCardsCache,
		loadTravelCardsCache,
		clearTravelCardsCache
	} from '$lib/services/travel-cards-cache';
	import { fade, scale } from 'svelte/transition';

	export let homeCity;
	export let preferredCities = [];
	export let useCurrentLocation = true;
	export let currentLocation = null; // Current location city name if available
	export let medicalData = null; // Add this prop to receive user's medical data

	let travelCards = [];
	let loading = false;
	let error = null;
	let currentCard = 0;
	let totalCards = 0;
	let touchStartX = 0;
	let touchEndX = 0;
	let touchStartY = 0;
	let touchEndY = 0;
	let cityList = [];
	let cardsGenerated = false;
	let cardHeight = 500; // Default height for the new tile layout
	let cardsContainerElement;
	let cardElements = [];
	let resizeObserver;
	let isDragging = false;
	let startDragX = 0;
	let currentDragX = 0;
	let cardWidth = 0;
	let progress = spring(0);
	let cardOffset = 0;
	let animating = false;
	let contentHeights = [];
	let showChatbot = false;
	let user = null;
	let adviceScrollableRef;
	let showHospitalPhoneIcon = [];
	let hospitalIconTimers = [];

	// Track if we should show navigation dots
	$: showDots = totalCards > 1;

	// Calculate current card height based on visible card content
	$: currentCardHeight =
		currentCard >= 0 && contentHeights[currentCard] ? contentHeights[currentCard] : cardHeight;
	// Subscribe to available cities
	const unsubscribeCities = availableCities.subscribe((cities) => {
		cityList = cities;
	});

	// On mount, try to load cached travel cards and state
	onMount(async () => {
		const cached = loadTravelCardsCache();
		if (cached && cached.cards && cached.cards.length > 0) {
			// Restore cards and state
			travelCards = cached.cards.map((card) => ({
				...card,
				rowOne: { tiles: [], inetReady: { advice: card.advice, status: card.status } },
				rowThree: { tiles: [{ pois: card.pois }, { hospitalPOI: card.hospital }] },
				timestamp: card.timestamp
			}));
			totalCards = travelCards.length;
			currentCard = cached.state.cardIndex || 0;
			// Optionally restore map state if you want to persist zoom/center
		} else {
			// Fetch medical data before generating cards
			try {
				medicalData = await getMedicalData();
			} catch (e) {
				console.error('Failed to fetch medical data:', e);
				medicalData = null;
			}
			try {
				user = await getCurrentUser();
			} catch (e) {
				user = null;
			}
			// Create resize observer to handle card height adjustments
			resizeObserver = new ResizeObserver((entries) => {
				for (let entry of entries) {
					const targetIndex = cardElements.findIndex((el) => el === entry.target);

					if (targetIndex >= 0) {
						// Store height of each card content
						contentHeights[targetIndex] = entry.contentRect.height;

						// Update card width
						cardWidth = entry.contentRect.width;

						// If this is the current card, update container height
						if (targetIndex === currentCard) {
							cardHeight = Math.max(entry.contentRect.height, 500);
						}
					}
				}
			});

			try {
				// Generate travel cards
				await generateTravelCards();

				cardsGenerated = true;
			} catch (err) {
				console.error('Error initializing travel cards:', err);
				error = 'Failed to load travel cards. Please try again later.';
			} finally {
				loading = false;
			}

			// Add keyboard navigation support
			window.addEventListener('keydown', handleKeydown);

			// Observe card container size
			if (cardsContainerElement) {
				resizeObserver.observe(cardsContainerElement);
			}

			// Set initial progress value
			progress.set(0);
		}

		if (travelCards && travelCards.length) {
			hospitalIconTimers.forEach(clearTimeout);
			showHospitalPhoneIcon = travelCards.map(() => false);
			hospitalIconTimers = travelCards.map(() => null);
			travelCards.forEach((_, idx) => {
				animateHospitalTile(idx);
			});
		}
	});

	// Save cache whenever cards or currentCard changes
	$: saveTravelCardsCache({
		cards: travelCards,
		cardIndex: currentCard,
		mapState: { center: travelCards[currentCard]?.toCity || '', zoom: 15 }
	});

	afterUpdate(() => {
		// Apply resize observer to all card elements
		if (cardElements.length > 0) {
			cardElements.forEach((el, index) => {
				if (el && !resizeObserver.observed) {
					resizeObserver.observe(el);
				}
			});
		}
	});

	// Clear cache on destroy (optional, or do this on logout/settings change)
	onDestroy(() => {
		clearTravelCardsCache();
		unsubscribeCities();
		window.removeEventListener('keydown', handleKeydown);

		if (resizeObserver) {
			resizeObserver.disconnect();
		}
		hospitalIconTimers.forEach(clearTimeout);
	});

	function animateHospitalTile(idx) {
		showHospitalPhoneIcon[idx] = false;
		showHospitalPhoneIcon = [...showHospitalPhoneIcon];
		hospitalIconTimers[idx] = setTimeout(() => {
			showHospitalPhoneIcon[idx] = true;
			showHospitalPhoneIcon = [...showHospitalPhoneIcon];
			hospitalIconTimers[idx] = setTimeout(() => {
				showHospitalPhoneIcon[idx] = false;
				showHospitalPhoneIcon = [...showHospitalPhoneIcon];
				animateHospitalTile(idx);
			}, 2000); // Show icon for 2s
		}, 5000); // Wait 5s before showing icon
	}

	// Helper: fetch nearby POIs using Mapbox Search Box API
	async function fetchNearbyPOIs({
		lat,
		lng,
		types = ['cafe', 'mall', 'establishment', 'restaurant', 'shopping', 'museum'],
		limit = 10
	}) {
		// @ts-ignore
		const accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
		if (!accessToken) {
			console.warn('Mapbox access token missing');
			return [];
		}

		const results = [];

		for (const category of types) {
			const url = `https://api.mapbox.com/search/searchbox/v1/category/${encodeURIComponent(category)}?proximity=${lng},${lat}&limit=${limit}&access_token=${accessToken}`;
			try {
				const res = await fetch(url);
				if (!res.ok) throw new Error('Mapbox API error');
				const data = await res.json();
				const features = data.features || [];
				for (const f of features) {
					const props = f.properties || {};
					// Add lat/lng for Google Maps pins
					results.push({
						title: props.name || '',
						address: props.full_address || props.address || '',
						category: props.poi_category ? props.poi_category[0] : '',
						id: props.mapbox_id || '',
						lat: props.coordinates?.latitude || f.geometry?.coordinates?.[1],
						lng: props.coordinates?.longitude || f.geometry?.coordinates?.[0]
					});
				}
			} catch (e) {
				console.error(`Failed to fetch POIs for category ${category} from Mapbox:`, e);
			}
		}

		// Remove duplicates by mapbox_id
		const unique = [];
		const seen = new Set();
		for (const poi of results) {
			if (!seen.has(poi.id)) {
				unique.push(poi);
				seen.add(poi.id);
			}
		}

		return unique.slice(0, 5);
	}

	// Helper to open Google Maps with 5 POIs as route pins, starting from origin/current location/homeCity
	function openGoogleMapsWithPOIs(pois, event) {
		if (event) {
			// Prevent accidental trigger if this was a drag/swipe
			if (Math.abs(touchStartX - touchEndX) > 20 || Math.abs(touchStartY - touchEndY) > 20) return;
		}
		if (!pois || pois.length === 0) return;
		// Get up to 5 POIs
		const pins = pois.slice(0, 5);
		// Get origin: current location, or home city, or fallback to first POI
		let origin = '';
		if (currentLocation && currentLocation.lat && currentLocation.lng) {
			origin = `${currentLocation.lat},${currentLocation.lng}`;
		} else if (homeCity) {
			const coords = getCityCoords(homeCity);
			if (coords) origin = `${coords.lat},${coords.lng}`;
		}
		if (!origin && pins[0] && pins[0].lat && pins[0].lng) {
			origin = `${pins[0].lat},${pins[0].lng}`;
		}
		// Build waypoints (all but last POI)
		const waypoints = pins
			.slice(0, -1)
			.map((poi) => `${poi.lat},${poi.lng}`)
			.join('|');
		// Destination is last POI
		const destination = pins[pins.length - 1];
		const destStr = `${destination.lat},${destination.lng}`;
		// Build Google Maps directions URL
		let url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destStr)}`;
		if (waypoints) {
			url += `&waypoints=${encodeURIComponent(waypoints)}`;
		}
		window.open(url, '_blank');
	}

	// Helper: fetch nearest hospital/clinic POI with phone number using Mapbox Search Box API
	async function fetchNearestHospitalPOI({ lat, lng }) {
		// @ts-ignore
		const accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
		if (!accessToken) {
			console.warn('Mapbox access token missing');
			return null;
		}
		// Only use emergency-related categories
		const types = ['emergency', 'hospital', 'emergency_room', 'urgent_care']; // prioritize emergency care
		for (const category of types) {
			const url = `https://api.mapbox.com/search/searchbox/v1/category/${encodeURIComponent(category)}?proximity=${lng},${lat}&limit=8&access_token=${accessToken}`;
			try {
				const res = await fetch(url);
				if (!res.ok) throw new Error('Mapbox API error');
				const data = await res.json();
				const features = data.features || [];
				for (const f of features) {
					const props = f.properties || {};
					const phone = props.metadata?.phone || props.phone || null;
					const categories = (props.poi_category_ids || []).map((x) => x.toLowerCase());
					// Filter out maternity, dental, physical therapy, and non-emergency clinics
					const isEmergency = categories.some((cat) =>
						['emergency', 'hospital', 'urgent_care', 'emergency_room'].includes(cat.toLowerCase())
					);
					const isNonEmergency = categories.some((cat) =>
						[
							'maternity',
							'obstetric',
							'dental',
							'physical_therapy',
							'rehabilitation',
							'optical',
							'spa',
							'wellness'
						].includes(cat.toLowerCase())
					);
					if (phone && isEmergency && !isNonEmergency) {
						return {
							title: props.name || '',
							address: props.full_address || props.address || '',
							phone,
							category: props.poi_category ? props.poi_category[0] : '',
							id: props.mapbox_id || '',
							lat: props.coordinates?.latitude || f.geometry?.coordinates?.[1],
							lng: props.coordinates?.longitude || f.geometry?.coordinates?.[0]
						};
					}
				}
			} catch (e) {
				console.error(`Failed to fetch hospital POIs for category ${category} from Mapbox:`, e);
			}
		}
		return null;
	}

	/**
	 * Generate travel cards for each preferred city
	 */
	async function generateTravelCards() {
		try {
			loading = true;
			error = null;
			travelCards = [];

			// Origin city is current location if available and useCurrentLocation is true,
			// otherwise use home city
			const fromCity = useCurrentLocation && currentLocation ? currentLocation : homeCity;

			let refCoords = null;
			if (useCurrentLocation && currentLocation) {
				const coords = getCityCoords(currentLocation);
				if (coords) refCoords = coords;
			}
			if (!refCoords && fromCity) {
				const coords = getCityCoords(fromCity);
				if (coords) refCoords = coords;
			}
			if (!refCoords && homeCity) {
				const coords = getCityCoords(homeCity);
				if (coords) refCoords = coords;
			}

			if (!fromCity) {
				error = 'No home city or current location set. Please update your preferences.';
				return;
			}

			// Filter out the fromCity from the destinations
			const destinations = preferredCities.filter((city) => city !== fromCity);

			if (destinations.length === 0) {
				error = 'No preferred cities added. Please add cities in your settings.';
				return;
			}

			// Generate basic travel cards for each city pair
			travelCards = await Promise.all(
				destinations.map(async (toCity) => {
					// For each card, get POIs near the destination city (or refCoords)
					let coords = getCityCoords(toCity) || refCoords;
					let pois = [];
					let hospitalPOI = null;
					if (coords) {
						pois = await fetchNearbyPOIs({ lat: coords.lat, lng: coords.lng });
						hospitalPOI = await fetchNearestHospitalPOI({ lat: coords.lat, lng: coords.lng });
					}
					return {
						fromCity,
						toCity,
						timestamp: new Date(),
						rowOne: { tiles: [] },
						rowTwo: { tiles: [] },
						rowThree: { tiles: [{ pois }, { hospitalPOI }] }, // POIs in col 1, hospital in col 2
						rowFour: { tiles: [] }
					};
				})
			);

			totalCards = travelCards.length;

			// Reset to the first card
			currentCard = 0;

			// Fetch heat index and INET-READY status/advice for each card
			await fetchHeatIndexesForCards(travelCards);
		} catch (err) {
			console.error('Error generating travel cards:', err);
			error = 'Failed to generate travel cards. Please try again later.';
		} finally {
			loading = false;
		}
	}

	// Helper to get heat index color
	function getHeatIndexColor(heatIndex) {
		if (heatIndex == null || isNaN(heatIndex)) return '#cccccc';
		if (heatIndex < 27) return '#43a047'; // Green
		if (heatIndex < 33) return '#fbc02d'; // Yellow
		if (heatIndex < 42) return '#fb8c00'; // Orange
		if (heatIndex < 52) return '#e53935'; // Red
		return '#8e24aa'; // Purple
	}

	// Helper: get flat weather icon name based on heat index intensity
	function getWeatherIconName(heatIndex) {
		if (heatIndex == null || isNaN(heatIndex)) return 'mdi:weather-partly-cloudy';
		if (heatIndex < 27) return 'mdi:weather-sunny'; // Safe
		if (heatIndex < 33) return 'mdi:weather-sunny-alert'; // Caution
		if (heatIndex < 42) return 'mdi:weather-hot'; // Warning
		if (heatIndex < 52) return 'mdi:weather-hurricane'; // Danger
		return 'mdi:fire'; // Extreme
	}

	// Fetch heat index and INET-READY status/advice for all destination cities and update travelCards
	async function fetchHeatIndexesForCards(cards) {
		// Fetch 7-day predictions for all cities
		let predictions = {};
		try {
			predictions = await getHeatIndexPredictions();
		} catch (e) {
			console.error('Failed to fetch heat index predictions:', e);
		}

		await Promise.all(
			cards.map(async (card) => {
				const cityData = await getCityData(card.toCity);
				if (!cityData) {
					console.warn(`No data found for city: ${card.toCity}`);
					return;
				}

				const heatIndex = cityData?.heat_index ?? null;
				const temperature = cityData?.temperature ?? null;
				const humidity = cityData?.humidity ?? null;

				// Find tomorrow's predicted heat index for this city
				let tomorrowPrediction = null;
				if (predictions.cities && predictions.cities[card.toCity]) {
					const forecastArr = predictions.cities[card.toCity];
					if (Array.isArray(forecastArr)) {
						const tomorrow = new Date();
						tomorrow.setDate(tomorrow.getDate() + 1);
						const tomorrowStr = tomorrow.toISOString().slice(0, 10);
						tomorrowPrediction =
							forecastArr.find((f) => f.date === tomorrowStr)?.heat_index ?? null;
					}
				}

				card.rowOne.tiles = [
					{
						heatIndex,
						tomorrowPrediction,
						color: getHeatIndexColor(heatIndex),
						temperature,
						humidity
					}
				];

				// Pass already-fetched data to getInetReadyStatus
				const inetResult = await getInetReadyStatus({
					fromCity: card.fromCity,
					toCity: card.toCity,
					medicalData,
					fromHeat: cityData?.heat_index, // Pass heat index directly
					toHeat: heatIndex // Use fetched heat index
				});

				card.rowOne.inetReady = inetResult;
			})
		);
	}

	// Helper: split advice into lines for display (handles periods and newlines)
	function getAdviceLines(advice) {
		if (!advice) return [];
		return advice
			.split(/\n|(?<=\.) /g)
			.map((l) => l.trim())
			.filter(Boolean);
	}

	// Group advice lines by type: warning, positive, info, disclaimer
	function groupAdviceLines(advice) {
		const lines = getAdviceLines(advice);
		const groups = { warning: [], positive: [], info: [], disclaimer: [] };
		for (const line of lines) {
			if (
				/informational purposes only|constitute medical advice|consult a licensed healthcare professional|privacy is protected/i.test(
					line
				)
			) {
				groups.disclaimer.push(line);
			} else if (
				/(avoid|warning|caution|not recommended|danger|risk|emergency|heat|hydrate|stay indoors|limit outdoor|seek shade|call|hospital|clinic|doctor|medical|urgent|critical|alert|high|postpone|unsafe|worsen|dehydration|heat stress|dizziness|headache|nausea|rest often|extra care|combined risk|especially unsafe|monitor for signs|travel is highly discouraged|very long trip|conditions worsen|traveling a long distance in dangerous heat|postpone your trip|no heat index data|data unavailable|general heat safety precautions|higher risk|sensitive to heat|children are more sensitive|older adults are at higher risk|extra caution|monitor for changes)/i.test(
					line
				)
			) {
				groups.warning.push(line);
			} else if (
				/(recommended|safe|good|ok|fine|clear|all set|ready|approved|can travel|proceed|no issues|no problem|healthy|normal|low risk|go ahead|suitable|safest|best|ideal|excellent|positive|yes|enjoy|ideal conditions|favorable|minimal risk|quick trip|conditions are good|weather is favorable|enjoy your day|it will be cooler|conditions improve|short trip|minimal travel risk|very short trip|minimal risk|conditions are good|ideal conditions for a quick trip)/i.test(
					line
				)
			) {
				groups.positive.push(line);
			} else {
				groups.info.push(line);
			}
		}
		return groups;
	}

	/**
	 * Handle card navigation
	 */
	function nextCard() {
		if (currentCard < totalCards - 1 && !animating) {
			animating = true;
			currentCard++;
			// After animation completes, update height to match the new current card
			progress.set(currentCard, { hard: false }).then(() => {
				animating = false;
				if (contentHeights[currentCard]) {
					cardHeight = Math.max(contentHeights[currentCard], 400);
				}
			});
		}
	}

	function prevCard() {
		if (currentCard > 0 && !animating) {
			animating = true;
			currentCard--;
			// After animation completes, update height to match the new current card
			progress.set(currentCard, { hard: false }).then(() => {
				animating = false;
				if (contentHeights[currentCard]) {
					cardHeight = Math.max(contentHeights[currentCard], 400);
				}
			});
		}
	}

	function goToCard(index) {
		if (index >= 0 && index < totalCards && !animating) {
			animating = true;
			currentCard = index;
			// After animation completes, update height to match the new current card
			progress.set(currentCard, { hard: false }).then(() => {
				animating = false;
				if (contentHeights[currentCard]) {
					cardHeight = Math.max(contentHeights[currentCard], 400);
				}
			});
		}
	}

	/**
	 * Handle keyboard navigation
	 */
	function handleKeydown(event) {
		if (event.key === 'ArrowRight') {
			nextCard();
		} else if (event.key === 'ArrowLeft') {
			prevCard();
		}
	}

	/**
	 * Handle mouse/touch drag events
	 */
	function handleDragStart(event) {
		if (totalCards <= 1) return; // Don't enable drag for single card

		isDragging = true;
		startDragX = getEventX(event);
		currentDragX = startDragX;

		// Pause any ongoing spring animation
		progress.stiffness = 0;
		progress.damping = 1;

		// Capture mouse events outside the element
		window.addEventListener('mousemove', handleDragMove);
		window.addEventListener('mouseup', handleDragEnd);
		window.addEventListener('touchmove', handleDragMove, { passive: false });
		window.addEventListener('touchend', handleDragEnd);
	}

	function handleDragMove(event) {
		if (!isDragging) return;

		// Prevent scrolling when dragging horizontally
		if (event.cancelable) event.preventDefault();

		currentDragX = getEventX(event);
		const dragDelta = (startDragX - currentDragX) / cardWidth;

		// Calculate new progress value based on drag
		let newProgress = currentCard + dragDelta;

		// Constrain within bounds with resistance at edges
		if (newProgress < 0) {
			newProgress = newProgress * 0.3; // Add resistance at start
		} else if (newProgress > totalCards - 1) {
			newProgress = totalCards - 1 + (newProgress - (totalCards - 1)) * 0.3; // Add resistance at end
		}

		// Update spring target value
		progress.set(newProgress, { hard: true });
	}

	function handleDragEnd() {
		if (!isDragging) return;

		// Remove event listeners
		window.removeEventListener('mousemove', handleDragMove);
		window.removeEventListener('mouseup', handleDragEnd);
		window.removeEventListener('touchmove', handleDragMove);
		window.removeEventListener('touchend', handleDragEnd);

		// Restore spring animation
		progress.stiffness = 0.15;
		progress.damping = 0.8;

		// Determine final card position based on drag distance
		const dragDelta = startDragX - currentDragX;
		const dragThreshold = cardWidth * 0.2; // Minimum drag distance required to change card

		if (Math.abs(dragDelta) > dragThreshold) {
			if (dragDelta > 0) {
				// Dragged right to left - go to next card
				currentCard = Math.min(currentCard + 1, totalCards - 1);
			} else {
				// Dragged left to right - go to previous card
				currentCard = Math.max(currentCard - 1, 0);
			}
		}

		// Spring animate to the final position
		progress.set(currentCard, { hard: false });
		isDragging = false;
	}

	/**
	 * Handle touch events for swipe
	 */
	function handleTouchStart(event) {
		touchStartX = event.touches[0].clientX;
		touchStartY = event.touches[0].clientY;
	}

	function handleTouchMove(event) {
		if (totalCards <= 1) return; // Don't process swipes for single card

		const touchX = event.touches[0].clientX;
		const touchY = event.touches[0].clientY;

		// Calculate horizontal and vertical distances
		const deltaX = touchStartX - touchX;
		const deltaY = touchStartY - touchY;

		// Only prevent default if horizontal swipe is greater than vertical (to allow scrolling)
		if (Math.abs(deltaX) > Math.abs(deltaY) && event.cancelable) {
			event.preventDefault();
		}
	}

	function handleTouchEnd(event) {
		touchEndX = event.changedTouches[0].clientX;
		touchEndY = event.changedTouches[0].clientY;
		handleSwipe();
	}

	function handleSwipe() {
		const deltaX = touchStartX - touchEndX;
		const deltaY = touchStartY - touchEndY;
		const threshold = 50; // Minimum distance required for swipe

		// Only handle horizontal swipes that are greater than vertical movement
		if (Math.abs(deltaX) > Math.abs(deltaY)) {
			if (deltaX > threshold && currentCard < totalCards - 1) {
				// Swiped left, go to next card
				nextCard();
			} else if (deltaX < -threshold && currentCard > 0) {
				// Swiped right, go to previous card
				prevCard();
			}
		}
	}

	/**
	 * Helper function to get X coordinate from event
	 */
	function getEventX(event) {
		return event.type.includes('touch') ? event.touches[0].clientX : event.clientX;
	} // No formatting function needed for now since we're using a simple tile layout    // Calculate the transform for each card based on progress value
	$: transformCards = () => {
		if (!travelCards || travelCards.length === 0) return [];

		return travelCards.map((_, i) => {
			const diff = i - $progress;
			let transform = `translateX(${100 * diff}%)`;
			let opacity = 1;
			let zIndex = 10 - Math.abs(diff);

			// Apply scaling effect for non-active cards
			if (diff !== 0) {
				const scale = 0.95;
				transform = `${transform} scale(${scale})`;
				opacity = 0.4;
			}

			return { transform, opacity, zIndex };
		});
	};

	// Watch progress updates
	$: cardTransforms = transformCards();

	// Helper: get coordinates for a city name
	function getCoordsForCity(cityName) {
		const coords = getCityCoords(cityName);
		if (!coords) return [120.9842, 14.5995]; // fallback
		return [coords.lng, coords.lat];
	}
</script>

<MapBackground
	center={getCoordsForCity(travelCards[currentCard]?.toCity)}
	zoom={15}
	pitch={60}
	bearing={-20}
/>

{#if loading && !cardsGenerated}
	<!-- Lottie spinner replacement -->
	<script
		src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs"
		type="module"
	></script>
	<div class="loading-container">
		<dotlottie-player
			src="https://lottie.host/84d1af88-e233-4f6c-9e90-215e78a342cd/irsoJpd7tz.lottie"
			background="transparent"
			speed="1"
			style="width: 300px; height: 300px"
			loop
			autoplay
		></dotlottie-player>
		<p>Loading travel cards...</p>
	</div>
{:else if error}
	<div class="error-container">
		<p class="error-message">{error}</p>
		<button on:click={generateTravelCards} class="retry-button">Try Again</button>
	</div>
{:else if travelCards.length === 0}
	<div class="no-advice-container">
		<p>No travel cards available. Please add preferred cities in your settings.</p>
	</div>
{:else}
	<div class="cards-wrapper" bind:this={cardsContainerElement}>
		<div
			class="cards-container"
			on:mousedown={handleDragStart}
			on:touchstart={handleTouchStart}
			on:touchmove={handleTouchMove}
			on:touchend={handleTouchEnd}
			style="height: calc(100vh - 250px); transition: height 0.3s ease-out;"
		>
			{#each travelCards as card, i}
				<div
					class="travel-card"
					class:active={currentCard === i}
					style="transform: {cardTransforms[i].transform}; 
                           opacity: {cardTransforms[i].opacity};
                           z-index: {cardTransforms[i].zIndex};"
					bind:this={cardElements[i]}
				>
					<div class="card-header">
						<h6 class="section-title location-label">travelling to</h6>
						<span class="city-name">{card.toCity}</span>
					</div>

					<div class="card-body">
						<!-- Row 1: Heat Index (60%) and INET-READY Status (40%) -->
						<div class="tile-row row-one">
							<div class="tile-column column-60">
								{#if card.rowOne.tiles.length === 0}
									<div class="tile empty-tile">
										<div class="tile-placeholder">Heat Index</div>
									</div>
								{:else}
									{#each card.rowOne.tiles.slice(0, 1) as tile}
										<div
											class="tile weather-tile"
											style="background-color: {tile.color}; color: white; padding: 0.8rem; align-items: stretch;"
										>
											<div class="weather-left">
												<div class="temp-main">
													{tile.heatIndex !== null ? tile.heatIndex.toFixed(0) + '°C' : 'N/A'}
													<span class="temp-label">HI</span>
												</div>
												{#if tile.tomorrowPrediction !== undefined}
													<div class="temp-tomorrow">
														Tomorrow {tile.tomorrowPrediction !== null
															? tile.tomorrowPrediction.toFixed(0) + '°'
															: 'N/A'}
													</div>
												{/if}
											</div>
											<div class="weather-right">
												<div class="weather-detail">
													<i class="bi bi-thermometer-half weather-detail-icon" title="Temperature"
													></i>
													<span
														>{tile.temperature !== null && tile.temperature !== undefined
															? tile.temperature.toFixed(0) + '°'
															: 'N/A'}</span
													>
												</div>
												<div class="weather-detail">
													<i class="bi bi-droplet-half weather-detail-icon" title="Humidity"></i>
													<span
														>{tile.humidity !== null && tile.humidity !== undefined
															? tile.humidity.toFixed(0) + '%'
															: 'N/A'}</span
													>
												</div>
												<div class="weather-detail">
													<i class="bi bi-speedometer2 weather-detail-icon" title="Intensity"></i>
													<span class="intensity-level">
														{tile.heatIndex !== null
															? tile.heatIndex < 27
																? 'Safe'
																: tile.heatIndex < 33
																	? 'Caution'
																	: tile.heatIndex < 42
																		? 'Warning'
																		: tile.heatIndex < 52
																			? 'Danger'
																			: 'Extreme'
															: 'N/A'}
													</span>
												</div>
											</div>
										</div>
									{/each}
								{/if}
							</div>
							<div class="tile-column column-40">
								{#if !card.rowOne.inetReady}
									<div class="tile empty-tile">
										<div class="tile-placeholder">INET-READY Status</div>
									</div>
								{:else}
									<div
										class="tile inet-status-tile"
										style="background-color: {card.rowOne.inetReady.status === 'INET-READY'
											? '#43a047'
											: '#e53935'}; color: white; position: relative; flex-direction: column; justify-content: center; align-items: center; padding: 0.5rem;"
									>
										{#if card.rowOne.inetReady.status === 'INET-READY'}
											<i class="bi bi-check-circle-fill inet-status-icon"></i>
											<span class="inet-status-text inet-ready">INET-READY</span>
										{:else}
											<i class="bi bi-exclamation-triangle-fill inet-status-icon"></i>
											<span class="inet-status-text not-ready-label">NOT</span>
											<span class="inet-status-text inet-not-ready">INET-READY</span>
										{/if}
									</div>
								{/if}
							</div>
						</div>

						<!-- Row 2: Advice -->
						<div
							class="tile advice-tile"
							class:no-scroll={adviceScrollableRef &&
								adviceScrollableRef.scrollHeight <= adviceScrollableRef.clientHeight}
						>
							{#if card.rowOne.inetReady && card.rowOne.inetReady.advice}
								{@const grouped = groupAdviceLines(card.rowOne.inetReady.advice)}
								<div class="advice-scrollable" bind:this={adviceScrollableRef}>
									<div class="advice-list">
										{#each grouped.warning as adviceLine (adviceLine)}
											<div class="advice-item">
												<i
													class="bi bi-exclamation-triangle-fill advice-icon warning"
													style="color: #fff;"
												></i>
												<span class="advice-text">{adviceLine}</span>
											</div>
										{/each}
										{#each grouped.positive as adviceLine (adviceLine)}
											<div class="advice-item">
												<i class="bi bi-check-circle-fill advice-icon positive" style="color: #fff;"
												></i>
												<span class="advice-text">{adviceLine}</span>
											</div>
										{/each}
										{#each grouped.info as adviceLine (adviceLine)}
											<div class="advice-item">
												<i class="bi bi-info-circle-fill advice-icon info" style="color: #fff;"></i>
												<span class="advice-text">{adviceLine}</span>
											</div>
										{/each}
									</div>
								</div>
								{#if grouped.disclaimer.length > 0}
									<div class="advice-disclaimer-fixed">
										{#each grouped.disclaimer as adviceLine (adviceLine)}
											<div>{adviceLine}</div>
										{/each}
									</div>
								{/if}
							{:else}
								<div class="tile-placeholder">Travel advice will appear here.</div>
							{/if}
						</div>

						<!-- Row 4 - now becomes Row 3 -->
						<div class="tile-row row-three">
							<div class="tile-column column-60">
								{#if card.rowThree.tiles.length === 0 || !card.rowThree.tiles[0].pois || card.rowThree.tiles[0].pois.length === 0}
									<div class="tile empty-tile">
										<div class="tile-placeholder">Nearby Cafes, Malls, Establishments</div>
									</div>
								{:else}
									<div
										class="tile poi-tile-purple"
										on:click={(e) =>
											openGoogleMapsWithPOIs(card.rowThree.tiles[0].pois.slice(0, 3), e)}
										on:touchend={(e) =>
											openGoogleMapsWithPOIs(card.rowThree.tiles[0].pois.slice(0, 3), e)}
										style="cursor: pointer;"
									>
										<div class="poi-tile-title center" style="position: relative;">
											<img
												src="/static/mapbox-icon.png"
												alt="Mapbox"
												class="mapbox-icon"
											/>
											Nearby Cool Indoor Areas
										</div>
										<ul class="poi-list">
											{#each card.rowThree.tiles[0].pois.slice(0, 3) as poi, j (poi.id || j)}
												<li class="poi-list-item">
													<i class="bi bi-geo-alt-fill poi-location-icon"></i>
													<div class="poi-info-col">
														<span class="poi-name">{poi.title}</span>
														{#if poi.address}
															<span class="poi-address">{poi.address}</span>
														{/if}
													</div>
												</li>
												{#if j < Math.min(card.rowThree.tiles[0].pois.length, 3) - 1}
													<hr class="poi-divider" />
												{/if}
											{/each}
										</ul>
									</div>
								{/if}
							</div>
							<div class="tile-column column-40">
								<div class="tile-row sub-row">
									{#if card.rowThree.tiles[1] && card.rowThree.tiles[1].hospitalPOI && card.rowThree.tiles[1].hospitalPOI.phone}
										<div
											class="tile hospital-tile"
											on:click={() => {
												const phone = card.rowThree.tiles[1].hospitalPOI.phone;
												if (phone) window.open(`tel:${phone.replace(/[^\d+]/g, '')}`);
											}}
											on:touchend={() => {
												const phone = card.rowThree.tiles[1].hospitalPOI.phone;
												if (phone) window.open(`tel:${phone.replace(/[^\d+]/g, '')}`);
											}}
										>
											{#if showHospitalPhoneIcon[i]}
												<div
													class="hospital-phone-anim"
													in:fade={{ duration: 300 }}
													out:fade={{ duration: 300 }}
												>
													<i class="bi bi-telephone-fill hospital-anim-icon"></i>
												</div>
											{:else}
												<div
													class="hospital-tile-content"
													in:fade={{ duration: 300 }}
													out:fade={{ duration: 300 }}
												>
													<span class="hospital-tile-title"
														>{card.rowThree.tiles[1].hospitalPOI.title}</span
													>
													<span class="hospital-tile-phone"
														>{card.rowThree.tiles[1].hospitalPOI.phone}</span
													>
												</div>
											{/if}
										</div>
									{:else}
										<div class="tile empty-tile">
											<div class="tile-placeholder">No hospital/clinic hotline found</div>
										</div>
									{/if}
								</div>

								<div class="tile-row sub-row">
									<!-- AI Chatbot Button -->
									<button
										class="tile ai-chat-btn safetrip-ai-btn"
										style="background: #2ecc71; color: #fff; font-weight: 600; font-size: 1rem; width: 100%; height: 100%; border: none; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; padding: 1rem;"
										on:click={() => (showChatbot = true)}
										aria-label="Ask AI Chatbot"
									>
										<i
											class="bi bi-robot safetrip-ai-icon"
											style="position: absolute; top: 0.1rem; right: 0.6rem; font-size: 1.5rem; color: #fff;"
										></i>
										<span style="font-size: 0.9rem; font-weight: 700; letter-spacing: 0.02em;"
											>SafeTrip AI</span
										>
									</button>
								</div>
							</div>
						</div>
					</div>

					<div class="card-footer">
						{#if card.timestamp}
							<div class="update-time">
								Weather data by 
								<a 
									href="https://open-meteo.com/" 
									target="_blank" 
									rel="noopener noreferrer" 
									class="open-meteo-link"
									style="color: orange; text-decoration: underline;"
								>
									Open-Meteo.com
								</a>
							</div>
							<div class="update-time">
								Updated: {new Date(card.timestamp).toLocaleString()}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>

		{#if showDots}
			<div class="navigation-dots">
				{#each Array(totalCards) as _, i}
					<button
						class="dot"
						class:active={currentCard === i}
						on:click={() => goToCard(i)}
						aria-label="Go to card {i + 1}"
					></button>
				{/each}
			</div>
		{/if}

		<div class="swipe-hint" class:hidden={currentCard > 0}>
			<div class="swipe-icon">←</div>
			<div class="swipe-icon">→</div>
			<span>Swipe to navigate</span>
		</div>
	</div>
{/if}

{#if showChatbot}
	<div class="chatbot-overlay">
		<Chatbot onClose={() => (showChatbot = false)} {user} />
	</div>
{/if}

<style>
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		text-align: center;
	}

	.loading-spinner {
		width: 32px;
		height: 32px;
		border: 2px solid rgba(0, 0, 0, 0.05);
		border-top-color: #dd815e;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error-container {
		padding: 1.5rem;
		text-align: center;
		background-color: #fff9f7;
		border-radius: 12px;
		margin-bottom: 1rem;
		border: none;
		box-shadow: 0 4px 12px rgba(221, 129, 94, 0.1);
	}

	.error-message {
		margin-bottom: 1.2rem;
		color: #c26744;
	}

	.retry-button {
		background-color: #dd815e;
		color: white;
		border: none;
		padding: 0.6rem 1.2rem;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s ease;
		box-shadow: 0 4px 8px rgba(221, 129, 94, 0.2);
	}

	.retry-button:hover {
		background-color: #c26744;
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(221, 129, 94, 0.3);
	}

	.no-advice-container {
		padding: 2rem;
		text-align: center;
		background-color: #f9f9f9;
		border-radius: 12px;
		color: #666;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
	}
	.cards-wrapper {
		position: relative;
		width: 100%;
		margin: 1rem 0;
		padding-bottom: 2rem; /* Space for navigation dots */
		overflow: hidden; /* Hide horizontal overflow */
		max-width: 100vw; /* Ensure it doesn't exceed viewport width */
	}

	.cards-container {
		position: relative;
		width: 100%;
		overflow: hidden; /* Prevent horizontal scroll */
		user-select: none;
		touch-action: pan-y;
		-webkit-user-select: none;
		-webkit-touch-callout: none;
	}
	.travel-card {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		background: white;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
		transition:
			transform 0.05s ease-out,
			opacity 0.2s ease;
		will-change: transform, opacity;
		touch-action: pan-y;
		max-width: 100%; /* Ensure card doesn't exceed container width */
		height: 100%; /* Make the card take up the full height of its parent */
		display: flex;
		flex-direction: column;
		max-height: calc(100vh - 250px);
	}

	.travel-card.active {
		z-index: 10;
	}
	.card-header {
		background: #dd815e;
		color: white;
		padding: 0.35rem 1rem;
		border-radius: 8px 8px 0 0;
		position: relative;
		overflow: hidden;
		text-align: center;
		background-image: linear-gradient(
			135deg,
			rgba(255, 255, 255, 0.12) 0%,
			rgba(0, 0, 0, 0.08) 100%
		);
	}

	.card-header::after {
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

	/* .card-title {
        margin: 0 0 1.2rem 0;
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
        position: relative;
        z-index: 1;
    } */
	.route-display {
		position: relative;
		z-index: 1;
		display: flex;
		justify-content: center;
		margin: 0.3rem 0 0.2rem;
	}
	/* .route-cities {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.15);
        border-radius: 50px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .city-circle {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        position: relative;
        z-index: 2;
        padding: 3rem;
    }
    
    .origin-city {
        color: #1e88e5;
    }
    
    .dest-city {
        color: #e53935;
    }
    
    .city-icon {
        width: 0px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.4rem;
    }
    
    .origin-city .city-icon {
        color: #1e88e5;
    }
    
    .dest-city .city-icon {
        color: #e53935;
    }
    
    .city-icon i {
        font-size: 1.5rem;
    }
    
    .route-path {
        flex: 1;
        position: relative;
        height: 6px;
        margin: 0 0.5rem;
    }
    
    .route-line {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background-color: rgba(255,255,255,0.7);
        transform: translateY(-50%);
    }
    
    .route-animation-pulse {
        position: absolute;
        top: 0;
        left: -20px;
        width: 80px;
        height: 100%;
        background: linear-gradient(90deg, 
            rgba(255,255,255,0) 0%, 
            rgba(255,255,255,0.8) 50%, 
            rgba(255,255,255,0) 100%);
        z-index: 1;
        animation: pulse-animation 2s infinite linear;
    }
    
    @keyframes pulse-animation {
        0% {
            left: -40px;
        }
        100% {
            left: 100%;
        }
    }
    
    .city-name {
        font-weight: 600;
        font-size: 0.8rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        letter-spacing: 0.5px;
        white-space: nowrap;
        text-align: center;
        color: white;
    } */
	.card-body {
		padding: 0.5rem;
		display: flex;
		flex-direction: column;
		flex: 1; /* Take up remaining space */
		overflow-y: auto; /* Add scroll if content overflows */
		max-height: calc(100vh - 250px);
	}

	/* Windows 10 Start Menu style tile rows */
	.tile-row {
		display: flex;
		gap: 0; /* Removed gap */
		width: 100%;
		margin-bottom: 0; /* Removed margin */
	}

	/* Adjusted height distribution: 25%, 35%, 40% */
	.row-one {
		height: 25%;
		min-height: 100px;
		display: flex;
	}

	.column-40 {
		width: 40%;
		display: flex;
		flex-direction: column;
		gap: 0; /* Removed gap */
	}

	.column-60 {
		width: 60%;
		display: flex;
		flex-direction: column;
		gap: 0; /* Removed gap */
	}

	.row-two {
		height: 35%;
		min-height: 140px;
	}

	.row-three {
		height: 40%;
		min-height: 160px;
		display: flex;
		margin-bottom: 0;
	}

	.sub-row {
		height: 50%;
		display: flex;
		gap: 0; /* Removed gap */
	}

	.tile {
		flex: 1;
		background-color: #f0f0f0;
		border-radius: 8px;
		overflow: hidden;
		position: relative;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.tile:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.empty-tile {
		background-color: #f9f9f9;
		border: 2px dashed #e0e0e0;
	}

	.tile-placeholder {
		color: #aaa;
		font-size: 0.9rem;
		text-align: center;
		padding: 1rem;
	}

	/* Redesigned section styles with modern flat design */
	/* .top-tip {
        background-color: #fff9f7;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        font-weight: 500;
        color: #b35d3a;
        box-shadow: 0 4px 12px rgba(221, 129, 94, 0.08);
        position: relative;
    }
    
    .top-tip::before {
        content: '⚡';
        position: absolute;
        top: 50%;
        left: -8px;
        transform: translateY(-50%);
        background: #dd815e;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    
    .advice-content h3 {
        color: #b35d3a;
        font-size: 1.1rem;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        padding-bottom: 0.5rem;
        border: none;
        position: relative;
        padding-left: 1rem;
    }
    
    .advice-content h3::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #dd815e;
        border-radius: 4px;
    }
    
    .weather-brief {
        margin-bottom: 1.5rem;
        background: #f9f9f9;
        padding: 1rem;
        border-radius: 12px;
    }
    
    .weather-brief p {
        margin: 0.5rem 0;
        color: #555;
    }
    
    .health-reminders ol {
        padding-left: 2rem;
        margin: 0.8rem 0;
    }
    
    .health-reminders li {
        margin-bottom: 0.8rem;
        padding-left: 0.5rem;
    }
    
    .warning-list, .tips-list {
        list-style-type: none;
        padding-left: 0;
        margin: 0.8rem 0;
    }
    
    .warning-list li {
        position: relative;
        padding-left: 2rem;
        margin-bottom: 0.8rem;
        background: #fff9f9;
        padding: 0.8rem 1rem 0.8rem 2.5rem;
        border-radius: 8px;
    }
    
    .warning-list li:before {
        content: "⚠️";
        position: absolute;
        left: 0.8rem;
        top: 0.8rem;
        font-size: 1rem;
    }
    
    .tips-list li {
        position: relative;
        padding-left: 2rem;
        margin-bottom: 0.8rem;
        background: #f8f8f8;
        padding: 0.8rem 1rem 0.8rem 2.5rem;
        border-radius: 8px;
    }
    
    .tips-list li:before {
        content: "✓";
        position: absolute;
        left: 1rem;
        top: 0.8rem;
        font-weight: bold;
        color: #dd815e;
    } */

	/* Card footer styling */
	.card-footer {
		background: #fafafa;
		padding: 0.5rem 0.75rem;
		border-top: 1px solid #f0f0f0;
		font-size: 0.8rem;
		color: #777;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	/* .disclaimer {
        font-style: italic;
        flex: 1;
    } */

	.update-time {
		color: #999;
		font-size: 0.5rem;
	}
	/* Navigation dots */
	.navigation-dots {
		display: flex;
		justify-content: center;
		margin-top: 0.8rem;
		gap: 0.5rem;
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 20px; /* Fixed height for the navigation dots container */
	}

	.dot {
		width: 8px;
		height: 8px;
		min-width: 8px; /* Prevent width compression */
		min-height: 8px; /* Prevent height compression */
		border-radius: 50%;
		background-color: rgba(221, 129, 94, 0.3);
		border: none;
		padding: 0;
		cursor: pointer;
		transition: background-color 0.2s ease; /* Only transition color, not dimensions */
	}

	.dot.active {
		background-color: #dd815e;
		transform: scale(1.2);
	}

	/* Swipe hint */
	.swipe-hint {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background: rgba(255, 255, 255, 0.9);
		padding: 0.8rem 1.2rem;
		border-radius: 50px;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		opacity: 0.8;
		pointer-events: none;
		animation: fadeOut 3s forwards;
		font-size: 0.9rem;
		color: #555;
		z-index: 100;
	}

	.swipe-hint.hidden {
		display: none;
	}

	@keyframes fadeOut {
		0% {
			opacity: 0.9;
		}
		70% {
			opacity: 0.9;
		}
		100% {
			opacity: 0;
		}
	}

	.swipe-icon {
		animation: swipeAnim 1.5s infinite;
		opacity: 0.7;
		font-size: 1.1rem;
		color: #dd815e;
	}

	.swipe-icon:first-child {
		animation-delay: 0s;
	}

	.swipe-icon:nth-child(2) {
		animation-delay: 0.5s;
	}

	@keyframes swipeAnim {
		0% {
			transform: translateX(0);
			opacity: 0.4;
		}
		50% {
			transform: translateX(4px);
			opacity: 1;
		}
		100% {
			transform: translateX(0);
			opacity: 0.4;
		}
	}

	/* Make responsive for mobile */
	@media (max-width: 600px) {
		/* .card-header h3 {
            font-size: 1.2rem;
        }
        
        .route {
            font-size: 1rem;
        }
        
        .card-body {
            padding: 1.2rem;
        }
        
        .advice-content {
            font-size: 0.9rem;
        }
        
        /* Update this selector to use :global since it's generated HTML */
		/* .advice-content :global(h3) {
            font-size: 1rem;
            color: #b35d3a;
        }
        
        .top-tip {
            font-size: 1rem;
            padding: 0.8rem 1rem 0.8rem 1.5rem;
        }
        
        .card-footer {
            padding: 0.8rem 1.2rem;
            flex-direction: column;
            align-items: flex-start;
        } */
	}

	/* .route-path {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        padding: 0.5rem;
        background: rgba(255,255,255,0.15);
        border-radius: 50px;
        margin-top: 0.5rem;
    }
    
    .city-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem 1rem;
    }
    
    .from-block {
        align-items: flex-start;
    }
    
    .to-block {
        align-items: flex-end;
    }
    
    .route-progress {
        flex: 1;
        position: relative;
        height: 4px;
        margin: 0 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .progress-line {
        height: 2px;
        background-color: rgba(255,255,255,0.6);
        width: 100%;
        position: absolute;
    }
    
    .arrow-icon {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(255,255,255,0.2);
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .origin-icon, .dest-icon {
        font-size: 1.2rem;
        margin-bottom: 0.3rem;
    }
    
    .origin-icon {
        color: #1e88e5;
    }
    
    .dest-icon {
        color: #e53935;
    }
    
    .city-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    } */
	.route-container {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: rgba(255, 255, 255, 0.15);
		border-radius: 50px;
		padding: 0.4rem 0.8rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		width: 100%;
		max-width: 100%;
		position: relative;
		overflow: hidden;
	}

	.route-shine {
		position: absolute;
		top: 0;
		left: -200px;
		height: 100%;
		width: 150px;
		background: linear-gradient(
			90deg,
			rgba(255, 255, 255, 0) 0%,
			rgba(255, 255, 255, 0.1) 50%,
			rgba(255, 255, 255, 0) 100%
		);
		animation: shine-animation 4s infinite ease-in-out;
		pointer-events: none;
	}

	@keyframes shine-animation {
		0% {
			left: -150px;
		}
		100% {
			left: 100%;
		}
	}
	.city-circle {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.25rem 0.5rem;
	}

	.city-circle i {
		font-size: 1rem;
		color: white;
		margin-bottom: 0;
		text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
	}

	.city-name {
		font-weight: 600;
		font-size: 1.5rem;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
		letter-spacing: 0.2px;
		white-space: nowrap;
		text-align: center;
		color: white;
		margin-top: 0;
	}
	.traveling-text {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.8);
		text-align: center;
		position: relative;
		font-style: italic;
		font-weight: 400;
		letter-spacing: 0.5px;
		margin: 0 0.25rem;
	}
	.ai-chat-btn {
		background: #fffbe7;
		color: #2ecc71;
		border: none;
		border-radius: 12px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.7rem;
	}
	.ai-chat-btn:hover {
		background: #ffe9b3;
		color: #a35d1a;
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(221, 129, 94, 0.08);
	}
	.chatbot-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		background: rgba(0, 0, 0, 0.25);
		z-index: 2000;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.tile.weather-tile {
		display: flex;
		justify-content: space-between;
		align-items: center; /* Align items vertically */
		gap: 0.8rem;
		padding: 0.8rem; /* Add padding */
		flex-wrap: nowrap; /* Prevent wrapping for main sections */
		overflow: hidden; /* Prevent content spilling out */
	}

	.weather-left {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center; /* Center content vertically */
		text-align: center;
		flex-shrink: 0; /* Prevent shrinking */
	}

	.weather-icon {
		font-size: 2.5rem; /* Adjust icon size */
		margin-bottom: 0.2rem;
		opacity: 0.9;
	}

	.temp-main {
		font-size: 2.4rem; /* Larger temperature */
		font-weight: bold;
		line-height: 1;
		display: flex;
		align-items: baseline; /* Align °C and HI */
		white-space: nowrap; /* Prevent main temp from wrapping */
	}

	.temp-label {
		font-size: 0.9rem;
		font-weight: 500;
		margin-left: 0.2rem;
		opacity: 0.8;
	}

	.temp-tomorrow {
		font-size: 0.9rem;
		margin-top: 0.1rem;
		opacity: 0.9;
		white-space: nowrap; /* Prevent tomorrow's temp from wrapping */
	}

	.weather-right {
		display: flex;
		flex-direction: column;
		justify-content: center; /* Center content vertically */
		flex-grow: 1; /* Allow this section to take remaining space */
		font-size: 0.9rem;
		gap: 0.3rem; /* Space between detail lines */
		min-width: 0; /* Allow shrinking if needed */
		overflow: hidden; /* Hide overflow within this section */
	}
	.weather-right {
		display: flex;
		flex-direction: column;
		justify-content: center; /* Center content vertically */
		flex-grow: 1; /* Allow this section to take remaining space */
		font-size: 0.9rem;
		gap: 0.3rem; /* Space between detail lines */
		min-width: 0; /* Allow shrinking if needed */
		overflow: hidden; /* Hide overflow within this section */
	}

	.weather-detail {
		display: flex;
		/* Removed justify-content: space-between; - let icon/span spacing handle it */
		align-items: center;
		border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Subtle separator */
		padding-bottom: 0.2rem;
		white-space: nowrap; /* Prevent wrapping within a detail line initially */
		overflow: hidden; /* Hide overflow */
	}

	.weather-detail:last-child {
		border-bottom: none; /* Remove border from last item */
	}

	.weather-detail-icon {
		font-size: 1rem; /* Adjust icon size as needed */
		opacity: 0.85;
		margin-right: 0.5rem; /* Space between icon and value */
		flex-shrink: 0; /* Prevent icon from shrinking */
		width: 1.2em; /* Give icon a consistent width */
		text-align: center;
	}

	.weather-detail span {
		/* Styles previously applied to :last-child now apply to the only span */
		font-weight: 500;
		text-align: right;
		flex-grow: 1; /* Allow span to take remaining space */
		overflow: hidden; /* Hide overflow */
		text-overflow: ellipsis; /* Add ellipsis if text still overflows */
		display: block; /* Ensure spans behave predictably */
	}

	.intensity-level {
		font-weight: bold;
	}

	.inet-status-tile {
		text-align: center;
		line-height: 1.2; /* Adjusted line height */
		overflow: hidden; /* Prevent content spillover */
		display: flex; /* Use flexbox for better control */
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 0.5rem; /* Ensure some padding */
	}

	.inet-status-icon {
		position: absolute;
		top: 0.5rem;
		right: 0.7rem;
		font-size: 1.5rem; /* Adjust size as needed */
		opacity: 0.9;
		flex-shrink: 0; /* Prevent icon from shrinking */
	}

	.inet-status-text {
		display: block;
		font-weight: bold;
		white-space: normal; /* Allow text wrapping */
		word-wrap: break-word; /* Break long words if necessary */
		max-width: 100%; /* Ensure text doesn't exceed tile width */
	}

	.inet-ready {
		font-size: 1.3rem; /* Slightly reduced size for better fit */
	}

	.not-ready-label {
		font-size: 0.85rem; /* Slightly reduced size */
		font-weight: 500;
		margin-bottom: -0.1rem; /* Adjust spacing */
	}

	.inet-not-ready {
		font-size: 1.3rem; /* Slightly reduced size */
	}

	.location-label {
		font-size: 0.7rem !important;
		font-style: italic;
		letter-spacing: 0.08em;
		margin-bottom: 0.1rem;
		font-weight: 500;
		opacity: 0.85;
		line-height: 1.1;
		padding: 0;
	}

	/* Responsive adjustments for smaller screens */
	@media (max-width: 400px) {
		.tile.weather-tile {
			gap: 0.4rem;
			padding: 0.6rem;
		}

		.weather-icon {
			font-size: 2rem;
		}

		.temp-main {
			font-size: 1.8rem; /* Reduced font size */
		}

		.temp-label {
			font-size: 0.75rem;
		}

		.temp-tomorrow {
			font-size: 0.75rem;
		}

		.weather-right {
			font-size: 0.8rem; /* Reduced font size */
			gap: 0.15rem;
		}

		.weather-detail span:first-child {
			margin-right: 0.3rem;
		}
		.inet-status-icon {
			font-size: 1.3rem; /* Smaller icon on small screens */
			top: 0.4rem;
			right: 0.5rem;
		}

		.inet-ready,
		.inet-not-ready {
			font-size: 1.1rem; /* Smaller text on small screens */
		}

		.not-ready-label {
			font-size: 0.75rem;
		}
	}

	@media (max-width: 350px) {
		.temp-main {
			font-size: 1.6rem;
		}
		.weather-icon {
			font-size: 1.8rem;
		}
		.weather-right {
			font-size: 0.75rem;
		}
		.weather-detail span:first-child {
			min-width: 30px; /* Further reduce min-width */
		}
	}
	.advice-tile {
		display: flex;
		flex-direction: column;
		align-items: stretch;
		justify-content: stretch;
		background: skyblue;
		color: #fff;
		width: 100%;
		min-height: 140px;
		height: 100%;
		padding: 0;
		box-sizing: border-box;
		position: relative;
		overflow: hidden;
	}
	.advice-scrollable {
		flex: 1 1 auto;
		width: 100%;
		max-height: none;
		min-height: 0;
		overflow-y: auto;
		margin-bottom: 0;
		padding: 1.1rem 0.8rem 2.1rem 0.8rem;
		scrollbar-width: thin;
		scrollbar-color: #b3e0ff transparent;
		transition: box-shadow 0.2s;
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		height: 100%;
		box-sizing: border-box;
	}
	.advice-tile.no-scroll .advice-scrollable {
		justify-content: center;
	}
	.advice-list {
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		flex: 1 1 auto;
		justify-content: flex-start;
	}
	.advice-disclaimer-fixed {
		position: absolute;
		left: 0.9rem;
		right: 0.9rem;
		bottom: 0.5rem;
		font-size: 0.68rem;
		color: #fff;
		opacity: 0.95;
		font-style: italic;
		max-width: unset;
		white-space: normal;
		pointer-events: none;
		background: rgba(0, 0, 0, 0.18);
		padding: 0.25em 0.7em 0.25em 0.5em;
		border-radius: 8px;
		z-index: 2;
		box-sizing: border-box;
	}
	@media (max-width: 600px) {
		.advice-tile {
			padding: 0;
		}
		.advice-scrollable {
			padding: 0.7rem 0.5rem 1.5rem 0.5rem;
		}
		.advice-disclaimer-fixed {
			left: 0.5rem;
			right: 0.5rem;
			bottom: 0.3rem;
		}
	}
	@media (max-width: 400px) {
		.advice-disclaimer-fixed {
			left: 0.3rem;
			right: 0.3rem;
			bottom: 0.2rem;
		}
	}
	.advice-icon.warning,
	.advice-icon.positive,
	.advice-icon.info {
		color: #fff !important;
	}
	.safetrip-ai-btn {
		background: #2ecc71 !important;
		color: #fff !important;
		font-weight: 600;
		font-size: 1rem;
		border: none;
		border-radius: 12px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.7rem;
	}
	.safetrip-ai-btn:hover {
		background: #c26744 !important;
		color: #fff !important;
	}
	.safetrip-ai-icon {
		position: absolute;
		top: 0;
		right: 0;
		font-size: 1.5rem;
		color: #fff;
		opacity: 0.95;
		margin: 0;
	}
	.hospital-tile {
		position: relative;
		background: #e53935;
		color: #fff;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-direction: column;
		padding: 0.5rem;
		min-height: 60px;
		width: 100%;
		box-sizing: border-box;
		overflow: hidden;
	}
	.hospital-phone-anim {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		min-height: 48px;
		min-width: 48px;
		animation:
			hospital-phone-fadein 0.3s,
			hospital-phone-fadeout 0.3s 1.7s;
	}
	.hospital-anim-icon {
		color: #fff;
		font-size: 2.2rem;
		animation: hospital-vibrate 0.18s linear 0s 8;
	}
	@keyframes hospital-vibrate {
		0% {
			transform: translate(0, 0);
		}
		20% {
			transform: translate(-2px, 1px);
		}
		40% {
			transform: translate(-1px, -2px);
		}
		60% {
			transform: translate(2px, 1px);
		}
		80% {
			transform: translate(1px, -1px);
		}
		100% {
			transform: translate(0, 0);
		}
	}
	@keyframes hospital-phone-fadein {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	@keyframes hospital-phone-fadeout {
		from {
			opacity: 1;
		}
		to {
			opacity: 0;
		}
	}
	.hospital-phone-btn {
		position: absolute;
		top: 0;
		right: 0;
		background: transparent;
		color: #fff;
		border: none;
		border-radius: 50%;
		width: 2.3rem;
		height: 0rem;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: none;
		cursor: pointer;
		font-size: 1rem;
		z-index: 2;
	}
	.hospital-phone-btn i {
		color: #fff;
		font-size: 1.1rem;
	}
	.hospital-tile-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 100%;
		text-align: center;
		word-break: break-word;
	}
	.hospital-tile-title {
		font-weight: 700;
		font-size: 0.95rem;
		margin-bottom: 0.18rem;
		color: #fff;
		display: block;
	}
	.hospital-tile-phone {
		font-size: 0.78rem;
		color: #fff;
		font-weight: 400;
		display: block;
		word-break: break-all;
	}
	@media (max-width: 600px) {
		.hospital-tile {
			padding: 0.5rem;
			min-height: 48px;
		}
		.safetrip-ai-btn {
			padding: 0.5rem;
		}
		.hospital-tile-title {
			font-size: 0.85rem;
		}
		.hospital-tile-phone {
			font-size: 0.7rem;
		}
		.hospital-phone-btn {
			width: 1.3rem;
			height: 1.3rem;
			font-size: 0.9rem;
			top: 0;
			right: 0;
		}
		.safetrip-ai-icon {
			font-size: 1.2rem;
			top: 0;
			right: 0;
			margin: 0;
		}
	}
	.poi-tile-purple {
		background: #7c3aed; /* Modern purple */
		color: #fff;
		flex-direction: column;
		align-items: flex-start;
		padding: 0.7rem 0.7rem 0.7rem 0.7rem;
		min-height: 120px;
		width: 100%;
		border-radius: 8px;
		overflow: hidden;
		box-sizing: border-box;
	}
	.poi-tile-title {
		font-weight: 700;
		font-size: 1.05rem;
		margin-bottom: 0.4rem;
		color: #fff;
		letter-spacing: 0.01em;
	}
	.poi-list {
		list-style: none;
		padding: 0;
		margin: 0;
		width: 100%;
	}
	.poi-list-item {
		display: flex;
		align-items: flex-start;
		margin-bottom: 0.2rem;
		flex-wrap: nowrap;
		word-break: break-word;
	}
	.poi-list-item:last-child {
		margin-bottom: 0;
	}
	.poi-location-icon {
		color: #fff;
		font-size: 1rem;
		margin-right: 0.5em;
		flex-shrink: 0;
		margin-top: 0.1em;
	}
	.poi-info-col {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		margin-left: 0.1em;
	}
	.poi-name {
		font-size: 0.93rem;
		font-weight: 500;
		color: #fff;
		line-height: 1.2;
		margin-bottom: 0.08em;
	}
	.poi-address {
		font-size: 0.75rem;
		color: #e0e7ff;
		margin-left: 0;
		display: block;
		line-height: 1.2;
		word-break: break-word;
		margin-top: 0.01em;
	}
	.poi-divider {
		border: none;
		border-top: 1px solid #a78bfa;
		margin: 0.3rem 0 0.3rem 1.5em;
		width: calc(100% - 1.5em);
		opacity: 0.5;
	}
	.poi-tile-title.center {
		text-align: center;
		width: 100%;
		display: block;
	}
	.mapbox-icon {
		position: absolute;
		top: 0.1rem;
		right: 0.6rem;
		width: 1.5rem;
		height: 1.5rem;
		object-fit: contain;
		opacity: 0.95;
		margin: 0;
		pointer-events: none;
	}
	@media (max-width: 600px) {
		.poi-tile-title {
			font-size: 0.95rem;
		}
		.poi-name {
			font-size: 0.85rem;
		}
		.poi-address {
			font-size: 0.68rem;
		}
		.poi-tile-purple {
			min-height: 70px;
			padding: 0.4rem 0.4rem 0.4rem 0.4rem;
		}
	}
</style>
