#!/usr/bin/env bash
# Regenerate all self-hosted profile cards from the authenticated GitHub API.
# Run manually any time, or let the pre-push hook / weekly workflow call it.
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/gen_header.py
python scripts/gen_langs.py
python scripts/gen_stats.py
echo "cards regenerated in assets/"
