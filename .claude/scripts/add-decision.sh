#!/usr/bin/env bash
# BetterAgents — add-decision.sh
# CLI to append a decision entry to decision-log.json
#
# Usage:
#   bash .claude/scripts/add-decision.sh <id> <title> <context> <agent> [status] [tags_csv]
#
# Arguments:
#   id          Decision identifier, e.g. DEC-05
#   title       Short decision title (use quotes for multi-word)
#   context     Why the decision was needed — the problem being solved (use quotes)
#   agent       Agent that made the decision: architect | coder | agentx | etc.
#   status      proposed | approved | implemented | rejected | superseded  (default: implemented)
#   tags_csv    Comma-separated tags, e.g. "dashboard,bugfix,memory"  (default: "")
#
# After running this script, AgentX can enrich the entry further by editing
# the JSON directly to add .decision and .consequences fields.
#
# Example:
#   bash .claude/scripts/add-decision.sh DEC-05 \
#     "Use jq for atomic JSON writes" \
#     "Direct bash writes corrupt JSON on concurrent access — jq produces valid output atomically" \
#     architect implemented "memory,reliability"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
DECISION_FILE="$MEMORY_DIR/decision-log.json"

# ── Validate dependencies ─────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
    echo "ERROR: jq is required but not found in PATH." >&2
    exit 1
fi

# ── Validate required arguments ───────────────────────────────────────────────
if [ $# -lt 4 ]; then
    echo "Usage: bash add-decision.sh <id> <title> <context> <agent> [status] [tags_csv]" >&2
    echo ""                                                                                 >&2
    echo "  id        Decision identifier, e.g. DEC-05"                                    >&2
    echo "  title     Short decision title (use quotes for multi-word)"                     >&2
    echo "  context   Why this decision was needed — the problem being solved"              >&2
    echo "  agent     Agent that made the decision, e.g. architect"                         >&2
    echo "  status    proposed | approved | implemented | rejected | superseded"            >&2
    echo "            (default: implemented)"                                                >&2
    echo "  tags_csv  Comma-separated tags, e.g. \"dashboard,bugfix\""                     >&2
    exit 1
fi

DEC_ID="$1"
DEC_TITLE="$2"
DEC_CONTEXT="$3"
DEC_AGENT="$4"
DEC_STATUS="${5:-implemented}"
DEC_TAGS_CSV="${6:-}"

# ── Validate status value ─────────────────────────────────────────────────────
case "$DEC_STATUS" in
    proposed|approved|implemented|rejected|superseded) ;;
    *)
        echo "ERROR: Invalid status '$DEC_STATUS'. Must be one of: proposed | approved | implemented | rejected | superseded" >&2
        exit 1
        ;;
esac

# ── Validate file exists ──────────────────────────────────────────────────────
if [ ! -f "$DECISION_FILE" ]; then
    echo "ERROR: decision-log.json not found at $DECISION_FILE" >&2
    exit 1
fi

# ── Create backup before write (atomic write safety) ──────────────────────────
BACKUP_FILE="$DECISION_FILE.bak"
cp "$DECISION_FILE" "$BACKUP_FILE" 2>/dev/null || {
    echo "WARNING: Could not create backup at $BACKUP_FILE" >&2
}

# ── Build ISO8601 timestamp ───────────────────────────────────────────────────
NOW=$(date '+%Y-%m-%dT%H:%M:%S%z')

# ── Convert comma-separated tags to JSON array ────────────────────────────────
if [ -n "$DEC_TAGS_CSV" ]; then
    TAGS_JSON=$(echo "$DEC_TAGS_CSV" | jq -R 'split(",")')
else
    TAGS_JSON='[]'
fi

# ── Atomic write: append decision + update summary counters ───────────────────
jq \
    --arg id      "$DEC_ID" \
    --arg title   "$DEC_TITLE" \
    --arg context "$DEC_CONTEXT" \
    --arg agent   "$DEC_AGENT" \
    --arg status  "$DEC_STATUS" \
    --arg now     "$NOW" \
    --argjson tags "$TAGS_JSON" \
    '
    # Build new decision entry with all dashboard-required fields
    . as $root
    | {
        id:        $id,
        title:     $title,
        date:      $now,
        timestamp: $now,
        agent:     $agent,
        status:    $status,
        tags:      $tags,
        context:   $context,
        rationale: $context,
        decision:  "",
        consequences: {
            positive: [],
            negative: [],
            risks:    []
        }
      } as $entry

    | .decisions += [$entry]

    # Update summary counters
    | .summary.totalDecisions = (.decisions | length)
    | .summary.byStatus[$status] = ((.summary.byStatus[$status] // 0) + 1)
    | .summary.byAgent[$agent]   = ((.summary.byAgent[$agent]   // 0) + 1)

    # Update top-level timestamp
    | .lastUpdated = $now
    ' \
    "$DECISION_FILE" > /tmp/_mem_decision_tmp.json

# ── Validate the new JSON is well-formed ──────────────────────────────────────
if ! jq empty /tmp/_mem_decision_tmp.json 2>/dev/null; then
    echo "ERROR: Corrupted JSON written to temp file. Rolling back from backup." >&2
    cp "$BACKUP_FILE" "$DECISION_FILE" 2>/dev/null || {
        echo "CRITICAL: Rollback failed. Check $BACKUP_FILE manually." >&2
        exit 1
    }
    exit 1
fi

# ── Atomic move: temp → final (fail if target write failed) ───────────────────
mv /tmp/_mem_decision_tmp.json "$DECISION_FILE" || {
    echo "ERROR: Failed to move temp file to $DECISION_FILE. Rolling back." >&2
    cp "$BACKUP_FILE" "$DECISION_FILE" 2>/dev/null
    exit 1
}

echo "💾 Decision logged: $DEC_ID — $DEC_TITLE [$DEC_STATUS]"
echo "   Backup: $BACKUP_FILE"
echo "   ℹ️  Enrich .decision and .consequences fields directly in decision-log.json"
