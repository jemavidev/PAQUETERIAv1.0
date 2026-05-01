#!/bin/bash
# BetterAgents - Fast Dashboard Rebuild
# Rebuilds dashboard from current memory files WITHOUT slow project-size calculation
# Called automatically when memory files change (via hooks)
# Usage: bash quick-dashboard.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec 2>/dev/null

# 1. Recalculate memory token stats
bash "$SCRIPT_DIR/memory-stats.sh" 2>/dev/null || true

# 2. Rebuild dashboard HTML with fresh embedded JSON
bash "$SCRIPT_DIR/update-dashboard.sh" 2>/dev/null || true

exit 0
