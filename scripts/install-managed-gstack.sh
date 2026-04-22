#!/usr/bin/env bash
set -euo pipefail

GSTACK_REPO_URL="${LOTUS_GSTACK_REPO_URL:-https://github.com/garrytan/gstack.git}"
GSTACK_DIR="${LOTUS_GSTACK_DIR:-$HOME/.gstack/repos/gstack}"
GSTACK_PARENT="$(dirname "$GSTACK_DIR")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
GSTACK_PROFILE="$(printf '%s' "${LOTUS_GSTACK_PROFILE:-core}" | tr '[:upper:]' '[:lower:]')"

CORE_EXPOSED_GSTACK_SKILLS=(
  "gstack"
  "gstack-office-hours"
  "gstack-plan-ceo-review"
  "gstack-plan-design-review"
  "gstack-plan-eng-review"
  "gstack-design-review"
  "gstack-review"
  "gstack-investigate"
  "gstack-browse"
  "gstack-qa"
  "gstack-ship"
)

DESIGN_PROFILE_EXTRAS=(
  "gstack-design-consultation"
  "gstack-design-shotgun"
  "gstack-design-html"
)

REVIEW_PROFILE_EXTRAS=(
  "gstack-qa-only"
  "gstack-health"
  "gstack-cso"
  "gstack-devex-review"
  "gstack-benchmark"
)

DEPLOY_PROFILE_EXTRAS=(
  "gstack-setup-deploy"
  "gstack-land-and-deploy"
  "gstack-canary"
  "gstack-document-release"
  "gstack-open-gstack-browser"
)

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Lotus global install needs '$1' to manage official gstack." >&2
    exit 1
  fi
}

need_cmd git
need_cmd bash
need_cmd bun

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    need_cmd node
    ;;
esac

mkdir -p "$GSTACK_PARENT"

case "$GSTACK_PROFILE" in
  core|design|review|deploy|full)
    ;;
  *)
    echo "Unsupported Lotus gstack profile: $GSTACK_PROFILE" >&2
    echo "Supported profiles: core, design, review, deploy, full" >&2
    exit 1
    ;;
esac

skill_in_list() {
  local skill_name="$1"
  shift
  local candidate

  for candidate in "$@"; do
    if [ "$candidate" = "$skill_name" ]; then
      return 0
    fi
  done
  return 1
}

should_expose_generated_skill() {
  local skill_name="$1"
  local allowed_skills=("${CORE_EXPOSED_GSTACK_SKILLS[@]}")

  case "$GSTACK_PROFILE" in
    core)
      ;;
    design)
      allowed_skills+=("${DESIGN_PROFILE_EXTRAS[@]}")
      ;;
    review)
      allowed_skills+=("${REVIEW_PROFILE_EXTRAS[@]}")
      ;;
    deploy)
      allowed_skills+=("${DEPLOY_PROFILE_EXTRAS[@]}")
      ;;
    full)
      return 0
      ;;
  esac

  skill_in_list "$skill_name" "${allowed_skills[@]}"
}

clone_fresh() {
  git clone --single-branch --depth 1 "$GSTACK_REPO_URL" "$GSTACK_DIR"
}

localized_gstack_description() {
  local skill_name="$1"
  local normalized_name="${skill_name#gstack-}"

  case "$normalized_name" in
    gstack)
      cat <<'EOF'
官方 gstack 工作流入口。用于调用完整的调研、评审、调试、QA 与发布能力。
EOF
      ;;
    autoplan)
      cat <<'EOF'
自动串联多轮计划评审，帮助你把方案从模糊想法收敛成可执行计划。
EOF
      ;;
    benchmark)
      cat <<'EOF'
做性能基准对比，检查页面加载、核心指标和资源体积有没有回退。
EOF
      ;;
    benchmark-models)
      cat <<'EOF'
对比不同模型在同一任务上的效果、速度和成本，方便做模型选型。
EOF
      ;;
    checkpoint)
      cat <<'EOF'
保存并恢复工作检查点，记录当前进度、决策和后续待办，方便无缝续上。
EOF
      ;;
    browse)
      cat <<'EOF'
快速无头浏览器。用于 QA、验站、走用户流程、截图和交互验证。
EOF
      ;;
    canary)
      cat <<'EOF'
部署后的金丝雀监控。持续观察线上报错、性能回退和页面异常。
EOF
      ;;
    careful)
      cat <<'EOF'
高风险操作安全模式。执行删除、强推、危险命令前先提醒你确认。
EOF
      ;;
    codex)
      cat <<'EOF'
在 gstack 流程里调用 Codex 专项能力，适合做更深的代码生成与审阅。
EOF
      ;;
    connect-chrome)
      cat <<'EOF'
启动由 gstack 控制的真实 Chrome，并自动加载侧边栏扩展，方便实时观看浏览器操作。
EOF
      ;;
    context-restore)
      cat <<'EOF'
恢复之前保存的工作上下文，方便中断后继续推进同一条任务线。
EOF
      ;;
    context-save)
      cat <<'EOF'
保存当前工作上下文、关键决策和剩余任务，方便后续接着做。
EOF
      ;;
    cso)
      cat <<'EOF'
安全负责人模式。检查基础设施、依赖、CI/CD、权限边界和 OWASP 风险。
EOF
      ;;
    design-consultation)
      cat <<'EOF'
设计顾问模式。梳理产品气质、视觉方向和完整设计系统，并沉淀成设计文档。
EOF
      ;;
    design-html)
      cat <<'EOF'
把已确认的设计方案落成可运行的生产级 HTML/CSS 页面。
EOF
      ;;
    design-review)
      cat <<'EOF'
设计质检模式。检查视觉一致性、层级、留白、动效和 AI 味过重的问题。
EOF
      ;;
    design-shotgun)
      cat <<'EOF'
批量生成多版设计方向，做对比、收集反馈，再快速迭代。
EOF
      ;;
    devex-review)
      cat <<'EOF'
开发者体验审查。实际走 onboarding、文档和命令流程，找出摩擦点。
EOF
      ;;
    document-release)
      cat <<'EOF'
发版后同步文档。把 README、架构说明、变更记录更新到和代码一致。
EOF
      ;;
    freeze)
      cat <<'EOF'
冻结编辑范围。限制本轮只能修改指定目录，避免误改无关文件。
EOF
      ;;
    upgrade)
      cat <<'EOF'
升级 gstack 到最新版本，并说明升级后有哪些变化。
EOF
      ;;
    guard)
      cat <<'EOF'
全量安全模式。组合危险命令提醒和目录级编辑限制，适合高风险场景。
EOF
      ;;
    health)
      cat <<'EOF'
代码健康度检查。汇总类型、lint、测试和死代码结果，给出整体分数。
EOF
      ;;
    investigate)
      cat <<'EOF'
系统化排查问题。先找根因，再提出修复，不允许靠猜测乱改代码。
EOF
      ;;
    land-and-deploy)
      cat <<'EOF'
落地并部署。合并、等待 CI、检查上线状态，再验证生产环境健康度。
EOF
      ;;
    learn)
      cat <<'EOF'
管理项目经验沉淀。回顾、搜索、清理和导出 gstack 的历史 learnings。
EOF
      ;;
    make-pdf)
      cat <<'EOF'
把内容整理成 PDF，适合生成可分享、可归档的正式文档输出。
EOF
      ;;
    office-hours)
      cat <<'EOF'
YC Office Hours 模式。用一组高质量问题帮你判断方向、需求和产品价值。
EOF
      ;;
    open-gstack-browser)
      cat <<'EOF'
打开可见的 gstack 浏览器，实时观看浏览器自动化和侧边栏活动。
EOF
      ;;
    pair-agent)
      cat <<'EOF'
把远程 AI agent 接到你的浏览器上，给它受控的页面访问能力。
EOF
      ;;
    plan-ceo-review)
      cat <<'EOF'
CEO 视角计划评审。重新看问题、挑战范围，判断方案是否足够有价值。
EOF
      ;;
    plan-design-review)
      cat <<'EOF'
设计视角计划评审。提前找出层级、交互和整体体验上的薄弱点。
EOF
      ;;
    plan-devex-review)
      cat <<'EOF'
开发者体验计划评审。提前检查文档、API、CLI 和 onboarding 是否顺手。
EOF
      ;;
    plan-eng-review)
      cat <<'EOF'
工程视角计划评审。锁定架构、数据流、风险点和测试覆盖策略。
EOF
      ;;
    plan-tune)
      cat <<'EOF'
调优 gstack 提问策略和开发者偏好，减少重复打断和无效追问。
EOF
      ;;
    qa)
      cat <<'EOF'
系统化做 QA 并修复发现的问题，适合“测一遍并顺手修掉”的场景。
EOF
      ;;
    qa-only)
      cat <<'EOF'
只做 QA 报告，不改代码。用于先拿一份问题清单和复现证据。
EOF
      ;;
    retro)
      cat <<'EOF'
工程周回顾。分析提交、工作模式和代码质量，沉淀本周经验。
EOF
      ;;
    review)
      cat <<'EOF'
合并前代码审查。优先抓 bug、风险、回归点和缺失测试。
EOF
      ;;
    setup-browser-cookies)
      cat <<'EOF'
把真实浏览器里的 cookies 导入测试浏览器，方便验证登录态页面。
EOF
      ;;
    setup-deploy)
      cat <<'EOF'
配置部署平台、生产地址和健康检查，为后续自动部署打基础。
EOF
      ;;
    ship)
      cat <<'EOF'
发版工作流。跑测试、审查差异、更新版本与变更记录，再推送交付。
EOF
      ;;
    unfreeze)
      cat <<'EOF'
解除冻结编辑范围，恢复本轮对整个项目的正常修改权限。
EOF
      ;;
    *)
      return 1
      ;;
  esac
}

rewrite_skill_description_block() {
  local skill_file="$1"
  local skill_name="$2"
  local localized
  local tmp_file

  localized="$(localized_gstack_description "$skill_name" || true)"
  if [ -z "$localized" ] || [ ! -f "$skill_file" ]; then
    return 0
  fi

  tmp_file="${skill_file}.lotus-tmp"

  awk -v localized="$localized" '
    BEGIN {
      frontmatter = 0
      skipping = 0
      localized_count = split(localized, localized_lines, "\n")
    }
    /^---$/ {
      if (frontmatter == 0) {
        frontmatter = 1
      } else if (frontmatter == 1) {
        frontmatter = 2
      }
      print
      next
    }
    frontmatter == 1 && /^description: \|$/ {
      print
      for (i = 1; i <= localized_count; i++) {
        if (localized_lines[i] != "") {
          print "  " localized_lines[i]
        }
      }
      skipping = 1
      next
    }
    frontmatter == 1 && skipping == 1 {
      if ($0 ~ /^[A-Za-z0-9_-]+:/ || $0 == "---") {
        skipping = 0
        print
      }
      next
    }
    {
      print
    }
  ' "$skill_file" > "$tmp_file"

  mv "$tmp_file" "$skill_file"
}

localize_skill_descriptions_in_dir() {
  local skills_dir="$1"
  local skill_dir
  local skill_name
  local skill_file

  if [ ! -d "$skills_dir" ]; then
    return 0
  fi

  for skill_dir in "$skills_dir"/*; do
    if [ -d "$skill_dir" ]; then
      skill_name="$(basename "$skill_dir")"
      skill_file="$skill_dir/SKILL.md"
      rewrite_skill_description_block "$skill_file" "$skill_name"
    fi
  done
}

reset_claude_managed_gstack_checkout() {
  local claude_gstack_dir="$HOME/.claude/skills/gstack"

  if [ -L "$claude_gstack_dir" ] || [ -d "$claude_gstack_dir" ]; then
    rm -rf "$claude_gstack_dir"
    echo "Cleared stale Claude-managed gstack checkout at $claude_gstack_dir"
  fi
}

claude_host_skill_name_for_generated_skill() {
  local skill_name="$1"
  local normalized_name="${skill_name#gstack-}"

  case "$normalized_name" in
    gstack)
      echo "gstack"
      ;;
    upgrade)
      echo "gstack-upgrade"
      ;;
    *)
      echo "$normalized_name"
      ;;
  esac
}

prune_claude_host_skills() {
  local generated_dir="$1"
  local target_dir="$2"
  local skill_dir
  local skill_name
  local host_skill_name
  local selected_host_skills=()
  local managed_host_skills=()
  local target_skill_dir
  local target_skill_name

  if [ ! -d "$target_dir" ] || [ ! -d "$generated_dir" ]; then
    return 0
  fi

  for skill_dir in "$generated_dir"/gstack*; do
    if [ -e "$skill_dir" ]; then
      skill_name="$(basename "$skill_dir")"
      host_skill_name="$(claude_host_skill_name_for_generated_skill "$skill_name")"
      managed_host_skills+=("$host_skill_name")
      if should_expose_generated_skill "$skill_name"; then
        selected_host_skills+=("$host_skill_name")
      fi
    fi
  done

  managed_host_skills+=("connect-chrome")

  for target_skill_dir in "$target_dir"/*; do
    if [ -d "$target_skill_dir" ]; then
      target_skill_name="$(basename "$target_skill_dir")"
      if skill_in_list "$target_skill_name" "${managed_host_skills[@]}" && \
        ! skill_in_list "$target_skill_name" "${selected_host_skills[@]}"; then
        rm -rf "$target_skill_dir"
      fi
    fi
  done

  echo "Pruned Claude top-level official gstack skills to profile $GSTACK_PROFILE"
}

sync_generated_host_skills() {
  local generated_dir="$1"
  local target_dir="$2"
  local host_name="$3"
  local staging_dir="$target_dir/.lotus-stage-gstack"
  local copied=0
  local generated_count=0
  local skill_name
  local final_path
  local backup_path
  local skill_dir
  local selected_skill_names=()

  if [ ! -d "$generated_dir" ]; then
    echo "Expected generated $host_name skills directory not found: $generated_dir" >&2
    exit 1
  fi

  mkdir -p "$target_dir"

  # Recover any previous interrupted swap before we stage a fresh sync.
  for backup_path in "$target_dir"/.lotus-backup-gstack*; do
    if [ -e "$backup_path" ]; then
      skill_name="$(basename "$backup_path")"
      skill_name="${skill_name#.lotus-backup-}"
      final_path="$target_dir/$skill_name"
      if [ ! -e "$final_path" ]; then
        mv "$backup_path" "$final_path"
      else
        rm -rf "$backup_path"
      fi
    fi
  done

  rm -rf "$staging_dir"
  mkdir -p "$staging_dir"

  for skill_dir in "$generated_dir"/gstack*; do
    if [ -e "$skill_dir" ]; then
      generated_count=$((generated_count + 1))
      skill_name="$(basename "$skill_dir")"
      if should_expose_generated_skill "$skill_name"; then
        cp -R "$skill_dir" "$staging_dir"/
        copied=$((copied + 1))
        selected_skill_names+=("$skill_name")
      fi
    fi
  done

  if [ "$generated_count" -lt 5 ]; then
    echo "Generated $host_name gstack skills look incomplete in: $generated_dir" >&2
    exit 1
  fi

  if [ "$copied" -lt 1 ]; then
    echo "Lotus gstack profile '$GSTACK_PROFILE' did not select any $host_name skills." >&2
    exit 1
  fi

  for skill_dir in "$staging_dir"/gstack*; do
    if [ -e "$skill_dir" ]; then
      skill_name="$(basename "$skill_dir")"
      final_path="$target_dir/$skill_name"
      backup_path="$target_dir/.lotus-backup-$skill_name"

      rm -rf "$backup_path"
      if [ -L "$final_path" ] || [ -e "$final_path" ]; then
        mv "$final_path" "$backup_path"
      fi
      mv "$skill_dir" "$final_path"
    fi
  done

  for final_path in "$target_dir"/gstack*; do
    if [ -e "$final_path" ]; then
      skill_name="$(basename "$final_path")"
      if ! skill_in_list "$skill_name" "${selected_skill_names[@]}"; then
        rm -rf "$final_path"
      fi
    fi
  done

  rm -rf "$staging_dir"
  find "$target_dir" -mindepth 1 -maxdepth 1 -name '.lotus-backup-gstack*' -exec rm -rf {} + 2>/dev/null || true

  echo "Synced $copied official gstack skills into $target_dir for $host_name (profile: $GSTACK_PROFILE)"
}

if [ -d "$GSTACK_DIR/.git" ]; then
  CURRENT_REMOTE="$(git -C "$GSTACK_DIR" remote get-url origin 2>/dev/null || true)"
  if [ "$CURRENT_REMOTE" != "$GSTACK_REPO_URL" ]; then
    BACKUP_DIR="${GSTACK_DIR}.lotus-bak-${TIMESTAMP}"
    mv "$GSTACK_DIR" "$BACKUP_DIR"
    echo "Backed up non-official gstack checkout to: $BACKUP_DIR"
    clone_fresh
  else
    git -C "$GSTACK_DIR" fetch origin main --depth 1
    git -C "$GSTACK_DIR" reset --hard FETCH_HEAD
  fi
elif [ -e "$GSTACK_DIR" ]; then
  BACKUP_DIR="${GSTACK_DIR}.lotus-bak-${TIMESTAMP}"
  mv "$GSTACK_DIR" "$BACKUP_DIR"
  echo "Backed up existing gstack path to: $BACKUP_DIR"
  clone_fresh
else
  clone_fresh
fi

cd "$GSTACK_DIR"

reset_claude_managed_gstack_checkout
./setup --host claude --team -q
./setup --host codex -q

localize_skill_descriptions_in_dir "$GSTACK_DIR/.agents/skills"
localize_skill_descriptions_in_dir "$HOME/.claude/skills"
prune_claude_host_skills "$GSTACK_DIR/.agents/skills" "$HOME/.claude/skills"

# Lotus does a final host-level sync after upstream setup so new installs and
# mid-stream upgrades land in a deterministic end state, even if the host had
# stale directories from older installs.
sync_generated_host_skills "$GSTACK_DIR/.agents/skills" "$HOME/.codex/skills" "Codex"

localize_skill_descriptions_in_dir "$HOME/.codex/skills"

./bin/gstack-config set auto_upgrade true >/dev/null 2>&1 || true
./bin/gstack-config set update_check true >/dev/null 2>&1 || true

VERSION="$(cat VERSION 2>/dev/null || echo unknown)"
echo "Managed official gstack ready at $GSTACK_DIR (version $VERSION)"
echo "Official gstack top-level profile: $GSTACK_PROFILE"
