# update_env_secret.ps1
# Updates the ENV_CONTENTS GitHub secret with the current .env file contents

$envFile = ".env"
$secretName = "ENV_CONTENTS"
$logFile = "update_env_secret.log"

function Log-Message {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $entry
}

Log-Message "Starting update_env_secret.ps1 script."

if (Test-Path $envFile) {
    Log-Message ".env file found. Reading contents."
    $envContent = Get-Content $envFile -Raw
    $envHash = [System.BitConverter]::ToString((Get-FileHash $envFile -Algorithm SHA256).Hash).Replace("-", "")
    Log-Message "Current .env SHA256: $envHash"
    try {
        gh secret set $secretName --body "$envContent"
        Write-Host "✅ Updated GitHub secret '$secretName' with latest .env contents."
        Log-Message "✅ Updated GitHub secret '$secretName' with latest .env contents. SHA256: $envHash"
    }
    catch {
        Write-Host "❌ Failed to update GitHub secret. $_"
        Log-Message "❌ Failed to update GitHub secret. $_"
    }
}
else {
    Write-Host "❌ .env file not found."
    Log-Message "❌ .env file not found."
}
