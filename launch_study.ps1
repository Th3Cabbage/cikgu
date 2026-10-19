<#
.SYNOPSIS
  Build the unified Cikgu study site and open it from 127.0.0.1 in the default browser.

.DESCRIPTION
  Runs `node site\build.mjs` (Node.js built-ins only) to regenerate site\dist, the same folder Netlify
  publishes, then starts site\server.py (standard-library Python, loopback only) on -Port, or the next
  free port if that one is taken. Before opening the page it confirms, through /__site_health and a
  random per-launch nonce, that the server answering is the one this script started.
  The site is static: the optional GPT tutor and local-PDF links need the single-lecture launchers
  (launch_control.ps1, launch_linear_systems.ps1, launch_stability_eigenvalues.ps1).
  Press Ctrl+C or close this window to stop the server. The server is also told this window's
  process ID and exits on its own if the window is killed before it can clean up.

.EXAMPLE
  .\launch_study.ps1
  .\launch_study.ps1 -Port 9200
  .\launch_study.ps1 -NoBrowser     # serve only; print the URL
  .\launch_study.ps1 -SkipBuild     # serve the existing site\dist without rebuilding
#>
param(
    [ValidateRange(1024, 65000)][int]$Port = 8800,
    [switch]$NoBrowser,
    [switch]$SkipBuild
)
$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$server = Join-Path $root 'site\server.py'
$build = Join-Path $root 'site\build.mjs'
$distIndex = Join-Path $root 'site\dist\index.html'
if (-not (Test-Path -LiteralPath $server)) { throw "site\server.py not found next to this script." }

if (-not $SkipBuild) {
    $node = Get-Command node -ErrorAction SilentlyContinue
    if ($node) {
        & $node.Source $build
        if ($LASTEXITCODE -ne 0) { throw "The site build failed (exit code $LASTEXITCODE); see the message above." }
    } elseif (Test-Path -LiteralPath $distIndex) {
        Write-Warning 'Node.js was not found, so the site was not rebuilt; serving the existing site\dist.'
    } else {
        throw 'Node.js was not found and site\dist has not been built. Install Node.js 18 or newer (see docs/SETUP.md).'
    }
}
if (-not (Test-Path -LiteralPath $distIndex)) { throw 'site\dist has not been built. Run without -SkipBuild.' }

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
$portFile = Join-Path ([IO.Path]::GetTempPath()) "cikgu-site-port-$nonce.txt"
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
                    $health = Invoke-RestMethod -Uri "http://127.0.0.1:$p/__site_health" -TimeoutSec 2
                    if ($health.app -eq 'CikguSite' -and $health.nonce -eq $nonce) {
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
    Write-Host "Cikgu study site running at $url" -ForegroundColor Green
    Write-Host "Ask GPT is off in this combined site; the single-lecture launchers provide it when a key is configured."
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
