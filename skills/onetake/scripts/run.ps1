param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Script,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArguments
)

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $skillRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw 'OneTake local Python environment is missing. See WINDOWS.md.'
}
if (-not [System.IO.Path]::IsPathRooted($Script)) {
    $Script = Join-Path $PSScriptRoot $Script
}
& $pythonExecutable -X utf8 $Script @ScriptArguments
exit $LASTEXITCODE
