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

	let promptSuggestions = [];
	let showPromptSuggestions = true;
	let suggestionTimeout;

	onMount(() => {
		// Run async logic separately
		(async () => {
			try {
				medicalData = await getMedicalData();
				heatIndexData = await getAllHeatIndexData();
				heatIndexPredictions = await getHeatIndexPredictions();
				// Generate prompt suggestions using AI
				const context = { user, medicalData, heatIndexData, heatIndexPredictions };
				const suggestionPrompt =
					'Suggest 3 helpful, relevant questions a user might ask about their health, travel, or heat safety. Respond as a JSON array of short strings.';
				let suggestionResponse = await askGemini(suggestionPrompt, context);
				try {
					// Try to parse JSON array from AI
					const parsed = JSON.parse(suggestionResponse.match(/\[.*\]/s)?.[0] || '[]');
					if (Array.isArray(parsed) && parsed.length > 0) {
						promptSuggestions = parsed.slice(0, 3);
					} else {
						promptSuggestions = [
							'What is the current heat index in my city?',
							'How can I stay safe in hot weather?',
							'Are there travel precautions for my health?'
						];
					}
				} catch {
					promptSuggestions = [
						'What is the current heat index in my city?',
						'How can I stay safe in hot weather?',
						'Are there travel precautions for my health?'
					];
				}
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
		// Add the user's message to the messages array
		messages = [...messages, { sender: 'user', text: input }];
		const sentInput = input;
		input = '';
		loading = true;
		error = null;
		aiTyping = false;
		aiTypedText = '';
		aiFullText = '';
		clearInterval(typingInterval);
		// Prepare chat history for context: include all user and AI messages in order
		const chatHistory = messages.map((m) => ({
			role: m.sender === 'user' ? 'user' : 'assistant',
			text: m.text
		}));
		try {
			const context = {
				user,
				medicalData,
				heatIndexData,
				heatIndexPredictions,
				chatHistory // always send full chat history
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
		clearTimeout(suggestionTimeout);
	});

	$: document.documentElement.style.setProperty('--keyboard-offset', keyboardOffset + 'px');

	function selectPromptSuggestion(suggestion) {
		input = suggestion;
		showPromptSuggestions = false;
		sendMessage();
	}

	$: if (input.trim() && showPromptSuggestions) {
		showPromptSuggestions = false;
	}

	function renderWithDisclaimer(text) {
		// If the disclaimer is present, split and style it
		const disclaimer =
			'Note: This is general guidance only. For medical advice, please consult a licensed healthcare provider.';
		if (text && text.includes(disclaimer)) {
			const [main, ...rest] = text.split(disclaimer);
			return `${marked(main)}<div class='ai-disclaimer'>${disclaimer}</div>${rest.length > 0 ? marked(rest.join(disclaimer)) : ''}`;
		}
		return marked(text || '');
	}

	function handleInputChange() {
		// Hide suggestions when typing
		showPromptSuggestions = false;
		// Clear any previous timer
		clearTimeout(suggestionTimeout);
		// If input is empty, set a timer to show suggestions after 4 seconds
		if (!input.trim()) {
			suggestionTimeout = setTimeout(() => {
				if (!input.trim() && messages.length === 0) {
					showPromptSuggestions = true;
				} else if (!input.trim()) {
					showPromptSuggestions = true;
				}
			}, 4000);
		}
	}

	// Watch input changes
	$: input, handleInputChange();
</script>

<div class="chatbot-fullpage">
	<header class="chatbot-appbar">
		<button class="close-btn" on:click={onClose} aria-label="Close"
			><i class="bi bi-arrow-left"></i></button
		>
		<span class="appbar-title">SafeTrip AI</span>
	</header>
	<main class="chatbot-main" bind:this={containerRef}>
		{#each messages as msg}
			<div class="message-row {msg.sender}">
				{#if msg.sender === 'ai'}
					<div class="message-bubble ai">
						<div class="markdown">{@html renderWithDisclaimer(msg.text)}</div>
					</div>
				{:else}
					<div class="message-bubble user">{msg.text}</div>
				{/if}
			</div>
		{/each}
		{#if aiTyping}
			<div class="message-row ai">
				<div class="message-bubble ai">
					<div class="markdown">
						{@html marked(aiTypedText + (aiTypedText.length < aiFullText.length ? '▍' : ''))}
					</div>
				</div>
			</div>
		{/if}
		{#if loading && !aiTyping}
			<div class="message-row ai"><div class="message-bubble ai">Thinking...</div></div>
		{/if}
		{#if error}
			<div class="error">{error}</div>
		{/if}
	</main>
	{#if showPromptSuggestions && promptSuggestions.length > 0 && messages.length === 0 && !input.trim()}
		<div class="prompt-suggestions-bar">
			<div class="prompt-suggestions">
				{#each promptSuggestions as suggestion}
					<button class="prompt-suggestion-btn" on:click={() => selectPromptSuggestion(suggestion)}
						>{suggestion}</button
					>
				{/each}
			</div>
		</div>
	{/if}
	<form
		class="chatbot-inputbar"
		on:submit|preventDefault={sendMessage}
		style="bottom: {keyboardOffset}px"
	>
		<div class="row w-100 g-0 align-items-center">
			<div class="col">
				<input
					type="text"
					bind:value={input}
					placeholder="Ask about your health, heat index, etc..."
					autocomplete="off"
					bind:this={inputRef}
					on:focus={handleInputFocus}
					class="form-control border-0 bg-light"
				/>
			</div>
			<div class="col-auto">
				<button
					type="submit"
					class="btn chatbot-send-btn ms-2 d-flex align-items-center justify-content-center"
					disabled={loading || !input.trim()}><i class="bi bi-send"></i></button
				>
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
		box-shadow: 0 2px 8px rgba(221, 129, 94, 0.08);
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
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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
		background: #1976d2;
		color: #ffffff;
		border-bottom-right-radius: 6px;
		border-bottom-left-radius: 18px;
	}
	.message-bubble.ai {
		background: #dd815e;
		color: #ffffff;
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
	.markdown ul,
	.markdown ol {
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
	.markdown h1,
	.markdown h2,
	.markdown h3 {
		margin: 0.5em 0 0.3em 0;
		font-weight: 700;
	}
	.markdown h1 {
		font-size: 1.3em;
	}
	.markdown h2 {
		font-size: 1.15em;
	}
	.markdown h3 {
		font-size: 1.05em;
	}
	.prompt-suggestions {
		display: flex;
		flex-direction: column;
		gap: 0.7rem;
		justify-content: center;
		align-items: center;
		margin: 4.5rem 1rem;
	}
	.prompt-suggestion-btn {
		background: #dd815e;
		color: white;
		border: none;
		padding: 1rem 1rem;
		border-radius: 1rem;
		cursor: pointer;
		font-size: 1rem;
		font-weight: 500;
		transition: background 0.2s;
		box-shadow: 0 2px 8px rgba(221, 129, 94, 0.07);
	}
	.prompt-suggestion-btn:hover {
		background: #c76b4e;
	}
	.ai-disclaimer {
		margin-top: 0.7em;
		background: rgba(255, 221, 51, 0.55);
		color: #fff;
		font-size: 0.7rem !important; /* Using rem to override inheritance and fixed size */
		border-radius: 10px;
		padding: 0.5em 1em;
		font-weight: 500;
		box-shadow: 0 1px 4px rgba(221, 129, 94, 0.07);
		display: inline-block;
	}
	.prompt-suggestions-bar {
		display: flex;
		justify-content: center;
		align-items: flex-end;
		width: 100%;
		margin-bottom: 0.7rem;
		position: relative;
		z-index: 10;
	}
	.chatbot-send-btn {
		width: 40px;
		height: 35px;
		background: #dd815e;
		color: white;
		border: none;
		transition: background 0.2s;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(221, 129, 94, 0.07);
		font-size: 1.2rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.chatbot-send-btn:disabled {
		background: #ccc;
		color: #fff;
		cursor: not-allowed;
	}
</style>
