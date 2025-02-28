<script>
    import { registerWithEmailAndPassword } from '$lib/firebase';
    
    let email = '';
    let password = '';
    let confirmPassword = '';
    let loading = false;
    let error = null;
    
    function validatePassword() {
        if (password !== confirmPassword) {
            return "Passwords don't match";
        }
        if (password.length < 6) {
            return "Password should be at least 6 characters";
        }
        return null;
    }
    
    async function handleRegister() {
        error = validatePassword();
        if (error) return;
        
        loading = true;
        try {
            await registerWithEmailAndPassword(email, password);
            // Auth listener will handle redirection
        } catch (err) {
            console.error("Registration error:", err);
            error = err.message || 'Registration failed. Please try again.';
        } finally {
            loading = false;
        }
    }
</script>

<form on:submit|preventDefault={handleRegister}>
    <h2>Create Account</h2>
    
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
            minlength="6"
            required
        />
    </div>
    
    <div class="form-group">
        <label for="confirm-password">Confirm Password</label>
        <input 
            type="password" 
            id="confirm-password"
            bind:value={confirmPassword}
            placeholder="Confirm your password"
            required
        />
    </div>
    
    <button type="submit" class="submit-btn" disabled={loading}>
        {loading ? 'Creating Account...' : 'Register'}
    </button>
</form>

<style>
    form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    input {
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    
    .submit-btn {
        background-color: #4285F4;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        margin-top: 0.5rem;
    }
    
    .submit-btn:hover {
        background-color: #3367D6;
    }
    
    .submit-btn:disabled {
        background-color: #b7b7b7;
        cursor: not-allowed;
    }
    
    .error {
        color: #d32f2f;
        background-color: #ffebee;
        padding: 0.75rem;
        border-radius: 4px;
    }
</style>
