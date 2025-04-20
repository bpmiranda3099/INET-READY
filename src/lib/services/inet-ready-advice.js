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

// Helper: extract city name before comma (e.g., 'Dasmariñas, Cavite' -> 'Dasmariñas')
function extractCityName(city) {
	if (!city) return '';
	return city.split(',')[0].trim();
}

// Main function: get INET-READY status and advice
export async function getInetReadyStatus({ fromCity, toCity, medicalData }) {
	// Always sanitize city names to avoid province/region mismatches
	const cleanFromCity = extractCityName(fromCity);
	const cleanToCity = extractCityName(toCity);

	const [fromData, toData] = await Promise.all([
		getCityData(cleanFromCity),
		getCityData(cleanToCity)
	]);
	const fromHeat = fromData?.heat_index;
	const toHeat = toData?.heat_index;
	const fromLevel = getHeatIndexLevel(fromHeat);
	const toLevel = getHeatIndexLevel(toHeat);
	const distance = getDistanceBetweenCities(cleanFromCity, cleanToCity);
	const vulnerable = isHeatVulnerable(medicalData);

	let safe = true;
	let reasons = [];
	let adviceParts = [];

	// HIPAA/PH privacy: never display or infer specific diagnoses, only general risk
	// Always remind to consult a healthcare professional for medical decisions

	// Edge: Same city (no travel)
	if (cleanFromCity === cleanToCity) {
		adviceParts.push('Origin and destination are the same. No travel needed.');
		if (fromLevel === 'danger' || fromLevel === 'extreme') {
			adviceParts.push('Stay indoors due to dangerous heat in your city.');
			safe = false;
			reasons.push('Dangerous heat in your city');
		}
		if (fromLevel === 'safe') adviceParts.push('Enjoy your day!');
		adviceParts.push('For any health concerns, consult a licensed healthcare provider.');
		return {
			status: safe ? 'INET-READY' : 'NOT INET-READY',
			advice: adviceParts.join(' '),
			fromHeat,
			toHeat,
			distance: 0,
			fromLevel,
			toLevel
		};
	}

	// Distance logic
	if (distance == null) {
		safe = false;
		reasons.push('Unknown route distance');
		adviceParts.push('Unable to determine travel safety due to missing route data.');
	}
	else {
		if (distance < 1) adviceParts.push('Very short trip. Minimal risk.');
		else if (distance < 10) adviceParts.push('Short trip: minimal travel risk.');
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
	if (fromLevel === 'unknown' || toLevel === 'unknown') {
		adviceParts.push('Heat index data unavailable for one or both cities. Use general heat safety precautions.');
	}
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

	// Medical risk logic (general, not specific)
	if (vulnerable) {
		if (heatLevels.includes('warning') || heatLevels.includes('danger') || heatLevels.includes('extreme')) {
			safe = false;
			reasons.push('Increased risk with current heat');
			adviceParts.push('Individuals with certain health conditions or age groups may be at higher risk in this heat.');
		} else {
			adviceParts.push('Some individuals may be more sensitive to heat. Monitor your well-being during travel.');
		}
	}

	// Specific advice for children and elderly (general, not personal)
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
		adviceParts.push(`Note: Heat index differs between ${cleanFromCity} (${fromLevel}) and ${cleanToCity} (${toLevel}). Prepare accordingly.`);
		if (fromLevel === 'safe' && toLevel === 'caution') adviceParts.push('Expect warmer conditions at your destination.');
		if (fromLevel === 'caution' && toLevel === 'safe') adviceParts.push('It will be cooler at your destination.');
		if (fromLevel === 'warning' && toLevel === 'danger') adviceParts.push('Conditions worsen as you travel. Take extra care.');
		if (fromLevel === 'danger' && toLevel === 'warning') adviceParts.push('Conditions improve at your destination, but remain alert.');
	}

	// If user has no medical data
	if (!medicalData) {
		adviceParts.push('No medical data found. For best advice, update your health profile.');
	}

	// If both cities are caution or higher, but not dangerous
	if (!heatLevels.includes('safe') && !heatLevels.includes('danger') && !heatLevels.includes('extreme')) {
		adviceParts.push('Monitor for signs of heat stress: dizziness, headache, or nausea.');
	}

	// Edge: Both cities have unknown heat index
	if (fromLevel === 'unknown' && toLevel === 'unknown') {
		adviceParts.push('No heat index data for either city. Use general heat safety precautions.');
	}

	// Edge: Distance is very large and both cities are dangerous/extreme
	if (distance > 100 && (fromLevel === 'danger' || toLevel === 'danger' || fromLevel === 'extreme' || toLevel === 'extreme')) {
		adviceParts.push('Traveling a long distance in dangerous heat is extremely risky. Postpone your trip.');
		safe = false;
	}

	// Edge: Vulnerable and both cities are warning or higher
	if (vulnerable && (fromLevel === 'warning' || toLevel === 'warning' || fromLevel === 'danger' || toLevel === 'danger' || fromLevel === 'extreme' || toLevel === 'extreme')) {
		adviceParts.push('Combined risk factors make travel especially unsafe.');
		safe = false;
	}

	// Edge: Not vulnerable, both cities are safe, but distance is long
	if (!vulnerable && heatLevels.every(l => l === 'safe') && distance > 50) {
		adviceParts.push('Even with safe weather, long trips require planning. Bring water and rest often.');
	}

	// Edge: Vulnerable, both cities are safe, distance is short
	if (vulnerable && heatLevels.every(l => l === 'safe') && distance < 10) {
		adviceParts.push('Conditions are good, but monitor your health during your trip.');
	}

	// Edge: Child or elderly, cities are caution or higher
	if ((age < 10 || age > 65) && (fromLevel === 'caution' || toLevel === 'caution' || fromLevel === 'warning' || toLevel === 'warning')) {
		adviceParts.push('Extra caution for children and elderly in warm weather.');
	}

	// Edge: If fromHeat or toHeat is very close to a threshold
	if (fromHeat && Math.abs(fromHeat - 27) < 1) adviceParts.push('Heat index is near caution threshold. Monitor for changes.');
	if (toHeat && Math.abs(toHeat - 27) < 1) adviceParts.push('Destination heat index is near caution threshold.');
	if (fromHeat && Math.abs(fromHeat - 33) < 1) adviceParts.push('Heat index is near warning threshold.');
	if (toHeat && Math.abs(toHeat - 33) < 1) adviceParts.push('Destination heat index is near warning threshold.');
	if (fromHeat && Math.abs(fromHeat - 42) < 1) adviceParts.push('Heat index is near danger threshold.');
	if (toHeat && Math.abs(toHeat - 42) < 1) adviceParts.push('Destination heat index is near danger threshold.');
	if (fromHeat && Math.abs(fromHeat - 52) < 1) adviceParts.push('Heat index is near extreme threshold.');
	if (toHeat && Math.abs(toHeat - 52) < 1) adviceParts.push('Destination heat index is near extreme threshold.');

	// Always add a general disclaimer for legal/medical compliance
	adviceParts.push('This advice is for informational purposes only and does not constitute medical advice. For any health concerns or symptoms, consult a licensed healthcare professional.');
	adviceParts.push('Your privacy is protected. No sensitive health details are shown.');

	const status = safe ? 'INET-READY' : 'NOT INET-READY';
	let advice = adviceParts.filter(Boolean).join(' ');
	if (!advice) advice = safe
		? `Travel from ${cleanFromCity} to ${cleanToCity} is considered safe at this time.`
		: `Travel from ${cleanFromCity} to ${cleanToCity} is not recommended now due to: ${reasons.join(', ')}.`;

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
