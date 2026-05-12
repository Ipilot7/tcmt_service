$ConfigPath = "$PSScriptRoot\device_config.txt"

if (Test-Path $ConfigPath) {
    $Config = Get-Content $ConfigPath -Encoding UTF8 | ConvertFrom-StringData
    $SerialNumber = $Config.SERIAL_NUMBER
    $HostUrl = $Config.SERVER_URL
}
else {
    $SerialNumber = "UNKNOWN_DEVICE"
    $HostUrl = "ws://127.0.0.1:8000"
}

# Улучшенное кодирование серийного номера для поддержки кириллицы и спецсимволов
$EncodedSerial = [uri]::EscapeDataString($SerialNumber)
$wsUri = "$HostUrl/ws/devices/$EncodedSerial/status/"

Write-Host "--- Equipment Status Agent Started (v2.0) ---" -ForegroundColor Cyan
Write-Host "Device: $SerialNumber"
Write-Host "Target: $HostUrl"
Write-Host "Full WS URI: $wsUri" -ForegroundColor DarkGray

while ($true) {
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $cts = New-Object System.Threading.CancellationTokenSource

    try {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connecting to server..." -ForegroundColor Gray
        $connectTask = $ws.ConnectAsync([Uri]$wsUri, $cts.Token)
        $connectTask.Wait()

        if ($ws.State -eq 'Open') {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connected successfully!" -ForegroundColor Green

            $buffer = New-Object byte[] 4096
            $receiveTask = $ws.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buffer)), $cts.Token)
            $lastHeartbeat = [DateTime]::MinValue

            while ($ws.State -eq 'Open') {
                # 1. Check for incoming messages/commands
                if ($receiveTask.IsCompleted) {
                    try {
                        $result = $receiveTask.Result
                        if ($result.MessageType -eq 'Close') {
                            break
                        }

                        $jsonText = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
                        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Message received: $jsonText" -ForegroundColor Gray
                        $data = $jsonText | ConvertFrom-Json

                        if ($data.command) {
                            $cmd = $data.command.ToLower()
                            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Executing command: $cmd" -ForegroundColor Cyan

                            if ($cmd -eq "shutdown") {
                                try {
                                    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Shutdown command received" -ForegroundColor Red

                                    $confirm = @{
                                        action = "log"
                                        data   = @{
                                            message = "Shutdown command accepted on $SerialNumber"
                                        }
                                    }

                                    $confirmJson = $confirm | ConvertTo-Json -Compress
                                    $confirmBytes = [System.Text.Encoding]::UTF8.GetBytes($confirmJson)

                                    $ws.SendAsync(
                                        (New-Object System.ArraySegment[byte] -ArgumentList @(,$confirmBytes)),
                                        [System.Net.WebSockets.WebSocketMessageType]::Text,
                                        $true,
                                        $cts.Token
                                    ).Wait()

                                    Start-Sleep -Seconds 1

                                    Write-Host "Shutdown command executing NOW..." -ForegroundColor Red

                                    shutdown.exe /s /f /t 0
                                }
                                catch {
                                    Write-Host "Shutdown failed: $($_.Exception.Message)" -ForegroundColor Red
                                }
                            }
                            elseif ($cmd -eq "reset_network") {
                                try {
                                    Write-Host "Resetting network settings..." -ForegroundColor Yellow

                                    # Send confirmation before connection reset
                                    $confirm = @{
                                        action = "log"
                                        data   = @{
                                            message = "Executing network reset on device $SerialNumber"
                                        }
                                    }

                                    $confirmJson = $confirm | ConvertTo-Json -Compress
                                    $confirmBytes = [System.Text.Encoding]::UTF8.GetBytes($confirmJson)

                                    $ws.SendAsync(
                                        (New-Object System.ArraySegment[byte] -ArgumentList @(,$confirmBytes)),
                                        [System.Net.WebSockets.WebSocketMessageType]::Text,
                                        $true,
                                        $cts.Token
                                    ).Wait()

                                    Start-Sleep -Seconds 2

                                    # Reset stack
                                    netsh winsock reset
                                    netsh int ip reset

                                    # DNS cleanup
                                    ipconfig /flushdns
                                    Clear-DnsClientCache

                                    Start-Sleep -Seconds 1

                                    # Restart adapters
                                    Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
                                        Disable-NetAdapter -Name $_.Name -Confirm:$false
                                    }

                                    Start-Sleep -Seconds 3

                                    Get-NetAdapter | ForEach-Object {
                                        Enable-NetAdapter -Name $_.Name -Confirm:$false
                                    }

                                    Start-Sleep -Seconds 5

                                    ipconfig /renew

                                    Write-Host "Network reset complete." -ForegroundColor Green

                                    # Optional reboot for full winsock apply
                                    shutdown.exe /r /f /t 5
                                }
                                catch {
                                    Write-Host "Network reset failed: $($_.Exception.Message)" -ForegroundColor Red
                                }
                            }
                        }
                    }
                    catch {
                        Write-Host "Error processing message: $($_.Exception.Message)" -ForegroundColor Red
                    }

                    # Start next receive task
                    $receiveTask = $ws.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buffer)), $cts.Token)
                }

                # 2. Send Heartbeat (Online status) every 15 seconds
                if ((Get-Date) -gt $lastHeartbeat.AddSeconds(15)) {
                    $payload = @{
                        action = "status"
                        data   = @{ status = "Online" }
                    }
                    $json = $payload | ConvertTo-Json -Compress
                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)

                    $sendTask = $ws.SendAsync(
                        (New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)),
                        [System.Net.WebSockets.WebSocketMessageType]::Text,
                        $true,
                        $cts.Token
                    )
                    $sendTask.Wait()

                    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Heartbeat sent"
                    $lastHeartbeat = Get-Date
                }

                # 3. Small delay to prevent CPU spinning
                Start-Sleep -Milliseconds 200
            }
        }
    }
    catch {
        $msg = if ($_.Exception.InnerException) { $_.Exception.InnerException.Message } else { $_.Exception.Message }
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connection error: $msg" -ForegroundColor Red
    }
    finally {
        if ($ws) { $ws.Dispose() }
        if ($cts) { $cts.Dispose() }
    }

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Reconnecting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}
