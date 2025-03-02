<script>
    import { onMount, onDestroy } from 'svelte';
    import { getHealthAdvice } from '$lib/services/health-advice-cache';
    import { getMedicalData } from '$lib/firebase';
    import { checkGeminiAvailability, geminiStatus } from '$lib/services/gemini-service';
    import { availableCities } from '$lib/services/weather-data-service';
    import { fade, slide } from 'svelte/transition';
    
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
    let geminiAvailable = false;
    let cityList = [];
    let medicalData = null;
    let cardsGenerated = false;
    let cardHeight = 400; // Default height
    let cardElement;
    let resizeObserver;
    
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
                if (entry.target === cardElement) {
                    // Update card height based on content
                    cardHeight = entry.contentRect.height;
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
    });
    
    onDestroy(() => {
        unsubscribeGemini();
        unsubscribeCities();
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
        if (currentCard < totalCards - 1) {
            currentCard++;
        }
    }
    
    function prevCard() {
        if (currentCard > 0) {
            currentCard--;
        }
    }
    
    /**
     * Handle touch events for swipe
     */
    function handleTouchStart(event) {
        touchStartX = event.touches[0].clientX;
    }
    
    function handleTouchEnd(event) {
        touchEndX = event.changedTouches[0].clientX;
        handleSwipe();
    }
    
    function handleSwipe() {
        const threshold = 50; // Minimum distance required for swipe
        if (touchStartX - touchEndX > threshold) {
            // Swipe left, go to next card
            nextCard();
        } else if (touchEndX - touchStartX > threshold) {
            // Swipe right, go to previous card
            prevCard();
        }
    }
    
    /**
     * Format the advice text with Markdown-like styling
     */
    function formatAdviceText(text) {
        if (!text) return '';
        
        return text
            // Handle headings
            .replace(/^###\s+(.*)$/gm, '<h3>$1</h3>')
            .replace(/^##\s+(.*)$/gm, '<h2>$1</h2>')
            .replace(/^#\s+(.*)$/gm, '<h1>$1</h1>')
            // Handle bullet points
            .replace(/^\s*[*\-]\s+(.*)$/gm, '<li>$1</li>')
            // Replace double line breaks with paragraph tags
            .replace(/\n\n/g, '</p><p>')
            // Cleanup lists
            .replace(/<\/li>\n<li>/g, '</li><li>')
            .replace(/<li>(.*?)<\/li>/gs, function(match) {
                return '<ul>' + match + '</ul>';
            })
            .replace(/<\/ul>\s*<ul>/g, '')
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.*?)__/g, '<strong>$1</strong>')
            // Italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/_(.*?)_/g, '<em>$1</em>');
    }
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
        class="card-container"
        on:touchstart={handleTouchStart}
        on:touchend={handleTouchEnd}
        style="min-height: {cardHeight + 80}px;"
    >
        <div class="card-navigation">
            <button 
                class="nav-button prev" 
                disabled={currentCard === 0}
                on:click={prevCard}
                aria-label="Previous card"
            >
                ‹
            </button>
            
            <div class="card-indicator">
                <span class="card-count">{currentCard + 1} of {totalCards}</span>
            </div>
            
            <button 
                class="nav-button next" 
                disabled={currentCard === totalCards - 1}
                on:click={nextCard}
                aria-label="Next card"
            >
                ›
            </button>
        </div>
        
        {#each healthAdvice as advice, i}
            {#if i === currentCard}
                <div 
                    class="health-advice-card"
                    transition:fade={{ duration: 300 }}
                    bind:this={cardElement}
                >
                    <div class="card-header">
                        <h3>Travel Health Advice</h3>
                        <div class="route">
                            <span class="city origin">{advice.fromCity}</span>
                            <span class="arrow">→</span>
                            <span class="city destination">{advice.toCity}</span>
                        </div>
                        {#if advice.timestamp}
                            <div class="update-time">
                                Updated: {new Date(advice.timestamp).toLocaleString()}
                            </div>
                        {/if}
                    </div>
                    
                    <div class="card-body">
                        <div class="advice-content">
                            {@html formatAdviceText(advice.adviceText)}
                        </div>
                    </div>
                    
                    <div class="card-footer">
                        <div class="disclaimer">
                            This advice is for general informational purposes only and is not a substitute for 
                            professional medical advice. Always consult with a healthcare professional for 
                            specific health concerns.
                        </div>
                    </div>
                </div>
            {/if}
        {/each}
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
        width: 40px;
        height: 40px;
        border: 3px solid rgba(0,0,0,0.1);
        border-top-color: #4285f4;
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
        background-color: #fff4f4;
        border-radius: 8px;
        border-left: 4px solid #f44336;
        margin-bottom: 1rem;
    }
    
    .error-message {
        margin-bottom: 1rem;
        color: #d32f2f;
    }
    
    .retry-button {
        background-color: #f44336;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    
    .no-advice-container {
        padding: 1.5rem;
        text-align: center;
        background-color: #f5f5f5;
        border-radius: 8px;
        color: #666;
    }
    
    .card-container {
        position: relative;
        width: 100%;
        overflow-x: hidden;
        margin: 1rem 0;
    }
    
    .card-navigation {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        padding: 0 0.5rem;
    }
    
    .nav-button {
        background: #4285f4;
        color: white;
        border: none;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        font-size: 1.5rem;
        line-height: 1;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .nav-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        box-shadow: none;
    }
    
    .card-indicator {
        font-size: 0.9rem;
        color: #666;
    }
    
    .health-advice-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        overflow: hidden;
        margin: 0 auto;
        width: 100%;
    }
    
    .card-header {
        background: #4285f4;
        color: white;
        padding: 1rem;
        border-radius: 8px 8px 0 0;
    }
    
    .card-header h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.4rem;
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
        color: #e8f0fe;
    }
    
    .destination {
        color: #e8f0fe;
    }
    
    .arrow {
        margin: 0 0.5rem;
        font-size: 1.2rem;
    }
    
    .update-time {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.8);
        text-align: right;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    .advice-content {
        color: #333;
        line-height: 1.6;
    }
    
    .advice-content h2 {
        color: #4285f4;
        margin: 1.5rem 0 0.75rem;
        font-size: 1.2rem;
    }
    
    .advice-content h3 {
        color: #202124;
        margin: 1.25rem 0 0.5rem;
        font-size: 1.1rem;
    }
    
    .advice-content p {
        margin: 0.75rem 0;
    }
    
    .advice-content ul {
        margin: 0.5rem 0 1rem 0;
        padding-left: 1.5rem;
    }
    
    .advice-content li {
        margin-bottom: 0.5rem;
    }
    
    .card-footer {
        background: #f8f9fa;
        padding: 1rem;
        border-top: 1px solid #eee;
    }
    
    .disclaimer {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
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
            padding: 1rem;
        }
        
        .advice-content h2 {
            font-size: 1.1rem;
        }
        
        .advice-content h3 {
            font-size: 1rem;
        }
    }
</style>
