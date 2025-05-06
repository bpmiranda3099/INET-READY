<script>
  import { onMount } from 'svelte';
  
  let showDeletionInstructions = false;
  let showPrivacyPolicy = true;
  
  onMount(() => {
    // Check if the URL has a hash for data-deletion
    if (window.location.hash === '#data-deletion') {
      showDeletionInstructions = true;
      showPrivacyPolicy = false;
    }
  });
  
  function toggleView(show) {
    if (show === 'deletion') {
      showDeletionInstructions = true;
      showPrivacyPolicy = false;
      window.history.pushState(null, '', '#data-deletion');
    } else {
      showDeletionInstructions = false;
      showPrivacyPolicy = true;
      window.history.pushState(null, '', window.location.pathname);
    }
  }
</script>

<svelte:head>
  <title>{showPrivacyPolicy ? 'Privacy Policy' : 'Data Deletion Instructions'} | INET-READY</title>
  <meta name="description" content={showPrivacyPolicy ? 'Privacy Policy for INET-READY - Your Heat Check for Safe and Informed Travel.' : 'How to request deletion of your data from INET-READY.'} />
</svelte:head>

{#if showDeletionInstructions}
  <div class="breadcrumbs">
    <a href="#" on:click|preventDefault={() => toggleView('privacy')}>Privacy Policy</a> &gt; Data Deletion Instructions
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
  <h1>Privacy Policy</h1>
  <p>Last updated: April 24, 2025</p>
  <p>
    INET-READY ("we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our app and services.
  </p>
  <h2>Information We Collect</h2>
  <ul>
    <li><strong>Account Information:</strong> Email address, password, and authentication data (including Google or Facebook login if used).</li>
    <li><strong>Profile & Health Data:</strong> Information you provide in your medical profile and travel preferences.</li>
    <li><strong>Usage Data:</strong> App usage statistics, device information, and analytics.</li>
  </ul>
  <h2>How We Use Your Information</h2>
  <ul>
    <li>To provide and improve our services.</li>
    <li>To personalize your experience and recommendations.</li>
    <li>To communicate with you about your account or important updates.</li>
    <li>To comply with legal obligations.</li>
  </ul>
  <h2>How We Share Your Information</h2>
  <ul>
    <li>We do <strong>not</strong> sell your personal information.</li>
    <li>We may share data with trusted service providers (such as cloud hosting and analytics) only as necessary to operate the app.</li>
    <li>We may disclose information if required by law or to protect our rights.</li>
  </ul>
  <h2>Data Security</h2>
  <p>Your data is protected using industry-standard security measures. However, no method of transmission or storage is 100% secure.</p>
  <h2>Your Rights & Choices</h2>
  <ul>
    <li>You can access, update, or delete your account information at any time from your profile settings.</li>
    <li>To request deletion of your data, please see our <a href="#" on:click|preventDefault={() => toggleView('deletion')}>Data Deletion Instructions</a>.</li>
  </ul>
  <h2>Children's Privacy</h2>
  <p>INET-READY is not intended for children under 13. We do not knowingly collect data from children under 13.</p>
  <h2>Contact Us</h2>
  <p>If you have questions about this policy, contact us at <a href="mailto:support@inet-ready.com">support@inet-ready.com</a>.</p>
  <h2>Changes to This Policy</h2>
  <p>We may update this Privacy Policy from time to time. Changes will be posted on this page.</p>
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
    margin-top: 0;
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
    margin: 0rem .5rem;
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
