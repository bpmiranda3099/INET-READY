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
- Follow Philippines Data Privacy Act (Republic Act No. 10173)
- Follow ISO 27000 standards, HIPAA principles, and FDA guidance on AI/ML in SaMD
- Comply with DOH Administrative Orders and NPC Philippines guidelines

RESPONSE FORMAT REQUIREMENTS:
Always structure your response using these exact sections, with proper spacing and formatting:

TOP TIP: [Single most important tip, max 15 words]

WEATHER BRIEF: [Brief note about key weather differences, 1-2 sentences]

HEALTH REMINDERS:
1. [First specific health reminder]
2. [Second specific health reminder]
3. [Third specific health reminder]
4. [Optional fourth reminder if needed]

WATCH FOR:
• [First warning sign]
• [Second warning sign]
• [Optional third warning sign]

QUICK TIPS:
• [First practical tip]
• [Second practical tip]

_Remember to consult a healthcare professional for personalized medical advice._

FORMATTING RULES:
- Use "TOP TIP:" on its own line
- Each numbered point must be on its own line
- Each bullet point must be on its own line
- Use numerals (1, 2, 3) for Health Reminders, not spelled out numbers
- Use bullet points (•) for Watch For and Quick Tips
- All sections must be clearly separated by line breaks
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
Generate health tips for a person traveling from ${fromCity} to ${toCity} in the Philippines.

CURRENT WEATHER SUMMARY:
- Origin (${fromCity}): ${weatherData?.fromCity ? `${weatherData.fromCity.temperature}°C, ${weatherData.fromCity.humidity}% humidity, Heat Index: ${weatherData.fromCity.heat_index}°C` : "Weather data not available"}
- Destination (${toCity}): ${weatherData?.toCity ? `${weatherData.toCity.temperature}°C, ${weatherData.toCity.humidity}% humidity, Heat Index: ${weatherData.toCity.heat_index}°C` : "Weather data not available"}

TRAVELER PROFILE:
${formatMedicalData(medicalData)}

IMPORTANT FORMATTING RULES:
- Number each item in the HEALTH REMINDERS section (1., 2., 3.)
- Use bullet points (•) for each item in WATCH FOR and QUICK TIPS sections
- Put EVERY numbered point and bullet point on its OWN line
- Always leave a line break between different sections
- ALWAYS maintain proper spacing and line breaks

FORMAT YOUR RESPONSE EXACTLY LIKE THIS TEMPLATE:
TOP TIP: [Single most important health advice specific to this journey]

WEATHER BRIEF: [Brief note about key weather differences]

HEALTH REMINDERS:
1. [First specific health reminder]
2. [Second specific health reminder]
3. [Third specific health reminder]

WATCH FOR:
• [First warning sign]
• [Second warning sign]

QUICK TIPS:
• [First practical tip]
• [Second practical tip]

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
