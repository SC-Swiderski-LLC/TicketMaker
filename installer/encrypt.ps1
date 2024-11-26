param (
    [string]$FreshdeskURL,
    [string]$FreshdeskApiKey,
    [switch]$EnableLogging
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

# Function to log messages if logging is enabled
function Write-Log {
    param (
        [string]$Message
    )
    if ($EnableLogging) {
        Add-Content -Path $LogFile -Value "$(Get-Date) - $Message"
    }
}

# Log inputs (only if logging is enabled)
Write-Log "Received FreshdeskURL: $FreshdeskURL"
Write-Log "Received FreshdeskApiKey: $FreshdeskApiKey"

# Encrypt and save
try {
    $EncryptedUrl = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
        [System.Text.Encoding]::UTF8.GetBytes($FreshdeskURL), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))
    Set-Content -Path $EncryptedUrlFile -Value $EncryptedUrl

    $EncryptedApiKey = [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Protect(
        [System.Text.Encoding]::UTF8.GetBytes($FreshdeskApiKey), $null, [System.Security.Cryptography.DataProtectionScope]::LocalMachine))
    Set-Content -Path $EncryptedApiKeyFile -Value $EncryptedApiKey

    Write-Log "Successfully encrypted and saved credentials."
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Exit 1
}
