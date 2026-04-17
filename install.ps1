param (
    [switch]$Global,
    [string]$Project
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

# Backup helper: creates a .bak copy if the target file already exists
function Backup-IfExists {
    param ([string]$FilePath)
    if (Test-Path $FilePath) {
        $BackupPath = "$FilePath.bak"
        Copy-Item $FilePath $BackupPath -Force
        Write-Host "    ⚠️  Backed up existing: $FilePath → $BackupPath" -ForegroundColor Yellow
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

# Convert a Lotus skill .md file into a Codex-compatible SKILL.md directory.
# Codex expects: ~/.codex/skills/<name>/SKILL.md with YAML frontmatter containing
# name, description, and allowed-tools fields.
function Convert-ToCodexSkill {
    param (
        [string]$SourceFile,
        [string]$TargetDir
    )

    $content = Get-Content $SourceFile -Raw -Encoding UTF8

    # Parse frontmatter to extract name
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

    # Fallback: derive name from filename if not in frontmatter
    if (-not $skillName) {
        $skillName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)
    }
    if (-not $description) {
        $description = "Lotus skill: $skillName"
    }

    # Determine allowed-tools based on skill type
    $allowedTools = switch ($skillName) {
        "auto-build" { "Bash, Read" }
        "btw"        { "Read, AskUserQuestion" }
        "feynman"    { "Read, AskUserQuestion" }
        "polanyi-tacit" { "Read, AskUserQuestion" }
        "powerup"    { "Read, AskUserQuestion" }
        "insights"   { "Read, Bash, Grep, Glob" }
        "loop"       { "Bash, Read, AskUserQuestion" }
        "subagent"   { "Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion" }
        "gstack"     { "Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion" }
        default      { "Read, AskUserQuestion" }
    }

    # Build Codex-compatible SKILL.md content
    # Rewrite frontmatter with allowed-tools, keep body unchanged
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

    # Create skill directory and write SKILL.md
    $skillDir = Join-Path $TargetDir $skillName
    if (-not (Test-Path $skillDir)) {
        New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
    }
    # Write without BOM — Codex App's YAML parser rejects BOM-prefixed files
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $skillDir "SKILL.md"), $codexContent, $utf8NoBom)
}

if ($Global) {
    Write-Host "Installing Global Rules & Skills..." -ForegroundColor Cyan
    
    # 1. Antigravity / Gemini CLI
    $GeminiDir = Join-Path $HOME ".gemini"
    if (-not (Test-Path $GeminiDir)) { New-Item -ItemType Directory -Path $GeminiDir -Force | Out-Null }
    Backup-IfExists (Join-Path $GeminiDir "GEMINI.md")
    Copy-Item $CoreAgents (Join-Path $GeminiDir "GEMINI.md") -Force
    
    $GeminiSkills = Join-Path $GeminiDir "antigravity\skills"
    if (-not (Test-Path $GeminiSkills)) { New-Item -ItemType Directory -Path $GeminiSkills -Force | Out-Null }
    Copy-LotusSkills -TargetDir $GeminiSkills -ExcludedSkills $ManagedOfficialSkills
    Write-Host "  ✅ Antigravity & Gemini CLI configured"
    
    # 2. Claude Code
    $ClaudeDir = Join-Path $HOME ".claude"
    if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }
    Backup-IfExists (Join-Path $ClaudeDir "CLAUDE.md")
    Copy-Item $CoreAgents (Join-Path $ClaudeDir "CLAUDE.md") -Force
    
    $ClaudeSkills = Join-Path $ClaudeDir "skills"
    if (-not (Test-Path $ClaudeSkills)) { New-Item -ItemType Directory -Path $ClaudeSkills -Force | Out-Null }
    Copy-LotusSkills -TargetDir $ClaudeSkills -ExcludedSkills $ManagedOfficialSkills
    Write-Host "  ✅ Claude Code configured"
    
    # 3. OpenCode
    $OpenCodeDir = Join-Path $HOME ".config\opencode"
    if (-not (Test-Path $OpenCodeDir)) { New-Item -ItemType Directory -Path $OpenCodeDir -Force | Out-Null }
    Backup-IfExists (Join-Path $OpenCodeDir "AGENTS.md")
    Copy-Item $CoreAgents (Join-Path $OpenCodeDir "AGENTS.md") -Force
    Write-Host "  ✅ OpenCode CLI configured"
    
    # 4. Windsurf
    $WindsurfDir = Join-Path $HOME ".windsurf\rules"
    if (-not (Test-Path $WindsurfDir)) { New-Item -ItemType Directory -Path $WindsurfDir -Force | Out-Null }
    Backup-IfExists (Join-Path $WindsurfDir "global.md")
    Copy-Item $CoreAgents (Join-Path $WindsurfDir "global.md") -Force
    Write-Host "  ✅ Windsurf Cascade configured"
    
    # 5. Codex CLI — Rules + Lotus-only compatible skills.
    #    Official gstack skills are installed by the managed upstream setup below.
    #    In-context-only Lotus skills are excluded — they work via AGENTS.md rules.
    $CodexDir = Join-Path $HOME ".codex"
    if (-not (Test-Path $CodexDir)) { New-Item -ItemType Directory -Path $CodexDir -Force | Out-Null }
    Backup-IfExists (Join-Path $CodexDir "AGENTS.md")
    Copy-Item $CoreAgents (Join-Path $CodexDir "AGENTS.md") -Force
    
    $CodexSkills = Join-Path $CodexDir "skills"
    if (-not (Test-Path $CodexSkills)) { New-Item -ItemType Directory -Path $CodexSkills -Force | Out-Null }
    
    # Clean up previously deployed incompatible skills
    foreach ($excluded in ($CodexExcludedSkills + $ManagedOfficialSkills)) {
        $excludedDir = Join-Path $CodexSkills $excluded
        if (Test-Path $excludedDir) {
            Remove-Item $excludedDir -Recurse -Force
            Write-Host "    🗑️  Removed incompatible skill: $excluded"
        }
    }
    
    # Convert compatible Lotus skills to Codex directory format
    Get-ChildItem (Join-Path $SkillsDir "*.md") | ForEach-Object {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        if (($CodexExcludedSkills + $ManagedOfficialSkills) -contains $baseName) {
            Write-Host "    ⏭️  Skipped (managed elsewhere or in-context only): $baseName"
        } else {
            Convert-ToCodexSkill -SourceFile $_.FullName -TargetDir $CodexSkills
            Write-Host "    📦 Converted skill: $baseName"
        }
    }
    Write-Host "  ✅ Codex CLI configured (rules + Lotus-only compatible skills)"
    
    # 6. Cursor (Global Rules)
    $CursorDir = Join-Path $HOME ".cursor\rules"
    if (-not (Test-Path $CursorDir)) { New-Item -ItemType Directory -Path $CursorDir -Force | Out-Null }
    $CursorFile = Join-Path $CursorDir "lotus.mdc"
    Backup-IfExists $CursorFile
    # Cursor .mdc format: wrap content in a rule block
    $cursorContent = @"
---
description: Lotus GStack Engineering Protocol - Global rules and workflow standards
globs:
alwaysApply: true
---

$(Get-Content $CoreAgents -Raw -Encoding UTF8)
"@
    $cursorContent | Out-File $CursorFile -Encoding UTF8 -Force
    Write-Host "  ✅ Cursor configured"
    
    # 7. Aider (merge, not overwrite)
    $AiderFile = Join-Path $HOME ".aider.conf.yml"
    Backup-IfExists $AiderFile
    @"
read:
  - CONVENTIONS.md
  - AGENTS.md
"@ | Out-File $AiderFile -Encoding UTF8
    Write-Host "  ✅ Aider AI configured"

    Write-Host "  ↻ Installing official gstack upstream..."
    if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
        throw "Git Bash is required to install official gstack on Windows. Install Git for Windows or ensure 'bash' is on PATH."
    }
    $BashManagedGstackInstaller = $ManagedGstackInstaller -replace '\\', '/'
    & bash $BashManagedGstackInstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Official gstack installation failed."
    }
    Write-Host "  ✅ Official gstack configured for Claude/Codex/OpenCode"
    
    Write-Host ""
    Write-Host "Global installation completed successfully!" -ForegroundColor Green
    Write-Host "If any existing configs were overwritten, .bak backups have been created." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Codex note:" -ForegroundColor Cyan
    Write-Host "  - Global rules were installed to $CodexDir\AGENTS.md and are auto-loaded in local repos."
    Write-Host "  - `-Global` does not create `AGENTS.md` inside each project folder."
    Write-Host "  - Run `.\install.ps1 -Project nextjs|vite|html` inside a project when you want local `AGENTS.md` and `.agents/rules/` files."
    Write-Host "  - Official gstack is managed at $HOME\.gstack\repos\gstack and kept auto-updatable."
}

if ($Project) {
    Write-Host "Installing Project Template: $Project..." -ForegroundColor Cyan
    $TemplateDir = Join-Path $RepoRoot "templates\$Project"
    
    if (-not (Test-Path $TemplateDir)) {
        Write-Error "Template '$Project' not found in templates directory."
        exit 1
    }
    
    # Copy template contents to current working directory
    Copy-Item (Join-Path $TemplateDir "*") (Get-Location) -Recurse -Force
    
    # Copy core conventions
    $ConventionsFile = Join-Path $RepoRoot "core\CONVENTIONS.md"
    if (Test-Path $ConventionsFile) {
        Copy-Item $ConventionsFile (Get-Location) -Force
    }
    
    Write-Host "Project template '$Project' applied to current directory." -ForegroundColor Green
    Write-Host "Remember to adjust the design system and tech stack files in ``.agents/rules/``." -ForegroundColor Yellow
}

if (-not $Global -and -not $Project) {
    Write-Host "Lotus Installer" -ForegroundColor Cyan
    Write-Host "--------------------"
    Write-Host "Usage:"
    Write-Host "  .\install.ps1 -Global              (Install global rules to all IDE/CLI folders)"
    Write-Host "  .\install.ps1 -Project <name>      (Apply template to current directory)"
    Write-Host ""
    Write-Host "Available templates: nextjs, vite, html"
}
