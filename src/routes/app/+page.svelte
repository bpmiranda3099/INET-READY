<script>
    import { onMount } from 'svelte';
    import { hasMedicalRecord } from '../../lib/services/medical-api.js';    import { 
        subscribeToAuthChanges, 
        getCurrentUser,
        isEmailVerified as isUserEmailVerified,
        loginWithEmailAndPassword,
        registerWithEmailAndPassword,
        signInWithGoogle,
        signInWithFacebook,
        sendPasswordReset,
        sendVerificationEmail
    } from '$lib/firebase/auth';
    
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

    // Login variables
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

    // Registration variables
    let confirmPassword = '';
    let agreedToTerms = false;
    let showConfirmPassword = false;
    let registrationSuccess = false;
    let registeredEmail = '';
    let passwordStrength = { score: 0, feedback: '' };
    let passwordsMatch = true;

    // Password requirements
    const minLength = 8;
    const hasUppercase = /[A-Z]/;
    const hasLowercase = /[a-z]/;
    const hasNumber = /[0-9]/;
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/;

    // Login functions
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
            const { user: authUser, error: loginError } = await loginWithEmailAndPassword(email, password, rememberMe);
            
            if (loginError) {
                if (loginError.code === 'auth/user-not-found' || loginError.code === 'auth/wrong-password') {
                    error = "Email or password is incorrect";
                } else if (loginError.code === 'auth/too-many-requests') {
                    error = "Too many failed login attempts. Please try again later";
                } else {
                    error = loginError.message || "Failed to login. Please try again";
                }
            } else if (authUser) {
                if (!isUserEmailVerified(authUser) && !authUser.providerData.some(provider => provider.providerId === 'google.com')) {
                    unverifiedUser = authUser;
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
    }    async function handleGoogleLogin() {
        error = null;
        loading = true;
        unverifiedUser = null;
        
        try {
            const { user: authUser, error: googleError } = await signInWithGoogle();
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

    async function handleFacebookLogin() {
        error = null;
        loading = true;
        unverifiedUser = null;
        
        try {
            const { user: authUser, error: facebookError } = await signInWithFacebook();
            if (facebookError) {
                error = facebookError.message || "Facebook login failed. Please try again";
            }
        } catch (err) {
            console.error("Facebook login error:", err);
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

    // Registration functions
    function checkPasswordStrength(pwd) {
        if (!pwd) return { score: 0, feedback: '' };
        
        let score = 0;
        let feedback = [];
        
        if (pwd.length < minLength) {
            feedback.push(`Password must be at least ${minLength} characters`);
        } else {
            score += 1;
        }
        
        if (!hasUppercase.test(pwd)) {
            feedback.push('Add an uppercase letter');
        } else {
            score += 1;
        }
        
        if (!hasLowercase.test(pwd)) {
            feedback.push('Add a lowercase letter');
        } else {
            score += 1;
        }
        
        if (!hasNumber.test(pwd)) {
            feedback.push('Add a number');
        } else {
            score += 1;
        }
        
        if (!hasSpecial.test(pwd)) {
            feedback.push('Add a special character (!@#$%^&*...)');
        } else {
            score += 1;
        }
        
        return {
            score,
            feedback: feedback.join(', ')
        };
    }

    function validatePasswordsMatch() {
        if (!confirmPassword) return true;
        passwordsMatch = password === confirmPassword;
        return passwordsMatch;
    }

    function handlePasswordChange() {
        passwordStrength = checkPasswordStrength(password);
        if (confirmPassword) validatePasswordsMatch();
    }

    function validateForm() {
        if (!emailValid) return false;
        if (passwordStrength.score < 3) return false;
        if (!passwordsMatch) return false;
        if (!agreedToTerms) return false;
        return true;
    }

    async function handleRegister() {
        if (!validateForm()) {
            if (!emailValid) {
                error = "Please enter a valid email address";
            } else if (passwordStrength.score < 3) {
                error = "Please create a stronger password";
            } else if (!passwordsMatch) {
                error = "Passwords don't match";
            } else if (!agreedToTerms) {
                error = "You must agree to the Terms and Conditions";
            }
            return;
        }
        
        error = null;
        loading = true;
        
        try {
            const { user: authUser, error: registerError } = await registerWithEmailAndPassword(email, password);
            
            if (registerError) {
                if (registerError.code === 'auth/email-already-in-use') {
                    error = "This email is already registered. Try logging in instead";
                } else {
                    error = registerError.message || "Registration failed. Please try again";
                }
            } else {
                registrationSuccess = true;
                registeredEmail = email;
            }
        } catch (err) {
            console.error("Registration error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }

    async function handleGoogleSignup() {
        if (!agreedToTerms) {
            error = "You must agree to the Terms and Conditions";
            return;
        }
        
        error = null;
        loading = true;
        
        try {
            const { user: authUser, error: googleError } = await signInWithGoogle();
            if (googleError) {
                error = googleError.message || "Google signup failed. Please try again";
            }
        } catch (err) {
            console.error("Google signup error:", err);
            error = "An unexpected error occurred. Please try again";
        } finally {
            loading = false;
        }
    }

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
        return () => {
            unsubscribe();
            if (resendTimer) {
                clearInterval(resendTimer);
            }
        };
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

        <div class="content-area">
            <div class="section-container">                <div class="section-header">
                    <h3>{showRegister ? 'Create Your Account' : 'Sign In To Your Account'}</h3>
                </div>
                <div class="section-body">
                    {#if showRegister}
                        {#if registrationSuccess}
                            <div class="success-container">
                                <h2>Verification Email Sent</h2>
                                <div class="verification-message">
                                    <p>We've sent a verification email to <strong>{registeredEmail}</strong>.</p>
                                    <p>Please check your inbox and click the verification link to activate your account.</p>
                                    <p class="small-text">If you don't see the email, check your spam folder.</p>
                                    <p class="warning">You must verify your email address before you can log in.</p>
                                </div>
                                <button class="submit-btn" on:click={() => registrationSuccess = false}>
                                    Return to Login
                                </button>
                            </div>
                        {:else}
                            <form on:submit|preventDefault={handleRegister} novalidate>
                                {#if error}
                                    <div class="error">{error}</div>
                                {/if}
                                
                                <div class="form-group">
                                    <label for="register-email">Email Address</label>
                                    <input 
                                        type="email" 
                                        id="register-email"
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
                                    <label for="register-password">Password</label>
                                    <div class="password-container">
                                        <input 
                                            type={showPassword ? "text" : "password"}
                                            id="register-password"
                                            bind:value={password}
                                            on:input={handlePasswordChange}
                                            placeholder="Create a strong password"
                                            autocomplete="new-password"
                                            minlength={minLength}
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
                                    
                                    {#if password}
                                        <div class="password-strength-container">
                                            <div class="password-strength-bar">
                                                <div 
                                                    class="password-strength-indicator" 
                                                    style="width: {passwordStrength.score * 20}%; background-color: {passwordStrength.score === 0 ? '#ddd' : passwordStrength.score < 3 ? '#f44336' : passwordStrength.score < 5 ? '#ff9800' : '#4caf50'};"
                                                ></div>
                                            </div>
                                            <div class="password-strength-text" style="color: {passwordStrength.score === 0 ? '#ddd' : passwordStrength.score < 3 ? '#f44336' : passwordStrength.score < 5 ? '#ff9800' : '#4caf50'}">
                                                {#if passwordStrength.score === 0}
                                                    Enter a password
                                                {:else if passwordStrength.score < 3}
                                                    Weak
                                                {:else if passwordStrength.score < 5}
                                                    Good
                                                {:else}
                                                    Strong
                                                {/if}
                                            </div>
                                        </div>
                                        {#if passwordStrength.feedback}
                                            <div class="field-info">{passwordStrength.feedback}</div>
                                        {/if}
                                    {/if}
                                </div>
                                
                                <div class="form-group">
                                    <label for="confirm-password">Confirm Password</label>
                                    <div class="password-container">
                                        <input 
                                            type={showConfirmPassword ? "text" : "password"}
                                            id="confirm-password"
                                            bind:value={confirmPassword}
                                            on:input={validatePasswordsMatch}
                                            on:blur={validatePasswordsMatch}
                                            class:invalid={!passwordsMatch && confirmPassword}
                                            placeholder="Confirm your password"
                                            autocomplete="new-password"
                                            required
                                        />
                                        {#if confirmPassword.length > 0}
                                            <button 
                                                type="button" 
                                                class="toggle-password" 
                                                on:click={() => showConfirmPassword = !showConfirmPassword}
                                                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                                            >
                                                {showConfirmPassword ? 'Hide' : 'Show'}
                                            </button>
                                        {/if}
                                    </div>
                                    {#if !passwordsMatch && confirmPassword}
                                        <div class="field-error">Passwords don't match</div>
                                    {/if}
                                </div>
                                
                                <div class="form-group">
                                    <label class="checkbox-container terms-checkbox">
                                        <input type="checkbox" bind:checked={agreedToTerms}>
                                        <span class="checkmark"></span>
                                        I agree to the <a href="/terms" target="_blank">&nbsp;Terms of Service&nbsp;</a> and <a href="/privacy" target="_blank">&nbsp;Privacy Policy</a>
                                    </label>
                                </div>
                                
                                <button 
                                    type="submit" 
                                    class="submit-btn subtitle mb-3" 
                                    style="background-color: #dd815e; font-size: 1rem; color: white; text-decoration: none;"
                                    disabled={loading || !validateForm()}
                                >
                                    {#if loading}
                                        <span class="spinner"></span>
                                        <span>Creating Account...</span>
                                    {:else}
                                        Create Account
                                    {/if}
                                </button>
                                
                                <div class="divider">
                                    <span>or</span>
                                </div>
                                <button 
                                    type="button" 
                                    class="google-btn"
                                    on:click={handleGoogleSignup}
                                    disabled={loading}
                                    style="margin-bottom: 1rem;"
                                >
                                    <i class="bi bi-google" style="font-size: 1.2rem;"></i>
                                    <span>Sign in with Google</span>
                                </button>

                                <button 
                                type="button" 
                                class="facebook-btn" 
                                on:click={handleFacebookLogin}
                                disabled={loading}
                            >
                                <i class="bi bi-facebook" style="font-size: 1.2rem;"></i>
                                <span>Sign in with Facebook</span>
                            </button>
                            </form>
                        {/if}
                    {:else}
                        <form on:submit|preventDefault={handleLogin} novalidate>
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
                                <div class="password-container">                    <input 
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
                                style="background-color: #dd815e; font-size: 1rem; color: white; text-decoration: none;"
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
                            </div>                              <button 
                                type="button" 
                                class="google-btn" 
                                on:click={handleGoogleLogin}
                                disabled={loading}
                                style="margin-bottom: 1rem;"
                            >
                                <i class="bi bi-google" style="font-size: 1.2rem;"></i>
                                <span>Sign in with Google</span>
                            </button>

                            <button 
                                type="button" 
                                class="facebook-btn" 
                                on:click={handleFacebookLogin}
                                disabled={loading}
                            >
                                <i class="bi bi-facebook" style="font-size: 1.2rem;"></i>
                                <span>Sign in with Facebook</span>
                            </button>
                        </form>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}

<style>    
.auth-page {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        padding-bottom: 60px; /* Space for bottom nav */
        padding-top: 60px; /* Space for app bar */
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
    }    .content-area {
        flex: 1;
        padding: 1rem 0;
        margin-top: 1rem;
    }    .section-container {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        width: 100%;
        margin: 0 auto;
    }

    .section-container .section-header {
        background: #dd815e;
        color: white;
        padding: 1rem;
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        overflow: hidden;
    }

    .section-container .section-header::after {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }

    .section-container .section-header h3 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
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
    }    .loading-container {
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

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .password-container {
        position: relative;
    }

    .toggle-password {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 5px;
    }

    .password-strength-container {
        margin-top: 0.5rem;
    }

    .password-strength-bar {
        height: 4px;
        background-color: #eee;
        border-radius: 2px;
        overflow: hidden;
    }

    .password-strength-indicator {
        height: 100%;
        transition: width 0.3s, background-color 0.3s;
    }

    .password-strength-text {
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .field-error {
        color: #f44336;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .field-info {
        color: #666;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .checkbox-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
    }

    .forgot-password {
        background: none;
        border: none;
        color: #dd815e;
        cursor: pointer;
        padding: 0.25rem;
    }

    .forgot-password:hover {
        text-decoration: underline;
    }    .submit-btn {
        width: 100%;
        border: none;
        border-radius: 8px;
        font-family: inherit;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .submit-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
    }

    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #ddd;
    }

    .divider span {
        padding: 0 10px;
        color: #666;
        font-size: 0.9rem;
    }    .google-btn {
        width: 100%;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        background: #dc3545;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: opacity 0.2s;
        font-family: inherit;
        font-weight: 600;
        font-size: 1rem;
    }

    .google-btn:hover {
        opacity: 0.9;
    }    .google-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .facebook-btn {
        width: 100%;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        background: #1877f2;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: opacity 0.2s;
        font-family: inherit;
        font-weight: 600;
        font-size: 1rem;
    }

    .facebook-btn:hover {
        opacity: 0.9;
    }

    .facebook-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .success-container {
        text-align: center;
        padding: 2rem;
    }

    .verification-message {
        margin: 1.5rem 0;
    }

    .verification-required {
        background-color: #fff3e0;
        border: 1px solid #ffe0b2;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .resend-btn {
        background: none;
        border: none;
        color: #dd815e;
        cursor: pointer;
        padding: 0.5rem;
        margin-top: 0.5rem;
    }

    .resend-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .error {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .warning {
        color: #f57c00;
        font-weight: 500;
    }

    .small-text {
        font-size: 0.9rem;
        color: #666;
    }

    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: spin 0.75s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-size: 1rem;
    }

    input:focus {
        outline: none;
        border-color: #dd815e;
    }

    input.invalid {
        border-color: #f44336;
    }

    .terms-checkbox {
        font-size: 0.9rem;
    }

    .terms-checkbox a {
        color: #dd815e;
        text-decoration: none;
    }

    .terms-checkbox a:hover {
        text-decoration: underline;
    }
</style>