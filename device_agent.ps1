param(
    [string]$SerialNumber = "SN-12345",
    [string]$HostUrl = "ws://localhost:8000"
)

$wsUri = "$HostUrl/ws/devices/$SerialNumber/status/"
Write-Host "Initialising connection to $wsUri" -ForegroundColor Cyan

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$cts = New-Object System.Threading.CancellationTokenSource

try {
    $task = $ws.ConnectAsync([Uri]$wsUri, $cts.Token)
    $task.Wait()
} catch {
    Write-Host "Failed to connect to server. Error: $($_.Exception.InnerException.Message)" -ForegroundColor Red
    exit
}

if ($ws.State -eq 'Open') {
    Write-Host "Connected successfully! Press Ctrl+C to stop." -ForegroundColor Green
    
    try {
        while ($ws.State -eq 'Open') {
            # Формируем JSON статус
            $json = '{"action": "status", "data": {"is_working": true, "temperature": 45, "error_code": null}}'
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
            $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
            
            # Отправляем в сокет
            $sendTask = $ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token)
            $sendTask.Wait()
            
            $time = Get-Date -Format "HH:mm:ss"
            Write-Host "[$time] Sent: $json" -ForegroundColor Yellow
            
            # Ждем 5 секунд перед следующей отправкой
            Start-Sleep -Seconds 5
        }
    } catch {
        Write-Host "Connection lost..." -ForegroundColor Red
    }
} else {
    Write-Host "Failed to open connection. State: $($ws.State)" -ForegroundColor Red
}
