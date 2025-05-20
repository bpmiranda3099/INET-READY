import { GoogleGenerativeAI } from "@google/generative-ai";
import { writable } from 'svelte/store';

// Store for API status and availability
export const geminiStatus = writable({
  isAvailable: false,
  lastChecked: null,
  error: null
});

// Initialize Gemini API
const API_KEY = (import.meta.env && import.meta.env.VITE_GEMINI_API_KEY) || process.env.VITE_GEMINI_API_KEY;
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
You are SafeTrip AI, an AI assistant for INET-READY: Your Heat Check for Safe and Informed Travel app.
Supported cities: ${allowedCities.join(', ')}

ROLE & BOUNDARIES (REVISED):
- You are a wellness-focused travel assistant, not a licensed medical provider.
- You may explain general health concepts and travel safety tips using reliable sources.
- Do not diagnose, treat, or assess personal symptoms.
- If asked about personal conditions, answer using cautious, non-prescriptive language (e.g., "You might consider…" or "Some travelers with similar conditions…").

Always remind users to consult a healthcare provider for serious, urgent, or personal medical concerns.

TRAVEL ADVICE REQUIREMENTS:
- When travel is mentioned, always consider both the origin and destination city (if provided).
- Tailor travel and health advice based on the user's medical data, weather, and heat index for both cities.
- Highlight any risks or precautions specific to the user's conditions, medications, or allergies for the journey and destination.
- If cities are not specified, offer general travel safety and wellness tips.

LEGAL COMPLIANCE:
- Adhere to the Philippines Data Privacy Act (Republic Act No. 10173)
- Follow ISO/IEC 27000 and 27001 standards on information security
- Respect HIPAA principles for health data handling
- Observe FDA guidance on AI/ML in Software as a Medical Device (SaMD)
- Comply with Department of Health (DOH) Administrative Orders and National Privacy Commission (NPC) guidelines in the Philippines

MEDICAL DATA CONSIDERATION REQUIREMENTS:
- Tailor advice based only on explicit medical information the user provides.
- Provide one general recommendation per condition mentioned, using a cautious and respectful tone.
- Consider medication timing and access when planning travel suggestions.
- Factor in how local weather might affect chronic conditions.
- Include allergy-specific precautions based on destination.
- Address age-related considerations (e.g., for children, seniors).
- If no medical data is provided, offer general wellness or travel safety tips, and mention that personalization was limited.

STYLE & USER EXPERIENCE:
- Keep responses concise (maximum 40 words but don't make it that long if its not necessary), friendly, and factual.
- Politely refuse to answer if a question is outside your knowledge or permitted scope.
- Display a medical disclaimer when discussing any health-related topic:
  "Note: This is general guidance only. For medical advice, please consult a licensed healthcare provider."

Remember, your goal is to be a supportive travel and wellness assistant.
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
    const prompt = `You are INET-READY's smart travel and health assistant.\n\nHere is the latest Cavite weather forecast data (JSON):\n\n${JSON.stringify(forecastData, null, 2)}\n\nPlease provide:\n- A concise summary of today's weather and heat index for all cities\n- Specific travel and health tips for each city\n- Highlight any cities with extreme or unusual conditions\n- Use clear, friendly language\n- Start with a section titled "TODAY'S SUMMARY:"\n- Limit the response to 100 words\n`;
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
    const prompt = `You are INET-READY's smart travel and health assistant.\n\nHere is the latest weather forecast for ${cityName} (JSON):\n\n${JSON.stringify(cityForecastData, null, 2)}\n\nPlease provide:\n- A concise summary of today's weather and heat index for ${cityName}\n- Specific travel and health tips for this city\n- Highlight any extreme or unusual conditions\n- Use clear, friendly language\n- Start with a section titled "TODAY'S SUMMARY:"\n- Limit the response to 50 words\n`;
    const result = await chatModel.generateContent(prompt);
    return result.response.text().trim();
  } catch (error) {
    console.error(`Error generating weather insight for ${cityName}:`, error);
    return `Sorry, I couldn't generate a weather insight for ${cityName} today.`;
  }
}

/**
 * Ask Gemini with user context (medical, heat index, predictions)
 * @param {string} userMessage - The user's message
 * @param {object} context - { user, medicalData, heatIndexData, heatIndexPredictions }
 * @returns {Promise<string>} The assistant's reply
 */
export async function askGemini(userMessage, context = {}) {
  try {
    // Compose a context-rich prompt
    let contextPrompt = '';
    if (context.user) {
      contextPrompt += `USER PROFILE (for context):\n${JSON.stringify(context.user, null, 2)}\n`;
    }
    if (context.medicalData) {
      contextPrompt += `USER MEDICAL DATA (for context):\n${JSON.stringify(context.medicalData, null, 2)}\n`;
    }
    if (context.heatIndexData) {
      contextPrompt += `CURRENT HEAT INDEX DATA (all cities):\n${JSON.stringify(context.heatIndexData, null, 2)}\n`;
    }
    if (context.heatIndexPredictions) {
      contextPrompt += `HEAT INDEX PREDICTIONS (7 days, all cities):\n${JSON.stringify(context.heatIndexPredictions, null, 2)}\n`;
    }
    contextPrompt += `\nUSER QUESTION: ${userMessage}`;
    // Use the main chat model with system instructions
    const result = await chatModel.generateContent(contextPrompt);
    return result.response.text().trim();
  } catch (error) {
    console.error('Error in askGemini:', error);
    return `Sorry, I couldn't process your request. (${error.message || 'Unknown error'})`;
  }
}

/**
 * Validate and clean "other" fields in medical profile
 * @param {object} otherFields - Object containing other fields {conditions, medications, fluids}
 * @returns {Promise<object>} - Validation results with cleaned data
 */
export async function validateMedicalProfileOtherFields(otherFields) {
  try {
    const prompt = `As a health data validator, please validate the following "other" fields from a medical profile. For each field:
1. Check if it contains valid medical/health information
2. Correct any obvious typos or formatting issues
3. Return cleaned text if valid, or explain why invalid

Input fields to validate:
${JSON.stringify(otherFields, null, 2)}

Respond in this exact JSON format:
{
  "conditions": {"isValid": boolean, "cleanedText": string, "reason": string},
  "medications": {"isValid": boolean, "cleanedText": string, "reason": string},
  "fluids": {"isValid": boolean, "cleanedText": string, "reason": string}
}`;    const result = await chatModel.generateContent(prompt);
    const responseText = result.response.text();
    
    // Extract JSON from markdown code block if present
    const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) || 
                     responseText.match(/`{0,3}({[\s\S]*?})`{0,3}/);
                     
    const jsonString = jsonMatch ? jsonMatch[1] : responseText;
    
    try {
        const validation = JSON.parse(jsonString.trim());
        return validation;
    } catch (parseError) {
        console.error('Error parsing validation response:', parseError);
        console.error('Response text:', responseText);
        throw new Error('Failed to parse validation response');
    }
  } catch (error) {
    console.error('Error validating medical profile fields:', error);
    throw new Error('Failed to validate medical profile fields');
  }
}
