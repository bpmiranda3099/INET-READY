<script>
  import { onMount } from 'svelte';
  
  let showDeletionInstructions = false;
  let showTerms = true;
  
  onMount(() => {
    // Check if the URL has a hash for data-deletion
    if (window.location.hash === '#data-deletion') {
      showDeletionInstructions = true;
      showTerms = false;
    }
  });
  
  function toggleView(show) {
    if (show === 'deletion') {
      showDeletionInstructions = true;
      showTerms = false;
      window.history.pushState(null, '', '#data-deletion');
    } else {
      showDeletionInstructions = false;
      showTerms = true;
      window.history.pushState(null, '', window.location.pathname);
    }
  }
</script>

<svelte:head>
  <title>{showTerms ? 'Terms of Service' : 'Data Deletion Instructions'} | INET-READY</title>
  <meta name="description" content={showTerms ? 'Terms of Service for INET-READY - Your Heat Check for Safe and Informed Travel.' : 'How to request deletion of your data from INET-READY.'} />
</svelte:head>

{#if showDeletionInstructions}
  <div class="breadcrumbs">
    <a href="#" on:click|preventDefault={() => toggleView('terms')}>Terms of Service</a> &gt; Data Deletion Instructions
  </div>
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
{:else}
  <h1>Terms of Service</h1>
  <p>Last updated: April 24, 2025</p>
  <p>
    Welcome to INET-READY. By accessing or using our app and services, you agree to these Terms of Service. Please read them carefully.
  </p>
  <h2>1. Use of Service</h2>
  <ul>
    <li>You must be at least 13 years old to use INET-READY.</li>
    <li>You agree to provide accurate information and keep your account secure.</li>
    <li>You are responsible for all activity under your account.</li>
  </ul>
  <h2>2. User Content</h2>
  <ul>
    <li>You retain ownership of any content or data you submit.</li>
    <li>By submitting content, you grant us a license to use it as needed to provide our services.</li>
    <li>You must not upload unlawful, harmful, or infringing content.</li>
  </ul>
  <h2>3. Health & Travel Information</h2>
  <ul>
    <li>INET-READY provides information for general guidance only. It is not a substitute for professional medical advice.</li>
    <li>Always consult a qualified healthcare provider for medical concerns.</li>
    <li>We do not guarantee the accuracy or completeness of travel or health information.</li>
  </ul>
  <h2>4. Account Termination</h2>
  <ul>
    <li>You may delete your account at any time. See our <a href="#" on:click|preventDefault={() => toggleView('deletion')}>Data Deletion Instructions</a>.</li>
    <li>We may suspend or terminate accounts that violate these terms or applicable laws.</li>
  </ul>
  <h2>5. Limitation of Liability</h2>
  <ul>
    <li>INET-READY is provided "as is" without warranties of any kind.</li>
    <li>We are not liable for any damages resulting from your use of the app.</li>
  </ul>
  <h2>6. Changes to Terms</h2>
  <p>We may update these Terms of Service from time to time. Changes will be posted on this page. Continued use of the app means you accept the new terms.</p>
  <h2>7. Contact</h2>
  <p>For questions about these terms, contact us at <a href="mailto:support@inet-ready.com">support@inet-ready.com</a>.</p>
{/if}

<style>
  :global(body) {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #1a1a1a;
    font-size: 1.08rem;
    background-color: #f9f9f9;
  }
  
  h1, h2, p, ul, ol, div {
    max-width: 700px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }
  
  h1 {
    color: #dd815e;
    font-size: 2.1rem;
    margin-bottom: 0.7rem;
    margin-top: 2.5rem;
  }
  
  h2 {
    color: #c26744;
    font-size: 1.2rem;
    margin-top: 1.5rem;
  }
  
  a {
    color: #dd815e;
    text-decoration: underline;
  }
  
  .breadcrumbs {
    max-width: 700px;
    width: 100%;
    margin: 2rem auto 1.5rem;
    font-size: 0.9rem;
    color: #666;
  }
  
  .breadcrumbs a {
    color: #dd815e;
    text-decoration: none;
  }
  
  .breadcrumbs a:hover {
    text-decoration: underline;
  }
</style>
