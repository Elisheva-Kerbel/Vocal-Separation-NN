@echo off
cd /d "%~dp0"
docker compose up -d
echo.
echo VocalSplit is running!
echo http://localhost:5173
echo.
start http://localhost:5173
pause
