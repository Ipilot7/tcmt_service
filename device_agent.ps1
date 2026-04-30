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

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$cts = New-Object System.Threading.CancellationTokenSource

try {
    $ws.ConnectAsync([Uri]$wsUri, $cts.Token).Wait()
    Write-Host "Connected: $SerialNumber" -ForegroundColor Green
    
    while ($ws.State -eq 'Open') {
        # Отправляем только статус
        $payload = @{ action = "status"; data = @{ status = "Online" } }
        $json = $payload | ConvertTo-Json -Compress
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $ws.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()
        
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Status sent"
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
