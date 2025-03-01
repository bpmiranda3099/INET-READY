<script>
    import { sendVerificationEmail, logoutUser } from '$lib/firebase';
    
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
    import { onDestroy } from 'svelte';
    
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

<style>
    .verification-container {
        max-width: 600px;
        margin: 0 auto;
        padding: var(--spacing-xl) var(--spacing-md);
        text-align: center;
    }
    
    .verification-card {
        background-color: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
    }
    
    .verification-icon {
        display: flex;
        justify-content: center;
        margin-bottom: var(--spacing-lg);
        color: var(--primary-color);
    }
    
    .verification-message {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: var(--spacing-lg);
    }
    
    .verification-actions {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
        margin: var(--spacing-xl) 0;
    }
    
    .resend-btn {
        background-color: var(--primary-color-light);
        color: var(--primary-color-dark);
        border: none;
        padding: var(--spacing-md);
        border-radius: var(--radius-md);
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .resend-btn:hover:not(:disabled) {
        background-color: var(--primary-color-lighter);
    }
    
    .resend-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    .logout-btn {
        background-color: transparent;
        border: 1px solid var(--border-color-dark);
        color: var(--text-color);
        padding: var(--spacing-md);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .logout-btn:hover {
        background-color: var(--bg-light);
    }
    
    .verification-tips {
        background-color: var(--bg-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        margin-top: var(--spacing-lg);
        text-align: left;
    }
    
    .verification-tips h4 {
        margin-top: 0;
        margin-bottom: var(--spacing-sm);
        color: var(--text-color);
    }
    
    .verification-tips ul {
        margin: 0;
        padding-left: var(--spacing-lg);
    }
    
    .verification-tips li {
        margin-bottom: var(--spacing-xs);
    }
    
    .success {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
        border-radius: var(--radius-sm);
        padding: var(--spacing-md);
        margin: var(--spacing-md) 0;
    }
    
    .error {
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ef9a9a;
        border-radius: var(--radius-sm);
        padding: var(--spacing-md);
        margin: var(--spacing-md) 0;
    }
    
    @media (min-width: 480px) {
        .verification-actions {
            flex-direction: row;
            justify-content: center;
        }
        
        .resend-btn, .logout-btn {
            min-width: 200px;
        }
    }
</style>