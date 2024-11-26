param (
    [string]$FreshdeskURL,
    [string]$FreshdeskApiKey
)

# Ensure the required .NET assembly is loaded
Add-Type -AssemblyName "System.Security"

# Paths for encrypted files
$EncryptedDataFolder = "C:\ProgramData\TicketMaker"
$EncryptedUrlFile = Join-Path $EncryptedDataFolder "FreshdeskURL.dat"
$EncryptedApiKeyFile = Join-Path $EncryptedDataFolder "FreshdeskApiKey.dat"
$LogFile = Join-Path $EncryptedDataFolder "EncryptionDebug.log"

# Ensure the data folder exists
if (!(Test-Path $EncryptedDataFolder)) {
    New-Item -ItemType Directory -Path $EncryptedDataFolder -Force | Out-Null
}

# Log inputs for debugging
Add-Content -Path $LogFile -Value "$(Get-Date) - Received FreshdeskURL: $FreshdeskURL"
Add-Content -Path $LogFile -Value "$(Get-Date) - Received FreshdeskApiKey: $FreshdeskApiKey"

# Encrypt and save
try {
    $EncryptedUrl = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
        [System.Text.Encoding]::UTF8.GetBytes($FreshdeskURL), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))
    Set-Content -Path $EncryptedUrlFile -Value $EncryptedUrl

    $EncryptedApiKey = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
        [System.Text.Encoding]::UTF8.GetBytes($FreshdeskApiKey), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))
    Set-Content -Path $EncryptedApiKeyFile -Value $EncryptedApiKey

    Add-Content -Path $LogFile -Value "$(Get-Date) - Successfully encrypted and saved credentials."
} catch {
    Add-Content -Path $LogFile -Value "$(Get-Date) - ERROR: $($_.Exception.Message)"
    Exit 1
}
