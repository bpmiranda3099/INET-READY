# INET-READY: Your Heat Check for Safe and Informed Travel

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Web-brightgreen)
![Status](https://img.shields.io/badge/status-Active-success)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Finet-ready-v2.vercel.app&up_message=live&down_message=offline&timeout=1000&label=Website&color=purple)](https://inet-ready-v2.vercel.app)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=bpmiranda3099.inet-ready-v2)
[![Heat Index Forecast Update](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/daily_heat_index_forecast_update.yml?branch=main&label=Heat%20Index%20Forecast)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/daily_heat_index_forecast_update.yml)
[![Historical Weather Update](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/daily_historical_weather_update.yml?branch=main&label=Historical%20Weather)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/daily_historical_weather_update.yml)
[![Weather Insights](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/daily_weather_insights.yml?branch=main&label=Weather%20Insights)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/daily_weather_insights.yml)
[![Heat Index Notifications](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/heat_index_notifications.yml?branch=main&label=Heat%20Index%20Notifications)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/heat_index_notifications.yml)
[![Hourly Weather Update](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/hourly_weather_update.yml?branch=main&label=Hourly%20Weather)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/hourly_weather_update.yml)
[![EHR Aptible CD](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/inet-ready-ehr/deploy.yml?branch=main&label=EHR%20Aptible)](https://github.com/bpmiranda3099/inet-ready-ehr/actions/workflows/deploy.yml)
[![GitLab Mirror](https://img.shields.io/github/actions/workflow/status/bpmiranda3099/INET-READY/gitlab_mirror.yml?branch=main&label=GitLab%20Mirror)](https://github.com/bpmiranda3099/INET-READY/actions/workflows/gitlab_mirror.yml)

_*For CI/CD details, see the [CI/CD README](/.github/workflows/README.md).*_

</div>

---

> **Compliance Notice:**  
> This deployment of INET-READY is intended solely for development and testing purposes. It is **not HIPAA compliant** as it is not running on a dedicated Aptible stack, which is a requirement for production-level HIPAA compliance.  
> **Do not use this system to store or process real Protected Health Information (PHI) or other sensitive data in a production environment.**
>
> **Production Use:**  
> INET-READY can be configured for HIPAA compliance when deployed on a dedicated Aptible stack, accompanied by appropriate organizational policies and safeguards. For production deployments involving healthcare data, please consult your compliance officer or legal counsel to ensure all regulatory requirements are met.

---

## 📝 Overview

INET-READY is a modern, privacy-focused platform for safe and informed travel. It combines real-time heat index forecasting, personalized health risk insights, and secure medical data management. The system leverages SvelteKit, Firebase, Python, and Node.js to deliver timely notifications and actionable travel health guidance.

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://img.shields.io/badge/SvelteKit-FF3E00?logo=svelte&logoColor=white&style=for-the-badge" alt="SvelteKit"/>
  <img src="https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=white&style=for-the-badge" alt="Firebase"/>
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge" alt="Python"/>
  <img src="https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white&style=for-the-badge" alt="Node.js"/>
  <img src="https://img.shields.io/badge/Mapbox-4264FB?logo=mapbox&logoColor=white&style=for-the-badge" alt="Mapbox"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white&style=for-the-badge" alt="Vite"/>
  <img src="https://img.shields.io/badge/Aptible-2B2B2B?logo=aptible&logoColor=white&style=for-the-badge" alt="Aptible"/>
</p>

---

## 🚧 Demo

> **Work in Progress**  
> A live demo will be available soon. Check back later for updates.

<!-- Replace with your actual screenshot or GIF when ready -->
<!-- <p align="center">
  <img src="assets/screenshot.png" alt="INET-READY Demo" width="600"/>
</p> -->

---

## Quick Start

```sh
git clone https://github.com/bpmiranda3099/inet-ready-v2.git
cd inet-ready-v2
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📦 Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- Python 3.8+
- Firebase project (web + service account)
- Mapbox API key (for maps)
- (Optional) Aptible/Vercel for deployment

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/bpmiranda3099/inet-ready-v2.git
   cd inet-ready-v2
   ```
2. **Install dependencies:**
   ```sh
   npm install
   ```
3. **Set up environment variables:**

   - Create a `.env` file in the root with:
     ```env
     VITE_FIREBASE_API_KEY=...
     VITE_FIREBASE_AUTH_DOMAIN=...
     VITE_FIREBASE_PROJECT_ID=...
     VITE_FIREBASE_STORAGE_BUCKET=...
     VITE_FIREBASE_MESSAGING_SENDER_ID=...
     VITE_FIREBASE_APP_ID=...
     VITE_FIREBASE_MEASUREMENT_ID=...
     VITE_FIREBASE_VAPID_KEY=...
     VITE_MAPBOX_API_KEY=...
     ```
   - Place your Firebase service account key in [`config/firebase-credentials.json`](config/firebase-credentials.json) for backend scripts.

4. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## 🌐 APIs Used in INET-READY

For a summary of the APIs used, see below. **Detailed API endpoint usage is described in the [API Endpoints (Medical Data)](#-api-endpoints-medical-data) section.**

### External APIs

#### a. OpenMeteo API

- **Purpose:** Weather, forecast, and historical data for all supported cities
- **Usage:** Python scripts (`openmeteo_requests`, `requests`) and data ingestion
- **Docs:** https://open-meteo.com/

#### b. Overpass API (OpenStreetMap)

- **Purpose:** Geospatial data for city coordinates
- **Usage:** Python scripts via `overpy`
- **Docs:** https://overpass-api.de/

#### c. Mapbox API

- **Purpose:** Interactive maps and geolocation in the frontend
- **Usage:** `mapbox-gl` in Svelte components
- **Docs:** https://docs.mapbox.com/

#### d. Google Gemini API (Generative AI)

- **Purpose:** AI-powered chatbot and medical/travel advice
- **Usage:** `@google/generative-ai` in `gemini-service.js` (frontend) and via Node.js bridge in backend scripts
- **Docs:** https://ai.google.dev/gemini-api/docs

#### e. Firebase APIs

- **Purpose:** Authentication, Firestore database, Cloud Messaging (FCM), Analytics
- **Usage:** Web SDK (`firebase`), backend scripts (`firebase-admin`, `google-cloud-firestore`)

#### f. Google Cloud APIs

- **Purpose:** Used by backend scripts for Firestore and service account access
- **Usage:** `google-api-python-client`, `google-cloud-firestore`

---

### 3. Other Notable Endpoints/Services

- **Firebase Cloud Functions**
  - `functions/sendTestNotification.js` — For sending test push notifications via FCM (see [Backend Scripts](#-usage))
- **Vercel Analytics**
  - `@vercel/speed-insights` — For frontend analytics

---

### 4. Service Workers

- **Path:** `/firebase-messaging-sw.js`
- **Purpose:** Handles push notifications and caching for offline support (see [Notifications](#-notifications) for user-facing info)

## 🌟 Features

- **Authentication & Account Management**: User registration/login (email, Google, Facebook), email verification, password reset, logout, linked accounts
- **Dashboard & Navigation**: Tabbed dashboard, bottom navigation, app bar
- **City Preferences & Location**: City selection, preferences, location tracking, permissions
- **Medical Profile & Form**: Medical data entry, profile display, health insights, visualizations
- **Travel Health Cards**: Dynamic cards for weather, heat index, health status, hospitals, advice
- **Notifications**: Real-time push notifications, notification history, permission management
- **Chatbot Assistant (SafeTrip AI)**: AI-powered travel and health Q&A, context-aware, mobile-friendly
- **Permissions & Settings**: Permissions panel, display preferences, privacy controls
- **Onboarding & Welcome**: Welcome modal, onboarding steps, user greeting
- **Visual & UI Components**: Cards, banners, responsive design, modals, tooltips
- **Data & Integration**: Weather, heat index, geospatial, and medical data integration
- **Automated Data Collection**: Automated scripts for weather and heat index updates (see [CI/CD & GitHub Workflows](#️-cicd--github-workflows))
- **Deployment & Security**: Automated deployment, secure credentials, manual workflow triggers (see [Deployment](#-deployment) and [CI/CD & GitHub Workflows](#️-cicd--github-workflows))
- **Miscellaneous**: Admin tools, analytics, FAQ, logout/session management

---

## 🧪 Usage

### Local Development

```sh
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) in your browser.

### Backend Scripts

- **Weather & Heat Index Forecasts:**
  - [`src/scripts/heat_index_forecast_api.py`](src/scripts/heat_index_forecast_api.py) — Generate and serve forecasts (CLI/API)
  - [`src/scripts/daily_weather_insights.py`](src/scripts/daily_weather_insights.py) — Generate insights, send notifications
  - [`src/scripts/generate_weather_insights.js`](src/scripts/generate_weather_insights.js) — Node.js bridge for Gemini AI
- **Medical Data API:**
  - [`src/lib/services/medical-api.js`](src/lib/services/medical-api.js) — Communicates with Aptible-hosted Express/Postgres backend
- **Notification Service:**
  - [`functions/sendTestNotification.js`](functions/sendTestNotification.js) — Firebase Cloud Function for push notification testing (see [Notifications](#-notifications) for user-facing info)

---

## 🧪 API Endpoints (Medical Data)

All endpoints require a valid Firebase ID token in the `Authorization: Bearer <token>` header.

### `POST /store-medical-data`

- **Description:** Create or update user medical data
- **Body:**
  ```json
  {
  	"medicalData": {
  		/* your data */
  	}
  }
  ```

### `GET /get-medical-data`

- **Description:** Fetch authenticated user's medical data

### `DELETE /delete-medical-data`

- **Description:** Delete user's medical data

---

## 🔔 Notifications

- Real-time push notifications via Firebase Cloud Messaging (FCM)
- Customizable alert thresholds and city preferences
- Service worker: `static/firebase-messaging-sw.js`

---

## 🗺️ Maps & Location

- Interactive city map (Mapbox)
- Location tracking and city-based risk insights

---

## 🌤️ Data Sources: OpenMeteo API

INET-READY collects and processes weather and heat index data using the [OpenMeteo API](https://open-meteo.com/):

- **Current Weather Data**: Hourly temperature, humidity, and other meteorological variables for supported cities.
- **Forecast Data**: Multi-day heat index and weather predictions for all tracked locations.
- **Historical Data**: Daily and hourly weather records for trend analysis and model validation.
- **City Geolocations**: City coordinates and metadata for mapping and risk calculations.

## 🗂️ Data Files in This Project

- `public/data/city_coords.csv` — City names, latitude, longitude (from OpenMeteo and Overpass APIs)
- `public/data/historical_weather_data.csv` — Historical weather data (OpenMeteo)
- `public/data/predicted_heat_index/YYYY-MM-DD_heat_index_prediction.csv` — Daily heat index predictions (OpenMeteo forecast + ML)
- `public/data/predicted_heat_index/YYYY-MM-DD_metrics_comparison_before.csv` — Model metrics before update
- `public/data/predicted_heat_index/YYYY-MM-DD_metrics_comparison_after.csv` — Model metrics after update

All weather and forecast data is fetched, processed, and validated using OpenMeteo API endpoints, then stored in these files for use by the app and backend scripts.

---

## 🤖 Machine Learning Process & Validation

INET-READY uses advanced machine learning to predict the heat index for each city, leveraging historical weather data and robust validation techniques. The process is implemented in `src/scripts/predict_heat_index.py` and related modules.

### **Algorithm**

- **Model:** XGBoost Regressor (`xgboost.XGBRegressor`)
- **Features:**
  - Day index (days since first record)
  - Temperature Max/Min
  - Apparent Temperature Max/Min
  - Wind Speed
  - Solar Radiation
  - Relative Humidity
- **Target:** Heat Index (°C)

### **Heat Index Equation**

The heat index is calculated using the standard formula:

```
HI = c1 + c2*T + c3*RH + c4*T*RH + c5*T^2 + c6*RH^2 + c7*T^2*RH + c8*T*RH^2 + c9*T^2*RH^2
```

Where:

- HI = Heat Index (°C)
- T = Air Temperature (°C)
- RH = Relative Humidity (%)
- c1..c9 = empirical constants (see [NOAA documentation](https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml))

### **Machine Learning Workflow**

1. **Data Loading & Preprocessing**
   - Load historical weather data from CSV
   - Ensure required columns and clean data
   - Feature engineering (e.g., day index)
2. **Train/Test Split**
   - Holdout set (10%) for final validation
   - Further split for cross-validation
3. **Model Training**
   - Train XGBoost regressor on training data
   - Use early stopping and parameter tuning
4. **Validation & Evaluation**
   - **K-Fold Cross-Validation**: Assess model stability
   - **Nested Cross-Validation**: Hyperparameter tuning
   - **Bootstrap Evaluation**: Estimate prediction uncertainty
   - **Permutation Test**: Assess feature importance
   - **Time-Based Validation**: Test on sequential data
   - **Holdout Validation**: Final unbiased test
5. **Metrics**
   - Mean Absolute Error (MAE)
   - Mean Squared Error (MSE)
   - R² Score (Coefficient of Determination)
   - Overall prediction quality rating (0-100, with qualitative label)
6. **Prediction**
   - Predict next 7 days' heat index for each city
   - Save results as CSV and JSON for app use

### **Validation Example (from code)**

- `perform_k_fold_cross_validation`
- `perform_nested_cv_with_param_tuning`
- `bootstrap_evaluation`
- `perform_permutation_test`
- `perform_time_based_validation`
- `validate_model`

All validation results and metrics are saved for transparency and model monitoring.

---

## 🗒️ Logs & Monitoring

All backend scripts and machine learning processes generate detailed logs for transparency and debugging. Logs are stored in the `src/scripts/logs/` directory and include:

- **Model Training Logs:**
  - Training/validation metrics for each run
  - Hyperparameter tuning results
  - Cross-validation and test set performance
- **Data Processing Logs:**
  - Data loading, cleaning, and feature engineering steps
  - Any missing or anomalous data detected
- **Forecast & Notification Logs:**
  - Timestamps and results of each forecast/notification job
  - API call status and error messages
- **Error Logs:**
  - Any exceptions or failures during script execution

Logs are automatically created and appended by the scripts. They are essential for:

- Auditing model performance over time
- Debugging data or prediction issues
- Ensuring reproducibility and traceability

> **Tip:** Check `src/scripts/logs/` after running any backend or ML script for the latest logs.

---

## 🚀 Deployment

- **Frontend:** Deploy on [Vercel](https://vercel.com/) or similar static hosting
- **Backend Scripts:** Deploy Python/Node.js scripts on Aptible or serverless platforms
- **Firebase Functions:** Deploy from `functions/` directory

---

## 🔄 Continuous Deployment & Secrets Management

- **GitLab Mirror for CD:**  
  This repository is automatically mirrored to a private GitLab instance for Continuous Deployment (CD). All changes pushed to the main branch are synced to GitLab using a GitHub Actions workflow ([`.github/workflows/gitlab_mirror.yml`](.github/workflows/gitlab_mirror.yml)), which triggers GitLab CI/CD pipelines for deployment.

- **Proton Drive .env Backup/Restore:**  
  The `.env` file is **encrypted and backed up to Proton Drive** on every push (see [`.git/hooks/pre-push`](.git/hooks/pre-push) and [`backup_env_to_proton.ps1`](backup_env_to_proton.ps1)).
  - To **restore** the latest `.env`, use [`recover_env_from_proton.ps1`](recover_env_from_proton.ps1), which downloads and decrypts the most recent backup from Proton Drive.
  - All encrypted backups are stored in the `.env_gpg/` folder during recovery.

> See [`backup_env_to_proton.ps1`](backup_env_to_proton.ps1) and [`recover_env_from_proton.ps1`](recover_env_from_proton.ps1) for details on the backup/restore process.

---

### Data Sources

- <a href="https://open-meteo.com/">Weather data by Open-Meteo.com</a>

---

## 📦 Dependencies

For a full list of Python libraries, see [`requirements.txt`](requirements.txt).
For a full list of Node.js modules, see [`package.json`](package.json) and [`package-lock.json`](package-lock.json).

---

## 🐍 Python Virtual Environment (venv) Setup

For instructions on setting up a Python virtual environment, see the official [Python venv documentation](https://docs.python.org/3/library/venv.html).

---

## 🧑‍💻 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

- **Author:** bpmiranda3099
- **Project:** [inet-ready-v2](https://github.com/bpmiranda3099/inet-ready-v2)
- **Support:** support@inet-ready.com

---

> _Your Heat Check for Safe and Informed Travel._
