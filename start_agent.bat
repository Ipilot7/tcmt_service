@echo off
color 0A
title Equipment Status Agent

echo ===================================================
echo TCMT Equipment WebSocket Agent
echo ===================================================

:: Настройки оборудования (Измените под конкретный аппарат)
set SERIAL_NUMBER=SN-12345

:: Адрес вашего сервера (например: ws://api.my-domain.com)
set SERVER_URL=ws://localhost:8000

echo Starting agent for Device: %SERIAL_NUMBER%
echo Connecting to Server: %SERVER_URL%
echo.

:: Запускаем PowerShell скрипт обходя политики безопасности
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0device_agent.ps1' -SerialNumber '%SERIAL_NUMBER%' -HostUrl '%SERVER_URL%'"

echo.
pause
