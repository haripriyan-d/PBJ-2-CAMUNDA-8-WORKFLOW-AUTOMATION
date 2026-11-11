@echo off
setlocal enabledelayedexpansion
title Camunda 8 Local Runner (c8run) - Labs 1, 2 and 3
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Ensure Java JDK is detected and configured
:: -----------------------------------------------------------------------------
if defined JAVA_HOME (
    set "JAVA_BIN=%JAVA_HOME%\bin\java.exe"
) else (
    if exist "C:\Program Files\Java\jdk-24\bin\java.exe" (
        set "JAVA_HOME=C:\Program Files\Java\jdk-24"
        set "PATH=%JAVA_HOME%\bin;%PATH%"
    )
)

:DETECT_EXE
set "C8_EXE="
if exist "%~dp0c8run.exe" (
    set "C8_EXE=%~dp0c8run.exe"
) else if exist "%~dp0c8run\c8run.exe" (
    set "C8_EXE=%~dp0c8run\c8run.exe"
) else (
    :: Look recursively in c8run subfolders if extracted into nested folder
    for /r "%~dp0c8run" %%F in (c8run.exe) do (
        if exist "%%F" set "C8_EXE=%%F"
    )
    if not defined C8_EXE (
        for %%X in (c8run.exe) do (
            if not "%%~$PATH:X"=="" set "C8_EXE=%%~$PATH:X"
        )
    )
)

:MENU
cls
echo ===============================================================================
echo            CAMUNDA 8 LOCAL RUNNER (C8RUN) - PBJ-2 PRACTICAL ASSIGNMENT
echo ===============================================================================
echo.
if defined C8_EXE (
    echo  [STATUS] c8run detected at: !C8_EXE!
) else (
    echo  [STATUS] c8run NOT yet detected. (Choose Option 5 to auto-download)
)
echo.
echo  =============================== MENU OPTIONS ================================
echo   [1] Start Camunda 8 Local Stack (Zeebe, Operate, Tasklist, Connectors)
echo   [2] Stop Camunda 8 Local Stack
echo   [3] View Status / Running Services
echo   [4] Open Camunda 8 Web Dashboards (Operate and Tasklist)
echo   [5] Auto-Download ^& Setup Camunda 8 Run (c8run) for Windows
echo   [6] Start Spring Boot External Workers (Port 8081)
echo   [7] Run Complete Automated Simulation Test Suite (15/15 Scenarios)
echo   [8] Exit
echo  =============================================================================
echo.
set /p opt="Enter your choice (1-8): "

if "%opt%"=="1" goto START_C8
if "%opt%"=="2" goto STOP_C8
if "%opt%"=="3" goto STATUS_C8
if "%opt%"=="4" goto OPEN_UI
if "%opt%"=="5" goto DOWNLOAD_C8
if "%opt%"=="6" goto START_WORKERS
if "%opt%"=="7" goto RUN_TESTS
if "%opt%"=="8" exit /b 0

echo Invalid choice. Please select 1 to 8.
timeout /t 2 >nul
goto MENU

:: -----------------------------------------------------------------------------
:: 1. Start Camunda 8 Local
:: -----------------------------------------------------------------------------
:START_C8
cls
echo ===============================================================================
echo                     STARTING CAMUNDA 8 LOCAL (C8RUN)
echo ===============================================================================
echo.
if not defined C8_EXE (
    echo c8run executable was not found. Launching auto-downloader...
    call :DOWNLOAD_C8
    goto DETECT_EXE
)

echo Starting Camunda 8 cluster in background...
echo (Zeebe Gateway: localhost:26500 ^| Web UI: http://localhost:8080)
echo.
"!C8_EXE!" start
echo.
echo ===============================================================================
echo Camunda 8 is starting up!
echo Default credentials:
echo   Username: demo
echo   Password: demo
echo.
echo Access URLs:
echo   Operate:  http://localhost:8080/operate
echo   Tasklist: http://localhost:8080/tasklist
echo ===============================================================================
echo.
pause
goto MENU

:: -----------------------------------------------------------------------------
:: 2. Stop Camunda 8 Local
:: -----------------------------------------------------------------------------
:STOP_C8
cls
echo ===============================================================================
echo                     STOPPING CAMUNDA 8 LOCAL (C8RUN)
echo ===============================================================================
echo.
if defined C8_EXE (
    "!C8_EXE!" stop
) else (
    echo c8run.exe not found.
)
echo.
pause
goto MENU

:: -----------------------------------------------------------------------------
:: 3. Status
:: -----------------------------------------------------------------------------
:STATUS_C8
cls
echo ===============================================================================
echo                      CAMUNDA 8 LOCAL STATUS
echo ===============================================================================
echo.
if defined C8_EXE (
    "!C8_EXE!" status
) else (
    echo c8run.exe not found.
)
echo.
echo Active ports check:
netstat -ano | findstr "26500 8080"
echo.
pause
goto MENU

:: -----------------------------------------------------------------------------
:: 4. Open Web UI
:: -----------------------------------------------------------------------------
:OPEN_UI
cls
echo Opening Camunda 8 Operate and Tasklist in your default browser...
start http://localhost:8080/operate
start http://localhost:8080/tasklist
timeout /t 2 >nul
goto MENU

:: -----------------------------------------------------------------------------
:: 5. Download & Setup c8run via dedicated script
:: -----------------------------------------------------------------------------
:DOWNLOAD_C8
cls
echo ===============================================================================
echo             AUTO-DOWNLOADING CAMUNDA 8 RUN (C8RUN) FOR WINDOWS
echo ===============================================================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_c8run.ps1"
echo.
:: Re-detect executable after download
if exist "%~dp0c8run.exe" (
    set "C8_EXE=%~dp0c8run.exe"
) else if exist "%~dp0c8run\c8run.exe" (
    set "C8_EXE=%~dp0c8run\c8run.exe"
) else (
    for /r "%~dp0c8run" %%F in (c8run.exe) do (
        if exist "%%F" set "C8_EXE=%%F"
    )
)
pause
goto MENU

:: -----------------------------------------------------------------------------
:: 6. Start Spring Boot Workers
:: -----------------------------------------------------------------------------
:START_WORKERS
cls
echo Starting Spring Boot External Job Workers ^& Mock REST APIs on port 8081...
cd "%~dp0spring-boot-workers"
call mvn clean spring-boot:run
cd "%~dp0"
pause
goto MENU

:: -----------------------------------------------------------------------------
:: 7. Run Test Suite
:: -----------------------------------------------------------------------------
:RUN_TESTS
cls
python "%~dp0test_all_scenarios.py"
pause
goto MENU
