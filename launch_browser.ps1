<#
.SYNOPSIS
  Serve the browser study guide on 127.0.0.1 and open it in the default browser.

.DESCRIPTION
  Starts courses\ode\browser\serve_local.py (loopback only) on -Port, or the next free port if that one
  is taken. Before opening the page it confirms, through /__guide_health and a random
  per-launch nonce, that the server answering is the one this script started.
  Press Ctrl+C or close this window to stop the server.

.EXAMPLE
  .\launch_browser.ps1
  .\launch_browser.ps1 -Port 9000
  .\launch_browser.ps1 -NoBrowser     # serve only; print the URL
#>
param(
    [int]$Port = 8765,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$server = Join-Path $root 'courses\ode\browser\serve_local.py'
$venvPython = @((Join-Path $root '.venv\Scripts\python.exe'),
                (Join-Path (Split-Path $root -Parent) 'ManimGL\.venv\Scripts\python.exe')) |
              Where-Object { Test-Path $_ } | Select-Object -First 1

if ($venvPython) {
    $python = $venvPython
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = (Get-Command python).Source
} else {
    throw 'Python not found. Expected .venv in this folder, ..\ManimGL\.venv, or python on PATH.'
}

$nonce = [guid]::NewGuid().ToString('N')
$portFile = Join-Path ([IO.Path]::GetTempPath()) "second-order-ode-port-$nonce.txt"
$proc = Start-Process -FilePath $python -NoNewWindow -PassThru -ArgumentList @(
    '-I', "`"$server`"", '--port', $Port, '--port-file', "`"$portFile`"", '--nonce', $nonce)
$serverPid = $null

try {
    $url = $null
    for ($i = 0; $i -lt 75 -and -not $url; $i++) {
        if ($proc.HasExited) { throw "The server exited early (code $($proc.ExitCode))." }
        if (Test-Path $portFile) {
            $p = (Get-Content $portFile -Raw).Trim()
            try {
                $health = Invoke-RestMethod -Uri "http://127.0.0.1:$p/__guide_health" -TimeoutSec 2
                if ($health.app -eq 'SecondOrderODE' -and $health.nonce -eq $nonce) {
                    $url = "http://127.0.0.1:$p/"
                    $serverPid = [int]$health.pid
                }
            } catch { }
        }
        if (-not $url) { Start-Sleep -Milliseconds 200 }
    }
    if (-not $url) { throw 'The server did not answer its health check.' }

    Write-Host ""
    Write-Host "Study guide running at $url" -ForegroundColor Green
    Write-Host "Press Ctrl+C (or close this window) to stop the server."
    if (-not $NoBrowser) { Start-Process $url }
    Wait-Process -Id $proc.Id
}
finally {
    # A venv python.exe is a launcher stub; the real server is its child ($serverPid).
    foreach ($id in @($serverPid, $proc.Id)) {
        if ($id) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
    }
    Remove-Item $portFile -ErrorAction SilentlyContinue
    Write-Host 'Server stopped.'
}
