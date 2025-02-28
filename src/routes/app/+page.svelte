<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { subscribeToAuthChanges, getCurrentUser } from '$lib/firebase';
    import Login from '../../components/login.svelte';
    import Register from '../../components/register.svelte';
    import Dashboard from '../../components/dashboard.svelte';

    let user = null;
    let showRegister = false;

    onMount(() => {
        // Subscribe to authentication state changes
        const unsubscribe = subscribeToAuthChanges((authUser) => {
            user = authUser;
            if (!authUser) {
                // If logged out, stay on this page but show login form
                showRegister = false;
            }
        });

        // Check if user is already logged in
        user = getCurrentUser();

        // Clean up subscription when component unmounts
        return unsubscribe;
    });

    function toggleForm() {
        showRegister = !showRegister;
    }
</script>

<div class="container">
    {#if user}
        <Dashboard {user} />
    {:else}
        <div class="auth-container">
            <h1>INET-READY</h1>
            
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