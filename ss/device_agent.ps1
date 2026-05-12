$ConfigPath = "$PSScriptRoot\device_config.txt"
if (Test-Path $ConfigPath) {
    $Config = Get-Content $ConfigPath -Encoding UTF8 | ConvertFrom-StringData
    $SerialNumber = $Config.SERIAL_NUMBER
    $HostUrl = $Config.SERVER_URL
} else {
    $SerialNumber = "UNKNOWN_DEVICE"; $HostUrl = "ws://127.0.0.1:8000"
}

$Bytes = [System.Text.Encoding]::UTF8.GetBytes($SerialNumber)
$EncodedSerial = ""; foreach ($Byte in $Bytes) { $EncodedSerial += "%{0:X2}" -f $Byte }
$wsUri = "$HostUrl/ws/devices/$EncodedSerial/status/"

Write-Host "--- Equipment Status Agent Started ---" -ForegroundColor Cyan
Write-Host "Device: $SerialNumber"
Write-Host "Target: $HostUrl"

while ($true) {
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $cts = New-Object System.Threading.CancellationTokenSource
    
    try {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connecting to server..." -ForegroundColor Gray
        $connectTask = $ws.ConnectAsync([Uri]$wsUri, $cts.Token)
        $connectTask.Wait()
        
        if ($ws.State -eq 'Open') {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connected successfully!" -ForegroundColor Green
            
            while ($ws.State -eq 'Open') {
                $payload = @{ action = "status"; data = @{ status = "Online" } }
                $json = $payload | ConvertTo-Json -Compress
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
                
                $sendTask = $ws.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token)
                $sendTask.Wait()
                
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Heartbeat sent (Online)"
                Start-Sleep -Seconds 15
            }
        }
    } catch {
        $msg = if ($_.Exception.InnerException) { $_.Exception.InnerException.Message } else { $_.Exception.Message }
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connection error: $msg" -ForegroundColor Red
    } finally {
        if ($ws) { $ws.Dispose() }
        if ($cts) { $cts.Dispose() }
    }
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Reconnecting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

