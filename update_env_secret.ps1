#!/bin/sh
# Git pre-push hook to update ENV_CONTENTS secret with latest .env (cross-platform)

# Get the repo root (two levels up from hooks dir)
REPO_ROOT="$(cd \"$(dirname \"$0\")/../..\" && pwd)"

# Call the PowerShell script using Windows PowerShell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$REPO_ROOT/update_env_secret.ps1"

exit $?