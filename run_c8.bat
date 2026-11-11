@echo off
setlocal enabledelayedexpansion
title Camunda 8 Local Runner (c8run)
cd /d "%~dp0"

:: Set Java JDK if not already in environment
if not defined JAVA_HOME (
    if exist "C:\Program Files\Java\jdk-24\bin\java.exe" (
        set "JAVA_HOME=C:\Program Files\Java\jdk-24"
        set "PATH=!JAVA_HOME!\bin;!PATH!"
    )
)

:: Locate c8run.exe
set "C8_EXE="
if exist "%~dp0c8run.exe" (
    set "C8_EXE=%~dp0c8run.exe"
) else if exist "%~dp0c8run\c8run.exe" (
    set "C8_EXE=%~dp0c8run\c8run.exe"
) else (
    for /r "%~dp0c8run" %%F in (c8run.exe) do (
        if exist "%%F" set "C8_EXE=%%F"
    )
    if not defined C8_EXE (
        for %%X in (c8run.exe) do (
            if not "%%~$PATH:X"=="" set "C8_EXE=%%~$PATH:X"
        )
    )
)

if not defined C8_EXE (
    echo [ERROR] c8run.exe was not found in:
    echo   - %~dp0
    echo   - %~dp0c8run\
    echo   - System PATH
    echo.
    echo Please ensure c8run.exe or the extracted 'c8run' folder is placed in this directory.
    echo Download link: https://github.com/camunda/camunda/releases/download/8.10.9/camunda8-run-8.10.9-windows-x86_64.zip
    echo.
    pause
    exit /b 1
)

:: If an argument was passed (e.g. stop, status), execute it directly
if not "%~1"=="" (
    "!C8_EXE!" %*
    exit /b %ERRORLEVEL%
)

:: Default action: Start Camunda 8 local stack
echo ===============================================================================
echo                   STARTING CAMUNDA 8 LOCAL STACK (C8RUN)
echo ===============================================================================
echo Using c8run at: "!C8_EXE!"
echo.
echo Starting Zeebe, Operate, Tasklist, and Connectors...
echo.

"!C8_EXE!" start

echo.
echo ===============================================================================
echo Camunda 8 cluster is running!
echo.
echo Default Credentials:
echo   Username: demo
echo   Password: demo
echo.
echo Web Dashboards:
echo   Operate:  http://localhost:8080/operate
echo   Tasklist: http://localhost:8080/tasklist
echo   Zeebe:    localhost:26500
echo ===============================================================================
echo.

:: Open Web Dashboards in default browser
timeout /t 3 >nul
start http://localhost:8080/operate
start http://localhost:8080/tasklist

echo Press any key to stop Camunda 8...
pause >nul

echo Stopping Camunda 8...
"!C8_EXE!" stop
echo Camunda 8 stopped.
pause
