Write-Host "Starting persistent ADB Reverse Bridge..."
adb start-server
while ($true) {
    adb reverse tcp:8005 tcp:8005 | Out-Null
    adb reverse tcp:5173 tcp:5173 | Out-Null
    Start-Sleep -Seconds 2
}
