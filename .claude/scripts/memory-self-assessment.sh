#!/bin/bash
# BetterAgents - Memory Self-Assessment Gate (Protocol §5b)
# Runs at Stop hook — checks if memory was written after file changes this response.
# Blocks response close if project files were modified but no memory entry was logged.
# Usage: Called automatically by .claude/settings.local.json Stop hook (runs BEFORE on-session-stop.sh)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

# No memory dir → skip silently
[ -d "$MEMORY_DIR" ] || exit 0
command -v jq &>/dev/null || exit 0

RESPONSE_CHANGED="$MEMORY_DIR/.response-changed"
LAST_MEMORY_COUNT="$MEMORY_DIR/.last-memory-count"

# ── No project files changed this response → exit cleanly ─────────────────────
if [ ! -f "$RESPONSE_CHANGED" ] || [ ! -s "$RESPONSE_CHANGED" ]; then
    [ -f "$RESPONSE_CHANGED" ] && rm -f "$RESPONSE_CHANGED"
    exit 0
fi

# ── Read files changed this response ──────────────────────────────────────────
CHANGED_FILES=$(cat "$RESPONSE_CHANGED")
FILE_COUNT=$(wc -l < "$RESPONSE_CHANGED" | tr -d ' ')

# Clear flag immediately — prevents re-triggering when Claude runs memory scripts
rm -f "$RESPONSE_CHANGED"

# ── Count current memory entries (tasks + decisions) ──────────────────────────
TASK_COUNT=$(jq '.tasks | length' "$MEMORY_DIR/progress.json" 2>/dev/null || echo 0)
DEC_COUNT=$(jq '.decisions | length' "$MEMORY_DIR/decision-log.json" 2>/dev/null || echo 0)
CURRENT_MEMORY=$(( TASK_COUNT + DEC_COUNT ))

# Baseline saved at UserPromptSubmit (before Claude's response began)
BASELINE_MEMORY=$(cat "$LAST_MEMORY_COUNT" 2>/dev/null || echo 0)
MEMORY_DELTA=$(( CURRENT_MEMORY - BASELINE_MEMORY ))

# ── Score §5b ─────────────────────────────────────────────────────────────────
# +1 file changed, +1 if 2+ files, +1 if code/config (non-doc) file
SCORE=1
[ "$FILE_COUNT" -ge 2 ] && SCORE=$(( SCORE + 1 ))
if echo "$CHANGED_FILES" | grep -qE '\.(sh|js|ts|py|json|go|rs|java|rb|c|cpp|cs|kt|swift|html|css|yml|yaml)$'; then
    SCORE=$(( SCORE + 1 ))
fi

# ── Update baseline for next response regardless of outcome ───────────────────
echo "$CURRENT_MEMORY" > "$LAST_MEMORY_COUNT"

# ── Evaluate ──────────────────────────────────────────────────────────────────
if [ "$SCORE" -ge 2 ] && [ "$MEMORY_DELTA" -le 0 ]; then
    cat <<MSG

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MEMORY GATE (Protocol §5b) — MEMORY WRITE REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files modified this response ($FILE_COUNT):
$(echo "$CHANGED_FILES" | sed 's/^/  • /')

Assessment score: $SCORE/3 — memory entry REQUIRED
Tasks logged: $TASK_COUNT | Decisions: $DEC_COUNT | Baseline: $BASELINE_MEMORY

AgentX: Run Protocol §5b NOW:

  bash .claude/scripts/add-task.sh \\
    TASK-NN "<title>" completed <agent> "<outcome>" <priority> "<tags>" <minutes>

After writing, respond "✅ Memory written" to close.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MSG
    exit 1
fi

# Score 1 (single doc file) — soft reminder only, non-blocking
if [ "$SCORE" -eq 1 ] && [ "$MEMORY_DELTA" -le 0 ]; then
    cat <<MSG
[§5b] File modified: $(echo "$CHANGED_FILES" | head -1) — consider: bash .claude/scripts/update-context.sh
MSG
fi

exit 0
