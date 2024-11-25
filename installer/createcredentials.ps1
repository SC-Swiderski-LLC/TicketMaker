# Path to save the encrypted files
$EncryptedDataFolder = "C:\ProgramData\TicketMaker"
$EncryptedUrlFile = Join-Path $EncryptedDataFolder "FreshdeskURL.dat"
$EncryptedApiKeyFile = Join-Path $EncryptedDataFolder "FreshdeskApiKey.dat"

# Ensure the folder exists
if (!(Test-Path $EncryptedDataFolder)) {
    New-Item -ItemType Directory -Path $EncryptedDataFolder -Force | Out-Null
}

# Input values - Passed by the installer
$FreshdeskURL = "[FRESHDESK_URL]"  # Replace with actual parameter from installer
$FreshdeskApiKey = "[FRESHDESK_APIKEY]"  # Replace with actual parameter from installer

# Validate inputs
if (-not $FreshdeskURL -or -not $FreshdeskApiKey) {
    Write-Error "Error: Both Freshdesk URL and API Key are required."
    Exit 1
}

# Encrypt data using DPAPI
$EncryptedUrl = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
    [System.Text.Encoding]::UTF8.GetBytes($FreshdeskURL), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))

$EncryptedApiKey = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
    [System.Text.Encoding]::UTF8.GetBytes($FreshdeskApiKey), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))

# Write encrypted data to files
Set-Content -Path $EncryptedUrlFile -Value $EncryptedUrl
Set-Content -Path $EncryptedApiKeyFile -Value $EncryptedApiKey

Write-Host "Encrypted credentials saved successfully."
