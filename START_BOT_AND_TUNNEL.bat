@echo off
title APEX SOVEREIGN BOT - 24/7 LAUNCHER
echo ========================================================
echo   APEX SOVEREIGN ALGORITHMIC TRADING CITADEL
echo   Starting Institutional Engine & Cloudflare Tunnel...
echo ========================================================

cd /d "%~dp0"

echo [1/2] Launching Apex Sovereign Engine & Web GUI on Port 8000...
start "Apex Trading Server" cmd /k "python -m src.web.server"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Cloudflare Tunnel...
start "Cloudflare Live Tunnel" cmd /k "cloudflared.exe tunnel --url http://localhost:8000"

echo ========================================================
echo   System running! Access your bot locally or via
echo   the public trycloudflare.com URL in the tunnel window.
echo ========================================================
pause
