# PowerShell Script to Clean Up TicketMaker Installation

# Function to remove registry keys
function Remove-RegistryKey {
    param (
        [string]$Path
    )
    try {
        if (Test-Path "Registry::$Path") {
            Remove-Item -Path "Registry::$Path" -Recurse -Force
            Write-Host "Removed registry key: $Path"
        } else {
            Write-Host "Registry key not found: $Path"
        }
    } catch {
        Write-Warning "Failed to remove registry key: $Path. Error: $_"
    }
}

# 1. Registry Cleanup
Write-Host "Starting registry cleanup for TicketMaker..." -ForegroundColor Cyan

$RegistryPaths = @(
    "HKLM:\SOFTWARE\TicketMaker",
    "HKCU:\SOFTWARE\TicketMaker",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TicketMaker",
    "HKCR:\Installer\Products" # Note: HKCR paths may require deeper inspection
)

foreach ($Path in $RegistryPaths) {
    Remove-RegistryKey -Path $Path
}

# Special case: Searching for residual keys under HKCR:\Installer\Products
Write-Host "Searching for residual TicketMaker registry entries under HKCR:\Installer\Products..."
Get-ChildItem -Path "HKCR:\Installer\Products" | ForEach-Object {
    $KeyPath = $_.PSPath
    $KeyContent = Get-ItemProperty -Path $KeyPath
    if ($KeyContent.PSObject.Properties.Name -contains "ProductName" -and $KeyContent.ProductName -like "*TicketMaker*") {
        Write-Host "Found and removing: $KeyPath"
        Remove-RegistryKey -Path $KeyPath
    }
}

Write-Host "Registry cleanup completed." -ForegroundColor Green

# 2. File System Cleanup
Write-Host "Starting file system cleanup for TicketMaker..." -ForegroundColor Cyan

$InstallPath = "C:\Program Files\TicketMaker"
if (Test-Path -Path $InstallPath) {
    try {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Host "Removed TicketMaker folder: $InstallPath"
    } catch {
        Write-Warning "Failed to remove folder: $InstallPath. Error: $_"
    }
} else {
    Write-Host "TicketMaker folder not found: $InstallPath"
}

Write-Host "File system cleanup completed." -ForegroundColor Green

# 3. Final Message
Write-Host "TicketMaker cleanup process completed. Please verify no residual entries remain." -ForegroundColor Cyan
