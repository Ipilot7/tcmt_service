@echo off
    cd /d "C:\ss"
    title Equipment Status Agent
    
    echo Searching for existing agent instances...
    powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*device_agent.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    
    echo Starting Equipment Status Agent...
    start /b PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ss\device_agent.ps1"
    exit