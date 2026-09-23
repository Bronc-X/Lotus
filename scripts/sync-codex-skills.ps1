param(
    [string]$CodexRoot = (Join-Path $env:USERPROFILE '.codex'),
    [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$skillRoot = [IO.Path]::GetFullPath((Join-Path $CodexRoot 'skills'))
$backupRoot = Join-Path $CodexRoot ('backups/lotus-skills-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$items = [Collections.Generic.List[object]]::new()
function Add-File($Source, $Destination) {
    $resolved = [IO.Path]::GetFullPath($Destination)
    if (-not $resolved.StartsWith($skillRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Target outside skill root' }
    if ($items.Destination -contains $resolved) { throw "Duplicate destination: $resolved" }
    if ((Split-Path $Source -Leaf) -eq 'openai.yaml' -and (Test-Path -LiteralPath $resolved)) {
        # Merge UI strings only; preserve icons, dependencies, and invocation policy.
        $existing = Get-Content -LiteralPath $resolved -Raw -Encoding utf8
        $template = Get-Content -LiteralPath $Source -Raw -Encoding utf8
        $merged = $existing
        foreach ($key in @('display_name','short_description','default_prompt')) {
            $line = [regex]::Match($template, '(?m)^  ' + $key + ':.*$').Value
            if ($line -and $merged -match ('(?m)^  ' + $key + ':.*$')) {
                $replacement = $line
                $merged = [regex]::Replace($merged, '(?m)^  ' + $key + ':.*$', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $replacement })
            }
        }
        if ($merged -ne $existing) {
            $prepared = Join-Path ([IO.Path]::GetTempPath()) ('lotus-ui-' + [guid]::NewGuid().ToString('N') + '.yaml')
            [IO.File]::WriteAllText($prepared, $merged, [Text.UTF8Encoding]::new($false))
            $Source = $prepared
        } else { return }
    }
    $items.Add([pscustomobject]@{ Source=$Source; Destination=$resolved })
}
# Update existing Lotus packages only. Preserve local-only files and private runtime settings.
Get-ChildItem (Join-Path $repo 'skills') -Directory | ForEach-Object {
    $target = Join-Path $skillRoot $_.Name
    if ((Test-Path (Join-Path $_.FullName 'SKILL.md')) -and (Test-Path (Join-Path $target 'SKILL.md'))) {
        $package = $_.FullName
        $voicePackage = $_.Name -in @('ai-podcast', 'toni-voice')
        Get-ChildItem $package -Recurse -File | Where-Object {
            ($_.Extension -in @('.md','.yaml','.yml') -or
                ($voicePackage -and ($_.Extension -in @('.py','.ps1') -or $_.Name -like '*.example.json'))) -and
                $_.FullName -notmatch '[\\/](__pycache__|node_modules)[\\/]'
        } | ForEach-Object { Add-File $_.FullName (Join-Path $target $_.FullName.Substring($package.Length + 1)) }
    }
}
Get-ChildItem (Join-Path $repo 'skills') -Filter '*.md' -File | Where-Object BaseName -NotIn @('gstack','btw','loop') | ForEach-Object {
    $target = Join-Path $skillRoot ($_.BaseName + '/SKILL.md')
    if (Test-Path -LiteralPath $target) { Add-File $_.FullName $target }
}
Get-ChildItem (Join-Path $repo 'adapters/gstack') -Directory | ForEach-Object {
    $target = Join-Path $skillRoot $_.Name
    if (Test-Path (Join-Path $target 'SKILL.md')) {
        $package = $_.FullName
        Get-ChildItem $package -Recurse -File | ForEach-Object { Add-File $_.FullName (Join-Path $target $_.FullName.Substring($package.Length + 1)) }
    }
}
$changed = @($items | Where-Object {
    -not (Test-Path -LiteralPath $_.Destination) -or
    (Get-FileHash -LiteralPath $_.Source).Hash -ne (Get-FileHash -LiteralPath $_.Destination).Hash
})
if ($WhatIf) { $changed | Select-Object Source,Destination; return }
if ($changed.Count -eq 0) { Write-Output 'Skills already synchronized.'; return }
# Reject links/junctions before writing; they could escape the intended target.
foreach ($item in $changed) {
    $cursor = $item.Destination
    while ($cursor.Length -ge $skillRoot.Length) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Linked destination requires manual review: $cursor" }
        $cursor = Split-Path $cursor -Parent
    }
}
New-Item -ItemType Directory -Path $backupRoot | Out-Null
$manifest = foreach ($item in $changed) {
    $relative = $item.Destination.Substring($skillRoot.Length + 1)
    $saved = Join-Path $backupRoot $relative
    $existed = Test-Path -LiteralPath $item.Destination
    if ($existed) {
        New-Item -ItemType Directory -Path (Split-Path $saved -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $item.Destination -Destination $saved
        if ((Get-FileHash $saved).Hash -ne (Get-FileHash $item.Destination).Hash) { throw 'Backup hash mismatch' }
    }
    [pscustomobject]@{ relativePath=$relative; existed=$existed; beforeHash=$(if ($existed) {(Get-FileHash $saved).Hash} else {$null}); afterHash=(Get-FileHash $item.Source).Hash }
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $backupRoot 'manifest.json') -Encoding utf8
foreach ($item in $changed) {
    New-Item -ItemType Directory -Path (Split-Path $item.Destination -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $item.Source -Destination $item.Destination -Force
    if ((Get-FileHash $item.Source).Hash -ne (Get-FileHash $item.Destination).Hash) { throw "Verification failed: $($item.Destination)" }
}
Write-Output "Updated $($changed.Count) files in $(@($changed | ForEach-Object { $_.Destination.Substring($skillRoot.Length + 1).Split([IO.Path]::DirectorySeparatorChar)[0] } | Sort-Object -Unique).Count) skills. Backup: $backupRoot"
