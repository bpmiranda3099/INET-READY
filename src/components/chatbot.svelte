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
let inputRef;
let containerRef;

onMount(async () => {
  try {
    medicalData = await getMedicalData();
    heatIndexData = await getAllHeatIndexData();
    heatIndexPredictions = await getHeatIndexPredictions();
  } catch (e) {
    error = 'Failed to load context data.';
  }
  // Scroll to bottom on mount
  setTimeout(scrollToBottom, 100);
});

function scrollToBottom() {
  if (containerRef) {
    containerRef.scrollTop = containerRef.scrollHeight;
  }
}

async function sendMessage() {
  if (!input.trim()) return;
  messages = [...messages, { sender: 'user', text: input }];
  loading = true;
  error = null;
  const chatHistory = messages.map(m => ({ role: m.sender === 'user' ? 'user' : 'model', text: m.text }));
  try {
    const context = {
      user,
      medicalData,
      heatIndexData,
      heatIndexPredictions,
      chatHistory
    };
    const response = await askGemini(input, context);
    messages = [...messages, { sender: 'ai', text: response }];
    input = '';
    setTimeout(scrollToBottom, 100);
  } catch (e) {
    error = 'AI failed to respond.';
  } finally {
    loading = false;
  }
}

function handleInputFocus() {
  // On mobile, scroll input into view
  setTimeout(() => {
    if (inputRef) inputRef.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, 100);
}
</script>

<div class="chatbot-fullpage">
  <header class="chatbot-appbar">
    <button class="close-btn" on:click={onClose} aria-label="Close"><i class="bi bi-arrow-left"></i></button>
    <span class="appbar-title">AI Health Assistant</span>
  </header>
  <main class="chatbot-main" bind:this={containerRef}>
    {#each messages as msg}
      <div class="message-row {msg.sender}">
        <div class="message-bubble {msg.sender}">{msg.text}</div>
      </div>
    {/each}
    {#if loading}
      <div class="message-row ai"><div class="message-bubble ai">Thinking...</div></div>
    {/if}
    {#if error}
      <div class="error">{error}</div>
    {/if}
  </main>
  <form class="chatbot-inputbar" on:submit|preventDefault={sendMessage}>
    <input type="text" bind:value={input} placeholder="Ask about your health, heat index, etc..." autocomplete="off" bind:this={inputRef} on:focus={handleInputFocus} />
    <button type="submit" disabled={loading || !input.trim()}><i class="bi bi-send"></i></button>
  </form>
</div>

<style>
.chatbot-fullpage {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: #f7f7f7;
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  max-width: 100vw;
  max-height: 100vh;
  overscroll-behavior: contain;
}
.chatbot-appbar {
  background: #dd815e;
  color: white;
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 1rem;
  box-shadow: 0 2px 8px rgba(221,129,94,0.08);
  font-size: 1.15rem;
  flex-shrink: 0;
}
.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.6rem;
  margin-right: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.appbar-title {
  font-weight: 600;
  font-size: 1.1rem;
  letter-spacing: 0.2px;
}
.chatbot-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.2rem 0.5rem 1.2rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #f7f7f7;
}
.message-row {
  display: flex;
  margin-bottom: 0.5rem;
}
.message-row.user {
  justify-content: flex-end;
}
.message-row.ai {
  justify-content: flex-start;
}
.message-bubble {
  max-width: 80vw;
  padding: 0.85rem 1.1rem;
  border-radius: 18px;
  font-size: 1rem;
  line-height: 1.5;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.message-bubble.user {
  background: #e3f2fd;
  color: #1976d2;
  border-bottom-right-radius: 6px;
  border-bottom-left-radius: 18px;
  align-self: flex-end;
}
.message-bubble.ai {
  background: #fff3e0;
  color: #b35d3a;
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 18px;
  align-self: flex-start;
}
.error {
  color: #e74c3c;
  margin: 1rem 0 0 0.5rem;
}
.chatbot-inputbar {
  display: flex;
  align-items: center;
  padding: 0.7rem 0.7rem 0.7rem 0.7rem;
  background: #fff;
  border-top: 1px solid #eee;
  flex-shrink: 0;
  gap: 0.5rem;
}
.chatbot-inputbar input {
  flex: 1;
  padding: 0.7rem 1rem;
  border-radius: 999px;
  border: 1px solid #eee;
  font-size: 1rem;
  background: #f9f9f9;
  outline: none;
  transition: border 0.2s;
}
.chatbot-inputbar input:focus {
  border: 1.5px solid #dd815e;
  background: #fff;
}
.chatbot-inputbar button {
  background: #dd815e;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.chatbot-inputbar button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
@media (max-width: 600px) {
  .chatbot-fullpage {
    height: 100dvh;
    max-height: 100dvh;
  }
  .chatbot-main {
    padding-bottom: 1.5rem;
  }
  .chatbot-inputbar {
    padding-bottom: env(safe-area-inset-bottom, 0);
  }
}
</style>
