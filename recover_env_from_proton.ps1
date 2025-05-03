# recover_env_from_proton.ps1
# Downloads the latest .env_*.gpg backup from Proton Drive and decrypts it to .env
# Requires: rclone, gpg, and your GPG private key

$gpgDir = ".env_gpg"
if (-not (Test-Path $gpgDir)) {
    New-Item -ItemType Directory -Path $gpgDir | Out-Null
}


# List all .env_*.gpg files in the remote backup folder with timestamps
$remoteFilesRaw = rclone lsf protondrive:backups/inet-ready/ --format=pt --files-only | Where-Object { $_ -like ".env_*.gpg*" }

if (-not $remoteFilesRaw) {
    Write-Error "No .env_*.gpg files found in Proton Drive backup."
    exit 1
}

# Parse filename and timestamp, then select the latest by timestamp
$latestFile = $null
$latestTime = $null
foreach ($line in $remoteFilesRaw) {
    if ($line -match "^(\.env_[^;]+\.gpg);([0-9\-: ]+)$") {
        $file = $matches[1]
        $time = Get-Date $matches[2]
        if ($latestTime -eq $null -or $time -gt $latestTime) {
            $latestTime = $time
            $latestFile = $file
        }
    }
}

if (-not $latestFile) {
    Write-Error "Could not determine the latest .env_*.gpg file."
    exit 1
}

Write-Host "Downloading $latestFile from Proton Drive..."
rclone copy "protondrive:backups/inet-ready/$latestFile" $gpgDir --progress

# Decrypt the file to .env in the repo root
$gpgFile = Join-Path $gpgDir $latestFile
if (-not (Test-Path $gpgFile)) {
    Write-Error "Failed to download $latestFile."
    exit 1
}

Write-Host "Decrypting $gpgFile to .env ..."
gpg --output .env --decrypt $gpgFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully decrypted to .env"
}
else {
    Write-Error "GPG decryption failed. Check your GPG key and passphrase."
    exit 1
}
