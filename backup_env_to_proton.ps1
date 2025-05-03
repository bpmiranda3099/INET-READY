#!/usr/bin/env pwsh
# backup_env_to_proton.ps1
# Encrypt and upload .env to Proton Drive using rclone (for CI/CD or manual use)

# Ensure rclone and gpg are installed
if (-not (Get-Command rclone -ErrorAction SilentlyContinue)) {
    Write-Error 'rclone is not installed. Please install rclone from https://rclone.org/downloads/'
    exit 1
}
if (-not (Get-Command gpg -ErrorAction SilentlyContinue)) {
    Write-Error 'gpg is not installed. Please install GPG (GnuPG) for Windows.'
    exit 1
}

$envFile = ".env"
$encryptedFile = ".env.gpg"
$protonRemote = "protondrive:backups/inet-ready/"

if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found in project root."
    exit 1
}

# Encrypt the .env file (prompt for passphrase)
gpg --batch --yes --symmetric --cipher-algo AES256 $envFile

if (-not (Test-Path $encryptedFile)) {
    Write-Error "Failed to create encrypted .env.gpg file."
    exit 1
}

# Upload the encrypted file to Proton Drive
rclone copy $encryptedFile $protonRemote

if ($LASTEXITCODE -ne 0) {
    Write-Error "rclone upload failed."
    exit 1
}

# Remove the encrypted file after upload
Remove-Item $encryptedFile

Write-Host "Encrypted .env uploaded to Proton Drive successfully."
