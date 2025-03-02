import { GoogleGenerativeAI } from "@google/generative-ai";
import { writable } from 'svelte/store';

// Store for API status and availability
export const geminiStatus = writable({
  isAvailable: false,
  lastChecked: null,
  error: null
});

// Initialize Gemini API with system instructions for health advice
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || process.env.VITE_GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY);

// Enhanced system instructions with stronger focus on medical data considerations
const SYSTEM_INSTRUCTION = `
You are a friendly health advisor providing practical, personalized travel health tips between cities in the Philippines.

LEGAL COMPLIANCE:
- Follow Philippines Data Privacy Act (Republic Act No. 10173)
- Follow ISO 27000 standards, HIPAA principles, and FDA guidance on AI/ML in SaMD
- Comply with DOH Administrative Orders and NPC Philippines guidelines

MEDICAL DATA CONSIDERATION REQUIREMENTS:
- Each piece of advice MUST be tailored to the traveler's specific medical profile
- For each medical condition mentioned, provide at least one specific recommendation
- Consider medication needs and timing when suggesting travel plans
- Consider how weather differences might impact existing health conditions
- For allergies, include specific precautions related to the destination
- Address age-appropriate concerns in your recommendations
- If no medical data is provided, give more general advice but mention this limitation

RESPONSE FORMAT REQUIREMENTS:
Always structure your response using these exact sections, with proper spacing and formatting:

TOP TIP: [Single most important health advice specific to this journey and the person's medical profile]

WEATHER BRIEF: [Brief note about key weather differences and how they might affect the person's specific health conditions]

HEALTH REMINDERS:
1. [First specific health reminder tailored to medical conditions]
2. [Second specific health reminder considering medications]
3. [Third specific health reminder addressing potential health risks]
4. [Optional fourth reminder related to allergies or specific concerns]

WATCH FOR:
• [First warning sign specific to the person's health conditions]
• [Second warning sign related to weather/travel impacts]

QUICK TIPS:
• [First practical tip considering medical needs]
• [Second practical tip for health management during travel]

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
    // Enhanced prompt with specific instructions about considering medical data
    const prompt = `
Generate personalized health tips for a person traveling from ${fromCity} to ${toCity} in the Philippines.

CURRENT WEATHER SUMMARY:
- Origin (${fromCity}): ${weatherData?.fromCity ? `${weatherData.fromCity.temperature}°C, ${weatherData.fromCity.humidity}% humidity, Heat Index: ${weatherData.fromCity.heat_index}°C` : "Weather data not available"}
- Destination (${toCity}): ${weatherData?.toCity ? `${weatherData.toCity.temperature}°C, ${weatherData.toCity.humidity}% humidity, Heat Index: ${weatherData.toCity.heat_index}°C` : "Weather data not available"}

TRAVELER MEDICAL PROFILE (IMPORTANT - TAILOR ADVICE TO THESE SPECIFIC CONDITIONS):
${formatMedicalData(medicalData)}

PERSONALIZATION REQUIREMENTS:
1. For each medical condition listed, provide at least one specific recommendation
2. If medications are mentioned, include advice on medication management during travel
3. Consider how the weather difference might affect their specific health conditions
4. If they have allergies, include advice on managing these during travel
5. Tailor advice to their age and gender where relevant

FORMATTING RULES:
- Number each item in the HEALTH REMINDERS section (1., 2., 3.)
- Use bullet points (•) for each item in WATCH FOR and QUICK TIPS sections
- Put EVERY numbered point and bullet point on its OWN line
- Always leave a line break between different sections

FORMAT YOUR RESPONSE EXACTLY LIKE THIS TEMPLATE:
TOP TIP: [Single most important health advice specific to this journey and their medical profile]

WEATHER BRIEF: [Brief note about key weather differences and how they might affect their specific health conditions]

HEALTH REMINDERS:
1. [First specific health reminder tailored to their medical conditions]
2. [Second specific health reminder considering their medications]
3. [Third specific health reminder addressing their potential health risks]

WATCH FOR:
• [First warning sign specific to their health conditions]
• [Second warning sign related to weather/travel impacts]

QUICK TIPS:
• [First practical tip considering their specific medical needs]
• [Second practical tip for managing their health during travel]

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
 * Format medical data for the prompt with enhanced structure
 * @param {Object} medicalData User's medical data
 * @returns {string} Formatted medical data
 */
function formatMedicalData(medicalData) {
  if (!medicalData) return "No medical information provided. Please provide general travel health advice.";
  
  const { age, gender, conditions = [], medications = [], allergies = [] } = medicalData;
  
  let formattedData = `
- Age: ${age || 'Not specified'} ${age ? `(${getAgeCategory(age)})` : ''}
- Gender: ${gender || 'Not specified'}
`;

  // Add medical conditions with emphasis if present
  if (conditions.length > 0) {
    formattedData += `- MEDICAL CONDITIONS (IMPORTANT): ${conditions.join(', ')}\n`;
  } else {
    formattedData += `- Medical conditions: None reported\n`;
  }
  
  // Add medications with emphasis if present
  if (medications.length > 0) {
    formattedData += `- MEDICATIONS (CONSIDER THESE): ${medications.join(', ')}\n`;
  } else {
    formattedData += `- Medications: None reported\n`;
  }
  
  // Add allergies with emphasis if present
  if (allergies.length > 0) {
    formattedData += `- ALLERGIES (ADDRESS THESE): ${allergies.join(', ')}`;
  } else {
    formattedData += `- Allergies: None reported`;
  }
  
  return formattedData;
}

/**
 * Helper function to categorize age for more tailored advice
 * @param {number} age User's age
 * @returns {string} Age category
 */
function getAgeCategory(age) {
  if (!age) return '';
  
  const ageNum = parseInt(age.toString());
  if (isNaN(ageNum)) return '';
  
  if (ageNum <= 12) return 'child';
  if (ageNum <= 17) return 'adolescent';
  if (ageNum <= 39) return 'young adult';
  if (ageNum <= 59) return 'middle-aged adult';
  if (ageNum <= 74) return 'older adult';
  return 'elderly';
}

/**
 * Generate daily weather insights based on heat index forecast data
 * @param {Object} forecastData Heat index forecast data
 * @returns {Promise<string>} The generated weather insights
 */
export async function generateDailyWeatherInsights(forecastData) {
  try {
    // Create a prompt for Gemini based on the forecast data
    const forecastDate = forecastData?.generated_on || 'recent';
    const overallRating = forecastData?.overall_rating || {};
    const ratingText = overallRating?.rating || 'N/A';
    const ratingScore = overallRating?.score || 0;
    
    // Get data for major cities (up to 5)
    const citiesData = [];
    if (forecastData?.cities) {
      for (const [city, forecasts] of Object.entries(forecastData.cities)) {
        if (forecasts && forecasts.length > 0) {
          // Get today's forecast or the first available
          const todayForecast = forecasts[0];
          citiesData.push({
            city,
            heat_index: todayForecast.heat_index ?? 'N/A',
            temperature: todayForecast.temperature ?? 'N/A',
            humidity: todayForecast.humidity ?? 'N/A'
          });
          
          // Only use up to 5 cities to keep the prompt concise
          if (citiesData.length >= 5) break;
        }
      }
    }

    const prompt = `
Generate a concise daily weather insight for Philippines travelers based on today's heat index forecast.

FORECAST DETAILS:
- Date: ${forecastDate}
- Overall heat comfort rating: ${ratingText} (${ratingScore}/100)
- Selected city data:
${JSON.stringify(citiesData, null, 2)}

FORMAT YOUR RESPONSE EXACTLY WITH THESE SECTIONS:
TODAY'S SUMMARY: [Brief 1-sentence overview of today's heat conditions nationwide]

CITY SPOTLIGHT: [Most notable city and its specific heat index situation]

TRAVEL TIP: [One practical travel tip based on today's heat forecast]

HEALTH ADVICE: [One key health precaution for travelers today]

Ensure your response is factual, concise, and based strictly on the provided heat index data. The entire response should be under 500 characters and formatted exactly as specified.
`;

    // Generate content using the existing model
    const result = await model.generateContent(prompt);
    return result.response.text().trim();
  } catch (error) {
    console.error("Error generating weather insights:", error);
    return `Could not generate weather insights. Error: ${error.message || "Unknown error"}. Please try again later.`;
  }
}

export { model };
