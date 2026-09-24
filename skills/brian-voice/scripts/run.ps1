param(
    [switch]$Check,
    [string]$TextFile,
    [ValidateSet('zh','en')][string]$Language = 'zh',
    [string]$OutputFile,
    [string]$JobsFile,
    [string]$RuntimeProfile
)
$ErrorActionPreference = 'Stop'
if (-not $RuntimeProfile) { $RuntimeProfile = Join-Path (Split-Path $PSScriptRoot -Parent) 'runtime.json' }
$RuntimeProfile = (Resolve-Path -LiteralPath $RuntimeProfile).Path
$runtimeSettings = Get-Content -LiteralPath $RuntimeProfile -Raw -Encoding utf8 | ConvertFrom-Json
if (-not (Test-Path -LiteralPath $runtimeSettings.python_executable)) { throw 'Configured CUDA Python is missing; repair runtime.json before synthesis.' }
$arguments = @((Join-Path $PSScriptRoot 'synthesize.py'), '--runtime', $RuntimeProfile)
if ($Check) { $arguments += '--check' }
elseif ($JobsFile) { $arguments += @('--jobs-file', (Resolve-Path -LiteralPath $JobsFile).Path) }
else {
    if (-not $TextFile -or -not $OutputFile) { throw 'Provide TextFile and OutputFile, or JobsFile, or Check.' }
    $arguments += @('--text-file', (Resolve-Path -LiteralPath $TextFile).Path, '--language', $Language, '--output', [System.IO.Path]::GetFullPath($OutputFile))
}
$env:PYTHONIOENCODING = 'utf-8'
& $runtimeSettings.python_executable @arguments
if ($LASTEXITCODE -ne 0) { throw "Brian Voice exited with code $LASTEXITCODE. Completed parts are preserved." }
