#!/usr/bin/env bash
# Plan Mode Tracker — PreToolUse hook for EnterPlanMode
# Fires every time AgentX triggers plan mode before a complex task

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/increment-safety-metric.sh" planModeTriggered 2>/dev/null

# Log to active-context.json recentChanges
MEMORY_DIR="$SCRIPT_DIR/../memory"
TS=$(date -Iseconds 2>/dev/null || date)

ENTRY=$(jq -n --arg ts "$TS" \
  '{"timestamp": $ts, "file": "plan-mode", "name": "EnterPlanMode triggered", "category": "safety"}')

TMP=$(mktemp)
if jq --argjson e "$ENTRY" \
  '.context.recentChanges = ([$e] + (.context.recentChanges // []) | .[0:15])' \
  "$MEMORY_DIR/active-context.json" > "$TMP" 2>/dev/null; then
  mv "$TMP" "$MEMORY_DIR/active-context.json"
else
  rm -f "$TMP"
fi
