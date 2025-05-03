# update_env_secret.ps1
# Updates the ENV_CONTENTS GitHub secret with the current .env file contents

$envFile = ".env"
$secretName = "ENV_CONTENTS"

if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    gh secret set $secretName --body "$envContent"
    Write-Host "✅ Updated GitHub secret '$secretName' with latest .env contents."
}
else {
    Write-Host "❌ .env file not found."
}
