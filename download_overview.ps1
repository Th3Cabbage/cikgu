<#
Download the Control Bootcamp overview and available English captions.
Uses an isolated Python environment and bundled FFmpeg. Requires Python and Node.js.
Run again to resume interrupted downloads. Sources stay local (ignored by Git).
#>
param([switch]$CaptionsOnly)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv-download\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & python -m venv (Join-Path $PSScriptRoot '.venv-download')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the downloader environment.' }
}
& $python -c "import importlib.util, sys; sys.exit(0 if all(importlib.util.find_spec(m) for m in ('yt_dlp', 'imageio_ffmpeg')) else 1)"
if ($LASTEXITCODE -ne 0) {
    & $python -m pip install 'yt-dlp[default]' imageio-ffmpeg
    if ($LASTEXITCODE -ne 0) { throw 'Could not install download tools.' }
}
$ffmpeg = & $python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'
if ($LASTEXITCODE -ne 0) { throw 'Could not locate FFmpeg.' }
$downloadArgs = @(
    '-m', 'yt_dlp', '--ignore-config', '--no-playlist', '--no-overwrites',
    '--js-runtimes', 'node', '--ffmpeg-location', $ffmpeg,
    '--write-subs', '--write-auto-subs', '--sub-langs', 'en,en-orig',
    '--sub-format', 'vtt', '--write-info-json', '--write-description',
    '--socket-timeout', '30', '--retries', '3', '--newline',
    '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b[height<=1080]',
    '--merge-output-format', 'mp4',
    '-o', (Join-Path $PSScriptRoot 'sources\control-bootcamp-overview\overview.%(ext)s')
)
if ($CaptionsOnly) { $downloadArgs += '--skip-download' }
$downloadArgs += 'https://www.youtube.com/watch?v=Pi7l8mMjYVE'
& $python @downloadArgs
if ($LASTEXITCODE -ne 0) { throw 'Download failed. See the yt-dlp message above; rerun this script to retry.' }
Write-Host 'Saved to sources\control-bootcamp-overview. Check the output for caption availability.'
