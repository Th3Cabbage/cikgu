<#
.SYNOPSIS
  Serve the Second Order Equations and Oscillation study companion on 127.0.0.1 and open it in the default browser.

.DESCRIPTION
  Starts courses\mit-de\second-order\server.py (standard-library Python, loopback only) on -Port, or the next free
  port if that one is taken. Before opening the page it confirms, through /__control_health and a
  random per-launch nonce, that the server answering is the one this script started.
  The optional tutor is enabled only if OPENAI_API_KEY is set in the environment of this window
  (OPENAI_MODEL optionally picks the model; default gpt-5-mini). The key is never printed.
  Press Ctrl+C or close this window to stop the server. The server is also told this window's
  process ID and exits on its own if the window is killed before it can clean up.

.EXAMPLE
  .\launch_second_order.ps1
  .\launch_second_order.ps1 -Port 9100
  .\launch_second_order.ps1 -NoBrowser     # serve only; print the URL
#>
param(
    [ValidateRange(1024, 65000)][int]$Port = 8833,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$server = Join-Path $root 'courses\mit-de\second-order\server.py'
if (-not (Test-Path -LiteralPath $server)) { throw "courses\mit-de\second-order\server.py not found next to this script." }
$venvPython = @((Join-Path $root '.venv\Scripts\python.exe'),
                (Join-Path (Split-Path $root -Parent) 'ManimGL\.venv\Scripts\python.exe')) |
              Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($venvPython) {
    $python = $venvPython
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = (Get-Command python).Source
} else {
    throw 'Python 3 not found. Expected .venv in this folder or python on PATH (viewing needs only the standard library).'
}

$nonce = [guid]::NewGuid().ToString('N')
$portFile = Join-Path ([IO.Path]::GetTempPath()) "second-order-port-$nonce.txt"
$proc = Start-Process -FilePath $python -NoNewWindow -PassThru -ArgumentList @(
    '-I', "`"$server`"", '--port', $Port, '--port-file', "`"$portFile`"", '--nonce', $nonce, '--watch-pid', $PID)
$serverPid = $null

try {
    $url = $null
    for ($i = 0; $i -lt 100 -and -not $url; $i++) {
        if ($proc.HasExited) { throw "The server exited early (code $($proc.ExitCode))." }
        if (Test-Path -LiteralPath $portFile) {
            $p = (Get-Content -LiteralPath $portFile -Raw).Trim()
            if ($p -match '^\d+$') {
                try {
                    $health = Invoke-RestMethod -Uri "http://127.0.0.1:$p/__control_health" -TimeoutSec 2
                    if ($health.app -eq 'Study_second_order' -and $health.nonce -eq $nonce) {
                        $url = "http://127.0.0.1:$p/"
                        $serverPid = [int]$health.pid
                    }
                } catch { }
            }
        }
        if (-not $url) { Start-Sleep -Milliseconds 200 }
    }
    if (-not $url) { throw 'The server did not answer its health check.' }

    Write-Host ""
    Write-Host "Second Order Equations and Oscillation companion running at $url" -ForegroundColor Green
    if ($env:OPENAI_API_KEY) {
        $model = if ($env:OPENAI_MODEL) { $env:OPENAI_MODEL } else { 'gpt-5-mini' }
        Write-Host "Tutor: enabled (model $model)."
    } else {
        Write-Host "Tutor: not configured (set OPENAI_API_KEY before launching to enable it). Everything else works."
    }
    Write-Host "Press Ctrl+C (or close this window) to stop the server."
    if (-not $NoBrowser) { Start-Process $url }
    Wait-Process -Id $proc.Id
}
finally {
    # A venv python.exe can be a launcher stub whose child is the real server ($serverPid).
    foreach ($id in @($serverPid, $proc.Id)) {
        if ($id) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
    }
    Remove-Item -LiteralPath $portFile -ErrorAction SilentlyContinue
    Write-Host 'Server stopped.'
}
