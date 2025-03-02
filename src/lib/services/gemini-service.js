import { GoogleGenerativeAI } from "@google/generative-ai";
import { writable } from 'svelte/store';

// Store for API status and availability
export const geminiStatus = writable({
  isAvailable: false,
  lastChecked: null,
  error: null
});

// Initialize Gemini API with system instructions for health advice
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY);

// Comprehensive system instructions for health advice with improved formatting guidance
const SYSTEM_INSTRUCTION = `
You are a friendly health advisor providing practical, easy-to-read travel health tips between cities in the Philippines.

LEGAL COMPLIANCE:
- Strictly comply with Philippines Data Privacy Act (Republic Act No. 10173) and its implementing rules
- Follow ISO 27000 series information security standards
- Adhere to HIPAA principles for health information
- Comply with FDA guidance on AI/ML in Software as a Medical Device (SaMD)
- Follow Department of Health (DOH) Administrative Orders for health information processing
- Adhere to National Privacy Commission (NPC) Philippines guidelines

RESPONSE FORMAT REQUIREMENTS:
Always structure your response using these exact sections in this order:
1. "TOP TIP" - A single, most important tip specific to the journey (max 15 words)
2. "WEATHER BRIEF" - 1-2 sentences about key weather differences
3. "HEALTH REMINDERS" - 3-5 short, numbered bullet points considering medical conditions
4. "WATCH FOR" - 2-3 short bullet points about warning signs
5. "QUICK TIPS" - 2-3 practical travel tips

TONE AND STYLE:
- Be conversational and friendly, like a caring friend giving advice
- Use simple, straightforward language (8th-grade reading level)
- Be concise - each section should be scannable in seconds
- Use active voice and direct instructions
- Be specific to the Philippines context

LIMITATIONS:
- Always end with a brief disclaimer about seeking professional medical advice
- Don't provide specific diagnosis or treatment recommendations
`;

// Create the model with system instructions
const model = genAI.getGenerativeModel({
  model: "gemini-1.5-flash",
  systemInstruction: SYSTEM_INSTRUCTION
});

/**
 * Check if the Gemini API is available and update the status store
 */
export async function checkGeminiAvailability() {
  try {
    // Simple test prompt to check if the API is responsive
    const result = await model.generateContent("Test connection. Respond with 'OK' only.");
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
 * Generate health advice for travel between cities based on user's health profile
 * @param {Object} params The parameters for generating health advice
 * @param {string} params.fromCity The origin city
 * @param {string} params.toCity The destination city
 * @param {Object} params.medicalData User's medical data
 * @param {Object} params.weatherData Weather data for both cities
 * @returns {Promise<string>} The generated health advice
 */
export async function generateTravelHealthAdvice({ fromCity, toCity, medicalData, weatherData }) {
  try {
    // Construct a detailed prompt based on the parameters with improved structure guidance
    const prompt = `
Generate a helpful health tip card for a person traveling from ${fromCity} to ${toCity} in the Philippines.

CURRENT WEATHER SUMMARY:
- Origin (${fromCity}): ${weatherData?.fromCity ? `${weatherData.fromCity.temperature}°C, ${weatherData.fromCity.humidity}% humidity, Heat Index: ${weatherData.fromCity.heat_index}°C` : "Weather data not available"}
- Destination (${toCity}): ${weatherData?.toCity ? `${weatherData.toCity.temperature}°C, ${weatherData.toCity.humidity}% humidity, Heat Index: ${weatherData.toCity.heat_index}°C` : "Weather data not available"}

TRAVELER PROFILE:
${formatMedicalData(medicalData)}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
TOP TIP: [Single most important health advice for this specific journey]

WEATHER BRIEF: [Brief note about key weather differences and impacts]

HEALTH REMINDERS:
1. [Specific health reminder]
2. [Specific health reminder]
3. [Specific health reminder]

WATCH FOR:
• [Warning sign]
• [Warning sign]

QUICK TIPS:
• [Practical tip]
• [Practical tip]

_Remember to consult a healthcare professional for personalized medical advice._
`;

    console.log("Generating advice with prompt:", prompt);
    
    // Generate content from Gemini
    const result = await model.generateContent(prompt);
    return result.response.text();
  } catch (error) {
    console.error("Error generating health advice:", error);
    return `Could not generate health advice. Error: ${error.message || "Unknown error"}. Please try again later.`;
  }
}

/**
 * Format medical data for the prompt
 * @param {Object} medicalData User's medical data
 * @returns {string} Formatted medical data
 */
function formatMedicalData(medicalData) {
  if (!medicalData) return "No medical information provided.";
  
  const { age, gender, conditions = [], medications = [], allergies = [] } = medicalData;
  
  return `
- Age: ${age || 'Not specified'}
- Gender: ${gender || 'Not specified'}
- Medical conditions: ${conditions.length > 0 ? conditions.join(', ') : 'None'}
- Medications: ${medications.length > 0 ? medications.join(', ') : 'None'}
- Allergies: ${allergies.length > 0 ? allergies.join(', ') : 'None'}
`;
}

export { model };
