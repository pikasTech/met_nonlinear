param(
    [Parameter(Mandatory = $true)][string]$PortName,
    [Parameter(Mandatory = $true)][int]$BaudRate,
    [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
    [Parameter(Mandatory = $true)][string]$ResultPath,
    [Parameter(Mandatory = $true)][string]$JsonlPath,
    [Parameter(Mandatory = $true)][string]$TextPath,
    [string[]]$SuccessMarker = @('validation_complete=1')
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$records = New-Object System.Collections.Generic.List[object]
$streamBuilder = New-Object System.Text.StringBuilder
$matchedMarkers = New-Object System.Collections.Generic.List[string]
$port = New-Object System.IO.Ports.SerialPort $PortName, $BaudRate, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$port.Encoding = [System.Text.Encoding]::ASCII
$port.ReadTimeout = 200
$port.WriteTimeout = 200
$port.DtrEnable = $false
$port.RtsEnable = $false
$status = 'completed'
$errorMessage = $null
$timedOut = $false
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $port.Open()
    $port.DiscardInBuffer()
    while ($stopwatch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        $chunk = $port.ReadExisting()
        if (-not [string]::IsNullOrEmpty($chunk)) {
            [void]$streamBuilder.Append($chunk)
            $records.Add([ordered]@{
                timestamp = [DateTimeOffset]::Now.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
                port = $PortName
                data = $chunk
            })
            $currentStream = $streamBuilder.ToString()
            $allMatched = $true
            foreach ($marker in $SuccessMarker) {
                if ($currentStream.Contains($marker)) {
                    if (-not $matchedMarkers.Contains($marker)) {
                        $matchedMarkers.Add($marker)
                    }
                } else {
                    $allMatched = $false
                }
            }
            if ($allMatched) {
                break
            }
        } else {
            Start-Sleep -Milliseconds 50
        }
    }
    if ($stopwatch.Elapsed.TotalSeconds -ge $TimeoutSeconds -and $matchedMarkers.Count -lt $SuccessMarker.Count) {
        $timedOut = $true
        $status = 'timeout'
    }
} catch {
    $status = 'error'
    $errorMessage = $_.Exception.Message
} finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}

$streamText = $streamBuilder.ToString()
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($ResultPath)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($JsonlPath)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($TextPath)) | Out-Null
[System.IO.File]::WriteAllText($TextPath, $streamText, $utf8NoBom)

$jsonlLines = @()
if ($records.Count -gt 0) {
    $jsonlLines = @(
        foreach ($record in $records) {
            $record | ConvertTo-Json -Compress -Depth 4
        }
    )
}
[System.IO.File]::WriteAllLines($JsonlPath, [string[]]$jsonlLines, $utf8NoBom)

$missingMarkers = @()
foreach ($marker in $SuccessMarker) {
    if (-not $matchedMarkers.Contains($marker)) {
        $missingMarkers += $marker
    }
}

$result = [ordered]@{
    status = $status
    port = $PortName
    baud_rate = $BaudRate
    timeout_seconds = $TimeoutSeconds
    timed_out = $timedOut
    record_count = $records.Count
    stream_length = $streamText.Length
    matched_success_markers = @($matchedMarkers)
    missing_success_markers = @($missingMarkers)
    result_path = $ResultPath
    jsonl_path = $JsonlPath
    text_path = $TextPath
    error = $errorMessage
}

$resultJson = $result | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($ResultPath, $resultJson, $utf8NoBom)
Write-Output $resultJson

if ($status -eq 'error') {
    exit 1
}
exit 0
