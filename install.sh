#!/usr/bin/env bash

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_AGENTS="$REPO_ROOT/core/AGENTS.md"
SKILLS_DIR="$REPO_ROOT/skills"
MANAGED_GSTACK_INSTALLER="$REPO_ROOT/scripts/install-managed-gstack.sh"

# Skills that rely on "staying in current conversation" and are incompatible
# with Codex App's architecture (each skill invocation = new task context).
# These skills work via AGENTS.md rule-level recognition instead.
CODEX_EXCLUDED_SKILLS=("btw" "loop")
MANAGED_OFFICIAL_SKILLS=("gstack")
HIDDEN_TOP_LEVEL_SKILLS=(
    "brandkit"
    "gstack-plan-ceo-review"
    "gstack-plan-design-review"
    "gstack-plan-eng-review"
    "imagegen"
    "openai-docs"
    "plugin-creator"
    "skill-creator"
    "skill-installer"
)
HIDDEN_CLAUDE_GSTACK_ALIASES=(
    "plan-ceo-review"
    "plan-design-review"
    "plan-eng-review"
)
OBSOLETE_LOTUS_SKILLS=(
    "auto-build"
    "conversion-copywriter"
    "debugging-strategies"
    "design-taste-frontend-v1"
    "gpt-taste"
    "gsap-core"
    "gsap-frameworks"
    "gsap-performance"
    "gsap-plugins"
    "gsap-react"
    "gsap-scrolltrigger"
    "gsap-timeline"
    "gsap-utils"
    "high-end-visual-design"
    "image-to-code"
    "imagegen-frontend-mobile"
    "imagegen-frontend-web"
    "industrial-brutalist-ui"
    "ios-ui-centering-fix"
    "minimalist-ui"
    "mobile-agent-bridge"
    "powerup"
    "redesign-existing-projects"
    "stitch-design-taste"
    "full-output-enforcement"
    "web-to-design-md"
)
CORE_EXPOSED_GSTACK_SKILLS=(
    "gstack"
    "gstack-office-hours"
    "gstack-investigate"
    "gstack-browse"
    "gstack-ship"
)

GLOBAL=0
PROJECT=""
ASSUME_YES=0
GSTACK_PROFILE="core"
OFFICIAL_GSTACK_INSTALLED=0
GSTACK_BOOTSTRAP_INSTALLED=0

prepend_path_if_dir() {
    local dir="$1"

    if [ -d "$dir" ]; then
        case ":$PATH:" in
            *":$dir:"*) ;;
            *) PATH="$dir:$PATH" ;;
        esac
    fi
}

prepend_common_tool_paths() {
    # GUI-launched agents often run non-login shells and miss user tool paths.
    prepend_path_if_dir "$HOME/.bun/bin"
    prepend_path_if_dir "$HOME/.local/bin"
    prepend_path_if_dir "/opt/homebrew/bin"
    prepend_path_if_dir "/usr/local/bin"
    export PATH
}

prepend_common_tool_paths

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --global) GLOBAL=1 ;;
        --project) PROJECT="$2"; shift ;;
        --gstack-profile) GSTACK_PROFILE="$2"; shift ;;
        --yes|-y) ASSUME_YES=1 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

backup_if_exists() {
    if [ -f "$1" ]; then
        cp "$1" "$1.bak"
        echo "    Backed up existing: $1 -> $1.bak"
    fi
}

path_exists_any() {
    for candidate in "$@"; do
        if [ -e "$candidate" ]; then
            return 0
        fi
    done
    return 1
}

require_skill_file() {
    local missing_ref="$1"
    shift
    local label="$1"
    shift

    if path_exists_any "$@"; then
        return 0
    fi

    eval "$missing_ref+=(\"\$label\")"
}

verify_managed_gstack_install() {
    local missing=()

    if [ ! -d "$HOME/.gstack/repos/gstack/.git" ]; then
        missing+=("official gstack repo (~/.gstack/repos/gstack)")
    fi

    require_skill_file missing "Claude runtime (~/.claude/skills/gstack)" \
        "$HOME/.claude/skills/gstack/SKILL.md" \
        "$HOME/.claude/skills/gstack"
    require_skill_file missing "Claude office-hours skill (~/.claude/skills/gstack-office-hours or office-hours)" \
        "$HOME/.claude/skills/gstack-office-hours/SKILL.md" \
        "$HOME/.claude/skills/office-hours/SKILL.md"
    require_skill_file missing "Claude investigate skill (~/.claude/skills/gstack-investigate or investigate)" \
        "$HOME/.claude/skills/gstack-investigate/SKILL.md" \
        "$HOME/.claude/skills/investigate/SKILL.md"
    require_skill_file missing "Claude browse skill (~/.claude/skills/gstack-browse or browse)" \
        "$HOME/.claude/skills/gstack-browse/SKILL.md" \
        "$HOME/.claude/skills/browse/SKILL.md"
    require_skill_file missing "Claude ship skill (~/.claude/skills/gstack-ship or ship)" \
        "$HOME/.claude/skills/gstack-ship/SKILL.md" \
        "$HOME/.claude/skills/ship/SKILL.md"

    require_skill_file missing "Codex gstack runtime (~/.codex/skills/gstack/SKILL.md)" \
        "$HOME/.codex/skills/gstack/SKILL.md"
    require_skill_file missing "Codex office-hours skill (~/.codex/skills/gstack-office-hours/SKILL.md)" \
        "$HOME/.codex/skills/gstack-office-hours/SKILL.md"
    require_skill_file missing "Codex investigate skill (~/.codex/skills/gstack-investigate/SKILL.md)" \
        "$HOME/.codex/skills/gstack-investigate/SKILL.md"
    require_skill_file missing "Codex browse skill (~/.codex/skills/gstack-browse/SKILL.md or gstack/browse/SKILL.md)" \
        "$HOME/.codex/skills/gstack-browse/SKILL.md" \
        "$HOME/.codex/skills/gstack/browse/SKILL.md"
    require_skill_file missing "Codex ship skill (~/.codex/skills/gstack-ship/SKILL.md)" \
        "$HOME/.codex/skills/gstack-ship/SKILL.md"

    if [ "${#missing[@]}" -gt 0 ]; then
        echo "Official gstack install is incomplete. Missing:" >&2
        for item in "${missing[@]}"; do
            echo "  - $item" >&2
        done
        echo "Lotus global rules live in AGENTS/CLAUDE files, but slash skills must exist in each host's global skills directory." >&2
        return 1
    fi
}

confirm_global_rule_overwrite() {
    local existing=()

    for candidate in "$@"; do
        if [ -f "$candidate" ]; then
            existing+=("$candidate")
        fi
    done

    if [ "${#existing[@]}" -eq 0 ]; then
        return 0
    fi

    if [ "$ASSUME_YES" -eq 1 ] || [ "${LOTUS_ASSUME_YES:-0}" = "1" ]; then
        echo "  Overwrite confirmation skipped (--yes / LOTUS_ASSUME_YES=1)."
        return 0
    fi

    if [ ! -t 0 ]; then
        echo "Existing global rule/config files would be overwritten, but no interactive confirmation is available." >&2
        echo "Re-run with --yes (or LOTUS_ASSUME_YES=1) if you want Lotus to overwrite them automatically." >&2
        return 1
    fi

    echo "Existing global rule/config files detected. Lotus will back them up to .bak and then overwrite them:"
    for file_path in "${existing[@]}"; do
        echo "  - $file_path"
    done
    echo
    read -r -p "Continue and overwrite these global files? [y/N] " response
    case "$response" in
        y|Y|yes|YES)
            return 0
            ;;
        *)
            echo "Cancelled. No global rules were overwritten."
            return 1
            ;;
    esac
}

is_skill_excluded() {
    local skill_name="$1"
    shift

    for excluded in "$@"; do
        if [ "$skill_name" = "$excluded" ]; then
            return 0
        fi
    done
    return 1
}

move_skill_to_lotus_hidden() {
    local source_path="$1"
    local host_group="$2"
    local hidden_dir="$HOME/.codex/hidden-skills/lotus/$host_group"
    local destination

    [ -e "$source_path" ] || return 0
    mkdir -p "$hidden_dir"
    destination="$hidden_dir/$(basename "$source_path")"
    rm -rf "$destination"
    mv "$source_path" "$destination"
    echo "    Hidden top-level skill: $source_path -> $destination"
}

hide_top_level_skills() {
    local target_dir="$1"
    local host_group="$2"
    local include_codex_system="${3:-0}"
    local skill_name

    for skill_name in "${HIDDEN_TOP_LEVEL_SKILLS[@]}"; do
        move_skill_to_lotus_hidden "$target_dir/$skill_name" "$host_group"
        move_skill_to_lotus_hidden "$target_dir/$skill_name.md" "$host_group"
    done

    if [ "$host_group" = "claude" ]; then
        for skill_name in "${HIDDEN_CLAUDE_GSTACK_ALIASES[@]}"; do
            move_skill_to_lotus_hidden "$target_dir/$skill_name" "$host_group"
            move_skill_to_lotus_hidden "$target_dir/$skill_name.md" "$host_group"
        done
    fi

    if [ "$include_codex_system" -eq 1 ]; then
        for skill_name in "${HIDDEN_TOP_LEVEL_SKILLS[@]}"; do
            move_skill_to_lotus_hidden "$target_dir/.system/$skill_name" "codex-system"
        done
    fi
}

write_anysearch_runtime_conf() {
    local skill_dir="$1"

    if [ "$(basename "$skill_dir")" != "anysearch" ]; then
        return 0
    fi

    local runtime
    local command
    if command -v python3 >/dev/null 2>&1; then
        runtime="Python"
        command="python3 \"$skill_dir/scripts/anysearch_cli.py\""
    elif command -v python >/dev/null 2>&1; then
        runtime="Python"
        command="python \"$skill_dir/scripts/anysearch_cli.py\""
    elif command -v node >/dev/null 2>&1; then
        runtime="Node.js"
        command="node \"$skill_dir/scripts/anysearch_cli.js\""
    else
        runtime="Shell"
        command="bash \"$skill_dir/scripts/anysearch_cli.sh\""
    fi

    cat > "$skill_dir/runtime.conf" <<RUNTIME_EOF
Runtime: $runtime
Command: $command
RUNTIME_EOF
}

copy_lotus_skill_packages() {
    local target_dir="$1"
    shift

    for skill_dir in "$SKILLS_DIR"/*; do
        [ -d "$skill_dir" ] || continue
        [ -f "$skill_dir/SKILL.md" ] || continue

        local skill_name
        skill_name="$(basename "$skill_dir")"
        if is_skill_excluded "$skill_name" "$@"; then
            continue
        fi

        local target_skill_dir="$target_dir/$skill_name"
        # Overlay voice workflow files; never remove local voice assets/configuration.
        if [ "$skill_name" = "ai-podcast" ] || [ "$skill_name" = "toni-voice" ] || [ "$skill_name" = "brian-voice" ] || [ "$skill_name" = "broncin-style-writer" ]; then
            mkdir -p "$target_skill_dir"
            while IFS= read -r -d '' source_file; do
                local relative="${source_file#"$skill_dir/"}"
                case "$relative" in
                    SKILL.md|.gitignore|agents/openai.yaml|scripts/*.py|scripts/*.ps1) ;;
                    references/content-script.md|references/distribution.md|references/validation.md|references/voice-runtime.md|assets/jobs.example.json|assets/runtime.example.json) [ "$skill_name" = "ai-podcast" ] || continue ;;
                    *) continue ;;
                esac
                local target_file="$target_skill_dir/$relative"
                mkdir -p "$(dirname "$target_file")"
                if [ -f "$target_file" ]; then
                    cmp -s "$source_file" "$target_file" && continue
                    cp "$target_file" "$target_file.lotus.bak"
                fi
                cp "$source_file" "$target_file"
            done < <(find "$skill_dir" -type f -print0)
            echo "    Updated voice skill package, preserving private files: $skill_name"
            continue
        fi
        local saved_runtime=""
        local had_runtime=0
        if [ -f "$target_skill_dir/runtime.local.json" ]; then
            saved_runtime="$(cat "$target_skill_dir/runtime.local.json")"
            had_runtime=1
        fi

        rm -rf "$target_skill_dir"
        mkdir -p "$target_skill_dir"
        (
            cd "$skill_dir"
            tar --exclude=".env" --exclude="runtime.conf" --exclude="runtime.local.json" -cf - .
        ) | (
            cd "$target_skill_dir"
            tar -xf -
        )
        if [ "$had_runtime" -eq 1 ]; then
            printf '%s\n' "$saved_runtime" > "$target_skill_dir/runtime.local.json"
        fi
        write_anysearch_runtime_conf "$target_skill_dir"
        echo "    Copied skill package: $skill_name"
    done
}

remove_obsolete_lotus_skills() {
    local target_dir="$1"

    [ -d "$target_dir" ] || return 0

    for skill_name in "${OBSOLETE_LOTUS_SKILLS[@]}"; do
        if [ -d "$target_dir/$skill_name" ]; then
            rm -rf "$target_dir/$skill_name"
            echo "    Removed merged skill: $skill_name"
        fi
        if [ -f "$target_dir/$skill_name.md" ]; then
            rm -f "$target_dir/$skill_name.md"
            echo "    Removed merged skill file: $skill_name.md"
        fi
    done
}

copy_lotus_skills() {
    local target_dir="$1"
    shift
    mkdir -p "$target_dir"

    remove_obsolete_lotus_skills "$target_dir"

    for skill_file in "$SKILLS_DIR"/*.md; do
        local skill_name
        skill_name="$(basename "$skill_file" .md)"
        if ! is_skill_excluded "$skill_name" "$@"; then
            rm -f "$target_dir/$skill_name.md"
            convert_to_codex_skill "$skill_file" "$target_dir"
        fi
    done

    copy_lotus_skill_packages "$target_dir" "$@"
}

claude_gstack_skill_name() {
    local skill_name="$1"

    if [ "$skill_name" = "gstack" ]; then
        echo "gstack"
    else
        echo "${skill_name#gstack-}"
    fi
}

write_gstack_bootstrap_skill() {
    local skill_file="$1"
    local skill_name="$2"
    local display_name="$3"
    local description

    case "$skill_name" in
        gstack)
            description="需 gstack 流程时打开总入口"
            ;;
        gstack-office-hours)
            description="讨论方案时快速找取舍"
            ;;
        gstack-investigate)
            description="需调研时收集线索给结论"
            ;;
        gstack-plan-eng-review)
            description="审工程计划时查实现风险"
            ;;
        gstack-plan-ceo-review)
            description="审产品计划时查目标取舍"
            ;;
        gstack-plan-design-review)
            description="审设计计划时查体验方向"
            ;;
        gstack-design-review)
            description="审界面时查视觉交互问题"
            ;;
        gstack-browse)
            description="验页面时浏览器检查效果"
            ;;
        gstack-qa)
            description="验质量时查测试回归风险"
            ;;
        gstack-review)
            description="审代码时查Bug和测试缺口"
            ;;
        gstack-ship)
            description="发布前检查构建验证风险"
            ;;
        *)
            description="需 gstack $display_name 时打开入口"
            ;;
    esac

    cat > "$skill_file" <<BOOTSTRAP_EOF
---
name: $skill_name
description: |
  $description
allowed-tools:
  - Read
  - AskUserQuestion
---

# 官方 gstack bootstrap

这是一个真实的顶层 skill 入口。Lotus 在完整官方 gstack runtime 暂时无法安装时写入它，避免 gstack slash 菜单入口消失。

完整的官方 gstack runtime 还没有安装。要启用完整工作流：

1. 安装 Git、bash 和 bun。
2. 打开新的终端。
3. 重新运行：

\`\`\`bash
install.sh --global
\`\`\`

如果你不在 Lotus 仓库目录内运行，请使用 \`install.sh\` 的完整路径。
BOOTSTRAP_EOF
}

is_gstack_bootstrap_skill_file() {
    local skill_file="$1"

    [ -f "$skill_file" ] && grep -Eq "Bootstrap entry for official gstack|官方 gstack bootstrap" "$skill_file"
}

write_gstack_bootstrap_skill_if_needed() {
    local skill_file="$1"
    local skill_name="$2"
    local display_name="$3"
    local only_missing="${4:-0}"

    if [ -f "$skill_file" ]; then
        if ! is_gstack_bootstrap_skill_file "$skill_file"; then
            return 1
        fi
        if [ "$only_missing" -eq 1 ]; then
            return 1
        fi
    fi

    write_gstack_bootstrap_skill "$skill_file" "$skill_name" "$display_name"
    return 0
}

install_gstack_bootstrap_skills() {
    local only_missing="${1:-0}"
    local codex_skill
    local claude_skill
    local display_name
    local codex_dir
    local claude_dir
    local written=0
    local preserved=0

    mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills"

    for codex_skill in "${CORE_EXPOSED_GSTACK_SKILLS[@]}"; do
        display_name="${codex_skill#gstack-}"
        if [ "$codex_skill" = "gstack" ]; then
            display_name="runtime"
        fi

        codex_dir="$HOME/.codex/skills/$codex_skill"
        mkdir -p "$codex_dir"
        if write_gstack_bootstrap_skill_if_needed "$codex_dir/SKILL.md" "$codex_skill" "$display_name" "$only_missing"; then
            written=$((written + 1))
        else
            preserved=$((preserved + 1))
        fi

        claude_skill="$(claude_gstack_skill_name "$codex_skill")"
        claude_dir="$HOME/.claude/skills/$claude_skill"
        mkdir -p "$claude_dir"
        if write_gstack_bootstrap_skill_if_needed "$claude_dir/SKILL.md" "$claude_skill" "$display_name" "$only_missing"; then
            written=$((written + 1))
        else
            preserved=$((preserved + 1))
        fi
    done

    echo "  Installed bootstrap entries for the curated official gstack top-level skills ($written written, $preserved preserved)"
}

# Convert a Lotus skill .md file into a Codex-compatible SKILL.md directory.
# Codex expects: ~/.codex/skills/<name>/SKILL.md with YAML frontmatter containing
# name and description. Most legacy Lotus skills also carry allowed-tools, but
# image-2 intentionally avoids a tool whitelist so native image tools stay available
# when the host exposes them.
convert_to_codex_skill() {
    local source_file="$1"
    local target_dir="$2"

    local content
    content=$(cat "$source_file")

    local skill_name=""
    local description=""
    local frontmatter=""

    if echo "$content" | head -1 | grep -q "^---"; then
        frontmatter=$(awk '
            NR == 1 && $0 == "---" {
                in_frontmatter = 1
                next
            }
            in_frontmatter == 1 && $0 == "---" {
                exit
            }
            in_frontmatter == 1 {
                print
            }
        ' "$source_file")
        skill_name=$(echo "$frontmatter" | grep '^name:' | sed 's/^name:[[:space:]]*//' || true)
        description=$(echo "$frontmatter" | grep '^description:' | sed 's/^description:[[:space:]]*//' || true)
    fi

    if [ -z "$skill_name" ]; then
        skill_name=$(basename "$source_file" .md)
    fi
    if [ -z "$description" ]; then
        description="Lotus skill: $skill_name"
    fi

    local allowed_tools
    case "$skill_name" in
        auto-build)     allowed_tools="Bash\n  - Read" ;;
        btw)            allowed_tools="Read\n  - AskUserQuestion" ;;
        feynman)        allowed_tools="Read\n  - AskUserQuestion" ;;
        polanyi-tacit)  allowed_tools="Read\n  - AskUserQuestion" ;;
        powerup)        allowed_tools="Read\n  - AskUserQuestion" ;;
        insights)       allowed_tools="Read\n  - Bash\n  - Grep\n  - Glob" ;;
        ai-progress-workspace) allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - Bash\n  - AskUserQuestion\n  - WebSearch" ;;
        loop)           allowed_tools="Bash\n  - Read\n  - AskUserQuestion" ;;
        agent-training-loop) allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - Bash\n  - AskUserQuestion" ;;
        baseline-packager) allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - Bash\n  - AskUserQuestion" ;;
        mini-investigate) allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - Bash\n  - AskUserQuestion" ;;
        conversion-copywriter) allowed_tools="Read\n  - AskUserQuestion" ;;
        subagent)       allowed_tools="Bash\n  - Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - AskUserQuestion" ;;
        web-to-design-md) allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - AskUserQuestion\n  - WebSearch" ;;
        taste-skill)    allowed_tools="Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - Bash\n  - AskUserQuestion" ;;
        gstack)         allowed_tools="Bash\n  - Read\n  - Write\n  - Edit\n  - Grep\n  - Glob\n  - AskUserQuestion" ;;
        *)              allowed_tools="Read\n  - AskUserQuestion" ;;
    esac

    local skill_dir="$target_dir/$skill_name"
    mkdir -p "$skill_dir"

    if echo "$frontmatter" | grep -q '^allowed-tools:'; then
        cp "$source_file" "$skill_dir/SKILL.md"
        echo "    Installed skill: $skill_name"
        return 0
    fi

    local body
    body=$(awk '
        NR == 1 && $0 == "---" {
            in_frontmatter = 1
            next
        }
        in_frontmatter == 1 && $0 == "---" {
            in_frontmatter = 0
            next
        }
        in_frontmatter == 1 {
            next
        }
        {
            print
        }
    ' "$source_file")

    if [ "$skill_name" = "image-2" ]; then
        cat > "$skill_dir/SKILL.md" <<CODEX_EOF
---
name: $skill_name
description: $description
---
$body
CODEX_EOF

        echo "    Converted skill: $skill_name"
        return 0
    fi

    cat > "$skill_dir/SKILL.md" <<CODEX_EOF
---
name: $skill_name
description: |
  $description
allowed-tools:
  - $(echo -e "$allowed_tools")
---
$body
CODEX_EOF

    echo "    Converted skill: $skill_name"
}

if [ "$GLOBAL" -eq 1 ]; then
    echo -e "\033[0;36mInstalling Global Rules & Skills...\033[0m"

    CLAUDE_RULE_FILE="$HOME/.claude/CLAUDE.md"
    CODEX_RULE_FILE="$HOME/.codex/AGENTS.md"

    if ! confirm_global_rule_overwrite \
        "$CLAUDE_RULE_FILE" \
        "$CODEX_RULE_FILE"; then
        exit 1
    fi

    mkdir -p ~/.claude/skills
    backup_if_exists "$CLAUDE_RULE_FILE"
    cp "$CORE_AGENTS" "$CLAUDE_RULE_FILE"
    copy_lotus_skills ~/.claude/skills "${MANAGED_OFFICIAL_SKILLS[@]}" "${HIDDEN_TOP_LEVEL_SKILLS[@]}"
    hide_top_level_skills ~/.claude/skills "claude"
    echo "  Claude Code configured"

    mkdir -p ~/.codex/skills
    backup_if_exists "$CODEX_RULE_FILE"
    cp "$CORE_AGENTS" "$CODEX_RULE_FILE"

    remove_obsolete_lotus_skills ~/.codex/skills

    for excluded in "${CODEX_EXCLUDED_SKILLS[@]}"; do
        if [ -d "$HOME/.codex/skills/$excluded" ]; then
            rm -rf "$HOME/.codex/skills/$excluded"
            echo "    Removed incompatible skill: $excluded"
        fi
    done

    for skill_file in "$SKILLS_DIR"/*.md; do
        skill_name=$(basename "$skill_file" .md)
        is_excluded=false
        for excluded in "${CODEX_EXCLUDED_SKILLS[@]}" "${MANAGED_OFFICIAL_SKILLS[@]}" "${HIDDEN_TOP_LEVEL_SKILLS[@]}"; do
            if [ "$skill_name" = "$excluded" ]; then
                is_excluded=true
                break
            fi
        done
        if [ "$is_excluded" = true ]; then
            echo "    Skipped (managed elsewhere or in-context only): $skill_name"
        else
            convert_to_codex_skill "$skill_file" ~/.codex/skills
        fi
    done
    copy_lotus_skill_packages ~/.codex/skills "${CODEX_EXCLUDED_SKILLS[@]}" "${MANAGED_OFFICIAL_SKILLS[@]}" "${HIDDEN_TOP_LEVEL_SKILLS[@]}"
    echo "  Codex CLI configured (rules + Lotus-only compatible skills)"

    echo "  Installing official gstack upstream..."
    if LOTUS_GSTACK_PROFILE="$GSTACK_PROFILE" bash "$MANAGED_GSTACK_INSTALLER" && verify_managed_gstack_install; then
        OFFICIAL_GSTACK_INSTALLED=1
        echo "  Official gstack configured for Claude/Codex"
    else
        echo "Official gstack installation or verification failed. Installing bootstrap slash entries instead." >&2
        install_gstack_bootstrap_skills 1
        GSTACK_BOOTSTRAP_INSTALLED=1
    fi

    hide_top_level_skills ~/.claude/skills "claude"
    hide_top_level_skills ~/.codex/skills "codex" 1

    if [ "$OFFICIAL_GSTACK_INSTALLED" -eq 1 ]; then
        for adapter in "$REPO_ROOT"/adapters/gstack/*; do
            [ -d "$adapter" ] || continue
            target="$HOME/.codex/skills/$(basename "$adapter")"
            if [ -f "$target/SKILL.md" ]; then
                cp "$adapter/SKILL.md" "$target/SKILL.md"
                if [ -d "$adapter/references" ]; then
                    mkdir -p "$target/references"
                    cp -R "$adapter/references"/. "$target/references"/
                fi
            fi
        done
    fi

    echo ""
    echo -e "\033[0;32mGlobal installation completed successfully!\033[0m"
    echo -e "\033[0;33mIf any existing configs were overwritten, .bak backups have been created.\033[0m"
    echo ""
    echo -e "\033[0;36mCodex note:\033[0m"
    echo "  - Global rules were installed to ~/.codex/AGENTS.md and are auto-loaded in local repos."
    echo "  - --global does not create AGENTS.md inside each project folder."
    echo "  - Run ./install.sh --project nextjs|vite|html inside a project when you want local AGENTS.md and .agents/rules/ files."
    if [ "$OFFICIAL_GSTACK_INSTALLED" -eq 1 ]; then
        echo "  - Official gstack is managed at ~/.gstack/repos/gstack and kept auto-updatable."
    elif [ "$GSTACK_BOOTSTRAP_INSTALLED" -eq 1 ]; then
        echo "  - The curated official gstack top-level skill entries were installed as bootstrap skills."
        echo "  - Install Git, bash, and bun, then re-run ./install.sh --global to install the full official gstack runtime."
    fi
    echo "  - Official gstack top-level exposure profile: $GSTACK_PROFILE"
    echo "  - Lotus keeps low-frequency skills out of the top-level menu under ~/.codex/hidden-skills/lotus."
    echo "  - Hidden official gstack skills stay in ~/.gstack/repos/gstack/.agents/skills and can still be routed by AGENTS.md."
    echo "  - Slash skills live in the managed global skills folders ~/.claude/skills and ~/.codex/skills."
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
    echo "  ./install.sh --global                            (Install global rules to the managed Claude/Codex folders)"
    echo "  ./install.sh --global --gstack-profile core     (Default curated official gstack top-level set)"
    echo "  ./install.sh --global --gstack-profile full     (Expose the full official gstack top-level set)"
    echo "  ./install.sh --global --yes                     (Overwrite existing global configs without prompting)"
    echo "  ./install.sh --project <name>                   (Apply template to current directory)"
    echo ""
    echo "Available gstack profiles: core, design, review, deploy, full"
    echo "Available templates: nextjs, vite, html"
fi
