#!/bin/bash
# BetterAgents - Bash Tool PostToolUse Hook
# Detects when a Bash command wrote to memory files and triggers a fast dashboard rebuild
# Usage: Called automatically by .claude/settings.local.json PostToolUse hook (Bash matcher)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec 2>/dev/null

command -v jq &>/dev/null || exit 0

# Read the bash command that was executed
TOOL_COMMAND=$(echo "${CLAUDE_TOOL_INPUT:-}" | jq -r '.command // ""' 2>/dev/null || echo "")

# Only act if command touched .claude/memory/ files
[[ "$TOOL_COMMAND" == *".claude/memory/"* ]] || exit 0

# Skip if it's only active-context.json (handled by on-file-change.sh)
# But act if it touched decision-log, progress, patterns, llm-usage, etc.
if [[ "$TOOL_COMMAND" != *"decision-log"* ]] && \
   [[ "$TOOL_COMMAND" != *"progress"* ]] && \
   [[ "$TOOL_COMMAND" != *"patterns"* ]] && \
   [[ "$TOOL_COMMAND" != *"llm-usage"* ]] && \
   [[ "$TOOL_COMMAND" != *"memory-stats"* ]]; then
    exit 0
fi

# Memory write detected — trigger fast dashboard rebuild in background (non-blocking)
bash "$SCRIPT_DIR/quick-dashboard.sh" 2>/dev/null &

exit 0
