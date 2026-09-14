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
echo Starting VocalSplit...
docker compose up -d --build
echo.
echo VocalSplit is running!
echo App:     http://localhost:5173
echo Adminer: http://localhost:8080
echo MinIO:   http://localhost:9001
echo.
start http://localhost:5173
pause
