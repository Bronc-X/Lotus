param (
    [switch]$Global,
    [string]$Project
)

$RepoRoot = $PSScriptRoot
$CoreAgents = Join-Path $RepoRoot "core\AGENTS.md"
$SkillsDir = Join-Path $RepoRoot "skills"

if ($Global) {
    Write-Host "Installing Global Rules & Skills..." -ForegroundColor Cyan
    
    # 1. Antigravity / Gemini CLI
    $GeminiDir = Join-Path $HOME ".gemini"
    if (-not (Test-Path $GeminiDir)) { New-Item -ItemType Directory -Path $GeminiDir -Force | Out-Null }
    Copy-Item $CoreAgents (Join-Path $GeminiDir "GEMINI.md") -Force
    
    $GeminiSkills = Join-Path $GeminiDir "antigravity\skills"
    if (-not (Test-Path $GeminiSkills)) { New-Item -ItemType Directory -Path $GeminiSkills -Force | Out-Null }
    Copy-Item (Join-Path $SkillsDir "*") $GeminiSkills -Force
    Write-Host "  ✅ Antigravity & Gemini CLI configured"
    
    # 2. Claude Code
    $ClaudeDir = Join-Path $HOME ".claude"
    if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }
    Copy-Item $CoreAgents (Join-Path $ClaudeDir "CLAUDE.md") -Force
    
    $ClaudeSkills = Join-Path $ClaudeDir "skills"
    if (-not (Test-Path $ClaudeSkills)) { New-Item -ItemType Directory -Path $ClaudeSkills -Force | Out-Null }
    Copy-Item (Join-Path $SkillsDir "*") $ClaudeSkills -Force
    Write-Host "  ✅ Claude Code configured"
    
    # 3. OpenCode
    $OpenCodeDir = Join-Path $HOME ".config\opencode"
    if (-not (Test-Path $OpenCodeDir)) { New-Item -ItemType Directory -Path $OpenCodeDir -Force | Out-Null }
    Copy-Item $CoreAgents (Join-Path $OpenCodeDir "AGENTS.md") -Force
    Write-Host "  ✅ OpenCode CLI configured"
    
    # 4. Windsurf
    $WindsurfDir = Join-Path $HOME ".windsurf\rules"
    if (-not (Test-Path $WindsurfDir)) { New-Item -ItemType Directory -Path $WindsurfDir -Force | Out-Null }
    Copy-Item $CoreAgents (Join-Path $WindsurfDir "global.md") -Force
    Write-Host "  ✅ Windsurf Cascade configured"
    
    # 5. Codex CLI
    $CodexDir = Join-Path $HOME ".codex"
    if (-not (Test-Path $CodexDir)) { New-Item -ItemType Directory -Path $CodexDir -Force | Out-Null }
    Copy-Item $CoreAgents (Join-Path $CodexDir "AGENTS.md") -Force
    Write-Host "  ✅ Codex CLI configured"
    
    # 6. Aider
    $AiderFile = Join-Path $HOME ".aider.conf.yml"
    @"
read:
  - CONVENTIONS.md
  - AGENTS.md
"@ | Out-File $AiderFile -Encoding UTF8
    Write-Host "  ✅ Aider AI configured"
    
    Write-Host "`nGlobal installation completed successfully!" -ForegroundColor Green
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
    Copy-Item (Join-Path $RepoRoot "core\CONVENTIONS.md") (Get-Location) -Force
    
    Write-Host "Project template '$Project' applied to current directory." -ForegroundColor Green
    Write-Host "Remember to adjust the design system and tech stack files in `.agents/rules/`." -ForegroundColor Yellow
}

if (-not $Global -and -not $Project) {
    Write-Host "AGENTRULES Installer" -ForegroundColor Cyan
    Write-Host "--------------------"
    Write-Host "Usage:"
    Write-Host "  .\install.ps1 -Global              (Install global rules to all IDE/CLI folders)"
    Write-Host "  .\install.ps1 -Project <name>      (Apply template to current directory)"
}
