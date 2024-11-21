$regPath = "HKLM:\Software\TicketMaker"

# Detect installer mode via UILevel
$uiLevel = $env:UILevel

if ($uiLevel -eq 2) {
    # Silent install: use passed parameters
    $msiURL = $env:URL
    $msiAPIKey = $env:API_KEY

    # if registry path exists, create it if not
    if (-not (Test-Path -Path $regPath)) {
        New-Item -Path $regPath -Force
    }

    # if passed via silent install
    if ($msiURL) {
        Set-ItemProperty -Path $regPath -Name "URL" -Value $msiURL
    }
    if ($msiAPIKey) {
        Set-ItemProperty -Path $regPath -Name "API_KEY" -Value $msiAPIKey
    }
} else {
    Write-Host "Interactive install detected. Skipping PowerShell registry handling."
}
