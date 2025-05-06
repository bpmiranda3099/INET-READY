<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { fly, fade } from 'svelte/transition';
    export let user = {};
    export let showAlways = false;

    const dispatch = createEventDispatcher();
    // Set initial value based on localStorage
    let showWelcome = !(localStorage.getItem('inet-ready-hide-welcome') === 'true') || showAlways;
    let doNotShowAgain = false;
    
    // Bootstrap will handle the carousel internally
    let bootstrapCarousel;    onMount(() => {
        // Initialize Bootstrap carousel after the component is mounted
        if (typeof document !== 'undefined') {
            // Add Bootstrap CSS and JS if they don't exist
            if (!document.getElementById('bootstrap-css')) {
                const bootstrapCSS = document.createElement('link');
                bootstrapCSS.id = 'bootstrap-css';
                bootstrapCSS.rel = 'stylesheet';
                bootstrapCSS.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css';
                document.head.appendChild(bootstrapCSS);
            }
            
            if (!document.getElementById('bootstrap-js')) {
                const bootstrapJS = document.createElement('script');
                bootstrapJS.id = 'bootstrap-js';
                bootstrapJS.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
                bootstrapJS.onload = () => {
                    // Initialize the carousel after Bootstrap is loaded
                    // Use window.bootstrap to access the global bootstrap object
                    // @ts-ignore
                    if (window.bootstrap) {
                        // @ts-ignore
                        bootstrapCarousel = new window.bootstrap.Carousel(document.getElementById('featureCarousel'), {
                            interval: 5000,
                            wrap: true
                        });
                    }
                };
                document.body.appendChild(bootstrapJS);
            } else {
                // If Bootstrap is already loaded, initialize the carousel directly
                setTimeout(() => {
                    // @ts-ignore
                    if (window.bootstrap) {
                        // @ts-ignore
                        bootstrapCarousel = new window.bootstrap.Carousel(document.getElementById('featureCarousel'), {
                            interval: 5000,
                            wrap: true
                        });
                    }
                }, 100);
            }
        }
        
        return () => {
            // Clean up if needed
            if (bootstrapCarousel && bootstrapCarousel.dispose) {
                bootstrapCarousel.dispose();
            }
        };    });
    
    function closeWelcome() {
        if (doNotShowAgain) {
            localStorage.setItem('inet-ready-hide-welcome', 'true');
        }
        showWelcome = false;
        dispatch('close');
    }
</script>

{#if showWelcome}
    <div class="welcome-overlay" transition:fade={{ duration: 300 }}>
        <div 
            class="welcome-container"
            transition:fly={{ y: 20, duration: 500, delay: 300 }}
        >
            <div class="welcome-header">
                <h2>Welcome to INET-READY</h2>
            </div>
            
            <div class="welcome-content">
                
                <div class="welcome-message">
                    <h3>Your Travel Health Companion</h3>
                    <p>INET-READY provides you with personalized insights and recommendations for safer, healthier travels.</p>
                </div>                  <div class="feature-carousel">
                    <div id="featureCarousel" class="carousel slide" data-bs-ride="carousel">
                        <div class="carousel-indicators">
                            <button type="button" data-bs-target="#featureCarousel" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
                            <button type="button" data-bs-target="#featureCarousel" data-bs-slide-to="1" aria-label="Slide 2"></button>
                            <button type="button" data-bs-target="#featureCarousel" data-bs-slide-to="2" aria-label="Slide 3"></button>
                        </div>
                        <div class="carousel-inner">
                            <div class="carousel-item active">
                                <div class="feature-card d-block w-100">
                                    <div class="feature-icon">🧳</div>
                                    <div class="feature-text">Travel Health Cards</div>
                                    <div class="feature-description">Dynamic cards showing weather, heat index, health status, nearby hospitals, and personalized travel advice.</div>
                                </div>
                            </div>
                            <div class="carousel-item">
                                <div class="feature-card d-block w-100">
                                    <div class="feature-icon">🔔</div>
                                    <div class="feature-text">Real-time Notifications</div>
                                    <div class="feature-description">Push alerts, notification history, and smart permission management for critical health updates.</div>
                                </div>
                            </div>
                            <div class="carousel-item">
                                <div class="feature-card d-block w-100">
                                    <div class="feature-icon">🤖</div>
                                    <div class="feature-text">SafeTrip AI Chatbot</div>
                                    <div class="feature-description">AI-powered assistant for travel and health questions with context-aware responses optimized for mobile.</div>
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
                
                <div class="buttons-container">
                    <button class="get-started-button" on:click={closeWelcome}>
                        <span class="button-icon">⚡</span>
                        <span>Get Started</span>
                    </button>
                    
                    <label class="dont-show-option">
                        <input type="checkbox" bind:checked={doNotShowAgain}>
                        <span class="checkbox-text">Don't show this welcome screen again</span>
                    </label>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .welcome-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        backdrop-filter: blur(3px);
    }
    
    .welcome-container {
        background-color: white;
        border-radius: 24px;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.2);
        width: 90%;
        max-width: 540px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-5px);
        }
        100% {
            transform: translateY(0px);
        }
    }
    
    .welcome-header {
        background-color: #dd815e;
        color: white;
        padding: 1rem 1rem;
        display: flex;
        justify-content: center;
        align-items: center;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .welcome-header h2 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .close-button {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        line-height: 1;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.2s;
    }
    
    .close-button:hover {
        background-color: rgba(255, 255, 255, 0.25);
        transform: rotate(90deg);
    }
    
    .welcome-content {
        padding: 1rem 0.5rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Bootstrap overrides */
    :global(.carousel-item.active),
    :global(.carousel-item-next),
    :global(.carousel-item-prev) {
        display: flex;
        justify-content: center;
    }
    
    /* Logo styling */
    .welcome-logo {
        position: relative;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
    
    .logo-icon {
        font-size: 3rem;
        position: relative;
        z-index: 2;
        animation: pulse 2s infinite;
    }
    
    .logo-pulse {
        position: absolute;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: rgba(221, 129, 94, 0.2);
        z-index: 1;
        animation: pulse-ring 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    @keyframes pulse-ring {
        0% {
            transform: scale(0.8);
            opacity: 0.8;
        }
        50% {
            transform: scale(1.2);
            opacity: 0.2;
        }
        100% {
            transform: scale(0.8);
            opacity: 0.8;
        }
    }
    
    /* User card styling */
    .user-card {
        background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        width: 100%;
        gap: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #dd815e, #c26744);
        color: white;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(221, 129, 94, 0.3);
    }
    
    .user-greeting {
        font-weight: 500;
        color: #444;
        font-size: 1.1rem;
        margin: 0;
        text-align: left;
    }
    
    .user-name {
        color: #dd815e;
        font-weight: 600;
        display: block;
        font-size: 0.9rem;
        margin-top: 0.2rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 300px;
    }
    
    /* Welcome message styling */
    .welcome-message {
        padding: 0 1rem;
    }
    
    .welcome-message h3 {
        color: #333;
        font-size: 1.3rem;
        margin: 0 0 0.6rem 0;
    }
    
    .welcome-message p {
        color: #666;
        margin: 0;
        line-height: 1.5;
        font-size: 1rem;
    }    /* Feature carousel styling */
    .feature-carousel {
        width: 100%;
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .carousel {
        width: 100%;
        max-width: 300px;
        border-radius: 16px;
        overflow: hidden;
    }
    
    .carousel-inner {
        border-radius: 16px;
    }    .feature-card {
        background-color: #dd815e;
        border-radius: 16px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.8rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        height: 230px;
        justify-content: center;
        color: white;
        position: relative;
        overflow: hidden;
    }
      /* Custom styling for Bootstrap carousel controls */
    .carousel-control-prev,
    .carousel-control-next {
        display: none;
    }
    
    .carousel-indicators {
        display: none;
    }
    
    .carousel-indicators [data-bs-target] {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #ddd;
        border: none;
        margin: 0 4px;
        opacity: 1;
    }
    
    .carousel-indicators .active {
        background-color: #dd815e;
        transform: scale(1.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }    .feature-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
        max-width: 100%;
        text-wrap: balance;
    }
      .feature-description {
        font-size: 0.95rem;
        color: white;
        text-align: center;
        line-height: 1.5;
        overflow-wrap: break-word;
        word-wrap: break-word;
        hyphens: auto;
        max-width: 100%;
        max-height: 100px;
        overflow-y: auto;
        margin: 0 auto;
        padding: 0 5px;
    }
    
    /* Buttons container styling */
    .buttons-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
        margin-top: 0.5rem;
    }
    
    .get-started-button {
        background: linear-gradient(135deg, #dd815e, #c26744);
        color: white;
        border: none;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        box-shadow: 0 4px 12px rgba(221, 129, 94, 0.3);
    }
    
    .get-started-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(221, 129, 94, 0.4);
    }
    
    .button-icon {
        font-size: 1.2rem;
    }
    
    .dont-show-option {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0.5rem 1rem;
        cursor: pointer;
        justify-content: center;
    }
    
    .dont-show-option input[type="checkbox"] {
        appearance: none;
        -webkit-appearance: none;
        width: 18px;
        height: 18px;
        border: 2px solid #ddd;
        border-radius: 4px;
        outline: none;
        transition: all 0.2s;
        position: relative;
        cursor: pointer;
    }
    
    .dont-show-option input[type="checkbox"]:checked {
        background-color: #dd815e;
        border-color: #dd815e;
    }
    
    .dont-show-option input[type="checkbox"]:checked::after {
        content: "✓";
        color: white;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 0.8rem;
    }
    
    .checkbox-text {
        font-size: 0.9rem;
        color: #777;
    }
</style>
