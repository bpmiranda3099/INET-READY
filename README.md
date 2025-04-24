# INET-READY: Your Heat Check for Safe and Informed Travel

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Web-brightgreen)
![Status](https://img.shields.io/badge/status-Active-success)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Finet-ready-v2.vercel.app&up_message=live&down_message=offline&timeout=1000&label=Website&color=purple)](https://inet-ready-v2.vercel.app)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=bpmiranda3099.inet-ready-v2)

</div>

---

## 📝 Overview

INET-READY is a modern, privacy-focused platform for safe and informed travel. It combines real-time heat index forecasting, personalized health risk insights, and secure medical data management. The system leverages SvelteKit, Firebase, Python, and Node.js to deliver timely notifications and actionable travel health guidance.

---

## 🌐 APIs Used in INET-READY

### 1. Internal REST API Endpoints (Medical Data, hosted on Aptible)

- **Base URL:** `https://app-91403.on-aptible.com`
- **Endpoints:**
  - `POST /store-medical-data` — Create or update user medical data
  - `GET /get-medical-data` — Fetch authenticated user's medical data
  - `DELETE /delete-medical-data` — Delete user's medical data

> All endpoints require a valid Firebase ID token in the `Authorization: Bearer <token>` header.

---

### 2. External APIs

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
- **Endpoints/Services:**
  - Auth: Email/password, Google, Facebook
  - Firestore: User and weather data storage
  - Messaging: Push notifications (FCM)
  - Analytics: Usage tracking

#### f. Google Cloud APIs

- **Purpose:** Used by backend scripts for Firestore and service account access
- **Usage:** `google-api-python-client`, `google-cloud-firestore`

---

### 3. Other Notable Endpoints/Services

- **Firebase Cloud Functions**

  - `functions/sendTestNotification.js` — For sending test push notifications via FCM

- **Vercel Analytics**
  - `@vercel/speed-insights` — For frontend analytics

---

### 4. Service Workers

- **Path:** `/firebase-messaging-sw.js`
- **Purpose:** Handles push notifications and caching for offline support

---

### 5. Data Files (as API-like sources)

- `public/data/city_coords.csv` — City geolocations (from OpenMeteo/Overpass)
- `public/data/historical_weather_data.csv` — Historical weather (OpenMeteo)
- `public/data/predicted_heat_index/*.csv` — Daily predictions and metrics

---

## 🚀 Features

- **User Authentication**: Secure login via Firebase (email, Google, Facebook).
- **Personal Medical Profiles**: Store, update, and manage health data securely.
- **Heat Index & Weather Forecasts**: Real-time and predictive analytics for cities worldwide.
- **Personalized Health Alerts**: Push notifications based on user preferences, location, and medical risk.
- **Travel Health Cards**: Generate and view digital health summaries for travel.
- **Interactive Dashboard**: Visualize weather, health risks, and travel tips.
- **Chatbot Assistant**: AI-powered travel and health Q&A (Gemini integration).
- **Data Privacy Controls**: Full data deletion and privacy management.
- **Admin & Analytics**: Usage analytics and admin tools (Firebase, Vercel, Aptible).

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
   - Place your Firebase service account key in `config/firebase-credentials.json` for backend scripts.

4. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## 🧪 Usage

### Local Development

```sh
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) in your browser.

### Backend Scripts

- **Weather & Heat Index Forecasts:**
  - `src/scripts/heat_index_forecast_api.py` — Generate and serve forecasts (CLI/API)
  - `src/scripts/daily_weather_insights.py` — Generate insights, send notifications
  - `src/scripts/generate_weather_insights.js` — Node.js bridge for Gemini AI
- **Medical Data API:**
  - `src/lib/services/medical-api.js` — Communicates with Aptible-hosted Express/Postgres backend
- **Notification Service:**
  - `functions/sendTestNotification.js` — Firebase Cloud Function for push notification testing

### Data Files

- `public/data/city_coords.csv` — City geolocations
- `public/data/historical_weather_data.csv` — Historical weather
- `public/data/predicted_heat_index/` — Daily predictions and metrics

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

### Data Files in This Project

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

## 🧑‍💻 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

---

## 🚀 Deployment

- **Frontend:** Deploy on [Vercel](https://vercel.com/) or similar static hosting
- **Backend Scripts:** Deploy Python/Node.js scripts on Aptible or serverless platforms
- **Firebase Functions:** Deploy from `functions/` directory

---

## ⚙️ CI/CD & GitHub Workflows

INET-READY uses GitHub Actions for automated data collection, processing, and deployment:

### Automated Workflows

- **Hourly Weather Update**

  - Runs every hour to collect current weather data.
  - Updates Firebase with the latest conditions.
  - Script: `src/scripts/hourly_heat_index_api.py`

- **Daily Historical Weather Update**

  - Runs daily at midnight UTC.
  - Updates historical weather records and commits changes to the repository.
  - Script: `src/scripts/daily_historical_weather_data.py`

- **Daily Heat Index Forecast**
  - Runs daily at 4:00 AM UTC.
  - Generates future heat index predictions and updates Firebase and the repository.
  - Script: `src/scripts/heat_index_forecast_api.py`

### Configuration & Security

- Uses GitHub Secrets for secure credential management (e.g., `FIREBASE_SERVICE_ACCOUNT_JSON`).
- Credentials are decoded and used only during workflow runs.

### Manual Triggers

- All workflows can be triggered manually from the GitHub Actions tab.

### Data Sources

- Weather data is collected from reliable meteorological sources and processed for accuracy.

---

## 🐍 Python Libraries Used

The backend and data science scripts in INET-READY use the following Python libraries (see `requirements.txt` for full list):

- **numpy** — Numerical operations and array handling
- **pandas** — Data manipulation and analysis
- **xgboost** — Gradient boosting for machine learning predictions
- **scikit-learn (sklearn)** — Model selection, metrics, and validation
- **loguru** — Advanced logging
- **requests** — HTTP requests for API calls
- **requests-cache** — Caching for HTTP requests
- **openmeteo_requests** — Open-Meteo API client
- **overpy** — Overpass API for geospatial data (city coordinates)
- **matplotlib, seaborn** — Data visualization
- **numba, llvmlite** — High-performance numerical functions
- **joblib, threadpoolctl, concurrent.futures, multiprocessing** — Parallel and asynchronous execution
- **tqdm** — Progress bars for scripts
- **firebase-admin, google-cloud-firestore, google-api-python-client** — Firebase and Google Cloud integration
- **pythermalcomfort** — Thermal comfort calculations
- **csv, os, sys, time, tempfile, subprocess** — Standard library modules for file, process, and system management

These libraries are required for weather data collection, prediction, validation, notifications, and integration with external APIs. All are listed in `requirements.txt` for reproducible setup.

---

## 📦 Node.js Modules Used

The frontend, backend, and build system use the following Node.js modules (see `package.json` and `package-lock.json` for full details):

### Core Application & Frameworks

- **svelte**, **@sveltejs/kit**, **@sveltejs/adapter-vercel**, **@sveltejs/vite-plugin-svelte** — SvelteKit app framework and Vercel adapter
- **vite** — Fast frontend build tool

### UI & Utilities

- **@iconify/svelte** — Icon support for Svelte
- **marked** — Markdown parsing for chat and content
- **mapbox-gl** — Interactive maps
- **uuid** — Unique ID generation
- **dotenv** — Environment variable management

### Cloud & AI

- **firebase** — Firebase web SDK (auth, Firestore, messaging, etc.)
- **@google/generative-ai** — Gemini AI integration
- **@vercel/speed-insights** — Vercel analytics

### Linting & Formatting (Dev)

- **eslint**, **eslint-plugin-svelte**, **eslint-config-prettier**, **prettier**, **prettier-plugin-svelte**, **@eslint/js**, **@eslint/compat**, **globals** — Code linting and formatting

### Other Notable Modules

- **all dependencies and devDependencies** are locked and versioned in `package-lock.json` for reproducibility. For a full list, see those files or run:

```sh
npm ls --all
```

---

## 📦 Node.js Project & venv Structure

- All Node.js dependencies are managed via `npm install` and tracked in `package-lock.json`.
- Python virtual environments (`venv/`) are recommended for backend scripts (see above).
- Scripts for activating/deactivating venv are included in the `Scripts/` directory (Windows).
- For cross-platform venv activation, see the [Python Virtual Environment (venv) Setup](#-python-virtual-environment-venv-setup) section above.

---

## 🐍 Python Virtual Environment (venv) Setup

It is strongly recommended to use a Python virtual environment for isolation and reproducibility:

### Create and Activate venv (Windows)

```sh
python -m venv venv
.\venv\Scripts\activate
```

### Create and Activate venv (macOS/Linux)

```sh
python3 -m venv venv
source venv/bin/activate
```

### Install All Dependencies

```sh
pip install -r requirements.txt
```

### Deactivate venv

```sh
deactivate
```

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
