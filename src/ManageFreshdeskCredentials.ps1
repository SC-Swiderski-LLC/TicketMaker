
param (
    [switch]$Add,
    [switch]$Retrieve,
    [switch]$Delete,
    [string]$Url,
    [string]$ApiKey
)

# Define credential names
$urlCredentialName = "TicketMaker_FreshdeskURL"
$apiKeyCredentialName = "TicketMaker_APIKey"

function Add-Credentials {
    param (
        [string]$Url,
        [string]$ApiKey
    )
    # Store Freshdesk URL
    cmdkey /generic:$urlCredentialName /user:"URL" /pass:$Url
    Write-Host "Freshdesk URL stored successfully."

    # Store Freshdesk API Key
    cmdkey /generic:$apiKeyCredentialName /user:"APIKey" /pass:$ApiKey
    Write-Host "Freshdesk API Key stored successfully."
}

function Retrieve-Credentials {
    # Retrieve Freshdesk URL
    $urlOutput = cmdkey /list | Select-String -Pattern $urlCredentialName
    if ($urlOutput) {
        $url = (cmdkey /list:$urlCredentialName | Select-String -Pattern "Password" | ForEach-Object {
            $_ -replace "Password\s*:\s*", ""
        }).Trim()
        Write-Host "Freshdesk URL: $url"
    } else {
        Write-Host "Freshdesk URL not found."
    }

    # Retrieve Freshdesk API Key
    $apiKeyOutput = cmdkey /list | Select-String -Pattern $apiKeyCredentialName
    if ($apiKeyOutput) {
        $apiKey = (cmdkey /list:$apiKeyCredentialName | Select-String -Pattern "Password" | ForEach-Object {
            $_ -replace "Password\s*:\s*", ""
        }).Trim()
        Write-Host "Freshdesk API Key: $apiKey"
    } else {
        Write-Host "Freshdesk API Key not found."
    }
}

function Delete-Credentials {
    # Delete Freshdesk URL
    cmdkey /delete:$urlCredentialName
    Write-Host "Freshdesk URL deleted."

    # Delete Freshdesk API Key
    cmdkey /delete:$apiKeyCredentialName
    Write-Host "Freshdesk API Key deleted."
}

# Main logic
if ($Add) {
    if (-not $Url -or -not $ApiKey) {
        Write-Host "Both -Url and -ApiKey parameters are required when using -Add."
    } else {
        Add-Credentials -Url $Url -ApiKey $ApiKey
    }
} elseif ($Retrieve) {
    Retrieve-Credentials
} elseif ($Delete) {
    Delete-Credentials
} else {
    Write-Host "No valid option provided. Use -Add, -Retrieve, or -Delete."
}
