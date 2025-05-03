# update_env_secret.ps1
# Updates the ENV_CONTENTS GitHub secret with the current .env file contents

$envFile = ".env"
$secretName = "ENV_CONTENTS"
$logFile = "update_env_secret.log"

function Write-LogMessage {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $entry
}

Write-LogMessage "Starting update_env_secret.ps1 script."

if (Test-Path $envFile) {
    Write-LogMessage ".env file found. Reading contents."
    $envContent = Get-Content $envFile -Raw
    $envHash = (Get-FileHash $envFile -Algorithm SHA256).Hash
    Write-LogMessage "Current .env SHA256: $envHash"
    try {
        # Dynamically determine the current repo in 'owner/name' format
        try {
            $repoInfo = gh repo view --json name, owner, url | ConvertFrom-Json
            $repo = "{0}/{1}" -f $repoInfo.owner.login, $repoInfo.name
            $repoUrl = $repoInfo.url
        }
        catch {
            # Fallback: use git remote
            $remoteUrl = git config --get remote.origin.url
            if ($remoteUrl -match "github.com[:/](.+/.+?)(\\.git)?$") {
                $repo = $Matches[1]
                $repoUrl = $remoteUrl
            }
            else {
                throw "Could not determine GitHub repository name."
            }
        }
        $ghAuth = gh auth status 2>&1
        Write-LogMessage "gh auth status: $ghAuth"
        Write-LogMessage "repo: $repo"
        Write-LogMessage "repoUrl: $repoUrl"
        $ghOutput = gh secret set $secretName --repo $repo --body "$envContent" 2>&1
        Write-Host $ghOutput
        Write-LogMessage "gh output: $ghOutput"
        Write-Host "✅ Updated GitHub secret '$secretName' with latest .env contents."
        Write-LogMessage "✅ Updated GitHub secret '$secretName' with latest .env contents. SHA256: $envHash"
    }
    catch {
        Write-Host "❌ Failed to update GitHub secret. $_"
        Write-LogMessage "❌ Failed to update GitHub secret. $_"
    }
}
else {
    Write-Host "❌ .env file not found."
    Write-LogMessage "❌ .env file not found."
}