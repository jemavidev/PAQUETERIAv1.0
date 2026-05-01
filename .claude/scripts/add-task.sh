#!/usr/bin/env bash
# BetterAgents — add-task.sh
# CLI to append a task entry to progress.json
#
# Usage:
#   bash .claude/scripts/add-task.sh <id> <title> <status> <agent> [outcome] [priority] [tags_csv] [duration_min]
#
# Arguments:
#   id           Task identifier, e.g. TASK-07
#   title        Short description (use quotes for multi-word)
#   status       todo | in-progress | blocked | completed | cancelled
#   agent        Agent name that owns this task, e.g. coder
#   outcome      What was done / what will be done (use quotes). Defaults to title.
#   priority     critical | high | medium | low  (default: medium)
#   tags_csv     Comma-separated tags, e.g. "bugfix,dashboard,memory"  (default: "")
#   duration_min Approximate time spent in minutes (number, default: 0)
#
# Example:
#   bash .claude/scripts/add-task.sh TASK-07 \
#     "Populate token-accounting.json with real data" \
#     completed coder \
#     "Extracted real token counts from llm-usage.json. Updated token-accounting.json with per-session breakdown. Fixed TOKEN USAGE TREND chart scale." \
#     medium "tokens,dashboard,charts" 35

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
PROGRESS_FILE="$MEMORY_DIR/progress.json"

# ── Validate dependencies ─────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
    echo "ERROR: jq is required but not found in PATH." >&2
    exit 1
fi

# ── Validate required arguments ───────────────────────────────────────────────
if [ $# -lt 4 ]; then
    echo "Usage: bash add-task.sh <id> <title> <status> <agent> [outcome] [priority] [tags_csv] [duration_min]" >&2
    echo ""                                                                                   >&2
    echo "  id           Task identifier, e.g. TASK-07"                                      >&2
    echo "  title        Short description (use quotes for multi-word)"                       >&2
    echo "  status       todo | in-progress | blocked | completed | cancelled"                >&2
    echo "  agent        Agent name that owns this task, e.g. coder"                          >&2
    echo "  outcome      What was done / will be done (default: same as title)"               >&2
    echo "  priority     critical | high | medium | low  (default: medium)"                   >&2
    echo "  tags_csv     Comma-separated tags, e.g. \"bugfix,dashboard\""                    >&2
    echo "  duration_min Time spent in minutes (default: 0)"                                  >&2
    exit 1
fi

TASK_ID="$1"
TASK_TITLE="$2"
TASK_STATUS="$3"
TASK_AGENT="$4"
TASK_OUTCOME="${5:-$2}"
TASK_PRIORITY="${6:-medium}"
TASK_TAGS_CSV="${7:-}"
TASK_DURATION="${8:-0}"

# ── Validate status value ─────────────────────────────────────────────────────
case "$TASK_STATUS" in
    todo|in-progress|blocked|completed|cancelled) ;;
    *)
        echo "ERROR: Invalid status '$TASK_STATUS'. Must be one of: todo | in-progress | blocked | completed | cancelled" >&2
        exit 1
        ;;
esac

# ── Validate priority value ───────────────────────────────────────────────────
case "$TASK_PRIORITY" in
    critical|high|medium|low) ;;
    *)
        echo "ERROR: Invalid priority '$TASK_PRIORITY'. Must be one of: critical | high | medium | low" >&2
        exit 1
        ;;
esac

# ── Validate file exists ──────────────────────────────────────────────────────
if [ ! -f "$PROGRESS_FILE" ]; then
    echo "ERROR: progress.json not found at $PROGRESS_FILE" >&2
    exit 1
fi

# ── Create backup before write (atomic write safety) ──────────────────────────
BACKUP_FILE="$PROGRESS_FILE.bak"
cp "$PROGRESS_FILE" "$BACKUP_FILE" 2>/dev/null || {
    echo "WARNING: Could not create backup at $BACKUP_FILE" >&2
}

# ── Build ISO8601 timestamp ───────────────────────────────────────────────────
NOW=$(date '+%Y-%m-%dT%H:%M:%S%z')

# ── Convert comma-separated tags to JSON array ────────────────────────────────
if [ -n "$TASK_TAGS_CSV" ]; then
    TAGS_JSON=$(echo "$TASK_TAGS_CSV" | jq -R 'split(",")')
else
    TAGS_JSON='[]'
fi

# ── Compute triviality score from status ─────────────────────────────────────
# Automated tasks (score 4-5) are typically sync/housekeeping
if [ "$TASK_STATUS" = "completed" ] && [ "$TASK_DURATION" -le 5 ] 2>/dev/null; then
    TRIVIALITY_SCORE=4
    TRIVIALITY_AUTO="true"
else
    TRIVIALITY_SCORE=2
    TRIVIALITY_AUTO="false"
fi

# ── Atomic write: append task + update summary counters ───────────────────────
jq \
    --arg id          "$TASK_ID" \
    --arg title       "$TASK_TITLE" \
    --arg status      "$TASK_STATUS" \
    --arg agent       "$TASK_AGENT" \
    --arg outcome     "$TASK_OUTCOME" \
    --arg priority    "$TASK_PRIORITY" \
    --arg now         "$NOW" \
    --argjson tags    "$TAGS_JSON" \
    --argjson dur     "$TASK_DURATION" \
    --argjson tscore  "$TRIVIALITY_SCORE" \
    --argjson tauto   "$TRIVIALITY_AUTO" \
    '
    # Build new task entry with all dashboard-required fields
    {
        id:          $id,
        title:       $title,
        status:      $status,
        agent:       $agent,
        priority:    $priority,
        date:        $now,
        createdAt:   $now,
        updatedAt:   $now,
        duration:    $dur,
        tags:        $tags,
        triviality:  { score: $tscore, automated: $tauto },
        outcome:     $outcome,
        description: $outcome
    } as $entry

    | .tasks += [$entry]

    # Update summary counters
    | .summary.totalTasks = (.tasks | length)
    | .summary.byStatus[$status]    = ((.summary.byStatus[$status]    // 0) + 1)
    | .summary.byAgent[$agent]      = ((.summary.byAgent[$agent]      // 0) + 1)
    | .summary.byPriority[$priority] = ((.summary.byPriority[$priority] // 0) + 1)

    # Recompute completion rate
    | .summary.completionRate = (
        ((.tasks | map(select(.status == "completed")) | length) * 100)
        / (.tasks | length)
        | floor
      )

    # Update top-level timestamp + metadata
    | .lastUpdated = $now
    | .metadata.totalEntries = (.tasks | length)
    | .metadata.lastUpdated  = $now
    ' \
    "$PROGRESS_FILE" > /tmp/_mem_task_tmp.json

# ── Validate the new JSON is well-formed ──────────────────────────────────────
if ! jq empty /tmp/_mem_task_tmp.json 2>/dev/null; then
    echo "ERROR: Corrupted JSON written to temp file. Rolling back from backup." >&2
    cp "$BACKUP_FILE" "$PROGRESS_FILE" 2>/dev/null || {
        echo "CRITICAL: Rollback failed. Check $BACKUP_FILE manually." >&2
        exit 1
    }
    exit 1
fi

# ── Atomic move: temp → final (fail if target write failed) ───────────────────
mv /tmp/_mem_task_tmp.json "$PROGRESS_FILE" || {
    echo "ERROR: Failed to move temp file to $PROGRESS_FILE. Rolling back." >&2
    cp "$BACKUP_FILE" "$PROGRESS_FILE" 2>/dev/null
    exit 1
}

echo "💾 Task added: $TASK_ID — $TASK_TITLE [$TASK_STATUS / $TASK_PRIORITY]"
echo "   Backup: $BACKUP_FILE"
