@echo off
title Stop Apex Sovereign Bot
echo Stopping Apex Sovereign Bot, Ngrok, and Cloudflare...

taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo All Apex Sovereign processes stopped safely.
pause
