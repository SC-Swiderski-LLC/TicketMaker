@echo off
setlocal

:: Define Variables
set ScriptDir=%~dp0
set LogDir=%LOCALAPPDATA%\TicketMaker\Logs
set InstallLog=%LogDir%\dependencies_install.log
set PythonPath=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

:: Ensure the log directory exists
if not exist "%LogDir%" (
    mkdir "%LogDir%"
)

:: Start Logging
echo Starting Python dependency installation in user context... > "%InstallLog%"
echo Starting Python dependency installation in user context...

:: Verify Python Installation
if not exist "%PythonPath%" (
    echo Python executable not found at: "%PythonPath%" >> "%InstallLog%"
    echo Python executable not found at: "%PythonPath%"
    exit /b 1
)

echo Using Python executable: "%PythonPath%" >> "%InstallLog%"
echo Using Python executable: "%PythonPath%"

:: Upgrade pip
echo Upgrading pip... >> "%InstallLog%"
"%PythonPath%" -m ensurepip --upgrade >> "%InstallLog%" 2>&1 || (
    echo Failed to upgrade ensurepip. Check the log for details. >> "%InstallLog%"
    exit /b 1
)

"%PythonPath%" -m pip install --upgrade pip --user >> "%InstallLog%" 2>&1 || (
    echo Failed to upgrade pip. Check the log for details. >> "%InstallLog%"
    exit /b 1
)

echo pip upgraded successfully. >> "%InstallLog%"
echo pip upgraded successfully.

:: Install Dependencies from requirements.txt
if not exist "%ScriptDir%requirements.txt" (
    echo requirements.txt not found in %ScriptDir%. >> "%InstallLog%"
    exit /b 1
)

echo Installing dependencies from requirements.txt in user context... >> "%InstallLog%"
"%PythonPath%" -m pip install --user -r "%ScriptDir%requirements.txt" >> "%InstallLog%" 2>&1 || (
    echo Failed to install dependencies. Check the log for details. >> "%InstallLog%"
    exit /b 1
)

echo Dependencies installed successfully. >> "%InstallLog%"

:: Completion Message
echo Python dependencies and post-installation steps completed successfully. >> "%InstallLog%"
exit /b 0
