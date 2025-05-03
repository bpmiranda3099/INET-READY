## GitHub Workflows

INET-READY uses GitHub Actions for automated data collection, processing, notifications, repository mirroring, and secure backup of sensitive files:

### Automated Workflows

- **Hourly Weather Update**
  - Runs every hour to collect current weather data and update Firebase.
  - Script: `src/scripts/hourly_heat_index_api.py`
- **Daily Historical Weather Update**
  - Runs daily at midnight UTC to update historical weather records and commit changes.
  - Script: `src/scripts/daily_historical_weather_data.py`
- **Daily Heat Index Forecast**
  - Runs daily at 4:00 AM UTC to generate future heat index predictions and update Firebase.
  - Script: `src/scripts/heat_index_forecast_api.py`
- **Daily Weather Insights**
  - Runs daily at 6:00 AM UTC to generate weather insights and send notifications.
  - Script: `src/scripts/daily_weather_insights.py`
- **Heat Index Change Notifications**

  - Runs after the hourly weather update to send notifications if significant heat index changes are detected.
  - Script: `src/scripts/heat_index_alert_service.py`

- **GitLab Mirror**

  - On every push to GitHub, runs CI steps and then mirrors all changes (branches, tags, deletions) to a linked GitLab repository.

### Manual Triggers

- All workflows can be triggered manually from the GitHub Actions tab.
