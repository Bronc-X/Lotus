#!/bin/bash

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_AGENTS="$REPO_ROOT/core/AGENTS.md"
SKILLS_DIR="$REPO_ROOT/skills"

GLOBAL=0
PROJECT=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --global) GLOBAL=1 ;;
        --project) PROJECT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Backup helper: creates a .bak copy if the target file already exists
backup_if_exists() {
    if [ -f "$1" ]; then
        cp "$1" "$1.bak"
        echo "    ⚠️  Backed up existing: $1 → $1.bak"
    fi
}

if [ "$GLOBAL" -eq 1 ]; then
    echo -e "\033[0;36mInstalling Global Rules & Skills...\033[0m"

    # 1. Antigravity / Gemini CLI
    mkdir -p ~/.gemini/antigravity/skills
    backup_if_exists ~/.gemini/GEMINI.md
    cp "$CORE_AGENTS" ~/.gemini/GEMINI.md
    cp "$SKILLS_DIR"/* ~/.gemini/antigravity/skills/
    echo "  ✅ Antigravity & Gemini CLI configured"

    # 2. Claude Code
    mkdir -p ~/.claude/skills
    backup_if_exists ~/.claude/CLAUDE.md
    cp "$CORE_AGENTS" ~/.claude/CLAUDE.md
    cp "$SKILLS_DIR"/* ~/.claude/skills/
    echo "  ✅ Claude Code configured"

    # 3. OpenCode
    mkdir -p ~/.config/opencode
    backup_if_exists ~/.config/opencode/AGENTS.md
    cp "$CORE_AGENTS" ~/.config/opencode/AGENTS.md
    echo "  ✅ OpenCode CLI configured"

    # 4. Windsurf
    mkdir -p ~/.windsurf/rules
    backup_if_exists ~/.windsurf/rules/global.md
    cp "$CORE_AGENTS" ~/.windsurf/rules/global.md
    echo "  ✅ Windsurf Cascade configured"

    # 5. Codex CLI
    mkdir -p ~/.codex
    backup_if_exists ~/.codex/AGENTS.md
    cp "$CORE_AGENTS" ~/.codex/AGENTS.md
    echo "  ✅ Codex CLI configured"

    # 6. Aider
    backup_if_exists ~/.aider.conf.yml
    cat <<EOF > ~/.aider.conf.yml
read:
  - CONVENTIONS.md
  - AGENTS.md
EOF
    echo "  ✅ Aider AI configured"

    echo ""
    echo -e "\033[0;32mGlobal installation completed successfully!\033[0m"
    echo -e "\033[0;33mIf any existing configs were overwritten, .bak backups have been created.\033[0m"
fi

if [ -n "$PROJECT" ]; then
    echo -e "\033[0;36mInstalling Project Template: $PROJECT...\033[0m"
    TEMPLATE_DIR="$REPO_ROOT/templates/$PROJECT"

    if [ ! -d "$TEMPLATE_DIR" ]; then
        echo -e "\033[0;31mTemplate '$PROJECT' not found.\033[0m"
        exit 1
    fi

    cp -R "$TEMPLATE_DIR"/* .
    cp -R "$TEMPLATE_DIR"/.[!.]* . 2>/dev/null || true
    
    CONVENTIONS_FILE="$REPO_ROOT/core/CONVENTIONS.md"
    if [ -f "$CONVENTIONS_FILE" ]; then
        cp "$CONVENTIONS_FILE" .
    fi
    
    echo -e "\033[0;32mProject template '$PROJECT' applied to current directory.\033[0m"
    echo -e "\033[0;33mRemember to adjust the design system and tech stack files in .agents/rules/.\033[0m"
fi

if [ "$GLOBAL" -eq 0 ] && [ -z "$PROJECT" ]; then
    echo -e "\033[0;36mLotus Installer\033[0m"
    echo "--------------------"
    echo "Usage:"
    echo "  ./install.sh --global              (Install global rules to all IDE/CLI folders)"
    echo "  ./install.sh --project <name>      (Apply template to current directory)"
    echo ""
    echo "Available templates: nextjs, vite, html"
fi
