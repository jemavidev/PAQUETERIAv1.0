#!/usr/bin/env bash
# BetterAgents — update-context.sh
# Updates active-context.json with current project state
#
# Usage:
#   bash .claude/scripts/update-context.sh [FLAGS]
#
# Flags:
#   --phase <text>              Update project.phase
#   --focus <text>              Update currentFocus.feature
#   --objective <text>          Update currentFocus.objective
#   --priority <level>          Update currentFocus.priority (high|medium|low)
#   --next-step <text>          Append one step to nextSteps[]
#   --clear-next-steps          Clear all nextSteps entries
#   --blocker <text>            Append one blocker to blockers[]
#   --clear-blockers            Clear all blockers entries
#   --stats-completed <N>       Set context.stats.completedTasks
#   --stats-pending <N>         Set context.stats.pendingTasks
#   --add-change <name> <file> <category> <summary>
#                               Prepend a recentChanges entry (max 6 kept)
#   --add-decision <id> <title> <category>
#                               Append to context.recentDecisions (max 3 kept)
#   --add-pattern <id> <name> <category>
#                               Append to context.activePatterns (max 3 kept)
#
# Example:
#   bash .claude/scripts/update-context.sh \
#     --phase "3.7 — Token accounting live" \
#     --focus "Populate charts with real token data" \
#     --objective "Fix flat TOKEN USAGE TREND chart by extracting real values from llm-usage.json" \
#     --priority high \
#     --next-step "Fix CODE QUALITY TREND — needs real metrics source" \
#     --stats-completed 7 --stats-pending 3 \
#     --add-change "Fix: TOKEN USAGE TREND chart" "token-accounting.json" "bugfix" \
#       "Extracted real token counts from llm-usage.json into token-accounting.json history array"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
CONTEXT_FILE="$MEMORY_DIR/active-context.json"

if ! command -v jq &>/dev/null; then
    echo "❌ jq not found. Install with: sudo apt install jq"
    exit 1
fi

if [ ! -f "$CONTEXT_FILE" ]; then
    echo "❌ active-context.json not found at $CONTEXT_FILE"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: bash update-context.sh [FLAGS]"
    echo ""
    echo "Flags:"
    echo "  --phase <text>               Update project.phase"
    echo "  --focus <text>               Update currentFocus.feature"
    echo "  --objective <text>           Update currentFocus.objective"
    echo "  --priority high|medium|low   Update currentFocus.priority"
    echo "  --next-step <text>           Append to nextSteps[]"
    echo "  --clear-next-steps           Clear nextSteps[]"
    echo "  --blocker <text>             Append to blockers[]"
    echo "  --clear-blockers             Clear blockers[]"
    echo "  --stats-completed <N>        Set context.stats.completedTasks"
    echo "  --stats-pending <N>          Set context.stats.pendingTasks"
    echo "  --add-change <name> <file> <category> <summary>"
    echo "                               Prepend recentChanges entry"
    echo "  --add-decision <id> <title> <category>"
    echo "                               Append to context.recentDecisions (max 3)"
    echo "  --add-pattern <id> <name> <category>"
    echo "                               Append to context.activePatterns (max 3)"
    exit 0
fi

TIMESTAMP=$(date -Iseconds)

# ── Start with identity transform, apply patches one by one ──────────────────
CURRENT=$(cat "$CONTEXT_FILE")

apply_jq() {
    CURRENT=$(echo "$CURRENT" | jq "$@")
}

# ── Parse and apply flags ─────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --phase)
            apply_jq --arg v "$2" '.project.phase = $v'
            echo "   Phase: $2"
            shift 2
            ;;
        --focus)
            apply_jq --arg v "$2" '.currentFocus.feature = $v'
            echo "   Focus: $2"
            shift 2
            ;;
        --objective)
            apply_jq --arg v "$2" '.currentFocus.objective = $v'
            echo "   Objective: $2"
            shift 2
            ;;
        --priority)
            apply_jq --arg v "$2" '.currentFocus.priority = $v'
            echo "   Priority: $2"
            shift 2
            ;;
        --next-step)
            apply_jq --arg v "$2" '.nextSteps += [$v]'
            echo "   Next step added: $2"
            shift 2
            ;;
        --clear-next-steps)
            apply_jq '.nextSteps = []'
            echo "   Next steps cleared"
            shift
            ;;
        --blocker)
            apply_jq --arg v "$2" '.blockers += [$v]'
            echo "   Blocker added: $2"
            shift 2
            ;;
        --clear-blockers)
            apply_jq '.blockers = []'
            echo "   Blockers cleared"
            shift
            ;;
        --stats-completed)
            apply_jq --argjson v "$2" '.context.stats.completedTasks = $v'
            echo "   Stats completed: $2"
            shift 2
            ;;
        --stats-pending)
            apply_jq --argjson v "$2" '.context.stats.pendingTasks = $v'
            echo "   Stats pending: $2"
            shift 2
            ;;
        --add-change)
            # --add-change <name> <file> <category> <summary>
            CHG_NAME="$2"
            CHG_FILE="$3"
            CHG_CAT="$4"
            CHG_SUM="$5"
            # Build the new entry and prepend
            CURRENT=$(echo "$CURRENT" | jq \
                --arg name    "$CHG_NAME" \
                --arg file    "$CHG_FILE" \
                --arg cat     "$CHG_CAT" \
                --arg summary "$CHG_SUM" \
                --arg ts      "$TIMESTAMP" \
                '
                .recentChanges = (
                    [{
                        name:      $name,
                        file:      $file,
                        category:  $cat,
                        timestamp: $ts,
                        summary:   $summary
                    }] + (.recentChanges // [])
                ) | .recentChanges = .recentChanges[0:6]
                ')
            echo "   Recent change added: $CHG_NAME ($CHG_CAT)"
            shift 5
            ;;
        --add-decision)
            # --add-decision <id> <title> <category>
            apply_jq \
                --arg id    "$2" \
                --arg title "$3" \
                --arg cat   "$4" \
                '
                .context.recentDecisions = (
                    (.context.recentDecisions // []) + [{ id: $id, title: $title, category: $cat }]
                ) | .context.recentDecisions = .context.recentDecisions[-3:]
                '
            echo "   Decision added to context: $2"
            shift 4
            ;;
        --add-pattern)
            # --add-pattern <id> <name> <category>
            apply_jq \
                --arg id   "$2" \
                --arg name "$3" \
                --arg cat  "$4" \
                '
                .context.activePatterns = (
                    (.context.activePatterns // []) + [{ id: $id, name: $name, category: $cat }]
                ) | .context.activePatterns = .context.activePatterns[-3:]
                '
            echo "   Pattern added to context: $2 ($3)"
            shift 4
            ;;
        *)
            echo "WARNING: Unknown flag '$1' — skipped" >&2
            shift
            ;;
    esac
done

# ── Always update lastUpdated and stats.lastUpdate ────────────────────────────
CURRENT=$(echo "$CURRENT" | jq \
    --arg ts "$TIMESTAMP" \
    --arg date "$(date '+%Y-%m-%d')" \
    '
    .lastUpdated = $ts
    | .context.stats.lastUpdate = $date
    ')

# ── Write result ──────────────────────────────────────────────────────────────
echo "$CURRENT" > "$CONTEXT_FILE"
echo "✅ Context updated at $TIMESTAMP"
