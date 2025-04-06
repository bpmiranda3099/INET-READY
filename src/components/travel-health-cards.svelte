<script>
    import { onMount, onDestroy, afterUpdate } from 'svelte';
    import { getHealthAdvice } from '$lib/services/health-advice-cache';
    import { getMedicalData } from '$lib/firebase';
    import { checkGeminiAvailability, geminiStatus } from '$lib/services/gemini-service';
    import { availableCities } from '$lib/services/weather-data-service';
    import { fade, fly, slide } from 'svelte/transition';
    import { spring } from 'svelte/motion';
    
    export let userId;
    export let homeCity;
    export let preferredCities = [];
    export let useCurrentLocation = true;
    export let currentLocation = null; // Current location city name if available
    
    let healthAdvice = [];
    let loading = true;
    let error = null;
    let currentCard = 0;
    let totalCards = 0;
    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;
    let geminiAvailable = false;
    let cityList = [];
    let medicalData = null;
    let cardsGenerated = false;
    let cardHeight = 400; // Default height
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
    $: currentCardHeight = (currentCard >= 0 && contentHeights[currentCard]) 
        ? contentHeights[currentCard] 
        : cardHeight;
    
    // Subscribe to Gemini status
    const unsubscribeGemini = geminiStatus.subscribe(status => {
        geminiAvailable = status.isAvailable;
    });
    
    // Subscribe to available cities
    const unsubscribeCities = availableCities.subscribe(cities => {
        cityList = cities;
    });
    
    onMount(async () => {
        // Create resize observer to handle card height adjustments
        resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                const targetIndex = cardElements.findIndex(el => el === entry.target);
                
                if (targetIndex >= 0) {
                    // Store height of each card content
                    contentHeights[targetIndex] = entry.contentRect.height;
                    
                    // Update card width
                    cardWidth = entry.contentRect.width;
                    
                    // If this is the current card, update container height
                    if (targetIndex === currentCard) {
                        cardHeight = Math.max(entry.contentRect.height, 400);
                    }
                }
            }
        });
        
        try {
            // Check if Gemini API is available
            await checkGeminiAvailability();
            
            // Get user's medical data
            medicalData = await getMedicalData(userId);
            
            // Generate health advice cards
            await generateHealthAdviceCards();
            
            cardsGenerated = true;
        } catch (err) {
            console.error("Error initializing health cards:", err);
            error = "Failed to load health advice. Please try again later.";
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
        unsubscribeGemini();
        unsubscribeCities();
        window.removeEventListener('keydown', handleKeydown);
        
        if (resizeObserver) {
            resizeObserver.disconnect();
        }
    });
    
    /**
     * Generate health advice cards for each preferred city
     */
    async function generateHealthAdviceCards() {
        try {
            loading = true;
            error = null;
            healthAdvice = [];
            
            // Origin city is current location if available and useCurrentLocation is true,
            // otherwise use home city
            const fromCity = (useCurrentLocation && currentLocation) ? currentLocation : homeCity;
            
            if (!fromCity) {
                error = "No home city or current location set. Please update your preferences.";
                return;
            }
            
            // Filter out the fromCity from the destinations
            const destinations = preferredCities.filter(city => city !== fromCity);
            
            if (destinations.length === 0) {
                error = "No preferred cities added. Please add cities in your settings.";
                return;
            }
            
            // Generate advice for each city pair
            const advicePromises = destinations.map(toCity => 
                getHealthAdvice({
                    userId,
                    fromCity,
                    toCity,
                    medicalData
                })
            );
            
            // Wait for all advice to be generated
            const results = await Promise.all(advicePromises);
            healthAdvice = results.filter(Boolean); // Remove any null results
            totalCards = healthAdvice.length;
            
            // Reset to the first card
            currentCard = 0;
        } catch (err) {
            console.error("Error generating health advice cards:", err);
            error = "Failed to generate health advice. Please try again later.";
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
        return event.type.includes('touch') 
            ? event.touches[0].clientX 
            : event.clientX;
    }

    /**
     * Format the advice text with improved, more robust formatting that handles line break issues
     */
    function formatAdviceText(text) {
        if (!text) return '';
        
        // Initial cleaning - normalize line endings and ensure proper breaks
        // Fix common issues with joined bullet points and numbered lists
        text = text
            // Ensure line breaks before section headings
            .replace(/([^\n])(WEATHER BRIEF|HEALTH REMINDERS|WATCH FOR|QUICK TIPS)/g, '$1\n\n$2')
            // Fix numbered list items that appear on the same line
            .replace(/(\d+\.?\)?\s+[^.\n]+\.)(\s*)(\d+\.?\)?\s+)/g, '$1\n$3')
            // Fix bullet points that appear on the same line
            .replace(/([.!?])(\s*)(•|\*|\-)\s+/g, '$1\n$3 ');
        
        // Split the text into sections
        const sections = {
            topTip: '',
            weatherBrief: '',
            healthReminders: [],
            watchFor: [],
            quickTips: [],
            disclaimer: ''
        };
        
        // Extract the top tip
        const topTipMatch = text.match(/TOP TIP:?\s*(.*?)(?:\n|$)/i);
        if (topTipMatch && topTipMatch[1]) sections.topTip = topTipMatch[1].trim();
        
        // Extract the weather brief section
        const weatherBriefMatch = text.match(/WEATHER BRIEF:?\s*([\s\S]*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?HEALTH REMINDERS)/i);
        if (weatherBriefMatch && weatherBriefMatch[1]) sections.weatherBrief = weatherBriefMatch[1].trim();
        
        // Extract health reminders with improved regex
        const healthRemindersSection = text.match(/HEALTH REMINDERS:?\s*([\s\S]*?)(?:\n\n|\n?WATCH FOR)/i);
        if (healthRemindersSection && healthRemindersSection[1]) {
            // Find all numbered points using regex
            const numberedItems = healthRemindersSection[1].match(/\n?\s*\d+\.?\)?\s+(.*?)(?=\n\s*\d+\.?\)?\s+|\n\n|\n?WATCH FOR|$)/gis);
            if (numberedItems) {
                // Process each match to extract just the content
                sections.healthReminders = numberedItems.map(item => {
                    const content = item.replace(/\n?\s*\d+\.?\)?\s+/, '').trim();
                    return content;
                }).filter(item => item.length > 0);
            }
        }
        
        // Extract Watch For items with improved regex
        const watchForSection = text.match(/WATCH FOR:?\s*([\s\S]*?)(?:\n\n|\n?QUICK TIPS|$)/i);
        if (watchForSection && watchForSection[1]) {
            // Split by bullet points, accounting for possible formatting issues
            const bulletItems = watchForSection[1].split(/\n\s*[•\-\*]\s+/).slice(1);
            if (bulletItems.length > 0) {
                // Clean each bullet point
                sections.watchFor = bulletItems.map(item => 
                    item.trim().replace(/\n([^•\-\*])/g, ' $1') // Join lines that aren't new bullets
                ).filter(item => item.length > 0);
            } else {
                // Fallback - try to extract content some other way
                const content = watchForSection[1].trim().replace(/^[•\-\*]\s+/gm, '');
                if (content) {
                    sections.watchFor = [content]; 
                }
            }
        }
        
        // Extract Quick Tips items with improved regex
        const quickTipsSection = text.match(/QUICK TIPS:?\s*([\s\S]*?)(?:\n\n|_|$)/i);
        if (quickTipsSection && quickTipsSection[1]) {
            // Split by bullet points, accounting for possible formatting issues
            const bulletItems = quickTipsSection[1].split(/\n\s*[•\-\*]\s+/).slice(1);
            if (bulletItems.length > 0) {
                // Clean each bullet point
                sections.quickTips = bulletItems.map(item => 
                    item.trim().replace(/\n([^•\-\*])/g, ' $1') // Join lines that aren't new bullets
                ).filter(item => item.length > 0);
            } else {
                // Fallback - try to extract content some other way
                const content = quickTipsSection[1].trim().replace(/^[•\-\*]\s+/gm, '');
                if (content) {
                    sections.quickTips = [content];
                }
            }
        }
        
        // Extract disclaimer - usually the last paragraph
        const disclaimerMatch = text.match(/(?:_|remember)(.*?)\.?$/is);
        if (disclaimerMatch && disclaimerMatch[1]) {
            sections.disclaimer = disclaimerMatch[1].trim();
        }

        // Now build the HTML with the structured sections
        let formattedHtml = '';
        
        // Top Tip 
        if (sections.topTip) {
            formattedHtml += `<div class="top-tip"> ${sections.topTip}</div>`;
        }
        
        // Weather Brief
        if (sections.weatherBrief) {
            formattedHtml += `<div class="weather-brief"><h3>Weather</h3><p>${sections.weatherBrief}</p></div>`;
        }
        
        // Health Reminders
        if (sections.healthReminders.length > 0) {
            formattedHtml += `<div class="health-reminders"><h3>Health Reminders</h3><ol>`;
            sections.healthReminders.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ol></div>`;
        }
        
        // Watch For
        if (sections.watchFor.length > 0) {
            formattedHtml += `<div class="watch-for"><h3>Watch For</h3><ul class="warning-list">`;
            sections.watchFor.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ul></div>`;
        }
        
        // Quick Tips
        if (sections.quickTips.length > 0) {
            formattedHtml += `<div class="quick-tips"><h3>Quick Tip</h3><ul class="tips-list">`;
            sections.quickTips.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ul></div>`;
        }
        
        return formattedHtml;
    }

    // Calculate the transform for each card based on progress value
    $: transformCards = () => {
        if (!healthAdvice || healthAdvice.length === 0) return [];
        
        return healthAdvice.map((_, i) => {
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
</script>

{#if loading && !cardsGenerated}
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Generating health advice for your travel...</p>
    </div>
{:else if error}
    <div class="error-container">
        <p class="error-message">{error}</p>
        <button on:click={generateHealthAdviceCards} class="retry-button">Try Again</button>
    </div>
{:else if healthAdvice.length === 0}
    <div class="no-advice-container">
        <p>No travel health advice available. Please add preferred cities in your settings.</p>
    </div>
{:else}
    <div 
        class="cards-wrapper"
        bind:this={cardsContainerElement}
    >
        <div 
            class="cards-container"
            on:mousedown={handleDragStart}
            on:touchstart={handleTouchStart}
            on:touchmove={handleTouchMove}
            on:touchend={handleTouchEnd}
            style="height: {cardHeight + 20}px; transition: height 0.3s ease-out;"
        >
            {#each healthAdvice as advice, i}
                <div 
                    class="health-advice-card"
                    class:active={currentCard === i}
                    style="transform: {cardTransforms[i].transform}; 
                           opacity: {cardTransforms[i].opacity};
                           z-index: {cardTransforms[i].zIndex};"
                    bind:this={cardElements[i]}
                >
                    <div class="card-header">
                        <div class="card-title-destination">
                            <div class="route">
                                <span class="city origin">{advice.fromCity}</span>
                                <span class="arrow">→</span>
                                <span class="city destination">{advice.toCity}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card-body">
                        <div class="advice-content">
                            {@html formatAdviceText(advice.adviceText)}
                        </div>
                    </div>
                    
                    <div class="card-footer">
                        <div class="disclaimer">
                            Always consult a healthcare professional for personalized medical advice.
                        </div>
                        {#if advice.timestamp}
                            <div class="update-time">
                                Updated: {new Date(advice.timestamp).toLocaleString()}
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
                        aria-label="Go to card {i+1}"
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
        border: 2px solid rgba(0,0,0,0.05);
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .cards-wrapper {
        position: relative;
        width: 100%;
        margin: 1.5rem 0;
        padding-bottom: 2.5rem; /* Add space for navigation dots */
    }
    
    .cards-container {
        position: relative;
        width: 100%;
        overflow: visible;
        user-select: none;
        touch-action: pan-y;
        -webkit-user-select: none;
        -webkit-touch-callout: none;
    }
    
    .health-advice-card {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        transition: transform 0.05s ease-out, opacity 0.2s ease;
        will-change: transform, opacity;
        touch-action: pan-y;
        overflow-y: visible; /* Allow card to expand to its full height */
    }
    
    .health-advice-card.active {
        z-index: 10;
    }
    
    .card-header {
        background: #dd815e;
        color: white;
        padding: 1.2rem;
        border-radius: 16px 16px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .card-header::after {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    
    .card-title-destination {
        position: relative;
        z-index: 1;
    }
    
    .card-header h3 {
        margin: 0 0 0.8rem 0;
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .route {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .city {
        font-weight: 600;
    }
    
    .origin {
        color: #fff;
    }
    
    .destination {
        color: #fff;
    }
    
    .arrow {
        margin: 0 0.8rem;
        font-size: 1.2rem;
        opacity: 0.8;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    .advice-content {
        color: #444;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Redesigned section styles with modern flat design */
    .top-tip {
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
    }
    
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
    
    .disclaimer {
        font-style: italic;
        flex: 1;
    }
    
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
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: rgba(221, 129, 94, 0.3);
        border: none;
        padding: 0;
        cursor: pointer;
        transition: all 0.2s ease;
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
        0% { opacity: 0.9; }
        70% { opacity: 0.9; }
        100% { opacity: 0; }
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
        0% { transform: translateX(0); opacity: 0.4; }
        50% { transform: translateX(4px); opacity: 1; }
        100% { transform: translateX(0); opacity: 0.4; }
    }
    
    /* Make responsive for mobile */
    @media (max-width: 600px) {
        .card-header h3 {
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
        .advice-content :global(h3) {
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
        }
    }
</style>
