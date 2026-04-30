@echo off
color 0A
title Equipment Status Agent

echo ===================================================
echo TCMT Equipment WebSocket Agent
echo ===================================================
echo Starting agent...
echo.

PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0device_agent.ps1'"

echo.
pause
