#!/usr/bin/env bash
# BetterAgents — add-pattern.sh
# CLI to append a pattern entry to patterns.json
#
# Usage:
#   bash .claude/scripts/add-pattern.sh <name> <category> <context> [agent] [solution] [tags_csv]
#
# Arguments:
#   name      Pattern name in kebab-case, e.g. atomic-json-write
#   category  architectural | design | implementation | testing | deployment | security
#   context   The problem this pattern solves (use quotes)
#   agent     Agent that identified the pattern (default: agentx)
#   solution  How the pattern is applied — the implementation approach (use quotes)
#   tags_csv  Comma-separated tags, e.g. "memory,reliability,json"  (default: "")
#
# The script auto-generates:
#   - id: PAT-NN (sequential based on current count)
#   - title: Human-readable version of name (kebab-case → Title Case)
#   - date: current ISO8601 timestamp
#   - applications: 0 (incremented manually as pattern is reused)
#
# Example:
#   bash .claude/scripts/add-pattern.sh \
#     "atomic-json-write" architectural \
#     "Direct bash writes to JSON files are not atomic — concurrent writes corrupt the file" \
#     agentx \
#     "Use jq to read, transform, and write to a temp file, then mv atomically. Never use echo or >> directly on JSON." \
#     "memory,json,reliability"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
PATTERNS_FILE="$MEMORY_DIR/patterns.json"

# ── Validate dependencies ─────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
    echo "ERROR: jq is required but not found in PATH." >&2
    exit 1
fi

# ── Validate required arguments ───────────────────────────────────────────────
if [ $# -lt 3 ]; then
    echo "Usage: bash add-pattern.sh <name> <category> <context> [agent] [solution] [tags_csv]" >&2
    echo ""                                                                                        >&2
    echo "  name      Pattern name in kebab-case, e.g. atomic-json-write"                         >&2
    echo "  category  architectural | design | implementation | testing | deployment | security"   >&2
    echo "  context   The problem this pattern solves (use quotes)"                                >&2
    echo "  agent     Agent that identified the pattern (default: agentx)"                         >&2
    echo "  solution  How the pattern is applied (use quotes)"                                     >&2
    echo "  tags_csv  Comma-separated tags, e.g. \"memory,json\""                                 >&2
    exit 1
fi

PAT_NAME="$1"
PAT_CATEGORY="$2"
PAT_CONTEXT="$3"
PAT_AGENT="${4:-agentx}"
PAT_SOLUTION="${5:-}"
PAT_TAGS_CSV="${6:-}"

# ── Validate category value ───────────────────────────────────────────────────
case "$PAT_CATEGORY" in
    architectural|design|implementation|testing|deployment|security) ;;
    *)
        echo "ERROR: Invalid category '$PAT_CATEGORY'. Must be one of: architectural | design | implementation | testing | deployment | security" >&2
        exit 1
        ;;
esac

# ── Validate file exists ──────────────────────────────────────────────────────
if [ ! -f "$PATTERNS_FILE" ]; then
    echo "ERROR: patterns.json not found at $PATTERNS_FILE" >&2
    exit 1
fi

# ── Create backup before write (atomic write safety) ──────────────────────────
BACKUP_FILE="$PATTERNS_FILE.bak"
cp "$PATTERNS_FILE" "$BACKUP_FILE" 2>/dev/null || {
    echo "WARNING: Could not create backup at $BACKUP_FILE" >&2
}

# ── Build ISO8601 timestamp ───────────────────────────────────────────────────
NOW=$(date '+%Y-%m-%dT%H:%M:%S%z')

# ── Auto-generate PAT-NN id based on current count ───────────────────────────
CURRENT_COUNT=$(jq '.patterns | length' "$PATTERNS_FILE")
NEXT_NUM=$(( CURRENT_COUNT + 1 ))
PAT_ID=$(printf "PAT-%02d" "$NEXT_NUM")

# ── Convert kebab-case name to Title Case for title ──────────────────────────
PAT_TITLE=$(echo "$PAT_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')

# ── Convert comma-separated tags to JSON array ────────────────────────────────
if [ -n "$PAT_TAGS_CSV" ]; then
    TAGS_JSON=$(echo "$PAT_TAGS_CSV" | jq -R 'split(",")')
else
    TAGS_JSON='[]'
fi

# ── Atomic write: append to .patterns array AND to .categories[category] ──────
jq \
    --arg id          "$PAT_ID" \
    --arg name        "$PAT_NAME" \
    --arg title       "$PAT_TITLE" \
    --arg category    "$PAT_CATEGORY" \
    --arg context     "$PAT_CONTEXT" \
    --arg solution    "$PAT_SOLUTION" \
    --arg agent       "$PAT_AGENT" \
    --arg now         "$NOW" \
    --argjson tags    "$TAGS_JSON" \
    '
    # Build the new pattern object with all dashboard-required fields
    . as $root
    | {
        id:           $id,
        name:         $name,
        title:        $title,
        category:     $category,
        date:         $now,
        createdAt:    $now,
        agent:        $agent,
        applications: 0,
        usageCount:   0,
        tags:         $tags,
        context:      $context,
        description:  $context,
        solution:     $solution
      } as $entry

    # Append to top-level .patterns array
    | .patterns += [$entry]

    # Append to the matching category sub-array (create if missing)
    | .categories[$category] = ((.categories[$category] // []) + [$entry])

    # Update summary counters
    | .summary.totalPatterns = (.patterns | length)
    | .summary.byCategory[$category] = ((.summary.byCategory[$category] // 0) + 1)
    | .summary.byAgent[$agent]        = ((.summary.byAgent[$agent]        // 0) + 1)

    # Update timestamps
    | .lastUpdated              = $now
    | .metadata.lastPatternScan = $now
    ' \
    "$PATTERNS_FILE" > /tmp/_mem_pattern_tmp.json

# ── Validate the new JSON is well-formed ──────────────────────────────────────
if ! jq empty /tmp/_mem_pattern_tmp.json 2>/dev/null; then
    echo "ERROR: Corrupted JSON written to temp file. Rolling back from backup." >&2
    cp "$BACKUP_FILE" "$PATTERNS_FILE" 2>/dev/null || {
        echo "CRITICAL: Rollback failed. Check $BACKUP_FILE manually." >&2
        exit 1
    }
    exit 1
fi

# ── Atomic move: temp → final (fail if target write failed) ───────────────────
mv /tmp/_mem_pattern_tmp.json "$PATTERNS_FILE" || {
    echo "ERROR: Failed to move temp file to $PATTERNS_FILE. Rolling back." >&2
    cp "$BACKUP_FILE" "$PATTERNS_FILE" 2>/dev/null
    exit 1
}

echo "💾 Pattern saved: $PAT_ID — $PAT_TITLE [$PAT_CATEGORY]"
echo "   Backup: $BACKUP_FILE"
