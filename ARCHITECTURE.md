# INET-READY System Architecture

This document provides an overview of the INET-READY system architecture, detailing the components, services, and integrations that power the application.

## Cloud Infrastructure

### Multi-Cloud Architecture

INET-READY uses a distributed cloud approach with these primary services:

- **Firebase (Google Cloud)**

  - Authentication: User identity management with email/password, Google, and Facebook providers
  - Firestore: NoSQL database for weather data, user preferences, and notifications
  - Cloud Messaging (FCM): Push notification delivery to browsers and mobile devices
  - Analytics: Usage tracking and performance monitoring

- **GitHub Actions**

  - Scheduled workflows for data collection, processing, and notifications
  - Automated deployment and integration testing
  - Repository mirroring to GitLab for CI/CD

- **Aptible**

  - HIPAA-compliant medical data backend (Express/PostgreSQL)
  - Secure API endpoints for medical profile management
  - Encryption, logging, and access controls for PHI

- **Vercel**
  - Frontend hosting and global CDN delivery
  - Analytics and performance monitoring
  - Integration with GitHub for CI/CD

## Frontend Architecture

### Progressive Web App (PWA)

- **SvelteKit**: Component-based UI framework with server-side rendering and hydration
- **Vite**: Modern build tooling for fast development and optimized production builds
- **Service Workers**: Offline support, push notifications, and caching
- **Responsive Design**: Mobile-first approach with fluid layouts and adaptive components
- **Bottom Navigation**: Mobile-optimized navigation with Dashboard, Medical Profile, Notifications, Settings, and Account sections

### Key Components

- **Authentication**: User registration, login, and account management
- **Dashboard**: Real-time weather data, heat index levels, city cards
- **Medical Profile**: Health information collection with risk visualization
- **Notifications**: Real-time alerts and notification history
- **Travel Health**: Dynamic cards with safety status between cities
- **Maps**: Interactive Mapbox integration for location visualization

## Backend Architecture

### Data Processing Pipeline

1. **Data Collection**

   - Hourly weather updates via OpenMeteo API
   - Historical data aggregation and storage
   - City coordinate management via OpenStreetMap

2. **Heat Index Calculation**

   - Real-time heat index computation from temperature and humidity
   - Implementation of standard NOAA heat index equation
   - Classification into INET levels (Safe, Caution, Warning, Danger, Extreme)

3. **Forecasting System**

   - XGBoost machine learning models for 7-day forecasting
   - Comprehensive validation (cross-validation, bootstrap, permutation tests)
   - Daily model updates and quality monitoring

4. **Notification System**

   - Detection of significant heat index changes (≥15% increase, ≥10% decrease)
   - City-specific notifications with contextual safety advice
   - Detailed delivery tracking and history logging

5. **AI Integration**
   - Node.js bridge to Google's Gemini API
   - Personalized health insights based on medical profile and weather conditions
   - Context-aware responses for travel planning questions

## Security Architecture

- **Authentication**: Firebase Authentication with multi-provider options
- **Authorization**: Firestore security rules for granular data access control
- **Encryption**: TLS for data in transit, AES for sensitive local data
- **HIPAA Compliance**: Medical data isolated on Aptible's HIPAA-ready platform
- **Session Management**: Token-based authentication with secure session handling

## Integration Architecture

- **OpenMeteo**: Weather data source for current, historical, and forecast data
- **OpenStreetMap**: Geographic data for city coordinates and mapping
- **Mapbox**: Interactive map visualization and geolocation services
- **Google Gemini AI**: Natural language processing for health insights
- **Firebase Cloud Messaging**: Cross-platform push notification delivery

## Automation Architecture

- **GitHub Actions Workflows**
  - Hourly Weather Update: Collects current conditions
  - Daily Historical Weather Update: Aggregates historical records
  - Daily Heat Index Forecast: Generates 7-day predictions
  - Daily Weather Insights: Produces AI-powered health recommendations
  - Heat Index Notifications: Sends alerts for significant changes
  - GitLab Mirror: Syncs repository for CI/CD

## Data Flow

1. **Weather Data Collection**

   - GitHub Actions triggers hourly_heat_index_api.py
   - Script fetches data from OpenMeteo
   - Data is processed and stored in Firestore

2. **User Interaction**

   - User selects cities of interest in the PWA
   - Firebase stores user preferences
   - Dashboard displays relevant weather data

3. **Heat Index Calculation**

   - Temperature and humidity processed with NOAA formula
   - System detects significant changes
   - Notifications triggered when thresholds exceeded

4. **Medical Data Management**

   - User submits medical profile through PWA
   - Data sent to Aptible backend via authenticated API
   - Medical risk levels calculated and returned to frontend

5. **Travel Health Assessment**
   - User selects origin and destination cities
   - System compares heat indices and user's medical profile
   - Travel safety status displayed (INET-READY, CAUTION, NOT INET-READY)

This architecture provides a secure, scalable foundation for the INET-READY system, enabling reliable heat index forecasting and health advisory services for users.
