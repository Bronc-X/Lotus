$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$fixture=Join-Path ([IO.Path]::GetTempPath()) ('lotus-sync-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path "$fixture/skills/recording/scripts","$fixture/skills/gstack-ship","$fixture/skills/unrelated" -Force | Out-Null
'old recording' | Set-Content "$fixture/skills/recording/SKILL.md"
'runtime sentinel' | Set-Content "$fixture/skills/recording/scripts/local-only.ps1"
'private runtime sentinel' | Set-Content "$fixture/skills/recording/runtime.local.json"
'old ship' | Set-Content "$fixture/skills/gstack-ship/SKILL.md"
New-Item -ItemType Directory -Path "$fixture/skills/gstack-ship/agents" | Out-Null
"interface:`n  display_name: old`n  short_description: old`n  default_prompt: old`n  icon_small: ./custom.png`npolicy:`n  allow_implicit_invocation: false" | Set-Content "$fixture/skills/gstack-ship/agents/openai.yaml"
'unrelated' | Set-Content "$fixture/skills/unrelated/SKILL.md"
'config sentinel' | Set-Content "$fixture/config.toml"
$protected=@('config.toml','skills/unrelated/SKILL.md','skills/recording/runtime.local.json','skills/recording/scripts/local-only.ps1')
$hashes=@{}
foreach($p in $protected){$hashes[$p]=(Get-FileHash "$fixture/$p").Hash}
& "$PSScriptRoot/sync-codex-skills.ps1" -CodexRoot $fixture
foreach($p in $protected){if((Get-FileHash "$fixture/$p").Hash -ne $hashes[$p]){throw "Protected file changed: $p"}}
foreach($pair in @(@('skills/recording/SKILL.md','skills/recording/SKILL.md'),@('adapters/gstack/gstack-ship/SKILL.md','skills/gstack-ship/SKILL.md'))){
 if((Get-FileHash "$repo/$($pair[0])").Hash -ne (Get-FileHash "$fixture/$($pair[1])").Hash){throw 'Sync mismatch'}
}
$backups=@(Get-ChildItem "$fixture/backups" -Directory)
$ui=Get-Content "$fixture/skills/gstack-ship/agents/openai.yaml" -Raw
if($ui -notmatch 'allow_implicit_invocation: false' -or $ui -notmatch 'icon_small: ./custom.png'){throw 'UI policy or icon lost'}
if($backups.Count -ne 1){throw 'Expected one backup'}
$manifest=@(Get-Content "$($backups[0].FullName)/manifest.json" -Raw | ConvertFrom-Json)
foreach($item in $manifest | Where-Object existed){if((Get-FileHash (Join-Path $backups[0].FullName $item.relativePath)).Hash -ne $item.beforeHash){throw 'Backup invalid'}}
& "$PSScriptRoot/sync-codex-skills.ps1" -CodexRoot $fixture
if(@(Get-ChildItem "$fixture/backups" -Directory).Count -ne 1){throw 'Second sync not idempotent'}
if(Test-Path "$fixture/skills/executive-sow-pricing"){throw 'Unrequested skill installed'}
Write-Output "Skill sync tests passed; fixture retained at $fixture"
