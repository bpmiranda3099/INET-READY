// INET-READY travel safety logic for health cards
import { getCityData } from './weather-data-service';
import { cityDistances } from './city-distances';

// Helper: get distance between two cities (returns km or null)
function getDistanceBetweenCities(cityA, cityB) {
	for (const entry of cityDistances) {
		if (
			(entry.cityA === cityA && entry.cityB === cityB) ||
			(entry.cityA === cityB && entry.cityB === cityA)
		) {
			return entry.distanceKm;
		}
	}
	return null;
}

// Helper: get heat index risk level
function getHeatIndexLevel(heatIndex) {
	if (heatIndex == null || isNaN(heatIndex)) return 'unknown';
	if (heatIndex < 27) return 'safe';
	if (heatIndex < 33) return 'caution';
	if (heatIndex < 42) return 'warning';
	if (heatIndex < 52) return 'danger';
	return 'extreme';
}

// Helper: determine if user is heat-vulnerable
function isHeatVulnerable(medicalData) {
	if (!medicalData) return false;
	const conditions = [
		'cardiovascular_disease',
		'diabetes',
		'kidney_disease',
		'neurological_disorders',
		'respiratory_issues',
		'heat_sensitivity',
		'asthma',
		'high_blood_pressure',
		'thyroid_disorder'
	];
	for (const cond of conditions) {
		if (medicalData.medical_conditions?.[cond]) return true;
	}
	// Age-based risk
	const age = Number(medicalData.demographics?.age);
	if (age && (age < 10 || age > 65)) return true;
	return false;
}

// Main function: get INET-READY status and advice
export async function getInetReadyStatus({ fromCity, toCity, medicalData }) {
	const [fromData, toData] = await Promise.all([
		getCityData(fromCity),
		getCityData(toCity)
	]);
	const fromHeat = fromData?.heat_index;
	const toHeat = toData?.heat_index;
	const fromLevel = getHeatIndexLevel(fromHeat);
	const toLevel = getHeatIndexLevel(toHeat);
	const distance = getDistanceBetweenCities(fromCity, toCity);
	const vulnerable = isHeatVulnerable(medicalData);

	// Decision logic
	let safe = true;
	let reasons = [];
	let adviceParts = [];

	if (distance == null) {
		safe = false;
		reasons.push('Unknown route distance');
		adviceParts.push('Unable to determine travel safety due to missing route data.');
	}
	if (distance !== null) {
		if (distance < 10) adviceParts.push('Short trip: minimal travel risk.');
		else if (distance < 50) adviceParts.push('Moderate distance: plan for hydration and rest.');
		else if (distance < 100) adviceParts.push('Longer journey: bring water, sun protection, and take breaks.');
		else {
			safe = false;
			reasons.push('Long travel distance');
			adviceParts.push('Very long trip: avoid travel if possible, especially in heat.');
		}
	}

	// Heat index logic for both cities
	const heatLevels = [fromLevel, toLevel];
	if (heatLevels.includes('extreme')) {
		safe = false;
		reasons.push('Extreme heat index');
		adviceParts.push('Extreme heat detected: travel is highly discouraged.');
	} else if (heatLevels.includes('danger')) {
		safe = false;
		reasons.push('Dangerous heat index');
		adviceParts.push('Dangerous heat index: avoid travel and stay indoors if possible.');
	} else if (heatLevels.includes('warning')) {
		adviceParts.push('Warning: High heat index. Limit outdoor activity and rest often.');
	} else if (heatLevels.includes('caution')) {
		adviceParts.push('Caution: Mild heat risk. Stay hydrated and wear light clothing.');
	} else if (heatLevels.every(l => l === 'safe')) {
		adviceParts.push('Weather is favorable for travel.');
	}

	// Medical risk logic
	if (vulnerable) {
		if (heatLevels.includes('warning') || heatLevels.includes('danger') || heatLevels.includes('extreme')) {
			safe = false;
			reasons.push('Medical risk with current heat');
			adviceParts.push('Your medical profile increases your risk in current heat. Consult your doctor before travel.');
		} else {
			adviceParts.push('You have medical conditions that may increase your risk. Monitor your health closely.');
		}
	}

	// Specific advice for children and elderly
	const age = Number(medicalData?.demographics?.age);
	if (age) {
		if (age < 10) adviceParts.push('Children are more sensitive to heat. Ensure frequent breaks and hydration.');
		if (age > 65) adviceParts.push('Older adults are at higher risk for heat-related illness. Avoid peak sun hours.');
	}

	// If both cities are safe and distance is short
	if (safe && heatLevels.every(l => l === 'safe') && distance !== null && distance < 10) {
		adviceParts.push('Ideal conditions for a quick trip.');
	}

	// If cities have different heat levels
	if (fromLevel !== toLevel) {
		adviceParts.push(`Note: Heat index differs between ${fromCity} (${fromLevel}) and ${toCity} (${toLevel}). Prepare accordingly.`);
	}

	// If user has no medical data
	if (!medicalData) {
		adviceParts.push('No medical data found. For best advice, update your health profile.');
	}

	// If both cities are caution or higher, but not dangerous
	if (!heatLevels.includes('safe') && !heatLevels.includes('danger') && !heatLevels.includes('extreme')) {
		adviceParts.push('Monitor for signs of heat stress: dizziness, headache, or nausea.');
	}

	// If user is traveling during midday (optional, if time data is available)
	// adviceParts.push('Avoid traveling during midday when heat is most intense.');

	const status = safe ? 'INET-READY' : 'NOT INET-READY';

	// Compose final advice sentence
	let advice = adviceParts.filter(Boolean).join(' ');
	if (!advice) advice = safe
		? `Travel from ${fromCity} to ${toCity} is considered safe at this time.`
		: `Travel from ${fromCity} to ${toCity} is not recommended now due to: ${reasons.join(', ')}.`;

	return {
		status,
		advice,
		fromHeat,
		toHeat,
		distance,
		fromLevel,
		toLevel
	};
}
