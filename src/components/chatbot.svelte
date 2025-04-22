<script>
import { onMount, onDestroy } from 'svelte';
import { askGemini } from '$lib/services/gemini-service';
import { getMedicalData } from '$lib/services/medical-api';
import { getAllHeatIndexData, getHeatIndexPredictions } from '$lib/services/weather-data-service';
import { marked } from 'marked';

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
let keyboardOffset = 0;

// Typing animation state
let aiTyping = false;
let aiTypedText = '';
let aiFullText = '';
let typingInterval;

onMount(() => {
  // Run async logic separately
  (async () => {
    try {
      medicalData = await getMedicalData();
      heatIndexData = await getAllHeatIndexData();
      heatIndexPredictions = await getHeatIndexPredictions();
    } catch (e) {
      error = 'Failed to load context data.';
    }
    // Scroll to bottom on mount
    setTimeout(scrollToBottom, 100);
  })();

  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', adjustForKeyboard);
    adjustForKeyboard();
  }
  return () => {
    if (window.visualViewport) {
      window.visualViewport.removeEventListener('resize', adjustForKeyboard);
    }
  };
});

function scrollToBottom() {
  if (containerRef) {
    containerRef.scrollTop = containerRef.scrollHeight;
  }
}

async function sendMessage() {
  if (!input.trim()) return;
  messages = [...messages, { sender: 'user', text: input }];
  const sentInput = input;
  input = '';
  loading = true;
  error = null;
  aiTyping = false;
  aiTypedText = '';
  aiFullText = '';
  clearInterval(typingInterval);
  const chatHistory = messages.map(m => ({ role: m.sender === 'user' ? 'user' : 'model', text: m.text }));
  try {
    const context = {
      user,
      medicalData,
      heatIndexData,
      heatIndexPredictions,
      chatHistory
    };
    const response = await askGemini(sentInput, context);
    aiFullText = response;
    aiTypedText = '';
    aiTyping = true;
    let i = 0;
    typingInterval = setInterval(() => {
      if (i < aiFullText.length) {
        aiTypedText += aiFullText[i];
        i++;
        setTimeout(scrollToBottom, 0);
      } else {
        clearInterval(typingInterval);
        aiTyping = false;
        messages = [...messages, { sender: 'ai', text: aiFullText }];
        aiTypedText = '';
        aiFullText = '';
        setTimeout(scrollToBottom, 100);
      }
    }, 18); // Typing speed (ms per character)
  } catch (e) {
    error = 'AI failed to respond.';
  } finally {
    loading = false;
  }
}

function handleInputFocus() {
  // On mobile, scroll input into view and adjust for keyboard
  setTimeout(() => {
    if (inputRef) inputRef.scrollIntoView({ behavior: 'smooth', block: 'end' });
    adjustForKeyboard();
  }, 100);
}

function adjustForKeyboard() {
  // On mobile, adjust the chatbot-main height so input is always visible
  if (window.visualViewport) {
    const vh = window.visualViewport.height;
    document.documentElement.style.setProperty('--chatbot-vh', vh + 'px');
    // Calculate keyboard offset (for iOS/Android)
    const offset = window.innerHeight - vh;
    keyboardOffset = offset > 0 ? offset : 0;
  }
}

onDestroy(() => {
  clearInterval(typingInterval);
});

$: document.documentElement.style.setProperty('--keyboard-offset', keyboardOffset + 'px');
</script>

<div class="chatbot-fullpage">
  <header class="chatbot-appbar">
    <button class="close-btn" on:click={onClose} aria-label="Close"><i class="bi bi-arrow-left"></i></button>
    <span class="appbar-title">AI Health Assistant</span>
  </header>
  <main class="chatbot-main" bind:this={containerRef}>
    {#each messages as msg}
      <div class="message-row {msg.sender}">
        {#if msg.sender === 'ai'}
          <div class="message-bubble ai"><div class="markdown">{@html marked(msg.text)}</div></div>
        {:else}
          <div class="message-bubble user">{msg.text}</div>
        {/if}
      </div>
    {/each}
    {#if aiTyping}
      <div class="message-row ai">
        <div class="message-bubble ai"><div class="markdown">{@html marked(aiTypedText + (aiTypedText.length < aiFullText.length ? '▍' : ''))}</div></div>
      </div>
    {/if}
    {#if loading && !aiTyping}
      <div class="message-row ai"><div class="message-bubble ai">Thinking...</div></div>
    {/if}
    {#if error}
      <div class="error">{error}</div>
    {/if}
  </main>
  <form class="chatbot-inputbar" on:submit|preventDefault={sendMessage} style="bottom: {keyboardOffset}px">
    <div class="row w-100 g-0 align-items-center">
      <div class="col">
        <input type="text" bind:value={input} placeholder="Ask about your health, heat index, etc..." autocomplete="off" bind:this={inputRef} on:focus={handleInputFocus} class="form-control border-0 bg-light" />
      </div>
      <div class="col-auto">
        <button type="submit" class="btn ms-2 d-flex align-items-center justify-content-center" disabled={loading || !input.trim()} style="width:40px;height:38px;background:#dd815e;color:white;"><i class="bi bi-send"></i></button>
      </div>
    </div>
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
@media (max-width: 600px) {
  .chatbot-fullpage {
    height: var(--chatbot-vh, 100dvh);
    max-height: var(--chatbot-vh, 100dvh);
  }
  .chatbot-main {
    padding-bottom: 1.5rem;
  }
  .chatbot-inputbar {
    position: fixed;
    left: 0;
    right: 0;
    width: 100vw;
    bottom: 0;
    z-index: 4000;
    background: #fff;
    border-top: 1px solid #eee;
    padding-bottom: calc(env(safe-area-inset-bottom, 0) + 0px);
  }
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
  padding: 1.2rem 0.5rem calc(1.2rem + var(--keyboard-offset, 0px)) 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #f7f7f7;
}
.message-row {
  display: flex;
  margin-bottom: 0.5rem;
  width: 100%;
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
.message-row.user .message-bubble.user {
  margin-left: auto;
  margin-right: 0;
  align-self: flex-end;
}
.message-row.ai .message-bubble.ai {
  margin-right: auto;
  margin-left: 0;
  align-self: flex-start;
}
.message-bubble.user {
  background: #e3f2fd;
  color: #1976d2;
  border-bottom-right-radius: 6px;
  border-bottom-left-radius: 18px;
}
.message-bubble.ai {
  background: #fff3e0;
  color: #b35d3a;
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 18px;
}
.error {
  color: #e74c3c;
  margin: 1rem 0 0 0.5rem;
}
.chatbot-inputbar {
  display: block;
  width: 100%;
  background: #fff;
  border-top: 1px solid #eee;
  flex-shrink: 0;
  padding: 0.7rem 0.7rem 0.7rem 0.7rem;
}
.chatbot-inputbar input.form-control {
  border-radius: 999px;
  font-size: 1rem;
  background: #f9f9f9;
  outline: none;
  transition: border 0.2s;
  box-shadow: none;
}
.chatbot-inputbar input.form-control:focus {
  border: 1.5px solid #dd815e;
  background: #fff;
  box-shadow: none;
}
.chatbot-inputbar button.btn {
  background: #dd815e;
  color: white;
  border: none;
  transition: background 0.2s;
}
.chatbot-inputbar button.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.markdown {
  font-size: 1rem;
  line-height: 1.6;
  word-break: break-word;
}
.markdown p {
  margin: 0 0 0.5em 0;
}
.markdown ul, .markdown ol {
  margin: 0.5em 0 0.5em 1.5em;
}
.markdown li {
  margin-bottom: 0.2em;
}
.markdown strong {
  font-weight: 600;
}
.markdown em {
  font-style: italic;
}
.markdown code {
  background: #f4f4f4;
  border-radius: 4px;
  padding: 0.1em 0.3em;
  font-size: 0.95em;
}
.markdown h1, .markdown h2, .markdown h3 {
  margin: 0.5em 0 0.3em 0;
  font-weight: 700;
}
.markdown h1 { font-size: 1.3em; }
.markdown h2 { font-size: 1.15em; }
.markdown h3 { font-size: 1.05em; }
</style>
