#!/bin/bash
# BetterAgents - Memory Stats Calculator
# Recalculates memory-stats.json with full token analysis of memory entries
# Output schema is compatible with dashboard renderTokenStats() function
# Usage: bash memory-stats.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
STATS_FILE="$MEMORY_DIR/memory-stats.json"

exec 2>/dev/null

command -v jq &>/dev/null || exit 0
[ -d "$MEMORY_DIR" ] || exit 0

TIMESTAMP=$(date -Iseconds)

# --- Read memory entries ---
DECISIONS=$(jq '.decisions // []' "$MEMORY_DIR/decision-log.json" 2>/dev/null || echo '[]')
TASKS=$(jq '.tasks // []' "$MEMORY_DIR/progress.json" 2>/dev/null || echo '[]')
PATTERNS=$(jq '.patterns // []' "$MEMORY_DIR/patterns.json" 2>/dev/null || echo '[]')

# --- Token size per entry (1 token ≈ 4 chars of JSON) ---
DEC_ENTRIES=$(echo "$DECISIONS" | jq '[.[] | {
    id: .id,
    agent: (.agent // "unknown"),
    category: "decisions",
    tokens: (. | tojson | length / 4 | ceil)
}]')

TASK_ENTRIES=$(echo "$TASKS" | jq '[.[] | {
    id: .id,
    agent: (.agent // "unknown"),
    category: "tasks",
    tokens: (. | tojson | length / 4 | ceil)
}]')

PAT_ENTRIES=$(echo "$PATTERNS" | jq '[.[] | {
    id: .id,
    agent: (.agent // "unknown"),
    category: "patterns",
    tokens: (. | tojson | length / 4 | ceil)
}]')

# --- Combine all entries ---
ALL_ENTRIES=$(jq -n \
    --argjson d "$DEC_ENTRIES" \
    --argjson t "$TASK_ENTRIES" \
    --argjson p "$PAT_ENTRIES" \
    '$d + $t + $p')

# --- Aggregate stats ---
TOTAL_TOKENS=$(echo "$ALL_ENTRIES" | jq '[.[].tokens] | add // 0')
TOTAL_ENTRIES=$(echo "$ALL_ENTRIES" | jq 'length')
DEC_TOKENS=$(echo "$DEC_ENTRIES" | jq '[.[].tokens] | add // 0')
TASK_TOKENS=$(echo "$TASK_ENTRIES" | jq '[.[].tokens] | add // 0')
PAT_TOKENS=$(echo "$PAT_ENTRIES" | jq '[.[].tokens] | add // 0')
MIN_TOKENS=$(echo "$ALL_ENTRIES" | jq 'if length > 0 then [.[].tokens] | min else 0 end')
MAX_TOKENS=$(echo "$ALL_ENTRIES" | jq 'if length > 0 then [.[].tokens] | max else 0 end')
AVG_TOKENS=$(echo "$ALL_ENTRIES" | jq 'if length > 0 then (([.[].tokens] | add) / length) | ceil else 0 end')

# --- By agent ---
BY_AGENT=$(echo "$ALL_ENTRIES" | jq \
    '[.[] | {agent, tokens}]
    | group_by(.agent)
    | map({(.[0].agent): ([.[].tokens] | add)})
    | add // {}')

# --- File sizes in tokens (all memory files) ---
FILE_STATS='{}'
for f in "$MEMORY_DIR"/*.json "$MEMORY_DIR"/*.md; do
    [ -f "$f" ] || continue
    FNAME=$(basename "$f")
    # Skip the stats file itself (circular) and temp files
    [[ "$FNAME" == "memory-stats.json" ]] && continue
    SIZE=$(wc -c < "$f" 2>/dev/null || echo 0)
    FTOKENS=$((SIZE / 4))
    FILE_STATS=$(echo "$FILE_STATS" | jq --arg k "$FNAME" --argjson v "$FTOKENS" '. + {($k): $v}')
done

# --- LLM usage stats ---
SESSIONS=0
LLM_TOTAL=0
[ -f "$MEMORY_DIR/llm-usage.json" ] && \
    SESSIONS=$(jq '.sessions | length' "$MEMORY_DIR/llm-usage.json" 2>/dev/null || echo 0) && \
    LLM_TOTAL=$(jq '.totals.total // 0' "$MEMORY_DIR/llm-usage.json" 2>/dev/null || echo 0)

# --- Storage stats (all memory files: json + md) ---
TOTAL_SIZE=0
FILE_COUNT=0
for f in "$MEMORY_DIR"/*.json "$MEMORY_DIR"/*.md; do
    [ -f "$f" ] || continue
    SIZE=$(wc -c < "$f" 2>/dev/null || echo 0)
    TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
    FILE_COUNT=$((FILE_COUNT + 1))
done

# --- Cleanup recommendations (threshold: 50k tokens) ---
THRESHOLD=50000
PERCENT=0
[ "$TOTAL_TOKENS" -gt 0 ] && PERCENT=$(awk "BEGIN {printf \"%d\", ($TOTAL_TOKENS / $THRESHOLD) * 100}")
if [ "$PERCENT" -ge 75 ]; then ACTION="cleanup"
elif [ "$PERCENT" -ge 50 ]; then ACTION="review"
else ACTION="none"
fi

# --- Write stats file ---
jq -n \
    --arg ts "$TIMESTAMP" \
    --argjson total "$TOTAL_TOKENS" \
    --argjson entries "$TOTAL_ENTRIES" \
    --argjson avg "$AVG_TOKENS" \
    --argjson min "$MIN_TOKENS" \
    --argjson max "$MAX_TOKENS" \
    --argjson dec "$DEC_TOKENS" \
    --argjson task "$TASK_TOKENS" \
    --argjson pat "$PAT_TOKENS" \
    --argjson byAgent "$BY_AGENT" \
    --argjson fileStats "$FILE_STATS" \
    --argjson threshold "$THRESHOLD" \
    --argjson percent "$PERCENT" \
    --arg action "$ACTION" \
    --argjson decisions "$(echo "$DECISIONS" | jq 'length')" \
    --argjson tasks "$(echo "$TASKS" | jq 'length')" \
    --argjson completed "$(echo "$TASKS" | jq '[.[] | select(.status == "completed")] | length')" \
    --argjson patterns "$(echo "$PATTERNS" | jq 'length')" \
    --argjson sessions "$SESSIONS" \
    --argjson llmTotal "$LLM_TOTAL" \
    --argjson files "$FILE_COUNT" \
    --argjson size "$TOTAL_SIZE" \
    '{
        lastCalculated: $ts,
        summary: {
            totalTokens: $total,
            inputTokens: 0,
            outputTokens: 0,
            totalEntries: $entries,
            avgTokensPerEntry: $avg,
            minTokens: $min,
            maxTokens: $max,
            byCategory: {
                decisions: $dec,
                tasks: $task,
                patterns: $pat
            },
            byAgent: $byAgent,
            bySkill: {}
        },
        cleanupRecommendations: {
            threshold: $threshold,
            currentUsage: $total,
            percentUsed: $percent,
            suggestedAction: $action
        },
        fileStats: $fileStats,
        timeline: {},
        entries: {
            decisions: $decisions,
            tasks: $tasks,
            completedTasks: $completed,
            patterns: $patterns
        },
        llmUsage: {
            sessions: $sessions,
            totalTokens: $llmTotal
        },
        storage: {
            files: $files,
            totalBytes: $size
        }
    }' > "$STATS_FILE"

exit 0
