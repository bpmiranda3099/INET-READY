<script>
    import { onMount } from 'svelte';
    import { 
        subscribeToAuthChanges, 
        getCurrentUser,
        hasMedicalRecord,
        isEmailVerified,
        sendVerificationEmail
    } from '$lib/firebase';
    
    import Login from '../../components/login.svelte';
    import Register from '../../components/register.svelte';
    import Dashboard from '../../components/dashboard.svelte';
    import MedicalForm from '../../components/medicalform.svelte';
    import VerificationStatusComponent from '../../components/verification-status.svelte';

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
                    isVerified = isEmailVerified(authUser);
                }
                
                if (isVerified) {
                    // Only check medical record if verified
                    checkingMedicalRecord = true;
                    const hasMedicalProfile = await hasMedicalRecord(authUser.uid);
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
                    isVerified = isEmailVerified(user);
                }
                
                if (isVerified) {
                    checkingMedicalRecord = true;
                    const hasMedicalProfile = await hasMedicalRecord(user.uid);
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
                <h1>Complete Your Medical Profile</h1>
                <p class="onboarding-message">
                    {#if justVerified}
                        Thank you for verifying your email! To continue,
                    {:else}
                        Welcome to INET-READY! To provide you with personalized insights and recommendations, 
                    {/if}
                    we need to collect some information about your health and habits.
                </p>
                <MedicalForm 
                    userId={user.uid} 
                    on:completed={handleMedicalFormCompleted}
                />
            </div>
        {:else}
            <Dashboard {user} />
        {/if}
    {:else}
        <div class="auth-container">
            <div class="container">
				<div class="row justify-content-center">
					<div class="col-md-10">
                        <div class="d-flex justify-content-center">
                            <i class="bi bi-sun-fill" style="font-size: 10rem; color: #e0b76b; clip-path: inset(0 0 40% 0);"></i>
                        </div>
						<h1 class="display-1 fw-bold mb-4" style="font-size: 3rem; margin-top: -6rem;">INET-READY</h1>
						<p class="subtitle mb-3" style="font-size: 1.25rem;">Your Heat Check for Safe and Informed Travel</p>
					</div>
				</div>
			</div>
            
            {#if !showRegister}
                <Login />
                <p>Don't have an account? <button on:click={toggleForm}>Register</button></p>
            {:else}
                <Register />
                <p>Already have an account? <button on:click={toggleForm}>Login</button></p>
            {/if}
        </div>
    {/if}
</div>