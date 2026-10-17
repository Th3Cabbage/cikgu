# Launcher QA for launch_control.ps1 (no browser window: uses -NoBrowser).
#   powershell -NoProfile -ExecutionPolicy Bypass -File qa\control_launcher_qa.ps1
# 1. Occupies 127.0.0.1:8770 with a dummy listener; the launcher must skip it, confirm its own
#    server by nonce, bind loopback only, serve the guide, and stop cleanly when the server ends.
# 2. Kills the launcher process outright (no finally block runs); the server must notice via
#    --watch-pid and release its port.
# OPENAI_* variables are cleared for the child so no real key is ever used here.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$results = @()
function Check($name, $ok, $detail = '') {
    $script:results += [pscustomobject]@{ check = $name; ok = [bool]$ok; detail = "$detail" }
    Write-Host ((@('FAIL ', 'PASS ')[[int][bool]$ok]) + $name + $(if ($detail) { "  [$detail]" } else { '' }))
}
foreach ($v in @(Get-ChildItem Env: | Where-Object { $_.Name -like 'OPENAI_*' })) { Remove-Item "Env:$($v.Name)" }

function Start-Launcher($port, $out, $err) {
    Start-Process powershell -PassThru -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err `
        -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$root\launch_control.ps1`"", '-NoBrowser', '-Port', $port)
}
function Wait-Url($out) {
    for ($i = 0; $i -lt 80; $i++) {
        Start-Sleep -Milliseconds 250
        if (Test-Path $out) {
            $m = Select-String -Path $out -Pattern 'running at (http://127\.0\.0\.1:\d+/)' | Select-Object -First 1
            if ($m) { return $m.Matches[0].Groups[1].Value }
        }
    }
    return $null
}

$blocker = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 8770)
$blocker.Start()
$out = Join-Path $env:TEMP 'ctl-launcher-out.txt'
$err = Join-Path $env:TEMP 'ctl-launcher-err.txt'
$launcher = Start-Launcher 8770 $out $err
try {
    $url = Wait-Url $out
    Check 'launcher reports a URL' $url $url
    $port = [int]([uri]$url).Port
    Check 'busy port 8770 skipped (dummy listener left alone)' ($port -ne 8770 -and $blocker.Server.IsBound) "port $port"
    $health = Invoke-RestMethod "$($url)__control_health"
    Check 'health endpoint identifies the control server' ($health.app -eq 'ControlBootcamp' -and $health.nonce.Length -eq 32) "pid $($health.pid)"
    $listen = Get-NetTCPConnection -State Listen -LocalPort $port
    Check 'server listens on 127.0.0.1 only' (@($listen | Where-Object { $_.LocalAddress -ne '127.0.0.1' }).Count -eq 0) (($listen.LocalAddress | Sort-Object -Unique) -join ',')
    $page = Invoke-WebRequest $url -UseBasicParsing
    Check 'serves the companion page' ($page.StatusCode -eq 200 -and $page.Content -match 'Control Bootcamp')
    $status = Invoke-RestMethod "$($url)api/status"
    Check 'tutor reported as not configured (no key in this environment)' (-not $status.tutor.configured)
    Check 'launcher prints tutor setup hint' ((Get-Content $out -Raw) -match 'Tutor: not configured')
    Stop-Process -Id $health.pid -Force
    $launcher.WaitForExit(10000) | Out-Null
    Check 'launcher exits when the server stops' $launcher.HasExited
    Start-Sleep -Milliseconds 300
    Check 'port released after stop' (-not (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue))
    Check 'launcher printed Server stopped' ((Get-Content $out -Raw) -match 'Server stopped')
}
finally {
    if (-not $launcher.HasExited) { Stop-Process -Id $launcher.Id -Force }
    $blocker.Stop()
    Remove-Item $out, $err -ErrorAction SilentlyContinue
}

# --- killed launcher: the server must exit by itself (watch-pid)
$launcher = Start-Launcher 8775 $out $err
try {
    $url = Wait-Url $out
    $port = [int]([uri]$url).Port
    $health = Invoke-RestMethod "$($url)__control_health"
    Stop-Process -Id $launcher.Id -Force       # no finally block runs in the launcher
    $gone = $false
    for ($i = 0; $i -lt 40 -and -not $gone; $i++) {
        Start-Sleep -Milliseconds 250
        $gone = -not (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)
    }
    Check 'killed launcher: server notices and releases its port' $gone "port $port"
    Start-Sleep -Milliseconds 500
    Check 'killed launcher: server process has exited' (-not (Get-Process -Id $health.pid -ErrorAction SilentlyContinue)) "pid $($health.pid)"
}
finally {
    if ($health -and (Get-Process -Id $health.pid -ErrorAction SilentlyContinue)) { Stop-Process -Id $health.pid -Force }
    Remove-Item $out, $err -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot 'results') | Out-Null
$results | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $PSScriptRoot 'results\control_launcher_qa.json')
$failed = @($results | Where-Object { -not $_.ok }).Count
Write-Host "`n$($results.Count - $failed)/$($results.Count) launcher checks passed"
exit $failed
