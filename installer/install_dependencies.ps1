param (
    [string]$TempDirPath = $env:TEMP
)

# Resolve paths and variables
$PythonPath = "C:\Program Files\Python312\python.exe"
$InstallLog = Join-Path $TempDirPath "dependencies_install.log"

# Start logging
"Starting Python dependency installation..." | Out-File -FilePath $InstallLog -Encoding utf8

# Verify Python installation
if (-Not (Test-Path $PythonPath)) {
    "Python executable not found at: $PythonPath" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

# Upgrade pip
try {
    "Upgrading pip..." | Out-File -FilePath $InstallLog -Append
    & $PythonPath -m ensurepip --upgrade | Out-File -FilePath $InstallLog -Append
    & $PythonPath -m pip install --upgrade pip | Out-File -FilePath $InstallLog -Append
    "pip upgraded successfully." | Out-File -FilePath $InstallLog -Append
} catch {
    "Failed to upgrade pip with error: $_" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

# Install dependencies from requirements.txt
try {
    "Installing dependencies from requirements.txt..." | Out-File -FilePath $InstallLog -Append
    & $PythonPath -m pip install -r "$TempDirPath\requirements.txt" | Out-File -FilePath $InstallLog -Append
} catch {
    "Failed to install dependencies. Error: $_" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

# Run pywin32 post-installation script
try {
    "Running pywin32 post-installation script..." | Out-File -FilePath $InstallLog -Append
    & $PythonPath "$($PythonPath -replace 'python.exe', 'Scripts\pywin32_postinstall.py')" -install | Out-File -FilePath $InstallLog -Append
    "pywin32 post-installation completed successfully." | Out-File -FilePath $InstallLog -Append
} catch {
    "pywin32 post-installation failed. Error: $_" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

"Python dependencies and post-installation steps completed successfully." | Out-File -FilePath $InstallLog -Append
Exit 0
