## GitHub Workflows

### Hourly Weather Update

- Runs every hour to collect current weather data
- Updates Firebase with latest conditions
- Script: `src/scripts/hourly_heat_index_api.py`

### Daily Historical Weather Update

- Runs once per day (at midnight UTC)
- Updates historical weather records
- Commits changes to the repository
- Script: `src/scripts/daily_historical_weather_data.py`

### Daily Heat Index Forecast

- Runs daily at 4:00 AM UTC
- Generates predictions for future heat index values
- Updates Firebase and repository with forecast data
- Script: `src/scripts/heat_index_forecast_api.py`

## Configuration

The system relies on GitHub Secrets for secure credential management:

- `FIREBASE_SERVICE_ACCOUNT_JSON`: Base64-encoded Firebase service account JSON

## Usage

The system runs automatically via GitHub Actions. To manually trigger any workflow:

1. Navigate to the Actions tab in your GitHub repository
2. Select the desired workflow
3. Click "Run workflow" button

## Data Sources

Weather data is collected from reliable meteorological sources and processed to ensure consistency and accuracy.
