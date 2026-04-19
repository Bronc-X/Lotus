#!/usr/bin/env bash
set -euo pipefail

GSTACK_REPO_URL="${LOTUS_GSTACK_REPO_URL:-https://github.com/garrytan/gstack.git}"
GSTACK_DIR="${LOTUS_GSTACK_DIR:-$HOME/.gstack/repos/gstack}"
GSTACK_PARENT="$(dirname "$GSTACK_DIR")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

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

clone_fresh() {
  git clone --single-branch --depth 1 "$GSTACK_REPO_URL" "$GSTACK_DIR"
}

sync_generated_host_skills() {
  local generated_dir="$1"
  local target_dir="$2"
  local host_name="$3"
  local staging_dir="$target_dir/.lotus-stage-gstack"
  local copied=0
  local skill_name
  local final_path
  local backup_path

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
      cp -R "$skill_dir" "$staging_dir"/
      copied=$((copied + 1))
    fi
  done

  if [ "$copied" -lt 5 ]; then
    echo "Generated $host_name gstack skills look incomplete in: $generated_dir" >&2
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

  rm -rf "$staging_dir"
  find "$target_dir" -mindepth 1 -maxdepth 1 -name '.lotus-backup-gstack*' -exec rm -rf {} + 2>/dev/null || true

  echo "Synced $copied official gstack skills into $target_dir for $host_name"
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

./setup --host claude --team -q
./setup --host codex -q
./setup --host opencode -q

# Lotus does a final host-level sync after upstream setup so new installs and
# mid-stream upgrades land in a deterministic end state, even if the host had
# stale directories from older installs.
sync_generated_host_skills "$GSTACK_DIR/.agents/skills" "$HOME/.codex/skills" "Codex"
sync_generated_host_skills "$GSTACK_DIR/.opencode/skills" "$HOME/.config/opencode/skills" "OpenCode"
sync_generated_host_skills "$GSTACK_DIR/.cursor/skills" "$HOME/.cursor/skills" "Cursor"

./bin/gstack-config set auto_upgrade true >/dev/null 2>&1 || true
./bin/gstack-config set update_check true >/dev/null 2>&1 || true

VERSION="$(cat VERSION 2>/dev/null || echo unknown)"
echo "Managed official gstack ready at $GSTACK_DIR (version $VERSION)"
