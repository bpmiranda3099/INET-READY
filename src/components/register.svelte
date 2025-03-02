<script>
    import { registerWithEmailAndPassword, signInWithGoogle } from '$lib/firebase';
    
    let email = '';
    let password = '';
    let confirmPassword = '';
    let agreedToTerms = false;
    let showPassword = false;
    let showConfirmPassword = false;
    let loading = false;
    let error = null;
    let registrationSuccess = false;
    let registeredEmail = '';
    
    // Validation states
    let emailValid = true;
    let passwordStrength = { score: 0, feedback: '' };
    let passwordsMatch = true;
    
    // Password requirements
    const minLength = 8;
    const hasUppercase = /[A-Z]/;
    const hasLowercase = /[a-z]/;
    const hasNumber = /[0-9]/;
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/;
    
    // Validate email format on blur
    function validateEmail() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        emailValid = emailRegex.test(email);
        return emailValid;
    }
    
    // Check password strength and provide feedback
    function checkPasswordStrength(pwd) {
        if (!pwd) return { score: 0, feedback: '' };
        
        let score = 0;
        let feedback = [];
        
        // Length check
        if (pwd.length < minLength) {
            feedback.push(`Password must be at least ${minLength} characters`);
        } else {
            score += 1;
        }
        
        // Character variety checks
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
    
    // Check if passwords match
    function validatePasswordsMatch() {
        if (!confirmPassword) return true;
        passwordsMatch = password === confirmPassword;
        return passwordsMatch;
    }
    
    // Call on password change
    function handlePasswordChange() {
        passwordStrength = checkPasswordStrength(password);
        if (confirmPassword) validatePasswordsMatch();
    }
    
    // Validate form before submission
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
            const { user, error: registerError } = await registerWithEmailAndPassword(email, password);
            
            if (registerError) {
                if (registerError.code === 'auth/email-already-in-use') {
                    error = "This email is already registered. Try logging in instead";
                } else {
                    error = registerError.message || "Registration failed. Please try again";
                }
            } else {
                // Registration successful, now verify email
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
            const { user, error: googleError } = await signInWithGoogle();
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
    
    // Get color for password strength indicator
    $: passwordColor = passwordStrength.score === 0 ? '#ddd' : 
                       passwordStrength.score < 3 ? '#f44336' :
                       passwordStrength.score < 5 ? '#ff9800' : '#4caf50';
</script>

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
        <h2 class="subtitle mb-3" style="color: black; font-size: 2rem; margin-top: -1rem;">Create Account</h2>
        
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
                            style="width: {passwordStrength.score * 20}%; background-color: {passwordColor};"
                        ></div>
                    </div>
                    <div class="password-strength-text" style="color: {passwordColor}">
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
            style="background-color: #dd815e; font-size: 1rem; color: white; margin-top: 1rem; text-decoration: none;"
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
{/if}
