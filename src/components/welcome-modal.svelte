<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { fly, fade } from 'svelte/transition';
      export let user = {};
    export let showAlways = false;
    
    const dispatch = createEventDispatcher();
    let showWelcome = true;
    let doNotShowAgain = false;
    
    onMount(() => {
        // Check local storage to see if the user has chosen to hide the welcome message
        const hideWelcome = localStorage.getItem('inet-ready-hide-welcome');
        if (hideWelcome === 'true' && !showAlways) {
            showWelcome = false;
        }
    });
    
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
                </div>
                
                <div class="feature-cards">
                    <div class="feature-card">
                        <div class="feature-icon">🌡️</div>
                        <div class="feature-text">Heat Index Alerts</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💊</div>
                        <div class="feature-text">Medication Reminders</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🩺</div>
                        <div class="feature-text">Health Recommendations</div>
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
    }
    
    /* Feature cards styling */
    .feature-cards {
        display: flex;
        gap: 1rem;
        width: 100%;
        margin: 0.5rem 0;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .feature-card {
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 1rem;
        width: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.7rem;
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background-color: #f0f0f0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    .feature-icon {
        font-size: 1.8rem;
    }
    
    .feature-text {
        font-size: 0.85rem;
        font-weight: 500;
        color: #555;
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
