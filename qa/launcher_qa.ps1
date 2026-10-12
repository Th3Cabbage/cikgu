# Launcher QA for launch_browser.ps1 (no browser window: uses -NoBrowser).
# Occupies 127.0.0.1:8765 with a dummy listener, starts the launcher, and checks that it
# skips the busy port, binds loopback only, serves the guide, and stops cleanly.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$results = @()
function Check($name, $ok, $detail = '') {
    $script:results += [pscustomobject]@{ check = $name; ok = [bool]$ok; detail = "$detail" }
    Write-Host ((@('FAIL ', 'PASS ')[[int][bool]$ok]) + $name + $(if ($detail) { "  [$detail]" } else { '' }))
}

$blocker = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 8765)
$blocker.Start()
$out = Join-Path $env:TEMP 'sode-launcher-out.txt'
$err = Join-Path $env:TEMP 'sode-launcher-err.txt'
$launcher = Start-Process powershell -PassThru -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err `
    -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$root\launch_browser.ps1`"", '-NoBrowser', '-Port', '8765')
try {
    $url = $null
    for ($i = 0; $i -lt 60 -and -not $url; $i++) {
        Start-Sleep -Milliseconds 250
        if (Test-Path $out) {
            $m = Select-String -Path $out -Pattern 'running at (http://127\.0\.0\.1:\d+/)' | Select-Object -First 1
            if ($m) { $url = $m.Matches[0].Groups[1].Value }
        }
    }
    Check 'launcher reports a URL' $url $url
    $port = [int]([uri]$url).Port
    Check 'busy port 8765 skipped (dummy listener left alone)' ($port -ne 8765 -and $blocker.Server.IsBound) "port $port"
    $health = Invoke-RestMethod "$($url)__guide_health"
    Check 'health endpoint identifies the guide server' ($health.app -eq 'SecondOrderODE') "pid $($health.pid)"
    $listen = Get-NetTCPConnection -State Listen -LocalPort $port
    Check 'server listens on 127.0.0.1 only' (@($listen | Where-Object { $_.LocalAddress -ne '127.0.0.1' }).Count -eq 0) (($listen.LocalAddress | Sort-Object -Unique) -join ',')
    $page = Invoke-WebRequest $url -UseBasicParsing
    Check 'serves index.html' ($page.StatusCode -eq 200 -and $page.Content -match 'Second-Order Linear ODEs')
    $course = Invoke-RestMethod "$($url)course.json"
    Check 'serves course.json' ($course.lessons.Count -eq 6 -and $course.quiz.Count -ge 8)
    # simulate the user stopping the server: end the real server process
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
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot 'results') | Out-Null
$results | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $PSScriptRoot 'results\launcher_results.json')
$failed = @($results | Where-Object { -not $_.ok }).Count
Write-Host "`n$($results.Count - $failed)/$($results.Count) launcher checks passed"
exit $failed
