<script>
    import { onMount } from 'svelte';
    import { hasMedicalRecord } from '../../lib/services/medical-api.js';
    import { 
        subscribeToAuthChanges, 
        getCurrentUser,
        isEmailVerified as isUserEmailVerified,
    } from '$lib/firebase/auth';
    
    import Login from '../../components/login.svelte';
    import Register from '../../components/register.svelte';
    import Dashboard from '../../components/dashboard.svelte';
    import MedicalForm from '../../components/medicalform.svelte';
    import VerificationStatusComponent from '../../components/verification-status.svelte';
    import WelcomeModal from '../../components/welcome-modal.svelte';

    let user = null;
    let showRegister = false;
    let needsMedicalForm = false;
    let checkingMedicalRecord = false;
    let isVerified = false;
    let justVerified = false;

    onMount(() => {
        // Check for verification status in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const mode = urlParams.get('mode');
        const oobCode = urlParams.get('oobCode');
        
        if (mode === 'verifyEmail' && oobCode) {
            // This means the user just clicked a verification link
            justVerified = true;
        }
        
        // Subscribe to authentication state changes
        const unsubscribe = subscribeToAuthChanges(async (authUser) => {
            if (authUser) {
                user = authUser;
                
                // Check if this is a Google provider or email is verified
                if (authUser.providerData.some(provider => provider.providerId === 'google.com')) {
                    isVerified = true;
                } else {
                    isVerified = isUserEmailVerified(authUser);
                }
                
                if (isVerified) {
                    // Only check medical record if verified
                    checkingMedicalRecord = true;
                    const hasMedicalProfile = await hasMedicalRecord();
                    needsMedicalForm = !hasMedicalProfile || justVerified;
                    checkingMedicalRecord = false;
                }
            } else {
                // If logged out, stay on this page but show login form
                user = null;
                showRegister = false;
                needsMedicalForm = false;
                isVerified = false;
            }
        });

        (async () => {
            // Check if user is already logged in
            user = getCurrentUser();
            if (user) {
                // Check if this is a Google provider or email is verified
                if (user.providerData.some(provider => provider.providerId === 'google.com')) {
                    isVerified = true;
                } else {
                    isVerified = isUserEmailVerified(user);
                }
                
                if (isVerified) {
                    checkingMedicalRecord = true;
                    const hasMedicalProfile = await hasMedicalRecord();
                    needsMedicalForm = !hasMedicalProfile || justVerified;
                    checkingMedicalRecord = false;
                }
            }
        })();

        // Clean up subscription when component unmounts
        return () => unsubscribe();
    });

    function toggleForm() {
        showRegister = !showRegister;
    }

    function handleMedicalFormCompleted() {
        needsMedicalForm = false;
        justVerified = false;
    }
</script>

{#if user}
    {#if !isVerified}
        <VerificationStatusComponent {user} />
    {:else if checkingMedicalRecord}
        <div class="loading-container">
            <span class="spinner"></span>
            <p>Loading your profile...</p>
        </div>
    {:else if needsMedicalForm}
        <div class="onboarding-container">
            <p class="onboarding-message">
                {#if justVerified}
                    Thank you for verifying your email! To continue,
                {:else}
                    Welcome to INET-READY! To provide you with personalized insights and recommendations, 
                {/if}
                we need to collect some information about your health and habits.
            </p>
            <MedicalForm 
                on:completed={handleMedicalFormCompleted}
            />
        </div>
    {:else}
        <Dashboard {user} />
        <WelcomeModal {user} showAlways={false} />
    {/if}
{:else}
    <div class="auth-page">
        <!-- App Bar -->
        <div class="app-bar">
            <div class="app-bar-content">
                <div class="app-bar-main">
                    <img src="/app-icon.png" alt="INET-READY" class="app-logo" />
                    <div class="app-titles">
                        <h2 class="section-title">INET-READY</h2>
                        <small class="app-title">Your Heat Check for Safe and Informed Travel</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom Navigation -->
        <div class="bottom-nav">
            <button 
                class="nav-item" 
                class:active={!showRegister}
                on:click={() => showRegister = false}
            >
                <i class="bi bi-box-arrow-in-right"></i>
                <span>Login</span>
            </button>
            <button 
                class="nav-item" 
                class:active={showRegister}
                on:click={() => showRegister = true}
            >
                <i class="bi bi-person-plus"></i>
                <span>Register</span>
            </button>
        </div>
    </div>
{/if}

<style>
    .auth-page {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        padding-bottom: 70px; /* Space for bottom nav */
        padding-top: 80px; /* Space for app bar */
        position: relative;
    }

    .app-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        background-color: #dd815e;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 16px;
        z-index: 1000;
    }

    .app-bar-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
    }

    .app-bar-main {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .app-logo {
        width: 35px;
        height: 35px;
        object-fit: contain;
    }

    .app-titles {
        display: flex;
        flex-direction: column;
    }

    .app-title {
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 1px;
        opacity: 0.8;
        margin: 0;
    }

    .section-title {
        font-size: 1.5rem;
        margin: 0;
        font-weight: 600;
    }

    .content-area {
        flex: 1;
        padding: 1rem;
    }

    .section-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        max-width: 500px;
        margin: 0 auto;
    }

    .section-body {
        padding: 2rem;
    }

    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: white;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
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
        transition: color 0.2s;
    }

    .nav-item i {
        font-size: 1.25rem;
        margin-bottom: 0.25rem;
    }

    .nav-item.active {
        color: white;
        background-color: #dd815e;
    }

    .nav-item:not(.active):hover {
        color: #dd815e;
    }

    .toggle-text {
        text-align: center;
        margin-top: 1rem;
    }

    .toggle-text button {
        background: none;
        border: none;
        color: #dd815e;
        font-weight: 600;
        cursor: pointer;
        padding: 0.25rem;
    }

    .toggle-text button:hover {
        text-decoration: underline;
    }

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        gap: 1rem;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #dd815e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .onboarding-container {
        max-width: 600px;
        margin: 2rem auto;
        padding: 1rem;
    }

    .onboarding-message {
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        color: #333;
        line-height: 1.5;
    }
</style>