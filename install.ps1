param (
    [switch]$Global,
    [string]$Project,
    [switch]$Force,
    [ValidateSet("core", "design", "review", "deploy", "full")]
    [string]$GstackProfile = "core"
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$CoreAgents = Join-Path $RepoRoot "core\AGENTS.md"
$SkillsDir = Join-Path $RepoRoot "skills"
$ManagedGstackInstaller = Join-Path $RepoRoot "scripts\install-managed-gstack.sh"

# Skills that rely on "staying in current conversation" and are incompatible
# with Codex App's architecture (each skill invocation = new task context).
# These skills work via AGENTS.md rule-level recognition instead.
$CodexExcludedSkills = @("btw", "loop")
$ManagedOfficialSkills = @("gstack")
$HiddenTopLevelSkills = @(
    "brandkit",
    "gstack-plan-ceo-review",
    "gstack-plan-design-review",
    "gstack-plan-eng-review",
    "imagegen",
    "openai-docs",
    "plugin-creator",
    "skill-creator",
    "skill-installer"
)
$HiddenClaudeGstackAliases = @(
    "plan-ceo-review",
    "plan-design-review",
    "plan-eng-review"
)
$ObsoleteLotusSkills = @(
    "auto-build",
    "conversion-copywriter",
    "debugging-strategies",
    "design-taste-frontend-v1",
    "gpt-taste",
    "gsap-core",
    "gsap-frameworks",
    "gsap-performance",
    "gsap-plugins",
    "gsap-react",
    "gsap-scrolltrigger",
    "gsap-timeline",
    "gsap-utils",
    "high-end-visual-design",
    "image-to-code",
    "imagegen-frontend-mobile",
    "imagegen-frontend-web",
    "industrial-brutalist-ui",
    "ios-ui-centering-fix",
    "minimalist-ui",
    "mobile-agent-bridge",
    "powerup",
    "redesign-existing-projects",
    "stitch-design-taste",
    "full-output-enforcement",
    "web-to-design-md"
)
$OfficialGstackInstalled = $false
$GstackBootstrapInstalled = $false
$CoreExposedGstackSkills = @(
    "gstack",
    "gstack-office-hours",
    "gstack-investigate",
    "gstack-browse",
    "gstack-ship"
)

function Backup-IfExists {
    param ([string]$FilePath)
    if (Test-Path $FilePath) {
        $BackupPath = "$FilePath.bak"
        Copy-Item $FilePath $BackupPath -Force
        Write-Host "    Backed up existing: $FilePath -> $BackupPath" -ForegroundColor Yellow
    }
}

function Ensure-DirectoryPath {
    param ([string]$Path)

    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -ne $item -and ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        $targets = @(@($item.Target) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
        if ($targets.Count -ne 1) {
            throw "Directory path is a broken reparse point with no single repairable target: $Path"
        }

        $target = [Environment]::ExpandEnvironmentVariables([string]$targets[0])
        if (-not [System.IO.Path]::IsPathRooted($target)) {
            $target = Join-Path ([System.IO.Path]::GetDirectoryName($Path)) $target
        }

        if (Test-Path -LiteralPath $target -PathType Container) {
            return
        }

        New-Item -ItemType Directory -Path $target -Force | Out-Null
        if (Test-Path -LiteralPath $Path -PathType Container) {
            Write-Host "    Repaired broken directory junction target: $Path -> $target" -ForegroundColor Yellow
            return
        }

        throw "Failed to repair broken directory junction: $Path -> $target"
    }

    if (Test-Path -LiteralPath $Path -PathType Container) {
        return
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "Failed to create directory: $Path"
    }
}

function Test-AnyPath {
    param ([string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $true
        }
    }
    return $false
}

function Add-MissingSkillIfAbsent {
    param (
        [System.Collections.Generic.List[string]]$Missing,
        [string]$Label,
        [string[]]$Candidates
    )

    if (-not (Test-AnyPath $Candidates)) {
        $Missing.Add($Label)
    }
}

function Assert-ManagedGstackInstall {
    param ([switch]$AllowArchiveInstall)

    $missing = New-Object System.Collections.Generic.List[string]

    $gstackRepoDir = Join-Path $HOME ".gstack\repos\gstack"
    $hasGitCheckout = Test-Path (Join-Path $gstackRepoDir ".git")
    $hasArchiveCheckout = (Test-Path (Join-Path $gstackRepoDir "VERSION")) -and (Test-Path (Join-Path $gstackRepoDir "package.json"))

    if (-not $hasGitCheckout -and -not ($AllowArchiveInstall -and $hasArchiveCheckout)) {
        $missing.Add("official gstack repo (~/.gstack/repos/gstack)")
    }

    Add-MissingSkillIfAbsent $missing "Claude runtime (~/.claude/skills/gstack)" @(
        (Join-Path $HOME ".claude\skills\gstack\SKILL.md"),
        (Join-Path $HOME ".claude\skills\gstack")
    )
    Add-MissingSkillIfAbsent $missing "Claude office-hours skill (~/.claude/skills/gstack-office-hours or office-hours)" @(
        (Join-Path $HOME ".claude\skills\gstack-office-hours\SKILL.md"),
        (Join-Path $HOME ".claude\skills\office-hours\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Claude investigate skill (~/.claude/skills/gstack-investigate or investigate)" @(
        (Join-Path $HOME ".claude\skills\gstack-investigate\SKILL.md"),
        (Join-Path $HOME ".claude\skills\investigate\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Claude browse skill (~/.claude/skills/gstack-browse or browse)" @(
        (Join-Path $HOME ".claude\skills\gstack-browse\SKILL.md"),
        (Join-Path $HOME ".claude\skills\browse\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Claude ship skill (~/.claude/skills/gstack-ship or ship)" @(
        (Join-Path $HOME ".claude\skills\gstack-ship\SKILL.md"),
        (Join-Path $HOME ".claude\skills\ship\SKILL.md")
    )

    Add-MissingSkillIfAbsent $missing "Codex gstack runtime (~/.codex/skills/gstack/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex office-hours skill (~/.codex/skills/gstack-office-hours/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-office-hours\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex investigate skill (~/.codex/skills/gstack-investigate/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-investigate\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex browse skill (~/.codex/skills/gstack-browse/SKILL.md or gstack/browse/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-browse\SKILL.md"),
        (Join-Path $HOME ".codex\skills\gstack\browse\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex ship skill (~/.codex/skills/gstack-ship/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-ship\SKILL.md")
    )

    if ($missing.Count -gt 0) {
        $message = @(
            "Official gstack install is incomplete. Missing:"
            ($missing | ForEach-Object { "  - $_" })
            "Lotus global rules live in AGENTS/CLAUDE files, but slash skills must exist in each host's global skills directory."
        ) -join "`n"
        throw $message
    }
}

function Confirm-GlobalRuleOverwrite {
    param ([string[]]$Targets)

    $existing = @($Targets | Where-Object { Test-Path $_ })
    if ($existing.Count -eq 0) {
        return
    }

    if ($Force -or $env:LOTUS_ASSUME_YES -eq "1") {
        Write-Host "  Overwrite confirmation skipped (-Force / LOTUS_ASSUME_YES=1)." -ForegroundColor Yellow
        return
    }

    if (-not [Environment]::UserInteractive) {
        throw "Existing global rule/config files would be overwritten, but no interactive confirmation is available. Re-run with -Force or LOTUS_ASSUME_YES=1."
    }

    Write-Host "Existing global rule/config files detected. Lotus will back them up to .bak and then overwrite them:" -ForegroundColor Yellow
    $existing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    $answer = Read-Host "Continue and overwrite these global files? [y/N]"
    if ($answer -notmatch '^(?i:y(?:es)?)$') {
        throw "Cancelled. No global rules were overwritten."
    }
}

function Test-SkillExcluded {
    param (
        [string]$SkillName,
        [string[]]$ExcludedSkills = @()
    )

    return ($ExcludedSkills -contains $SkillName)
}

function Move-SkillToLotusHidden {
    param (
        [string]$SourcePath,
        [string]$HostGroup
    )

    if (-not (Test-Path $SourcePath)) {
        return
    }

    $hiddenDir = Join-Path $HOME ".codex\hidden-skills\lotus\$HostGroup"
    New-Item -ItemType Directory -Path $hiddenDir -Force | Out-Null
    $destination = Join-Path $hiddenDir ([System.IO.Path]::GetFileName($SourcePath))
    if (Test-Path $destination) {
        Remove-Item $destination -Recurse -Force
    }
    Move-Item $SourcePath $destination -Force
    Write-Host "    Hidden top-level skill: $SourcePath -> $destination"
}

function Hide-TopLevelSkills {
    param (
        [string]$TargetDir,
        [string]$HostGroup,
        [switch]$IncludeCodexSystem
    )

    foreach ($skillName in $HiddenTopLevelSkills) {
        Move-SkillToLotusHidden -SourcePath (Join-Path $TargetDir $skillName) -HostGroup $HostGroup
        Move-SkillToLotusHidden -SourcePath (Join-Path $TargetDir "$skillName.md") -HostGroup $HostGroup
    }

    if ($HostGroup -eq "claude") {
        foreach ($skillName in $HiddenClaudeGstackAliases) {
            Move-SkillToLotusHidden -SourcePath (Join-Path $TargetDir $skillName) -HostGroup $HostGroup
            Move-SkillToLotusHidden -SourcePath (Join-Path $TargetDir "$skillName.md") -HostGroup $HostGroup
        }
    }

    if ($IncludeCodexSystem) {
        $systemSkills = Join-Path $TargetDir ".system"
        foreach ($skillName in $HiddenTopLevelSkills) {
            Move-SkillToLotusHidden -SourcePath (Join-Path $systemSkills $skillName) -HostGroup "codex-system"
        }
    }
}

function Write-AnySearchRuntimeConf {
    param ([string]$SkillDir)

    if ([System.IO.Path]::GetFileName($SkillDir) -ne "anysearch") {
        return
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        $runtime = "Python"
        $command = "python `"$SkillDir\scripts\anysearch_cli.py`""
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $runtime = "Python"
        $command = "python3 `"$SkillDir\scripts\anysearch_cli.py`""
    } elseif (Get-Command node -ErrorAction SilentlyContinue) {
        $runtime = "Node.js"
        $command = "node `"$SkillDir\scripts\anysearch_cli.js`""
    } else {
        $runtime = "PowerShell"
        $command = "powershell -ExecutionPolicy Bypass -File `"$SkillDir\scripts\anysearch_cli.ps1`""
    }

    $content = "Runtime: $runtime`nCommand: $command`n"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $SkillDir "runtime.conf"), $content, $utf8NoBom)
}

function Copy-LotusSkillPackages {
    param (
        [string]$TargetDir,
        [string[]]$ExcludedSkills = @()
    )

    Get-ChildItem $SkillsDir -Directory | ForEach-Object {
        $skillName = $_.Name
        if ((Test-SkillExcluded -SkillName $skillName -ExcludedSkills $ExcludedSkills) -or
            -not (Test-Path (Join-Path $_.FullName "SKILL.md"))) {
            return
        }

        $destination = Join-Path $TargetDir $skillName
        $localRuntime = Join-Path $destination "runtime.local.json"
        $savedLocalRuntime = $null
        if (Test-Path $localRuntime) {
            $savedLocalRuntime = Get-Content $localRuntime -Raw -Encoding UTF8
        }

        if (Test-Path $destination) {
            Remove-Item $destination -Recurse -Force
        }

        Copy-Item $_.FullName $destination -Recurse -Force
        Remove-Item (Join-Path $destination ".env") -Force -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $destination "runtime.conf") -Force -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $destination "runtime.local.json") -Force -ErrorAction SilentlyContinue
        if ($null -ne $savedLocalRuntime) {
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($localRuntime, $savedLocalRuntime, $utf8NoBom)
        }
        Write-AnySearchRuntimeConf -SkillDir $destination
        Write-Host "    Copied skill package: $skillName"
    }
}

function Remove-ObsoleteLotusSkills {
    param ([string]$TargetDir)

    if (-not (Test-Path $TargetDir)) {
        return
    }

    foreach ($skillName in $ObsoleteLotusSkills) {
        $staleDir = Join-Path $TargetDir $skillName
        $staleFile = Join-Path $TargetDir "$skillName.md"

        if (Test-Path $staleDir) {
            Remove-Item $staleDir -Recurse -Force
            Write-Host "    Removed merged skill: $skillName"
        }
        if (Test-Path $staleFile) {
            Remove-Item $staleFile -Force
            Write-Host "    Removed merged skill file: $skillName.md"
        }
    }
}

function Copy-LotusSkills {
    param (
        [string]$TargetDir,
        [string[]]$ExcludedSkills = @()
    )

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

    Remove-ObsoleteLotusSkills -TargetDir $TargetDir

    Get-ChildItem (Join-Path $SkillsDir "*.md") | ForEach-Object {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        if (-not (Test-SkillExcluded -SkillName $baseName -ExcludedSkills $ExcludedSkills)) {
            Remove-Item (Join-Path $TargetDir "$baseName.md") -Force -ErrorAction SilentlyContinue
            Convert-ToCodexSkill -SourceFile $_.FullName -TargetDir $TargetDir
        }
    }

    Copy-LotusSkillPackages -TargetDir $TargetDir -ExcludedSkills $ExcludedSkills
}

function Convert-ToCodexSkill {
    param (
        [string]$SourceFile,
        [string]$TargetDir
    )

    $content = Get-Content $SourceFile -Raw -Encoding UTF8

    $skillName = ""
    $description = ""
    $frontmatter = ""
    if ($content -match '(?s)^---\r?\n(.*?)\r?\n---') {
        $frontmatter = $Matches[1]
        if ($frontmatter -match 'name:\s*(.+)') {
            $skillName = $Matches[1].Trim()
        }
        if ($frontmatter -match 'description:\s*(.+)') {
            $description = $Matches[1].Trim()
        }
    }

    if (-not $skillName) {
        $skillName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)
    }
    if (-not $description) {
        $description = "Lotus skill: $skillName"
    }

    $skillDir = Join-Path $TargetDir $skillName
    if (-not (Test-Path $skillDir)) {
        New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
    }

    if ($frontmatter -match '(?m)^allowed-tools\s*:') {
        Copy-Item $SourceFile (Join-Path $skillDir "SKILL.md") -Force
        return
    }

    if ($skillName -eq "image-2") {
        $body = $content -replace '(?s)^---\r?\n.*?\r?\n---\r?\n?', ''
        $codexContent = @"
---
name: $skillName
description: $description
---

$body
"@
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText((Join-Path $skillDir "SKILL.md"), $codexContent, $utf8NoBom)
        return
    }

    $allowedTools = switch ($skillName) {
        "auto-build" { "Bash, Read" }
        "btw" { "Read, AskUserQuestion" }
        "feynman" { "Read, AskUserQuestion" }
        "polanyi-tacit" { "Read, AskUserQuestion" }
        "powerup" { "Read, AskUserQuestion" }
        "insights" { "Read, Bash, Grep, Glob" }
        "ai-progress-workspace" { "Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, WebSearch" }
        "loop" { "Bash, Read, AskUserQuestion" }
        "agent-training-loop" { "Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion" }
        "baseline-packager" { "Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion" }
        "mini-investigate" { "Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion" }
        "conversion-copywriter" { "Read, AskUserQuestion" }
        "subagent" { "Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion" }
        "web-to-design-md" { "Read, Write, Edit, Grep, Glob, AskUserQuestion, WebSearch" }
        "taste-skill" { "Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion" }
        "gstack" { "Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion" }
        default { "Read, AskUserQuestion" }
    }

    $body = $content -replace '(?s)^---\r?\n.*?\r?\n---\r?\n?', ''

    $codexFrontmatter = @"
---
name: $skillName
description: |
  $description
allowed-tools:
$(($allowedTools -split ', ' | ForEach-Object { "  - $_" }) -join "`n")
---
"@

    $codexContent = "$codexFrontmatter`n$body"

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $skillDir "SKILL.md"), $codexContent, $utf8NoBom)
}

function Get-ClaudeGstackSkillName {
    param ([string]$SkillName)

    if ($SkillName -eq "gstack") {
        return "gstack"
    }

    return ($SkillName -replace '^gstack-', '')
}

function Test-ShouldSyncGstackSkillForCodex {
    param ([string]$SkillName)

    return @(
        "gstack-browse",
        "gstack-open-gstack-browser",
        "gstack-setup-browser-cookies"
    ) -notcontains $SkillName
}

function Copy-DirectoryClean {
    param (
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($Destination)) -Force | Out-Null
    Copy-Item $Source $Destination -Recurse -Force
}

function Sync-GstackSkillsFromGeneratedDocs {
    param (
        [string]$GstackDir,
        [string]$ClaudeSkills,
        [string]$CodexSkills
    )

    $agentsSkills = Join-Path $GstackDir ".agents\skills"
    if (-not (Test-Path $agentsSkills)) {
        throw "Generated gstack skills not found at $agentsSkills."
    }

    New-Item -ItemType Directory -Path $ClaudeSkills -Force | Out-Null
    New-Item -ItemType Directory -Path $CodexSkills -Force | Out-Null

    foreach ($skillName in $CoreExposedGstackSkills) {
        $sourceSkillDir = Join-Path $agentsSkills $skillName
        $sourceSkillFile = Join-Path $sourceSkillDir "SKILL.md"
        if (-not (Test-Path $sourceSkillFile)) {
            throw "Expected generated gstack skill is missing: $sourceSkillFile"
        }

        if (Test-ShouldSyncGstackSkillForCodex -SkillName $skillName) {
            $codexTarget = Join-Path $CodexSkills $skillName
            Copy-DirectoryClean -Source $sourceSkillDir -Destination $codexTarget
        }

        $claudeSkillName = Get-ClaudeGstackSkillName $skillName
        $claudeTarget = Join-Path $ClaudeSkills $claudeSkillName
        New-Item -ItemType Directory -Path $claudeTarget -Force | Out-Null
        Copy-Item $sourceSkillFile (Join-Path $claudeTarget "SKILL.md") -Force
    }

    foreach ($duplicateCodexBrowserSkill in @("gstack-browse", "gstack-open-gstack-browser", "gstack-setup-browser-cookies")) {
        $duplicateCodexBrowserSkillDir = Join-Path $CodexSkills $duplicateCodexBrowserSkill
        if (Test-Path $duplicateCodexBrowserSkillDir) {
            Remove-Item $duplicateCodexBrowserSkillDir -Recurse -Force
        }
    }

    Write-Host "  Synced official gstack top-level skills without Git/Bash"
}

function New-GstackBootstrapSkillContent {
    param (
        [string]$SkillName,
        [string]$DisplayName
    )

    $description = switch ($SkillName) {
        "gstack" { "需 gstack 流程时打开总入口" }
        "gstack-office-hours" { "讨论方案时快速找取舍" }
        "gstack-investigate" { "需调研时收集线索给结论" }
        "gstack-plan-eng-review" { "审工程计划时查实现风险" }
        "gstack-plan-ceo-review" { "审产品计划时查目标取舍" }
        "gstack-plan-design-review" { "审设计计划时查体验方向" }
        "gstack-design-review" { "审界面时查视觉交互问题" }
        "gstack-browse" { "验页面时浏览器检查效果" }
        "gstack-qa" { "验质量时查测试回归风险" }
        "gstack-review" { "审代码时查Bug和测试缺口" }
        "gstack-ship" { "发布前检查构建验证风险" }
        default { "需 gstack $DisplayName 时打开入口" }
    }

    return @"
---
name: $SkillName
description: |
  $description
allowed-tools:
  - Read
  - AskUserQuestion
---

# 官方 gstack bootstrap

这是一个真实的顶层 skill 入口。Lotus 在当前机器缺少 Git 或 Git Bash 时安装它，避免 `/gstack-*` 菜单入口消失。

完整的官方 gstack runtime 还没有安装。要启用完整工作流：

1. 安装 Git for Windows: https://git-scm.com/download/win
2. 打开新的 PowerShell。
3. 重新运行：

```powershell
install.ps1 -Global
```

如果你不在 Lotus 仓库目录内运行，请使用 `install.ps1` 的完整路径。
"@
}

function Test-IsGstackBootstrapSkillFile {
    param ([string]$SkillFile)

    if (-not (Test-Path $SkillFile)) {
        return $false
    }

    $content = Get-Content $SkillFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    return ($content -like "*Bootstrap entry for official gstack*") -or
        ($content -like "*官方 gstack bootstrap*")
}

function Write-GstackBootstrapSkillIfNeeded {
    param (
        [string]$TargetDir,
        [string]$SkillName,
        [string]$DisplayName,
        [System.Text.UTF8Encoding]$Encoding,
        [switch]$OnlyMissing
    )

    $skillFile = Join-Path $TargetDir "SKILL.md"
    if (Test-Path $skillFile) {
        if (-not (Test-IsGstackBootstrapSkillFile -SkillFile $skillFile)) {
            return $false
        }
        if ($OnlyMissing) {
            return $false
        }
    }

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    [System.IO.File]::WriteAllText(
        $skillFile,
        (New-GstackBootstrapSkillContent -SkillName $SkillName -DisplayName $DisplayName),
        $Encoding
    )

    return $true
}

function Install-GstackBootstrapSkills {
    param (
        [string]$ClaudeSkills,
        [string]$CodexSkills,
        [switch]$OnlyMissing
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    New-Item -ItemType Directory -Path $ClaudeSkills, $CodexSkills -Force | Out-Null
    $written = 0
    $preserved = 0

    foreach ($skillName in $CoreExposedGstackSkills) {
        $displayName = if ($skillName -eq "gstack") { "runtime" } else { ($skillName -replace '^gstack-', '') }

        $codexTarget = Join-Path $CodexSkills $skillName
        if (Write-GstackBootstrapSkillIfNeeded -TargetDir $codexTarget -SkillName $skillName -DisplayName $displayName -Encoding $utf8NoBom -OnlyMissing:$OnlyMissing) {
            $written++
        } else {
            $preserved++
        }

        $claudeSkillName = Get-ClaudeGstackSkillName $skillName
        $claudeTarget = Join-Path $ClaudeSkills $claudeSkillName
        if (Write-GstackBootstrapSkillIfNeeded -TargetDir $claudeTarget -SkillName $claudeSkillName -DisplayName $displayName -Encoding $utf8NoBom -OnlyMissing:$OnlyMissing) {
            $written++
        } else {
            $preserved++
        }
    }

    Write-Host "  Installed bootstrap entries for the curated official gstack top-level skills ($written written, $preserved preserved)"
}

if ($Global) {
    Write-Host "Installing Global Rules & Skills..." -ForegroundColor Cyan

    $ClaudeRuleFile = Join-Path $HOME ".claude\CLAUDE.md"
    $CodexRuleFile = Join-Path $HOME ".codex\AGENTS.md"

    Confirm-GlobalRuleOverwrite @(
        $ClaudeRuleFile,
        $CodexRuleFile
    )

    $ClaudeDir = Join-Path $HOME ".claude"
    Ensure-DirectoryPath $ClaudeDir
    Backup-IfExists $ClaudeRuleFile
    Copy-Item $CoreAgents $ClaudeRuleFile -Force

    $ClaudeSkills = Join-Path $ClaudeDir "skills"
    Ensure-DirectoryPath $ClaudeSkills
    Copy-LotusSkills -TargetDir $ClaudeSkills -ExcludedSkills ($ManagedOfficialSkills + $HiddenTopLevelSkills)
    Hide-TopLevelSkills -TargetDir $ClaudeSkills -HostGroup "claude"
    Write-Host "  Claude Code configured"

    $CodexDir = Join-Path $HOME ".codex"
    Ensure-DirectoryPath $CodexDir
    Backup-IfExists $CodexRuleFile
    Copy-Item $CoreAgents $CodexRuleFile -Force

    $CodexSkills = Join-Path $CodexDir "skills"
    Ensure-DirectoryPath $CodexSkills

    Remove-ObsoleteLotusSkills -TargetDir $CodexSkills

    foreach ($excluded in $CodexExcludedSkills) {
        $excludedDir = Join-Path $CodexSkills $excluded
        if (Test-Path $excludedDir) {
            Remove-Item $excludedDir -Recurse -Force
            Write-Host "    Removed incompatible skill: $excluded"
        }
    }

    Get-ChildItem (Join-Path $SkillsDir "*.md") | ForEach-Object {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        if (($CodexExcludedSkills + $ManagedOfficialSkills + $HiddenTopLevelSkills) -contains $baseName) {
            Write-Host "    Skipped (managed elsewhere or in-context only): $baseName"
        } else {
            Convert-ToCodexSkill -SourceFile $_.FullName -TargetDir $CodexSkills
            Write-Host "    Converted skill: $baseName"
        }
    }
    Copy-LotusSkillPackages -TargetDir $CodexSkills -ExcludedSkills ($CodexExcludedSkills + $ManagedOfficialSkills + $HiddenTopLevelSkills)
    Write-Host "  Codex CLI configured (rules + Lotus-only compatible skills)"

    Write-Host "  Installing official gstack upstream..."
    $gitBash = if ($env:ProgramFiles) { Join-Path $env:ProgramFiles "Git\bin\bash.exe" } else { $null }
    if ([string]::IsNullOrWhiteSpace($gitBash) -or -not (Test-Path -LiteralPath $gitBash)) {
        Write-Warning "Git Bash was not found. Installing bootstrap entries for the official gstack top-level skills."
        Install-GstackBootstrapSkills -ClaudeSkills $ClaudeSkills -CodexSkills $CodexSkills
        $GstackBootstrapInstalled = $true
    } else {
        $BashManagedGstackInstaller = $ManagedGstackInstaller -replace '\\', '/'

        $previousGstackProfile = $env:LOTUS_GSTACK_PROFILE
        $env:LOTUS_GSTACK_PROFILE = $GstackProfile
        try {
            & $gitBash $BashManagedGstackInstaller
            if ($LASTEXITCODE -ne 0) {
                throw "Official gstack installation failed. Lotus rules were written, but slash skills were not fully installed."
            }

            Assert-ManagedGstackInstall
            $OfficialGstackInstalled = $true
            Write-Host "  Official gstack configured for Claude/Codex"
        }
        catch {
            Write-Warning $_
            Write-Warning "Installing bootstrap entries so the default gstack slash skills remain visible."
            Install-GstackBootstrapSkills -ClaudeSkills $ClaudeSkills -CodexSkills $CodexSkills -OnlyMissing
            $GstackBootstrapInstalled = $true
        }
        finally {
            if ($null -ne $previousGstackProfile) {
                $env:LOTUS_GSTACK_PROFILE = $previousGstackProfile
            } else {
                Remove-Item Env:LOTUS_GSTACK_PROFILE -ErrorAction SilentlyContinue
            }
        }
    }

    Hide-TopLevelSkills -TargetDir $ClaudeSkills -HostGroup "claude"
    Hide-TopLevelSkills -TargetDir $CodexSkills -HostGroup "codex" -IncludeCodexSystem

    Write-Host ""
    Write-Host "Global installation completed successfully!" -ForegroundColor Green
    Write-Host "If any existing configs were overwritten, .bak backups have been created." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Codex note:" -ForegroundColor Cyan
    Write-Host "  - Global rules were installed to $CodexDir\AGENTS.md and are auto-loaded in local repos."
    Write-Host "  - `-Global` does not create `AGENTS.md` inside each project folder."
    Write-Host "  - Run `.\install.ps1 -Project nextjs|vite|html` inside a project when you want local `AGENTS.md` and `.agents/rules/` files."
    if ($OfficialGstackInstalled) {
        Write-Host "  - Official gstack is managed at $HOME\.gstack\repos\gstack and kept auto-updatable."
    } elseif ($GstackBootstrapInstalled) {
        Write-Host "  - The curated official gstack top-level skill entries were installed as bootstrap skills."
        Write-Host "  - Install Git for Windows, then re-run install.ps1 -Global to install the full official gstack runtime."
    }
    Write-Host "  - Official gstack top-level exposure profile: $GstackProfile"
    Write-Host "  - Lotus keeps low-frequency skills out of the top-level menu under ~/.codex/hidden-skills/lotus."
    Write-Host "  - Hidden official gstack skills stay in ~/.gstack/repos/gstack/.agents/skills and can still be routed by AGENTS.md."
    Write-Host "  - Slash skills live in the managed global skills folders ~/.claude/skills and ~/.codex/skills."
}

if ($Project) {
    Write-Host "Installing Project Template: $Project..." -ForegroundColor Cyan
    $TemplateDir = Join-Path $RepoRoot "templates\$Project"

    if (-not (Test-Path $TemplateDir)) {
        Write-Error "Template '$Project' not found in templates directory."
        exit 1
    }

    Copy-Item (Join-Path $TemplateDir "*") (Get-Location) -Recurse -Force

    $ConventionsFile = Join-Path $RepoRoot "core\CONVENTIONS.md"
    if (Test-Path $ConventionsFile) {
        Copy-Item $ConventionsFile (Get-Location) -Force
    }

    Write-Host "Project template '$Project' applied to current directory." -ForegroundColor Green
    Write-Host "Remember to adjust the design system and tech stack files in `.agents/rules/`." -ForegroundColor Yellow
}

if (-not $Global -and -not $Project) {
    Write-Host "Lotus Installer" -ForegroundColor Cyan
    Write-Host "--------------------"
    Write-Host "Usage:"
    Write-Host "  .\install.ps1 -Global                                  (Install global rules to the managed Claude/Codex folders)"
    Write-Host "  .\install.ps1 -Global -GstackProfile core              (Default curated official gstack top-level set)"
    Write-Host "  .\install.ps1 -Global -GstackProfile full              (Expose the full official gstack top-level set)"
    Write-Host "  .\install.ps1 -Global -Force                           (Overwrite existing global configs without prompting)"
    Write-Host "  .\install.ps1 -Project <name>                          (Apply template to current directory)"
    Write-Host ""
    Write-Host "Available gstack profiles: core, design, review, deploy, full"
    Write-Host "Available templates: nextjs, vite, html"
}
