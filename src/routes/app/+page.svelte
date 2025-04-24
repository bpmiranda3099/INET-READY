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

<div class="container">
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
                <!-- Removed duplicate h1: Complete Your Medical Profile -->
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
            </div>        {:else}
            <Dashboard {user} />
            <WelcomeModal {user} showAlways={false} />
        {/if}
    {:else}
        <div class="dashboard" style="min-height: 100vh; padding-bottom: 70px; padding-top: 80px;">
            <!-- App Bar -->
            <div class="app-bar">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <img src="/app-icon.png" alt="INET-READY Logo" style="height: 48px; width: 48px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); background: white;" />
                    <div style="display: flex; flex-direction: column; justify-content: center;">
                        <span class="app-title" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8;">INET-READY</span>
                        <span style="font-size: 1.1rem; color: white; font-weight: 500;">Your Heat Check for Safe and Informed Travel</span>
                    </div>
                </div>
            </div>
            <div class="container" style="max-width: 100%; margin: 0 auto; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh;">
                <div style="width: 100%; max-width: 420px; margin: 0 auto;">
                    {#if !showRegister}
                        <Login />
                        <p style="text-align: center; margin-top: 1.5rem;">Don't have an account? <button on:click={toggleForm}>Register</button></p>
                    {:else}
                        <Register />
                        <p style="text-align: center; margin-top: 1.5rem;">Already have an account? <button on:click={toggleForm}>Login</button></p>
                    {/if}
                </div>
            </div>
            <!-- Bottom Navigation Bar -->
            <div class="bottom-nav">
                <button class="nav-item active" style="pointer-events: none;">
                    <i class="bi bi-house"></i>
                    <span>Home</span>
                </button>
                <button class="nav-item" style="pointer-events: none;">
                    <i class="bi bi-heart-pulse"></i>
                    <span>Medical</span>
                </button>
                <button class="nav-item" style="pointer-events: none;">
                    <i class="bi bi-bell"></i>
                    <span>Notifications</span>
                </button>
                <button class="nav-item" style="pointer-events: none;">
                    <i class="bi bi-gear"></i>
                    <span>Settings</span>
                </button>
                <button class="nav-item" style="pointer-events: none;">
                    <i class="bi bi-person"></i>
                    <span>Account</span>
                </button>
            </div>
        </div>
    {/if}
</div>