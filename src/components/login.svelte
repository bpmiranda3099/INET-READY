<script>
    import { loginWithEmailAndPassword, signInWithGoogle, sendPasswordReset, isEmailVerified, sendVerificationEmail } from '$lib/firebase';
    
    let email = '';
    let password = '';
    let showPassword = false;
    let rememberMe = false;
    let loading = false;
    let error = null;
    let emailValid = true;
    let unverifiedUser = null;
    let resendCooldown = 0;
    let resendTimer = null;
    
    // Function to validate email format
    function validateEmail() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        emailValid = emailRegex.test(email);
        return emailValid;
    }
    
    async function handleLogin() {
        if (!validateEmail()) {
            error = "Please enter a valid email address";
            return;
        }
        
        if (password.length < 6) {
            error = "Password must be at least 6 characters";
            return;
        }
        
        error = null;
        loading = true;
        unverifiedUser = null;
        
        try {
            const { user, error: loginError } = await loginWithEmailAndPassword(email, password, rememberMe);
            
            if (loginError) {
                if (loginError.code === 'auth/user-not-found' || loginError.code === 'auth/wrong-password') {
                    error = "Email or password is incorrect";
                } else if (loginError.code === 'auth/too-many-requests') {
                    error = "Too many failed login attempts. Please try again later";
                } else {
                    error = loginError.message || "Failed to login. Please try again";
                }
            } else if (user) {
                // Check if email is verified
                if (!isEmailVerified(user) && !user.providerData.some(provider => provider.providerId === 'google.com')) {
                    unverifiedUser = user;
                    error = "Please verify your email address before logging in";
                }
            }
        } catch (err) {
            console.error("Login error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }
    
    async function handleResendVerification() {
        if (!unverifiedUser || resendCooldown > 0) return;
        
        loading = true;
        try {
            const { success, error: resendError } = await sendVerificationEmail(unverifiedUser);
            if (success) {
                // Start cooldown timer
                resendCooldown = 60;
                resendTimer = setInterval(() => {
                    resendCooldown--;
                    if (resendCooldown <= 0) {
                        clearInterval(resendTimer);
                        resendTimer = null;
                    }
                }, 1000);
                
                error = "Verification email has been resent. Please check your inbox.";
            } else {
                error = resendError.message || "Failed to resend verification email";
            }
        } catch (err) {
            console.error("Resend verification error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }
    
    async function handleGoogleLogin() {
        error = null;
        loading = true;
        unverifiedUser = null;
        
        try {
            const { user, error: googleError } = await signInWithGoogle();
            if (googleError) {
                error = googleError.message || "Google login failed. Please try again";
            }
        } catch (err) {
            console.error("Google login error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }
    
    async function handleForgotPassword() {
        if (!email) {
            error = "Please enter your email address first";
            return;
        }
        
        if (!validateEmail()) {
            error = "Please enter a valid email address";
            return;
        }
        
        error = null;
        loading = true;
        
        try {
            const { success, error: resetError } = await sendPasswordReset(email);
            if (success) {
                error = null;
                alert("Password reset link has been sent to your email");
            } else {
                error = resetError.message || "Failed to send password reset email";
            }
        } catch (err) {
            console.error("Password reset error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }
</script>

<form on:submit|preventDefault={handleLogin} novalidate>
    <h2 class="subtitle mb-3" style="color: black; font-size: 2rem; margin-top: -1rem;">Login</h2>
    
    {#if error}
        <div class="error">{error}</div>
    {/if}
    
    {#if unverifiedUser}
        <div class="verification-required">
            <p>Your email address has not been verified.</p>
            <button 
                type="button" 
                class="resend-btn" 
                on:click={handleResendVerification}
                disabled={loading || resendCooldown > 0}
            >
                {#if resendCooldown > 0}
                    Resend in {resendCooldown}s
                {:else}
                    Resend Verification Email
                {/if}
            </button>
        </div>
    {/if}
    
    <div class="form-group">
        <label for="email">Email Address</label>
        <input 
            type="email" 
            id="email"
            bind:value={email}
            on:blur={validateEmail}
            class:invalid={!emailValid && email}
            placeholder="your@email.com"
            autocomplete="email"
            required
        />
        {#if !emailValid && email}
            <div class="field-error">Please enter a valid email address</div>
        {/if}
    </div>
    
    <div class="form-group">
        <label for="password">Password</label>
        <div class="password-container">
            <input 
                type={showPassword ? "text" : "password"}
                id="password"
                bind:value={password}
                placeholder="Enter your password"
                autocomplete="current-password"
                required
            />
            {#if password.length > 0}
                <button 
                    type="button" 
                    class="toggle-password" 
                    on:click={() => showPassword = !showPassword}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                >
                    {showPassword ? 'Hide' : 'Show'}
                </button>
            {/if}
        </div>
    </div>
    
    <div class="form-options">
        <label class="checkbox-container">
            <input type="checkbox" bind:checked={rememberMe}>
            <span class="checkmark"></span>
            Remember me
        </label>
        <button type="button" class="forgot-password" on:click={handleForgotPassword}>
            Forgot password?
        </button>
    </div>
    
    <button
        type="submit" 
        class="submit-btn subtitle mb-3" 
        style="background-color: #dd815e; font-size: 1rem; color: white; margin-top: 1rem; text-decoration: none;"
        disabled={loading || !email || !password}
    >
        {#if loading}
            <span class="spinner"></span>
            <span>Logging in...</span>
        {:else}
            Login
        {/if}
    </button>
    
    <div class="divider">
        <span>or</span>
    </div>
    
    <button 
        type="button" 
        class="google-btn" 
        on:click={handleGoogleLogin}
        disabled={loading}
    >
        <img 
            src="https://upload.wikimedia.org/wikipedia/commons/archive/c/c1/20190923152039%21Google_%22G%22_logo.svg" 
            alt="Google Logo" 
            width="18" 
            height="18"
            style="margin-bottom: 3rem;"
        />
        <span style="margin-bottom: 3rem;">Sign in with Google</span>
    </button>
</form>
