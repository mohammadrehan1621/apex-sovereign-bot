@echo off
title Apex Sovereign Bot - Standalone 24/7 Runner
echo ===================================================================
echo     APEX SOVEREIGN AI BOT - PERMANENT STATIC URL RUNNER
echo ===================================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching Apex Sovereign Trading Engine & Web Server...
start "Apex-Server" /min cmd /c "python -m src.web.server"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Permanent Ngrok Static Tunnel...
start "Apex-Tunnel" /min cmd /c "ngrok.exe http 8000 --url=trodden-winner-arrive.ngrok-free.dev --log=ngrok.log"

echo.
echo ===================================================================
echo  ONLINE & SECURED!
echo.
echo  Local Dashboard:    http://localhost:8000
echo  Permanent URL:      https://trodden-winner-arrive.ngrok-free.dev
echo ===================================================================
echo.
pause
