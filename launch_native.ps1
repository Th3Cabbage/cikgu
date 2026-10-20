<#
.SYNOPSIS
  Open the native ManimGL study guide window (1280x720).

.DESCRIPTION
  Runs courses\ode\native\study_guide.py from this checkout with ManimGL. It uses the repo-local .venv
  (see README) and falls back to a sibling ..\ManimGL\.venv if that exists instead.
  MiKTeX is added to this process's PATH only (Machine + User PATH re-read; nothing is
  saved). The first visit to each lesson page compiles its LaTeX once (a few seconds);
  later visits use ManimGL's cache.

  Controls: click tabs/buttons, drag sliders, 1/2/3 switch views, arrows navigate,
  Space reveals a step or plays the marker, H shows help, Q or Esc closes.

.PARAMETER CheckOnly
  Verify the venv, guide files, LaTeX and window config, print the command, and exit
  without opening a window.
#>
param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$venvDirs = @((Join-Path $root '.venv'),
              (Join-Path (Split-Path $root -Parent) 'ManimGL\.venv'))
$venv = $venvDirs | Where-Object { Test-Path (Join-Path $_ 'Scripts\manimgl.exe') } | Select-Object -First 1
if (-not $venv) { throw "ManimGL venv not found. Create .venv in $root (see README)." }
$manimgl = Join-Path $venv 'Scripts\manimgl.exe'

$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not (Get-Command latex -ErrorAction SilentlyContinue)) {
    Write-Warning 'latex was not found on PATH; lesson formulas need MiKTeX (see README).'
}

# Relative to this checkout, which is the working directory for manimgl.
$guide = 'courses\ode\native\study_guide.py'
$config = 'courses\ode\native\guide_config.yml'

Push-Location $root
try {
    foreach ($f in $guide, $config, 'courses\ode\course.json') {
        if (-not (Test-Path $f)) { throw "Missing $f" }
    }
    if ($CheckOnly) {
        $py = Join-Path $venv 'Scripts\python.exe'
        # No double quotes inside: Windows PowerShell 5.1 does not escape them for native programs.
        $code = "import sys; sys.argv=['manimgl','--config_file',sys.argv[1]]; " +
                "from manimlib.config import manim_config as c; " +
                "print('window size', c.window.size, '| camera', c.camera.resolution)"
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'   # manimlib prints a harmless pkg_resources warning on stderr
        & $py -W ignore -c $code $config 2>$null
        $ErrorActionPreference = $prev
        Write-Host "OK. Would run (from $root):"
        Write-Host "  $manimgl $guide SecondOrderStudyGuide --config_file $config"
        return
    }
    & $manimgl $guide 'SecondOrderStudyGuide' '--config_file' $config
}
finally {
    Pop-Location
}
