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

  - Sensitive files like `.env` are excluded from git but are securely backed up to Proton Drive using [rclone](https://rclone.org/protondrive/) and GPG encryption.
  - The `backup_env_to_proton.ps1` script in the project root encrypts `.env` with AES256 (via GPG) and uploads it to Proton Drive using rclone. You can run this script manually on Windows/PowerShell, or integrate it into your workflow.
  - Before using, ensure your Proton Drive remote is configured in your `rclone.conf` (see the script for details). The script will prompt for a GPG passphrase if not provided.
  - For CI/CD and automated backups, the GitHub Actions workflow `.github/workflows/backup_env_to_proton.yml` automates this process on every push (and can be triggered manually).

    - The workflow restores `.env` from the `ENV_CONTENTS` secret, encrypts it with the passphrase from `GPG_PASSPHRASE`, and uploads it to Proton Drive using the `RCLONE_CONFIG` secret for authentication.

    - To keep the backup up-to-date, use the `update_env_secret.ps1` script to update the `ENV_CONTENTS` secret with your latest `.env` before every push (requires GitHub CLI and permissions). You can run this script manually, or set it up as a pre-push git hook by creating a `.git/hooks/pre-push` file that calls this script.
    - **Example pre-push hook for Windows/PowerShell:**
      ```sh
      # .git/hooks/pre-push (make sure this file is executable and uses the correct shell)
      powershell.exe -ExecutionPolicy Bypass -File "$PWD/update_env_secret.ps1"
      ```
    - **Required repository secrets:**
      - `ENV_CONTENTS`: The contents of your `.env` file (automatically updated by the script or hook)
      - `RCLONE_CONFIG`: Your rclone configuration for Proton Drive
      - `GPG_PASSPHRASE`: The passphrase for GPG encryption

### Manual Triggers

- All workflows can be triggered manually from the GitHub Actions tab.
