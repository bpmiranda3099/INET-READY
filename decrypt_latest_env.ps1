# decrypt_latest_env.ps1
# Finds the latest .env_*.gpg file in .env_gpg and decrypts it to .env

$gpgDir = ".env_gpg"
if (-not (Test-Path $gpgDir)) {
    Write-Error ".env_gpg directory does not exist. Run the download script first."
    exit 1
}

# Find the latest .env_*.gpg file by LastWriteTime
$latestGpg = Get-ChildItem $gpgDir -Filter ".env_*.gpg" | Sort-Object LastWriteTime | Select-Object -Last 1

if (-not $latestGpg) {
    Write-Error "No .env_*.gpg files found in $gpgDir."
    exit 1
}

Write-Host "Decrypting $($latestGpg.Name) to .env ..."
gpg --yes --output .env --decrypt $latestGpg.FullName
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully decrypted to .env"
    if (Test-Path .env) {
        Write-Host "First lines of decrypted .env:"
        Get-Content .env -TotalCount 5 | ForEach-Object { Write-Host $_ }
    }
    exit 0
}
else {
    Write-Error "GPG decryption failed. Check your GPG key and passphrase."
    exit 1
}
