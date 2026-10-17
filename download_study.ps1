<# Download one lecture and prepare compact, timestamped research sources. #>
param(
    [Parameter(Mandatory=$true)][string]$Url,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')][string]$Slug,
    [string]$BookPages = '',
    [switch]$CaptionsOnly,
    [switch]$Transcribe,
    [switch]$Refresh
)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv-download\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & python -m venv (Join-Path $PSScriptRoot '.venv-download')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the downloader environment.' }
}
& $python -c "import importlib.util,sys; sys.exit(not all(importlib.util.find_spec(m) for m in ('yt_dlp','imageio_ffmpeg','pymupdf')))"
if ($LASTEXITCODE -ne 0) {
    & $python -m pip install 'yt-dlp[default]' imageio-ffmpeg pymupdf
    if ($LASTEXITCODE -ne 0) { throw 'Could not install source-preparation tools.' }
}
$studyArgs = @((Join-Path $PSScriptRoot 'tools\prepare_study.py'), '--url', $Url, '--slug', $Slug)
if ($BookPages) { $studyArgs += @('--book-pages', $BookPages) }
if ($CaptionsOnly) { $studyArgs += '--captions-only' }
if ($Transcribe) { $studyArgs += '--transcribe' }
if ($Refresh) { $studyArgs += '--refresh' }
& $python @studyArgs
if ($LASTEXITCODE -ne 0) { throw 'Source preparation failed; see the message above.' }
