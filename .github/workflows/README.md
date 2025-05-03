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

- **.env Backup to Proton Drive**
  - On every push (and manually), encrypts the `.env` file and uploads it to Proton Drive using rclone and GPG.
  - Workflow: `.github/workflows/backup_env_to_proton.yml`
  - Script: `backup_env_to_proton.ps1`

### Configuration & Security

- Uses GitHub Secrets for secure credential management (e.g., `FIREBASE_SERVICE_ACCOUNT_JSON`, `GITLAB_URL`, `GITLAB_USERNAME`, `GITLAB_TOKEN`, `RCLONE_CONFIG`, `GPG_PASSPHRASE`).
- Credentials are decoded and used only during workflow runs.
-
- #### Backing up .env to Proton Drive
  - Sensitive files like `.env` are excluded from git but can be securely backed up to Proton Drive using [rclone](https://rclone.org/protondrive/).
  - Use the provided `backup_env_to_proton.ps1` script to encrypt and upload `.env` to Proton Drive. This can be run manually or integrated into CI/CD.
  - Proton Drive remote must be configured in rclone (see project root script for details).
  - The GitHub Actions workflow `.github/workflows/backup_env_to_proton.yml` automates this process and runs on every push.
    - Requires repository secrets `RCLONE_CONFIG` (your rclone.conf contents) and `GPG_PASSPHRASE` (your encryption passphrase).

### Manual Triggers

- All workflows can be triggered manually from the GitHub Actions tab.
