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
        if ($null -eq $latestTime -or $time -gt $latestTime) {
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

$gpgFile = Join-Path $gpgDir $latestFile
if (-not (Test-Path $gpgFile)) {
    Write-Error "Failed to download $latestFile."
    exit 1
}

# Show file size for diagnostics
$gpgInfo = Get-Item $gpgFile
Write-Host "Downloaded file size: $($gpgInfo.Length) bytes"
if ($gpgInfo.Length -eq 0) {
    Write-Error "Downloaded GPG file is empty. Aborting."
    exit 1
}

# Automatically decrypt the latest file after download
$latestGpg = Get-ChildItem $gpgDir -Filter ".env_*.gpg" | Sort-Object LastWriteTime | Select-Object -Last 1
if (-not $latestGpg) {
    Write-Error "No .env_*.gpg files found in $gpgDir after download."
    exit 1
}
Write-Host "Decrypting $($latestGpg.Name) to .env ..."
gpg --yes --output .env --decrypt $latestGpg.FullName
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully decrypted to .env"
    exit 0
}
else {
    Write-Error "GPG decryption failed. Check your GPG key and passphrase."
    exit 1
}
