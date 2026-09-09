@echo off
chcp 65001 >nul
title Explorer Admin

set "DIR=%~dp0"
set "PORT=5010"

echo ================================================
echo           Explorer Admin Console
echo ================================================
echo.

REM ---- Find Python ----
set "PY="

REM WorkBuddy managed venv (has flask + requests)
if exist "C:\Users\xiaox\.workbuddy\binaries\python\envs\default\Scripts\python.exe" (
    set "PY=C:\Users\xiaox\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
)

REM Portable python next to script
if "%PY%"=="" if exist "%DIR%.python\python.exe" set "PY=%DIR%.python\python.exe"

REM Known install paths
if "%PY%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if "%PY%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if "%PY%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"

REM Try PATH
if "%PY%"=="" for /f "tokens=*" %%i in ('where python 2^>nul') do set "PY=%%i"

if "%PY%"=="" (
    echo [ERROR] Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Using Python: %PY%
echo.

if not exist "%DIR%explorer_admin.py" (
    echo [ERROR] explorer_admin.py not found!
    pause
    exit /b 1
)

REM ---- Ensure deps (flask + requests) ----
"%PY%" -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies: flask, requests ...
    "%PY%" -m pip install -q flask requests pycryptodome
    echo Done.
    echo.
)

REM ---- Stop old service on port ----
echo Stopping old service if running...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
    echo Stopped process %%a
)

setlocal enabledelayedexpansion

REM ---- Wait for port release (max 10s) ----
echo Waiting for port %PORT% to be released...
set "WAIT_CNT=0"
:wait_port
timeout /t 1 >nul
netstat -ano 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    set /a WAIT_CNT+=1
    if !WAIT_CNT! leq 10 goto wait_port
    echo [ERROR] Port %PORT% still occupied after 10s.
    pause
    exit /b 1
)
echo Port %PORT% is free.
echo.

REM ---- Clean __pycache__ ----
echo Cleaning __pycache__...
if exist "%DIR%__pycache__" rmdir /s /q "%DIR%__pycache__"
echo Done.
echo.

REM ---- Start service (no console window) ----
echo Starting service...
set "PYW=%PY:python.exe=pythonw.exe%"
if exist "%PYW%" (
    start "" "%PYW%" "%DIR%explorer_admin.py"
) else (
    start "" "%PY%" "%DIR%explorer_admin.py"
)

REM ---- Verify and open browser ----
timeout /t 3 >nul
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /c "pythonw" >nul
if errorlevel 1 (
    tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /c "python.exe" >nul
)
echo.
echo Opening browser...
start http://127.0.0.1:%PORT%
echo Done!
endlocal
pause
