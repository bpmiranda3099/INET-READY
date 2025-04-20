<script>
import { onMount } from 'svelte';
import { askGemini } from '$lib/services/gemini-service';
import { getMedicalData } from '$lib/services/medical-api';
import { getAllHeatIndexData, getHeatIndexPredictions } from '$lib/services/weather-data-service';

export let onClose = () => {};
export let user = null;

let input = '';
let messages = [];
let loading = false;
let error = null;
let medicalData = null;
let heatIndexData = null;
let heatIndexPredictions = null;

onMount(async () => {
  try {
    medicalData = await getMedicalData();
    heatIndexData = await getAllHeatIndexData();
    heatIndexPredictions = await getHeatIndexPredictions();
  } catch (e) {
    error = 'Failed to load context data.';
  }
});

async function sendMessage() {
  if (!input.trim()) return;
  messages = [...messages, { sender: 'user', text: input }];
  loading = true;
  error = null;
  try {
    const context = {
      user,
      medicalData,
      heatIndexData,
      heatIndexPredictions
    };
    const response = await askGemini(input, context);
    messages = [...messages, { sender: 'ai', text: response }];
    input = '';
  } catch (e) {
    error = 'AI failed to respond.';
  } finally {
    loading = false;
  }
}
</script>

<div class="chatbot-container">
  <div class="chatbot-header">
    <span>AI Health Assistant</span>
    <button class="close-btn" on:click={onClose} aria-label="Close">×</button>
  </div>
  <div class="chatbot-messages">
    {#each messages as msg}
      <div class="message {msg.sender}">{msg.text}</div>
    {/each}
    {#if loading}
      <div class="message ai">Thinking...</div>
    {/if}
    {#if error}
      <div class="error">{error}</div>
    {/if}
  </div>
  <form class="chatbot-input" on:submit|preventDefault={sendMessage}>
    <input type="text" bind:value={input} placeholder="Ask about your health, heat index, etc..." autocomplete="off" />
    <button type="submit" disabled={loading || !input.trim()}>Send</button>
  </form>
</div>

<style>
.chatbot-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  max-width: 420px;
  width: 100%;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  height: 80vh;
  position: relative;
}
.chatbot-header {
  background: #dd815e;
  color: white;
  padding: 1rem;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2rem;
}
.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
}
.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f9f9f9;
  border-bottom: 1px solid #eee;
}
.message {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 80%;
  word-break: break-word;
}
.message.user {
  background: #e3f2fd;
  align-self: flex-end;
  color: #1976d2;
}
.message.ai {
  background: #fff3e0;
  align-self: flex-start;
  color: #b35d3a;
}
.error {
  color: #e74c3c;
  margin-bottom: 1rem;
}
.chatbot-input {
  display: flex;
  padding: 1rem;
  background: white;
  border-radius: 0 0 16px 16px;
}
.chatbot-input input {
  flex: 1;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #eee;
  font-size: 1rem;
  margin-right: 0.5rem;
}
.chatbot-input button {
  background: #dd815e;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.chatbot-input button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
