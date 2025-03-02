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

// Comprehensive system instructions for health advice
const SYSTEM_INSTRUCTION = `
You are a health advisor providing travel health recommendations between cities in the Philippines.

LEGAL COMPLIANCE:
- Strictly comply with Philippines Data Privacy Act (Republic Act No. 10173) and its implementing rules
- Follow ISO 27000 series information security standards
- Adhere to HIPAA principles for health information
- Comply with FDA guidance on AI/ML in Software as a Medical Device (SaMD)
- Follow Department of Health (DOH) Administrative Orders for health information processing
- Adhere to National Privacy Commission (NPC) Philippines guidelines

RESPONSE GUIDELINES:
- Provide clear, evidence-based travel health advice
- Consider both origin and destination cities' current weather conditions
- Factor in user's medical conditions when providing recommendations
- Always include general disclaimers about seeking professional medical advice
- Format advice in easily readable bullet points with clear headings
- Include contextual information about relevant environmental factors
- Never claim to provide medical diagnosis or treatment
- Use professional, compassionate language
- Focus on preventive measures and best practices
- Be specific to Philippines context and local health considerations

LIMITATIONS:
- Clearly indicate you're providing general advice, not personalized medical treatment
- Never claim diagnostics capabilities or replace medical professionals
- Include disclaimer about consulting healthcare providers for specific concerns
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
    // Construct a detailed prompt based on the parameters
    const prompt = `
    I need health advice for travel from ${fromCity} to ${toCity} in the Philippines.
    
    Current weather conditions:
    - Origin (${fromCity}): ${weatherData?.fromCity ? `Temperature: ${weatherData.fromCity.temperature}°C, Humidity: ${weatherData.fromCity.humidity}%, Heat Index: ${weatherData.fromCity.heat_index}°C` : "Weather data not available"}
    - Destination (${toCity}): ${weatherData?.toCity ? `Temperature: ${weatherData.toCity.temperature}°C, Humidity: ${weatherData.toCity.humidity}%, Heat Index: ${weatherData.toCity.heat_index}°C` : "Weather data not available"}
    
    Medical profile:
    ${formatMedicalData(medicalData)}
    
    Please provide:
    1. Health risks based on the weather difference and travel between these locations
    2. Precautions to take before and during travel considering the medical conditions
    3. Signs to watch for that might indicate health problems during travel
    4. General wellness tips for travel in this region
    
    Format the response with clear headings and bullet points.
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
