@echo off
title Camunda 8 Workflow Automation - PBJ-2 Practical Assignment
cls
echo ===============================================================================
echo   PBJ-2 PRACTICAL ASSIGNMENT: CAMUNDA 8 WORKFLOW AUTOMATION
echo   Labs 1, 2, and 3: Models, Workers, Connectors, Tasklist and Operate
echo ===============================================================================
echo.
echo [1] Launch Web Simulation, Modeler & Monitoring Platform (Port 8080)
echo [2] Run Comprehensive Test Suite (15 Scenarios Across Labs 1, 2, 3)
echo [3] Run Spring Boot External Job Workers & Mock REST APIs (Port 8081)
echo [4] Recapture All Screenshots from Live Implementation
echo [5] Exit
echo.
set /p opt="Choose an option (1-5): "

if "%opt%"=="1" (
    echo Starting Web Server...
    start http://localhost:8080
    python web-simulation-platform\server.py
    pause
)
if "%opt%"=="2" (
    python test_all_scenarios.py
    pause
)
if "%opt%"=="3" (
    cd spring-boot-workers
    mvn spring-boot:run
    pause
)
if "%opt%"=="4" (
    python web-simulation-platform\capture_screenshots.py
    pause
)
if "%opt%"=="5" (
    exit
)
