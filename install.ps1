param (
    [switch]$Global,
    [string]$Project,
    [switch]$Force
)

$RepoRoot = $PSScriptRoot
$CoreAgents = Join-Path $RepoRoot "core\AGENTS.md"
$SkillsDir = Join-Path $RepoRoot "skills"
$ManagedGstackInstaller = Join-Path $RepoRoot "scripts\install-managed-gstack.sh"

# Skills that rely on "staying in current conversation" and are incompatible
# with Codex App's architecture (each skill invocation = new task context).
# These skills work via AGENTS.md rule-level recognition instead.
$CodexExcludedSkills = @("btw", "loop")
$ManagedOfficialSkills = @("gstack")

function Backup-IfExists {
    param ([string]$FilePath)
    if (Test-Path $FilePath) {
        $BackupPath = "$FilePath.bak"
        Copy-Item $FilePath $BackupPath -Force
        Write-Host "    Backed up existing: $FilePath -> $BackupPath" -ForegroundColor Yellow
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
    $missing = New-Object System.Collections.Generic.List[string]

    if (-not (Test-Path (Join-Path $HOME ".gstack\repos\gstack\.git"))) {
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
    Add-MissingSkillIfAbsent $missing "Claude plan-eng-review skill (~/.claude/skills/gstack-plan-eng-review or plan-eng-review)" @(
        (Join-Path $HOME ".claude\skills\gstack-plan-eng-review\SKILL.md"),
        (Join-Path $HOME ".claude\skills\plan-eng-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Claude qa skill (~/.claude/skills/gstack-qa or qa)" @(
        (Join-Path $HOME ".claude\skills\gstack-qa\SKILL.md"),
        (Join-Path $HOME ".claude\skills\qa\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Claude review skill (~/.claude/skills/gstack-review or review)" @(
        (Join-Path $HOME ".claude\skills\gstack-review\SKILL.md"),
        (Join-Path $HOME ".claude\skills\review\SKILL.md")
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
    Add-MissingSkillIfAbsent $missing "Codex plan-eng-review skill (~/.codex/skills/gstack-plan-eng-review/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-plan-eng-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex qa skill (~/.codex/skills/gstack-qa/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-qa\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex review skill (~/.codex/skills/gstack-review/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Codex ship skill (~/.codex/skills/gstack-ship/SKILL.md)" @(
        (Join-Path $HOME ".codex\skills\gstack-ship\SKILL.md")
    )

    Add-MissingSkillIfAbsent $missing "OpenCode gstack runtime (~/.config/opencode/skills/gstack/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode office-hours skill (~/.config/opencode/skills/gstack-office-hours/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-office-hours\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode investigate skill (~/.config/opencode/skills/gstack-investigate/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-investigate\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode plan-eng-review skill (~/.config/opencode/skills/gstack-plan-eng-review/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-plan-eng-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode qa skill (~/.config/opencode/skills/gstack-qa/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-qa\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode review skill (~/.config/opencode/skills/gstack-review/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "OpenCode ship skill (~/.config/opencode/skills/gstack-ship/SKILL.md)" @(
        (Join-Path $HOME ".config\opencode\skills\gstack-ship\SKILL.md")
    )

    Add-MissingSkillIfAbsent $missing "Cursor gstack runtime (~/.cursor/skills/gstack/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor office-hours skill (~/.cursor/skills/gstack-office-hours/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-office-hours\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor investigate skill (~/.cursor/skills/gstack-investigate/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-investigate\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor plan-eng-review skill (~/.cursor/skills/gstack-plan-eng-review/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-plan-eng-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor qa skill (~/.cursor/skills/gstack-qa/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-qa\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor review skill (~/.cursor/skills/gstack-review/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-review\SKILL.md")
    )
    Add-MissingSkillIfAbsent $missing "Cursor ship skill (~/.cursor/skills/gstack-ship/SKILL.md)" @(
        (Join-Path $HOME ".cursor\skills\gstack-ship\SKILL.md")
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

function Copy-LotusSkills {
    param (
        [string]$TargetDir,
        [string[]]$ExcludedSkills = @()
    )

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

    Get-ChildItem (Join-Path $SkillsDir "*.md") | ForEach-Object {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        if ($ExcludedSkills -notcontains $baseName) {
            Copy-Item $_.FullName $TargetDir -Force
        }
    }
}

function Convert-ToCodexSkill {
    param (
        [string]$SourceFile,
        [string]$TargetDir
    )

    $content = Get-Content $SourceFile -Raw -Encoding UTF8

    $skillName = ""
    $description = ""
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

    $allowedTools = switch ($skillName) {
        "auto-build" { "Bash, Read" }
        "btw" { "Read, AskUserQuestion" }
        "feynman" { "Read, AskUserQuestion" }
        "polanyi-tacit" { "Read, AskUserQuestion" }
        "powerup" { "Read, AskUserQuestion" }
        "insights" { "Read, Bash, Grep, Glob" }
        "loop" { "Bash, Read, AskUserQuestion" }
        "subagent" { "Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion" }
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

    $skillDir = Join-Path $TargetDir $skillName
    if (-not (Test-Path $skillDir)) {
        New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $skillDir "SKILL.md"), $codexContent, $utf8NoBom)
}

if ($Global) {
    Write-Host "Installing Global Rules & Skills..." -ForegroundColor Cyan

    $GeminiRuleFile = Join-Path $HOME ".gemini\GEMINI.md"
    $ClaudeRuleFile = Join-Path $HOME ".claude\CLAUDE.md"
    $OpenCodeRuleFile = Join-Path $HOME ".config\opencode\AGENTS.md"
    $WindsurfRuleFile = Join-Path $HOME ".windsurf\rules\global.md"
    $CodexRuleFile = Join-Path $HOME ".codex\AGENTS.md"
    $CursorRuleFile = Join-Path $HOME ".cursor\rules\lotus.mdc"
    $AiderFile = Join-Path $HOME ".aider.conf.yml"

    Confirm-GlobalRuleOverwrite @(
        $GeminiRuleFile,
        $ClaudeRuleFile,
        $OpenCodeRuleFile,
        $WindsurfRuleFile,
        $CodexRuleFile,
        $CursorRuleFile,
        $AiderFile
    )

    $GeminiDir = Join-Path $HOME ".gemini"
    if (-not (Test-Path $GeminiDir)) { New-Item -ItemType Directory -Path $GeminiDir -Force | Out-Null }
    Backup-IfExists $GeminiRuleFile
    Copy-Item $CoreAgents $GeminiRuleFile -Force

    $GeminiSkills = Join-Path $GeminiDir "antigravity\skills"
    if (-not (Test-Path $GeminiSkills)) { New-Item -ItemType Directory -Path $GeminiSkills -Force | Out-Null }
    Copy-LotusSkills -TargetDir $GeminiSkills -ExcludedSkills $ManagedOfficialSkills
    Write-Host "  Antigravity & Gemini CLI configured"

    $ClaudeDir = Join-Path $HOME ".claude"
    if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }
    Backup-IfExists $ClaudeRuleFile
    Copy-Item $CoreAgents $ClaudeRuleFile -Force

    $ClaudeSkills = Join-Path $ClaudeDir "skills"
    if (-not (Test-Path $ClaudeSkills)) { New-Item -ItemType Directory -Path $ClaudeSkills -Force | Out-Null }
    Copy-LotusSkills -TargetDir $ClaudeSkills -ExcludedSkills $ManagedOfficialSkills
    Write-Host "  Claude Code configured"

    $OpenCodeDir = Join-Path $HOME ".config\opencode"
    if (-not (Test-Path $OpenCodeDir)) { New-Item -ItemType Directory -Path $OpenCodeDir -Force | Out-Null }
    Backup-IfExists $OpenCodeRuleFile
    Copy-Item $CoreAgents $OpenCodeRuleFile -Force
    Write-Host "  OpenCode CLI configured"

    $WindsurfDir = Join-Path $HOME ".windsurf\rules"
    if (-not (Test-Path $WindsurfDir)) { New-Item -ItemType Directory -Path $WindsurfDir -Force | Out-Null }
    Backup-IfExists $WindsurfRuleFile
    Copy-Item $CoreAgents $WindsurfRuleFile -Force
    Write-Host "  Windsurf Cascade configured"

    $CodexDir = Join-Path $HOME ".codex"
    if (-not (Test-Path $CodexDir)) { New-Item -ItemType Directory -Path $CodexDir -Force | Out-Null }
    Backup-IfExists $CodexRuleFile
    Copy-Item $CoreAgents $CodexRuleFile -Force

    $CodexSkills = Join-Path $CodexDir "skills"
    if (-not (Test-Path $CodexSkills)) { New-Item -ItemType Directory -Path $CodexSkills -Force | Out-Null }

    foreach ($excluded in ($CodexExcludedSkills + $ManagedOfficialSkills)) {
        $excludedDir = Join-Path $CodexSkills $excluded
        if (Test-Path $excludedDir) {
            Remove-Item $excludedDir -Recurse -Force
            Write-Host "    Removed incompatible skill: $excluded"
        }
    }

    Get-ChildItem (Join-Path $SkillsDir "*.md") | ForEach-Object {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        if (($CodexExcludedSkills + $ManagedOfficialSkills) -contains $baseName) {
            Write-Host "    Skipped (managed elsewhere or in-context only): $baseName"
        } else {
            Convert-ToCodexSkill -SourceFile $_.FullName -TargetDir $CodexSkills
            Write-Host "    Converted skill: $baseName"
        }
    }
    Write-Host "  Codex CLI configured (rules + Lotus-only compatible skills)"

    $CursorDir = Join-Path $HOME ".cursor\rules"
    if (-not (Test-Path $CursorDir)) { New-Item -ItemType Directory -Path $CursorDir -Force | Out-Null }
    Backup-IfExists $CursorRuleFile
    $cursorContent = @"
---
description: Lotus GStack Engineering Protocol - Global rules and workflow standards
globs:
alwaysApply: true
---

$(Get-Content $CoreAgents -Raw -Encoding UTF8)
"@
    $cursorContent | Out-File $CursorRuleFile -Encoding UTF8 -Force
    Write-Host "  Cursor configured"

    Backup-IfExists $AiderFile
    @"
read:
  - CONVENTIONS.md
  - AGENTS.md
"@ | Out-File $AiderFile -Encoding UTF8
    Write-Host "  Aider AI configured"

    Write-Host "  Installing official gstack upstream..."
    if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
        throw "Git Bash is required to install official gstack on Windows. Install Git for Windows or ensure 'bash' is on PATH."
    }

    $BashManagedGstackInstaller = $ManagedGstackInstaller -replace '\\', '/'
    & bash $BashManagedGstackInstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Official gstack installation failed. Lotus rules were written, but slash skills were not fully installed."
    }

    Assert-ManagedGstackInstall
    Write-Host "  Official gstack configured for Claude/Codex/OpenCode/Cursor"

    Write-Host ""
    Write-Host "Global installation completed successfully!" -ForegroundColor Green
    Write-Host "If any existing configs were overwritten, .bak backups have been created." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Codex note:" -ForegroundColor Cyan
    Write-Host "  - Global rules were installed to $CodexDir\AGENTS.md and are auto-loaded in local repos."
    Write-Host "  - `-Global` does not create `AGENTS.md` inside each project folder."
    Write-Host "  - Run `.\install.ps1 -Project nextjs|vite|html` inside a project when you want local `AGENTS.md` and `.agents/rules/` files."
    Write-Host "  - Official gstack is managed at $HOME\.gstack\repos\gstack and kept auto-updatable."
    Write-Host "  - Slash skills live in host-specific global skills folders such as ~/.codex/skills, ~/.claude/skills, ~/.cursor/skills, and ~/.config/opencode/skills."
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
    Write-Host "  .\install.ps1 -Global              (Install global rules to all IDE/CLI folders)"
    Write-Host "  .\install.ps1 -Global -Force       (Overwrite existing global configs without prompting)"
    Write-Host "  .\install.ps1 -Project <name>      (Apply template to current directory)"
    Write-Host ""
    Write-Host "Available templates: nextjs, vite, html"
}
