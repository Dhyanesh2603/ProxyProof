[Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementPublisher, Windows.Devices.Bluetooth, ContentType = WindowsRuntime] | Out-Null
[Windows.Devices.Bluetooth.Advertisement.BluetoothLEManufacturerData, Windows.Devices.Bluetooth, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.Streams.DataWriter, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null

$pub = New-Object Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementPublisher
$mdata = New-Object Windows.Devices.Bluetooth.Advertisement.BluetoothLEManufacturerData
$mdata.CompanyId = 0x5050

$writer = New-Object Windows.Storage.Streams.DataWriter
# 24 bytes payload: 4-byte session_id (1), 4-byte window_index (0), 16-byte token ASCII
$bytes = [byte[]](0, 0, 0, 1, 0, 0, 0, 0) + [System.Text.Encoding]::ASCII.GetBytes("e3b0c44298fc1c14")
$writer.WriteBytes($bytes)
$mdata.Data = $writer.DetachBuffer()

$pub.Advertisement.ManufacturerData.Add($mdata)
$pub.Start()

Start-Sleep -Milliseconds 500
Write-Host "BLE Advertisement Publisher Status: $($pub.Status)"

if ($pub.Status -eq "Started") {
    Write-Host "SUCCESS: PC Bluetooth radio is physically broadcasting BLE advertisement signal over the air!"
} else {
    Write-Host "Status returned: $($pub.Status)"
}

$pub.Stop()
Write-Host "Stopped test broadcaster."
