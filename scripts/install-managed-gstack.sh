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

./bin/gstack-config set auto_upgrade true >/dev/null 2>&1 || true
./bin/gstack-config set update_check true >/dev/null 2>&1 || true

VERSION="$(cat VERSION 2>/dev/null || echo unknown)"
echo "Managed official gstack ready at $GSTACK_DIR (version $VERSION)"
