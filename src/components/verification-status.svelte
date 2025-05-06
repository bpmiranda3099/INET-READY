<script>    import { sendVerificationEmail, logoutUser } from '$lib/firebase';
    import { onDestroy, onMount } from 'svelte';
    
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

<svelte:head>
    <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script>
</svelte:head>

<h2>Email Verification Required</h2>

<div class="verification-icon">
    <dotlottie-player
      src="https://lottie.host/968cbead-20d7-4607-9854-3ebc3f044716/MmY1zA0krS.lottie"
      background="transparent"
      speed="1"
      style="width: 200px; height: 200px"
      loop
      autoplay
    ></dotlottie-player>
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

<style>  :global(body) {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #1a1a1a;
    font-size: 1.08rem;
    background-color: #f9f9f9;
  }
  
  h2, h4, p, ul, div {
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
  }
  
  h2 {
    color: #dd815e;
    font-size: 2.1rem;
    margin-bottom: 0.7rem;
    margin-top: 2rem;
    text-align: center;
  }
  
  h4 {
    color: #c26744;
    font-size: 1.2rem;
    margin-top: 0.7rem;
    margin-bottom: 0.7rem;
  }
    .verification-icon {
    display: flex;
    justify-content: center;
    margin-bottom: 1.5rem;
  }
  
  .verification-message {
    margin-bottom: 1.5rem;
    text-align: center;
    margin-left: 1rem;
    margin-right: 1rem;
  }
  
  .verification-actions {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    margin-top: 1.5rem;
  }
  
  button {
    padding: 0.6rem 1.2rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
    border: none;
    width: 100%;
  }
  
  .resend-btn {
    background-color: #dd815e;
    color: white;
  }
  
  .resend-btn:hover:not(:disabled) {
    background-color: #c26744;
  }
  
  .resend-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  .logout-btn {
    background-color: transparent;
    color: #dd815e;
    border: 1px solid #dd815e;
  }
  
  .logout-btn:hover {
    background-color: rgba(221, 129, 94, 0.1);
  }
  
  .verification-tips {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    padding-bottom: 1rem;
  }
  
  .verification-tips ul {
    padding-left: 1.5rem;
    margin-top: 0.5rem;
  }
  
  .verification-tips li {
    margin-bottom: 0.5rem;
  }
  
  .error {
    color: #e74c3c;
    background-color: #fdecea;
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  .success {
    color: #27ae60;
    background-color: #e8f8f0;
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  a {
    color: #dd815e;
    text-decoration: underline;
  }
</style>