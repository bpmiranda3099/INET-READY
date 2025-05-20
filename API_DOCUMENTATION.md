# INET-READY API Documentation

This document details the internal and external APIs used in the INET-READY system, including authentication requirements, endpoint specifications, request/response formats, and implementation details.

## Table of Contents

1. [External APIs](#external-apis)

   - [OpenMeteo API](#openmeteo-api)
   - [Overpass API (OpenStreetMap)](#overpass-api-openstreetmap)
   - [Mapbox API](#mapbox-api)
   - [Google Gemini API](#google-gemini-api)
   - [Firebase APIs](#firebase-apis)

2. [Internal APIs](#internal-apis)

   - [Medical Data API](#medical-data-api)
   - [Weather Data Service](#weather-data-service)
   - [Notification Service](#notification-service)

3. [Authentication & Authorization](#authentication--authorization)

   - [Firebase Authentication](#firebase-authentication)
   - [Firestore Security Rules](#firestore-security-rules)

4. [Data Formats](#data-formats)
   - [Heat Index Data](#heat-index-data)
   - [City Data](#city-data)
   - [Medical Profile](#medical-profile)
   - [Notification History](#notification-history)

## External APIs

### OpenMeteo API

#### Base URL

```
https://api.open-meteo.com/v1
```

#### Endpoints

##### Historical Weather Data

```
GET /forecast
```

**Parameters**:

- `latitude`: City latitude (float)
- `longitude`: City longitude (float)
- `hourly`: Comma-separated list of weather variables
- `past_days`: Number of past days to retrieve
- `forecast_days`: Number of forecast days
- `timezone`: Location timezone

**Example Request**:

```python
# From daily_historical_weather_data.py
params = {
    'latitude': city_data['latitude'],
    'longitude': city_data['longitude'],
    'hourly': 'temperature_2m,relativehumidity_2m,apparent_temperature,windspeed_10m,direct_radiation',
    'past_days': 1,
    'forecast_days': 0,
    'timezone': 'auto'
}
url = f"https://api.open-meteo.com/v1/forecast"
response = openmeteo_requests.get(url, params=params)
```

**Example Response**:

```json
{
  "latitude": 14.6042,
  "longitude": 120.9822,
  "generationtime_ms": 0.3380775451660156,
  "utc_offset_seconds": 28800,
  "timezone": "Asia/Manila",
  "timezone_abbreviation": "PST",
  "hourly": {
    "time": ["2023-05-19T00:00", "2023-05-19T01:00", ...],
    "temperature_2m": [28.3, 28.0, ...],
    "relativehumidity_2m": [84, 85, ...],
    "apparent_temperature": [32.5, 32.1, ...],
    "windspeed_10m": [5.8, 5.5, ...],
    "direct_radiation": [0, 0, ...]
  },
  "hourly_units": {
    "temperature_2m": "°C",
    "relativehumidity_2m": "%",
    "apparent_temperature": "°C",
    "windspeed_10m": "km/h",
    "direct_radiation": "W/m²"
  }
}
```

##### Weather Forecast

```
GET /forecast
```

**Parameters**:

- `latitude`: City latitude (float)
- `longitude`: City longitude (float)
- `hourly`: Comma-separated list of weather variables
- `forecast_days`: Number of days to forecast (1-16)
- `timezone`: Location timezone

**Example Request**:

```python
# From heat_index_forecast_api.py
params = {
    'latitude': city_data['latitude'],
    'longitude': city_data['longitude'],
    'hourly': 'temperature_2m,relativehumidity_2m,apparent_temperature,windspeed_10m,direct_radiation',
    'forecast_days': 7,
    'timezone': 'auto'
}
url = f"https://api.open-meteo.com/v1/forecast"
response = openmeteo_requests.get(url, params=params)
```

### Overpass API (OpenStreetMap)

Used for retrieving city coordinates and geospatial data.

#### Base URL

```
https://overpass-api.de/api/interpreter
```

**Example Usage**:

```python
# From city_coords.py
import overpy

api = overpy.Overpass()

# Query for city data in the Philippines
query = """
[out:json];
area["name"="Philippines"]["admin_level"="2"];
(
  node["place"="city"](area);
  node["place"="town"](area);
);
out body;
"""

result = api.query(query)
```

### Mapbox API

Used for interactive maps and geolocation services.

#### Base URL

```
https://api.mapbox.com
```

**Client Integration**:

```javascript
// From map-background.svelte
import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_KEY;

const initMap = () => {
	const map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/streets-v11',
		center: [centerLng, centerLat],
		zoom: 5
	});

	// Add markers for cities
	cityData.forEach((city) => {
		const marker = new mapboxgl.Marker()
			.setLngLat([city.longitude, city.latitude])
			.setPopup(
				new mapboxgl.Popup().setHTML(`<h3>${city.name}</h3><p>Heat Index: ${city.heatIndex}°C</p>`)
			)
			.addTo(map);
	});

	return map;
};
```

### Google Gemini API

Used for generating personalized weather insights and health recommendations.

#### Integration

```javascript
// From gemini-service.js
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function generateWeatherInsights(cityData, userProfile) {
	const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

	const prompt = `
    Generate a personalized weather insight for a user in ${cityData.city}.
    
    Current weather conditions:
    - Temperature: ${cityData.temperature}°C
    - Heat Index: ${cityData.heatIndex}°C
    - Humidity: ${cityData.humidity}%
    - INET Level: ${cityData.inetLevel}
    
    User medical profile:
    - Age: ${userProfile.age}
    - Medical conditions: ${userProfile.conditions.join(', ')}
    - Heat-related conditions: ${userProfile.heatConditions.join(', ')}
    - Activity level: ${userProfile.activityLevel}
    
    Provide a concise insight about today's weather conditions and personalized health recommendations based on the user's profile.
  `;

	const result = await model.generateContent(prompt);
	const response = await result.response;
	return response.text();
}
```

### Firebase APIs

#### Firestore

```javascript
// From firebase.js
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';

// Initialize Firebase
const app = initializeApp({
	apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
	authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
	projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
	storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
	messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
	appId: import.meta.env.VITE_FIREBASE_APP_ID,
	measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
});

export const db = getFirestore(app);
```

#### Authentication

```javascript
// From firebase.js
import {
	getAuth,
	signInWithEmailAndPassword,
	createUserWithEmailAndPassword,
	signOut
} from 'firebase/auth';

export const auth = getAuth(app);

// Sign in with email/password
export async function signIn(email, password) {
	return signInWithEmailAndPassword(auth, email, password);
}

// Register new user
export async function signUp(email, password) {
	return createUserWithEmailAndPassword(auth, email, password);
}

// Sign out
export async function logOut() {
	return signOut(auth);
}
```

#### Cloud Messaging

```javascript
// From firebase.js
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

export const messaging = getMessaging(app);

// Request permission and get FCM token
export async function requestNotificationPermission() {
	try {
		const permission = await Notification.requestPermission();
		if (permission === 'granted') {
			const token = await getToken(messaging, {
				vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
			});
			return token;
		}
	} catch (error) {
		console.error('Error requesting notification permission:', error);
	}
	return null;
}

// Handle foreground messages
export function setupMessageListener(callback) {
	return onMessage(messaging, (payload) => {
		callback(payload);
	});
}
```

## Internal APIs

### Medical Data API

Securely stores and retrieves medical profile data using Aptible's HIPAA-compliant infrastructure.

#### Base URL

```
https://app-91403.on-aptible.com
```

#### Authentication

All requests require a Firebase ID token in the Authorization header:

```javascript
// From medical-api.js
const headers = {
	'Content-Type': 'application/json',
	Authorization: `Bearer ${await getIdToken()}`
};

// Get Firebase ID token
async function getIdToken() {
	const user = auth.currentUser;
	if (!user) throw new Error('User not authenticated');
	return user.getIdToken();
}
```

#### Endpoints

##### Store Medical Data

```
POST /store-medical-data
```

**Request Body**:

```json
{
	"medicalData": {
		"demographics": {
			"age": 35,
			"gender": "female",
			"weight": 65,
			"height": 165
		},
		"medicalConditions": ["asthma", "hypertension"],
		"medications": ["albuterol", "lisinopril"],
		"heatConditions": ["heat_exhaustion", "heat_rash"],
		"fluidIntake": {
			"water": 2000,
			"sportsDrinks": 500,
			"coffee": 250
		},
		"activityLevel": {
			"frequency": "daily",
			"intensity": "moderate",
			"duration": 45
		}
	}
}
```

**Response**:

```json
{
	"success": true,
	"message": "Medical data stored successfully"
}
```

##### Get Medical Data

```
GET /get-medical-data
```

**Response**:

```json
{
  "medicalData": {
    "demographics": { ... },
    "medicalConditions": [ ... ],
    "medications": [ ... ],
    "heatConditions": [ ... ],
    "fluidIntake": { ... },
    "activityLevel": { ... }
  },
  "riskLevel": "medium",
  "lastUpdated": "2023-05-19T10:15:30.123Z"
}
```

##### Delete Medical Data

```
DELETE /delete-medical-data
```

**Response**:

```json
{
	"success": true,
	"message": "Medical data deleted successfully"
}
```

### Weather Data Service

Internal service for retrieving and processing weather data.

#### Example Usage

```javascript
// From weather-data-service.js
import { db } from '$lib/firebase';
import { collection, query, where, orderBy, limit, getDocs } from 'firebase/firestore';

export async function getCurrentWeather(city) {
	try {
		const q = query(
			collection(db, 'current_weather'),
			where('city', '==', city),
			orderBy('timestamp', 'desc'),
			limit(1)
		);

		const querySnapshot = await getDocs(q);
		if (querySnapshot.empty) {
			return null;
		}

		return {
			id: querySnapshot.docs[0].id,
			...querySnapshot.docs[0].data()
		};
	} catch (error) {
		console.error(`Error getting current weather for ${city}:`, error);
		throw error;
	}
}

export async function getHeatIndexForecast(city, days = 7) {
	try {
		const today = new Date();
		const endDate = new Date();
		endDate.setDate(today.getDate() + days);

		const q = query(
			collection(db, 'heat_index_predictions'),
			where('city', '==', city),
			where('date', '>=', today),
			where('date', '<=', endDate),
			orderBy('date', 'asc')
		);

		const querySnapshot = await getDocs(q);
		return querySnapshot.docs.map((doc) => ({
			id: doc.id,
			...doc.data(),
			date: doc.data().date.toDate()
		}));
	} catch (error) {
		console.error(`Error getting heat index forecast for ${city}:`, error);
		throw error;
	}
}
```

### Notification Service

Internal service for sending and managing notifications.

#### Example Usage

```javascript
// Firebase Cloud Function for sending test notifications
// From functions/sendTestNotification.js
const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

exports.sendTestNotification = functions.https.onCall(async (data, context) => {
	// Verify authentication
	if (!context.auth) {
		throw new functions.https.HttpsError(
			'unauthenticated',
			'The function must be called while authenticated.'
		);
	}

	const { token, title, body } = data;

	try {
		await admin.messaging().send({
			notification: {
				title,
				body
			},
			token
		});

		// Log notification to history
		await admin.firestore().collection('notification_history').add({
			userId: context.auth.uid,
			title,
			body,
			status: 'success',
			category: 'system',
			timestamp: admin.firestore.FieldValue.serverTimestamp()
		});

		return { success: true };
	} catch (error) {
		console.error('Error sending notification:', error);
		return {
			success: false,
			error: error.message
		};
	}
});
```

## Authentication & Authorization

### Firebase Authentication

#### User Authentication Flow

1. **Sign Up**:

   ```javascript
   // Register with email/password
   async function signUp(email, password) {
   	try {
   		const userCredential = await createUserWithEmailAndPassword(auth, email, password);
   		return userCredential.user;
   	} catch (error) {
   		console.error('Error signing up:', error);
   		throw error;
   	}
   }

   // Register with Google
   async function signUpWithGoogle() {
   	const provider = new GoogleAuthProvider();
   	try {
   		const userCredential = await signInWithPopup(auth, provider);
   		return userCredential.user;
   	} catch (error) {
   		console.error('Error signing up with Google:', error);
   		throw error;
   	}
   }
   ```

2. **Sign In**:

   ```javascript
   // Sign in with email/password
   async function signIn(email, password) {
   	try {
   		const userCredential = await signInWithEmailAndPassword(auth, email, password);
   		return userCredential.user;
   	} catch (error) {
   		console.error('Error signing in:', error);
   		throw error;
   	}
   }

   // Sign in with Google
   async function signInWithGoogle() {
   	const provider = new GoogleAuthProvider();
   	try {
   		const userCredential = await signInWithPopup(auth, provider);
   		return userCredential.user;
   	} catch (error) {
   		console.error('Error signing in with Google:', error);
   		throw error;
   	}
   }
   ```

3. **Sign Out**:
   ```javascript
   async function signOut() {
   	try {
   		await auth.signOut();
   	} catch (error) {
   		console.error('Error signing out:', error);
   		throw error;
   	}
   }
   ```

### Firestore Security Rules

Security rules that protect user data:

```
// Example Firestore security rules for INET-READY

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User profiles - only accessible by the user
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // City preferences - only accessible by the user
    match /cityPreferences/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Notification history - only accessible by the user
    match /notification_history/{notificationId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow write: if false; // Only writable by server
    }

    // Weather data - publicly readable
    match /current_weather/{docId} {
      allow read: if true;
      allow write: if false; // Only writable by server
    }

    // Heat index predictions - publicly readable
    match /heat_index_predictions/{docId} {
      allow read: if true;
      allow write: if false; // Only writable by server
    }
  }
}
```

## Data Formats

### Heat Index Data

#### Current Weather

```json
{
	"city": "Manila",
	"temperature": 32.5,
	"humidity": 75,
	"heatIndex": 41.2,
	"windSpeed": 5.8,
	"inetLevel": "WARNING",
	"timestamp": "2023-05-19T10:15:30.123Z"
}
```

#### Heat Index Prediction

```json
{
	"city": "Manila",
	"date": "2023-05-20",
	"temperature": 33.1,
	"humidity": 78,
	"heatIndex": 42.7,
	"inetLevel": "DANGER",
	"modelQualityRating": 85
}
```

### City Data

```json
{
	"name": "Manila",
	"latitude": 14.6042,
	"longitude": 120.9822,
	"country": "Philippines",
	"population": 1780148,
	"timezone": "Asia/Manila"
}
```

### Medical Profile

```json
{
	"demographics": {
		"age": 35,
		"gender": "female",
		"weight": 65,
		"height": 165
	},
	"medicalConditions": ["asthma", "hypertension"],
	"medications": ["albuterol", "lisinopril"],
	"heatConditions": ["heat_exhaustion", "heat_rash"],
	"fluidIntake": {
		"water": 2000,
		"sportsDrinks": 500,
		"coffee": 250,
		"tea": 300,
		"soda": 0,
		"juice": 200,
		"milkTea": 0
	},
	"activityLevel": {
		"frequency": "daily",
		"intensity": "moderate",
		"duration": 45
	}
}
```

### Notification History

```json
{
	"userId": "user123",
	"title": "Heat Index Alert: Manila",
	"body": "Significant increase detected in Manila. Stay indoors and always hydrate!",
	"data": {
		"type": "increase",
		"city": "Manila",
		"current_value": 42.7,
		"previous_value": 36.2,
		"percent_change": 18.0,
		"inet_level": "DANGER"
	},
	"category": "emergency",
	"status": "success",
	"timestamp": "2023-05-19T10:15:30.123Z"
}
```

## API Best Practices

When interacting with INET-READY APIs, follow these best practices:

1. **Authentication**

   - Always include Firebase ID tokens for authenticated endpoints
   - Refresh tokens when they expire (typically after 1 hour)

2. **Error Handling**

   - Implement proper error handling for all API calls
   - Check response status codes and handle errors gracefully
   - Include retry logic for transient errors with external APIs

3. **Rate Limiting**

   - Respect rate limits for external APIs (OpenMeteo, Mapbox, etc.)
   - Implement caching where appropriate to reduce API calls
   - Use batch operations when possible to reduce the number of requests

4. **Performance**

   - Use query limits and pagination for large data sets
   - Filter data server-side whenever possible
   - Use indexing for frequently queried fields
   - Minimize payload sizes by requesting only needed fields

5. **Security**
   - Never store API keys in client-side code
   - Use environment variables for sensitive configuration
   - Validate all user inputs before sending to APIs
   - Follow the principle of least privilege for API access
