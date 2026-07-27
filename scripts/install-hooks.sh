#!/usr/bin/env bash
# Install the repo's git hooks into .git/hooks (which git does not version).
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cp "$repo_root/scripts/hooks/pre-push" "$repo_root/.git/hooks/pre-push"
chmod +x "$repo_root/.git/hooks/pre-push"
echo "installed pre-push hook"
