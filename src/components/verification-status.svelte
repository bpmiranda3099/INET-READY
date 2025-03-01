<script>
    import { sendVerificationEmail, logoutUser } from '$lib/firebase';
    import { onDestroy } from 'svelte';
    
    export let user;
    
    let loading = false;
    let error = null;
    let success = null;
    let lastResendTime = null;
    let resendCooldown = 0;
    let resendTimer = null;
    
    // Check if user has already requested a resend recently
    const COOLDOWN_PERIOD = 60; // seconds
    
    function startCooldownTimer() {
        lastResendTime = Date.now();
        resendCooldown = COOLDOWN_PERIOD;
        
        // Store last resend time in localStorage
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(`verif_cooldown_${user.uid}`, lastResendTime.toString());
        }
        
        // Start the timer
        if (resendTimer) {
            clearInterval(resendTimer);
        }
        
        resendTimer = setInterval(() => {
            resendCooldown--;
            if (resendCooldown <= 0) {
                clearInterval(resendTimer);
                resendTimer = null;
            }
        }, 1000);
    }
    
    // Check if there's an existing cooldown
    function checkExistingCooldown() {
        if (typeof localStorage !== 'undefined' && user) {
            const storedTime = localStorage.getItem(`verif_cooldown_${user.uid}`);
            
            if (storedTime) {
                const elapsed = (Date.now() - parseInt(storedTime)) / 1000;
                if (elapsed < COOLDOWN_PERIOD) {
                    resendCooldown = Math.floor(COOLDOWN_PERIOD - elapsed);
                    startCooldownTimer();
                }
            }
        }
    }
    
    // Call this on component initialization
    checkExistingCooldown();
    
    async function handleResendVerification() {
        if (loading || resendCooldown > 0) return;
        
        loading = true;
        error = null;
        success = null;
        
        try {
            const { success: resendSuccess, error: resendError } = await sendVerificationEmail(user);
            
            if (resendSuccess) {
                success = "Verification email has been sent. Please check your inbox.";
                startCooldownTimer();
            } else {
                error = resendError.message || "Failed to send verification email. Please try again.";
            }
        } catch (err) {
            console.error("Resend verification error:", err);
            error = "An unexpected error occurred. Please try again.";
        } finally {
            loading = false;
        }
    }
    
    async function handleLogout() {
        await logoutUser();
    }
    
    // Clean up timer on component destruction
    onDestroy(() => {
        if (resendTimer) {
            clearInterval(resendTimer);
        }
    });
</script>

<div class="verification-container">
    <h2>Email Verification Required</h2>
    
    <div class="verification-card">
        <div class="verification-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
        </div>
        
        <p class="verification-message">
            We've sent a verification email to <strong>{user.email}</strong>. 
            Please check your inbox and click the verification link to activate your account.
        </p>
        
        {#if error}
            <div class="error">{error}</div>
        {/if}
        
        {#if success}
            <div class="success">{success}</div>
        {/if}
        
        <div class="verification-actions">
            <button 
                class="resend-btn" 
                on:click={handleResendVerification} 
                disabled={loading || resendCooldown > 0}
            >
                {#if resendCooldown > 0}
                    Resend Verification ({resendCooldown}s)
                {:else}
                    Resend Verification Email
                {/if}
            </button>
            
            <button class="logout-btn" on:click={handleLogout}>
                Back to Login
            </button>
        </div>
        
        <div class="verification-tips">
            <h4>Can't find the email?</h4>
            <ul>
                <li>Check your spam or junk folder</li>
                <li>Make sure your email address is correct</li>
                <li>Try adding noreply@firebase.com to your contacts</li>
            </ul>
        </div>
    </div>
</div>