param (
    [string]$TempDirPath = $env:TEMP
)

# Resolve paths and variables
$PythonInstaller = Join-Path $TempDirPath "python-3.12.7-amd64.exe"
$InstallLog = Join-Path $TempDirPath "python_install.log"

# Start logging
"Starting Python 3.12.7 installation process..." | Out-File -FilePath $InstallLog -Encoding utf8

# Verify installer file exists
if (-Not (Test-Path $PythonInstaller)) {
    "Python installer not found at: $PythonInstaller" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

# Run Python installer silently for all users
try {
    "Running Python installer with arguments for system-wide installation..." | Out-File -FilePath $InstallLog -Append
    Start-Process -FilePath $PythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait -NoNewWindow
    "Python installation completed." | Out-File -FilePath $InstallLog -Append
} catch {
    "Python installation failed with error: $_" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

# Verify Python installation explicitly
$PythonPath = "C:\Program Files\Python312\python.exe"
if (-Not (Test-Path $PythonPath)) {
    "Python installation verification failed. Expected path not found: $PythonPath" | Out-File -FilePath $InstallLog -Append
    Exit 1
} else {
    "Python installed successfully at: $PythonPath" | Out-File -FilePath $InstallLog -Append
}

# Ensure pip is available and up to date
try {
    "Updating pip..." | Out-File -FilePath $InstallLog -Append
    & $PythonPath -m ensurepip --upgrade | Out-File -FilePath $InstallLog -Append
    & $PythonPath -m pip install --upgrade pip | Out-File -FilePath $InstallLog -Append
    "pip updated successfully." | Out-File -FilePath $InstallLog -Append
} catch {
    "Failed to update pip with error: $_" | Out-File -FilePath $InstallLog -Append
    Exit 1
}

"Python and pip setup completed successfully." | Out-File -FilePath $InstallLog -Append
Exit 0
