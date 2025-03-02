#!/usr/bin/env node

/**
 * Script to generate weather insights using the gemini-service
 * This acts as a bridge between Python and the JavaScript Gemini service
 */
import { fileURLToPath } from 'url';
import { dirname, resolve, join } from 'path';
import fs from 'fs/promises';
import { generateDailyWeatherInsights } from '../lib/services/gemini-service.js';

// Get the directory of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
    const forecastData = JSON.parse(await fs.readFile(inputFile, 'utf-8'));

    // Generate insights using the gemini-service
    const insights = await generateDailyWeatherInsights(forecastData);

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
