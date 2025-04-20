<script>
	import { onMount, onDestroy, afterUpdate } from 'svelte';
	import { availableCities } from '$lib/services/weather-data-service';
	import { fade, fly, slide } from 'svelte/transition';
	import { spring } from 'svelte/motion';
	import MapBackground from './map-background.svelte';
	import { getCityCoords } from '$lib/services/city-coords';

	export let homeCity;
	export let preferredCities = [];
	export let useCurrentLocation = true;
	export let currentLocation = null; // Current location city name if available

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

	// Track if we should show navigation dots
	$: showDots = totalCards > 1;

	// Calculate current card height based on visible card content
	$: currentCardHeight =
		currentCard >= 0 && contentHeights[currentCard] ? contentHeights[currentCard] : cardHeight;
	// Subscribe to available cities
	const unsubscribeCities = availableCities.subscribe((cities) => {
		cityList = cities;
	});

	onMount(async () => {
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

	onDestroy(() => {
		unsubscribeCities();
		window.removeEventListener('keydown', handleKeydown);

		if (resizeObserver) {
			resizeObserver.disconnect();
		}
	});
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
			travelCards = destinations.map((toCity) => ({
				fromCity,
				toCity,
				timestamp: new Date(),
				// Creating empty data structures for the 4 tile rows
				rowOne: {
					// Row 1 (15% height) tiles - can be populated later
					tiles: []
				},
				rowTwo: {
					// Row 2 (15% height) tiles - can be populated later
					tiles: []
				},
				rowThree: {
					// Row 3 (30% height) tiles - can be populated later
					tiles: []
				},
				rowFour: {
					// Row 4 (40% height) tiles - can be populated later
					tiles: []
				}
			}));

			totalCards = travelCards.length;

			// Reset to the first card
			currentCard = 0;
		} catch (err) {
			console.error('Error generating travel cards:', err);
			error = 'Failed to generate travel cards. Please try again later.';
		} finally {
			loading = false;
		}
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
				opacity = 0.7;
			}

			return { transform, opacity, zIndex };
		});
	};

	// Watch progress updates
	$: cardTransforms = transformCards();

	// Helper: get coordinates for a city name
	function getCoordsForCity(cityName) {
		const coords = getCityCoords(cityName);
		if (!coords) return [120.9842, 14.5995]; // fallback: Manila
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
	<div class="loading-container">
		<div class="loading-spinner"></div>
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
						<span class="city-name">{card.toCity}</span>
					</div>

					<div class="card-body">
						<!-- Row 1 - 15% height -->
						<div class="tile-row row-one">
							{#if card.rowOne.tiles.length === 0}
								<div class="tile empty-tile">
									<div class="tile-placeholder">Row 1 Content</div>
								</div>
							{:else}
								{#each card.rowOne.tiles as tile}
									<div class="tile">
										<!-- Tile content will be filled later -->
									</div>
								{/each}
							{/if}
						</div>

						<!-- Row 2 - 15% height -->
						<div class="tile-row row-two">
							{#if card.rowTwo.tiles.length === 0}
								<div class="tile empty-tile">
									<div class="tile-placeholder">Row 2 Content</div>
								</div>
							{:else}
								{#each card.rowTwo.tiles as tile}
									<div class="tile">
										<!-- Tile content will be filled later -->
									</div>
								{/each}
							{/if}
						</div>

						<!-- Row 3 - 30% height -->
						<div class="tile-row row-three">
							{#if card.rowThree.tiles.length === 0}
								<div class="tile empty-tile">
									<div class="tile-placeholder">Row 3 Content</div>
								</div>
							{:else}
								{#each card.rowThree.tiles as tile}
									<div class="tile">
										<!-- Tile content will be filled later -->
									</div>
								{/each}
							{/if}
						</div>

						<!-- Row 4 - 40% height -->
						<div class="tile-row row-four">
							{#if card.rowFour.tiles.length === 0}
								<div class="tile empty-tile">
									<div class="tile-placeholder">Row 4 Content</div>
								</div>
							{:else}
								{#each card.rowFour.tiles as tile}
									<div class="tile">
										<!-- Tile content will be filled later -->
									</div>
								{/each}
							{/if}
						</div>
					</div>

					<div class="card-footer">
						{#if card.timestamp}
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
		padding-bottom: 1rem; /* Space for navigation dots */
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
		border-radius: 12px; /* Reduced from 16px */
		overflow: hidden;
		box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); /* Lighter shadow */
		transition:
			transform 0.05s ease-out,
			opacity 0.2s ease;
		will-change: transform, opacity;
		touch-action: pan-y;
		overflow-y: hidden; /* Changed from visible to hidden to prevent overflow */
		max-width: 100%; /* Ensure card doesn't exceed container width */
	}

	.travel-card.active {
		z-index: 10;
	}
	.card-header {
		background: #dd815e;
		color: white;
		padding: 0.35rem 1rem;
		border-radius: 16px 16px 0 0;
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
		padding: 0.5rem; /* Reduced padding */
		display: flex;
		flex-direction: column;
		height: calc(100% - 80px); /* Adjust for header and footer height */
	}

	/* Windows 10 Start Menu style tile rows */
	.tile-row {
		display: flex;
		gap: 0.5rem; /* Reduced gap */
		width: 100%;
		margin-bottom: 0.5rem; /* Reduced margin */
	}

	/* Height distribution as specified: 15%, 15%, 30%, 40% */
	.row-one {
		height: 15%;
		min-height: 60px;
	}

	.row-two {
		height: 15%;
		min-height: 60px;
	}

	.row-three {
		height: 30%;
		min-height: 120px;
	}

	.row-four {
		height: 40%;
		min-height: 160px;
		margin-bottom: 0;
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
		padding: 1rem 1.5rem;
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
		font-size: 0.75rem;
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
		padding: 6px 0; /* Add padding to prevent layout shifts */
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
		font-size: 0.75rem;
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
</style>
