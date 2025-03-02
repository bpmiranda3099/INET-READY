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
                        <h3>Travel Health Tips</h3>
                        <div class="route">
                            <span class="city origin">{advice.fromCity}</span>
                            <span class="arrow">→</span>
                            <span class="city destination">{advice.toCity}</span>
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
        padding: 1rem;
    }
    
    .advice-content {
        color: #333;
        line-height: 1.5;
    }
    
    /* Redesigned section styles */
    .top-tip {
        background-color: #e3f2fd;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        color: #1565c0;
    }
    
    .tip-label {
        background: #1565c0;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.5rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .advice-content h3 {
        color: #333;
        font-size: 1rem;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3rem;
    }
    
    .weather-brief {
        margin-bottom: 1rem;
    }
    
    .weather-brief p {
        margin: 0.5rem 0;
    }
    
    .health-reminders ol {
        padding-left: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .health-reminders li {
        margin-bottom: 0.5rem;
    }
    
    .warning-list, .tips-list {
        list-style-type: none;
        padding-left: 0;
        margin: 0.5rem 0;
    }
    
    .warning-list li {
        position: relative;
        padding-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .warning-list li:before {
        content: "⚠️";
        position: absolute;
        left: 0;
        top: 0;
        font-size: 0.9rem;
    }
    
    .tips-list li {
        position: relative;
        padding-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tips-list li:before {
        content: "✓";
        position: absolute;
        left: 0.2rem;
        top: -1px;
        font-weight: bold;
        color: #4caf50;
    }
    
    /* Card footer styling */
    .card-footer {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-top: 1px solid #eee;
        font-size: 0.8rem;
        color: #666;
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
        color: #888;
        font-size: 0.75rem;
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
        
        /* Update this selector to use :global since it's generated HTML */
        .advice-content :global(h3) {
            font-size: 1rem;
        }
        
        .top-tip {
            font-size: 1rem;
            padding: 0.6rem;
        }
        
        .card-body {
            padding: 0.75rem;
        }
        
        .card-footer {
            padding: 0.6rem 0.75rem;
            flex-direction: column;
            align-items: flex-start;
        }
    }
</style>
