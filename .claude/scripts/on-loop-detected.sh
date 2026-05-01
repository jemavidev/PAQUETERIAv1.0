#!/usr/bin/env bash
# Loop Detection Tracker
# Called by AgentX when anti-loop protocol activates (model cooperation)
# Also called by on-file-change.sh heuristic when same file edited repeatedly
#
# Usage: bash on-loop-detected.sh [reason]
# Example: bash .claude/scripts/on-loop-detected.sh "same file edited 3x"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REASON="${1:-unknown}"

bash "$SCRIPT_DIR/increment-safety-metric.sh" loopDetections 2>/dev/null

# Append to active-context.json for visibility
MEMORY_DIR="$SCRIPT_DIR/../memory"
TS=$(date -Iseconds 2>/dev/null || date)

ENTRY=$(jq -n --arg ts "$TS" --arg reason "$REASON" \
  '{"timestamp": $ts, "file": "anti-loop", "name": ("Loop detected: " + $reason), "category": "safety"}')

TMP=$(mktemp)
if jq --argjson e "$ENTRY" \
  '.context.recentChanges = ([$e] + (.context.recentChanges // []) | .[0:15])' \
  "$MEMORY_DIR/active-context.json" > "$TMP" 2>/dev/null; then
  mv "$TMP" "$MEMORY_DIR/active-context.json"
else
  rm -f "$TMP"
fi

echo "⚠️ Loop detection recorded: $REASON" >&2
