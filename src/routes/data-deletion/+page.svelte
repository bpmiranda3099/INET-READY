<script>
  import { onMount } from 'svelte';
  
  // Check if the user came from privacy or terms page
  let referrer = '';
  
  onMount(() => {
    // Check and store the referrer if coming from privacy or terms
    if (document.referrer.includes('/privacy')) {
      referrer = '/privacy';
    } else if (document.referrer.includes('/terms')) {
      referrer = '/terms';
    }
    
    // If coming from privacy or terms, redirect with hash
    if (referrer) {
      window.location.href = `${referrer}#data-deletion`;
    }
  });
</script>

<svelte:head>
  <title>Data Deletion Instructions | INET-READY</title>
  <meta name="description" content="How to request deletion of your data from INET-READY." />
</svelte:head>

<div class="policy-container">
  <h1>Data Deletion Instructions</h1>
  <p>Last updated: April 24, 2025</p>
  <p>
    You have the right to request deletion of your account and all associated data from INET-READY at any time.
  </p>
  <h2>How to Request Data Deletion</h2>
  <ol>
    <li>Send an email to <a href="mailto:support@inet-ready.com">support@inet-ready.com</a> from the email address associated with your INET-READY account.</li>
    <li>Include the subject line: <strong>"Data Deletion Request"</strong>.</li>
    <li>In the body of the email, please confirm your request to delete your account and all related data.</li>
  </ol>
  <p>
    Once we receive your request, we will verify your identity and process the deletion within 30 days. You will receive a confirmation email when your data has been deleted.
  </p>
  <h2>Questions?</h2>
  <p>If you have any questions, contact us at <a href="mailto:support@inet-ready.com">support@inet-ready.com</a>.</p>
  
  <div class="navigation-links">
    <a href="/privacy">View Privacy Policy</a> | <a href="/terms">View Terms of Service</a>
  </div>
</div>

<style>
.policy-container {
  max-width: 700px;
  margin: 2rem auto;
  background: #fff;
  border-radius: 1.5rem;
  box-shadow: 0 2px 12px rgba(221,129,94,0.08);
  padding: 2.5rem 1.5rem;
  color: #1a1a1a;
  font-size: 1.08rem;
}
.policy-container h1 {
  color: #dd815e;
  font-size: 2.1rem;
  margin-bottom: 0.7rem;
}
.policy-container h2 {
  color: #c26744;
  font-size: 1.2rem;
  margin-top: 1.5rem;
}
.policy-container a {
  color: #dd815e;
  text-decoration: underline;
}
.navigation-links {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  text-align: center;
  font-size: 0.9rem;
}
</style>
