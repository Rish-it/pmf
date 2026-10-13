#!/bin/sh
# Install the pmf skills into the global skills folder of each agent.
#
# Usage:
#   ./install.sh            symlink the skills into all three agents
#   ./install.sh --copy     copy instead of symlinking (survives moving the repo)
#   ./install.sh --uninstall  remove them again
#
# Targets: ~/.claude/skills, ~/.codex/skills, ~/.config/opencode/skills

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE="link"
ACTION="install"

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --uninstall) ACTION="uninstall" ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

count=0
for rel in .claude/skills .codex/skills .config/opencode/skills; do
  target="$HOME/$rel"
  mkdir -p "$target"
  for skill in "$ROOT"/skills/pmf*; do
    name=$(basename "$skill")
    rm -rf "$target/$name"
    if [ "$ACTION" = "install" ]; then
      if [ "$MODE" = "copy" ]; then
        cp -R "$skill" "$target/$name"
      else
        ln -s "$skill" "$target/$name"
      fi
      count=$((count + 1))
    fi
  done
  echo "$ACTION: $target"
done

if [ "$ACTION" = "install" ]; then
  echo "done: $((count / 3)) skills in each of the three agent skills folders"
fi
