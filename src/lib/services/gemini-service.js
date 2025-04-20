import { GoogleGenerativeAI } from "@google/generative-ai";
import { writable } from 'svelte/store';

// Store for API status and availability
export const geminiStatus = writable({
  isAvailable: false,
  lastChecked: null,
  error: null
});

// Initialize Gemini API
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY
const genAI = new GoogleGenerativeAI(API_KEY);

// Define allowed cities
export const allowedCities = [
  "Amadeo", "Imus", "General Trias", "Dasmariñas", "Bacoor", "Carmona", "Kawit",
  "Noveleta", "Silang", "Naic", "Tanza", "Alfonso", "Indang", "Rosario",
  "Trece Martires", "General Mariano Alvarez", "Cavite City", "Tagaytay",
  "Mendez", "Ternate", "Maragondon", "Magallanes"
];

// System instructions for the chatbot
const SYSTEM_INSTRUCTION = `
You are INET-READY's smart travel and health assistant, focusing on the following cities in Cavite, Philippines:

${allowedCities.join(', ')}

LEGAL COMPLIANCE:
- Adhere to the Philippines Data Privacy Act (Republic Act No. 10173)
- Follow ISO 27000 standards, HIPAA principles, and FDA guidance on AI/ML in Software as a Medical Device (SaMD)
- Comply with Department of Health (DOH) Administrative Orders and National Privacy Commission (NPC) Philippines guidelines

MEDICAL DATA CONSIDERATION REQUIREMENTS:
- Tailor each piece of advice to the traveler's specific medical profile
- Provide at least one specific recommendation for each medical condition mentioned
- Consider medication needs and timing when suggesting travel plans
- Assess how weather differences might impact existing health conditions
- Include specific precautions related to the destination for allergies
- Address age-appropriate concerns in recommendations
- If no medical data is provided, offer general advice and mention this limitation

Always be concise, friendly, and factual. If a question is outside your scope, politely indicate so. Never provide medical diagnoses—remind users to consult a healthcare professional for urgent or personal medical issues.
`;

// Create the chatbot model with system instructions
const chatModel = genAI.getGenerativeModel({
  model: "gemini-2.5-flash-preview-04-17",
  systemInstruction: SYSTEM_INSTRUCTION
});

/**
 * Check if the Gemini API is available and update the status store
 */
export async function checkGeminiAvailability() {
  try {
    const result = await chatModel.generateContent("Test connection. Respond with 'OK' only.");
    const text = result.response.text();
    geminiStatus.set({
      isAvailable: true,
      lastChecked: new Date(),
      error: null
    });
    return true;
  } catch (error) {
    console.error("Gemini API error:", error);
    geminiStatus.set({
      isAvailable: false,
      lastChecked: new Date(),
      error: error.message || "Could not connect to Gemini API"
    });
    return false;
  }
}

/**
 * General-purpose chatbot for user queries
 * @param {string} userMessage - The user's message or question
 * @param {Array} chatHistory - Array of previous messages (for context)
 * @returns {Promise<string>} The assistant's reply
 */
export async function askInetReadyAssistant(userMessage, chatHistory = []) {
  try {
    // Format chat history for Gemini
    const history = chatHistory.map(msg => ({
      role: msg.role === 'user' ? 'user' : 'model',
      parts: [{ text: msg.text }]
    }));
    const chat = chatModel.startChat({ history });
    const result = await chat.sendMessage(userMessage);
    return result.response.text().trim();
  } catch (error) {
    console.error("Error in chatbot:", error);
    return `Sorry, I couldn't process your request. (${error.message || 'Unknown error'})`;
  }
}

/**
 * Generate daily weather insights from forecast data using Gemini
 * @param {object} forecastData - The weather forecast data (cities, values, etc)
 * @returns {Promise<string>} The generated insights text
 */
export async function generateDailyWeatherInsights(forecastData) {
  try {
    // Compose a prompt for Gemini based on the forecast data
    const prompt = `You are INET-READY's smart travel and health assistant.\n\nHere is the latest Cavite weather forecast data (JSON):\n\n${JSON.stringify(forecastData, null, 2)}\n\nPlease provide:\n- A concise summary of today's weather and heat index for all cities\n- Specific travel and health tips for each city\n- Highlight any cities with extreme or unusual conditions\n- Use clear, friendly language\n- Start with a section titled "TODAY'S SUMMARY:"\n- Limit the response to 800 words\n`;
    const result = await chatModel.generateContent(prompt);
    return result.response.text().trim();
  } catch (error) {
    console.error("Error generating daily weather insights:", error);
    return "Sorry, I couldn't generate weather insights today.";
  }
}

/**
 * Generate a weather insight for a single city using Gemini
 * @param {string} cityName - The name of the city
 * @param {object} cityForecastData - The forecast data for the city
 * @returns {Promise<string>} The generated insight for the city
 */
export async function generateCityWeatherInsight(cityName, cityForecastData) {
  try {
    const prompt = `You are INET-READY's smart travel and health assistant.\n\nHere is the latest weather forecast for ${cityName} (JSON):\n\n${JSON.stringify(cityForecastData, null, 2)}\n\nPlease provide:\n- A concise summary of today's weather and heat index for ${cityName}\n- Specific travel and health tips for this city\n- Highlight any extreme or unusual conditions\n- Use clear, friendly language\n- Start with a section titled "TODAY'S SUMMARY:"\n- Limit the response to 300 words\n`;
    const result = await chatModel.generateContent(prompt);
    return result.response.text().trim();
  } catch (error) {
    console.error(`Error generating weather insight for ${cityName}:`, error);
    return `Sorry, I couldn't generate a weather insight for ${cityName} today.`;
  }
}
