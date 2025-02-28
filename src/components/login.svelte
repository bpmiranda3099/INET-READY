<script>
    import { loginWithEmailAndPassword, signInWithGoogle } from '$lib/firebase';
    
    let email = '';
    let password = '';
    let loading = false;
    let error = null;
    
    async function handleLogin() {
        error = null;
        loading = true;
        
        try {
            await loginWithEmailAndPassword(email, password);
            // No need to redirect, the auth listener will handle it
        } catch (err) {
            console.error("Login error:", err);
            error = err.message || 'Login failed. Please try again.';
        } finally {
            loading = false;
        }
    }    
    
    async function handleGoogleLogin() {
        error = null;
        loading = true;
        
        try {
            await signInWithGoogle();
            // Auth listener will handle redirection
        } catch (err) {
            console.error("Google login error:", err);
            error = err.message || 'Google login failed. Please try again.';
        } finally {
            loading = false;
        }
    }
</script>

<form on:submit|preventDefault={handleLogin}>
    <h2>Login</h2>
    
    {#if error}
        <div class="error">{error}</div>
    {/if}
    
    <div class="form-group">
        <label for="email">Email</label>
        <input 
            type="email" 
            id="email"
            bind:value={email}
            placeholder="Enter your email"
            required
        />
    </div>
    
    <div class="form-group">
        <label for="password">Password</label>
        <input 
            type="password" 
            id="password"
            bind:value={password}
            placeholder="Enter your password"
            required
        />
    </div>
    
    <button type="submit" class="submit-btn" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
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
        />
        <span>Sign in with Google</span>
    </button>
</form>
