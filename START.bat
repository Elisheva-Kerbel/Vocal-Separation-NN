@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Checking Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start...
    :wait_docker
    timeout /t 3 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 goto wait_docker
    echo Docker is ready!
)

echo.
echo Checking Docker Hub login...
docker pull hello-world >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================
    echo   Docker Hub requires login to pull images.
    echo   Create a free account at hub.docker.com
    echo   then run: docker login
    echo ============================================
    echo.
    echo Running docker login now...
    docker login
    if errorlevel 1 (
        echo Login failed. Please try again.
        pause
        exit /b 1
    )
)

echo.
echo Starting VocalSplit...
docker compose up -d --build
if errorlevel 1 (
    echo.
    echo =============================================
    echo   Something went wrong. Common fixes:
    echo   1. Run: docker login
    echo   2. Make sure .env file exists (copy from .env.example)
    echo   3. Restart Docker Desktop and try again
    echo =============================================
    echo.
    pause
    exit /b 1
)

echo.
echo VocalSplit is running!
echo App:     http://localhost:5173
echo Adminer: http://localhost:8080
echo MinIO:   http://localhost:9001
echo.
start http://localhost:5173
pause
