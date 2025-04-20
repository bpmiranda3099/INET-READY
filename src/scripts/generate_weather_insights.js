#!/usr/bin/env node

/**
 * Script to generate weather insights using the gemini-service
 * This acts as a bridge between Python and the JavaScript Gemini service
 */
import { fileURLToPath } from 'url';
import { dirname, resolve, join } from 'path';
import fs from 'fs/promises';
import { generateDailyWeatherInsights, generateCityWeatherInsight } from '../lib/services/gemini-service.js';

// Get the directory of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Parse ISO date strings in the forecast data back to Date objects 
 * This reverses what the Python script did for JSON serialization
 */
function parseISODates(obj) {
  if (obj === null || obj === undefined) return obj;
  
  if (typeof obj === 'string') {
    // Check if string is an ISO date
    const iso8601Regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/;
    if (iso8601Regex.test(obj)) {
      return new Date(obj);
    }
    return obj;
  }
  
  if (typeof obj === 'object') {
    if (Array.isArray(obj)) {
      return obj.map(parseISODates);
    }
    
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = parseISODates(value);
    }
    return result;
  }
  
  return obj;
}

/**
 * Process forecast data and generate insights using Gemini
 */
async function processForecasts() {
  try {
    // Check if input file was provided as argument
    const inputFile = process.argv[2];
    if (!inputFile) {
      console.error("Error: No input file specified");
      console.error("Usage: node generate_weather_insights.js <input-json-file> [output-file]");
      process.exit(1);
    }

    // Check if output file was provided as argument, otherwise use stdout
    const outputFile = process.argv[3];

    // Read the forecast data from the input file
    let forecastData = JSON.parse(await fs.readFile(inputFile, 'utf-8'));
    
    // Parse any ISO date strings back to Date objects
    forecastData = parseISODates(forecastData);

    let insights;
    // Detect if input is for a single city (has 'city' and 'forecast' keys)
    if (
      forecastData &&
      typeof forecastData === 'object' &&
      'city' in forecastData &&
      'forecast' in forecastData
    ) {
      insights = await generateCityWeatherInsight(forecastData.city, forecastData.forecast);
    } else {
      insights = await generateDailyWeatherInsights(forecastData);
    }

    // Either write to file or stdout
    if (outputFile) {
      await fs.writeFile(outputFile, insights);
      console.log(`Insights written to ${outputFile}`);
    } else {
      // Write directly to stdout so the Python script can capture it
      process.stdout.write(insights);
    }
  } catch (error) {
    console.error("Error generating weather insights:", error);
    process.exit(1);
  }
}

// Execute the main function
processForecasts();
