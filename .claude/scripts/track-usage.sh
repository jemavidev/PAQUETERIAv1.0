#!/bin/bash
# BetterAgents - Session Usage Tracker
# Records session activity as LLM usage visualization data.
# NOTE: Token counts are ESTIMATES based on git diff — Claude Code does not
#       expose actual API token counts. Use these as relative activity indicators,
#       not billing-accurate figures.
# Called by on-session-stop.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
USAGE_FILE="$MEMORY_DIR/llm-usage.json"
CONTEXT_FILE="$MEMORY_DIR/active-context.json"

exec 2>/dev/null

command -v jq &>/dev/null || exit 0
[ -f "$USAGE_FILE" ] || exit 0

TIMESTAMP=$(date -Iseconds)
LINES_ADDED=0
LINES_REMOVED=0
FILES_CHANGED=0
FILES_LIST="[]"
LAST_COMMIT=""
PROMPTS_JSON="[]"
FIRST_PROMPT=""
CATEGORIES=""
SESSION_FOCUS=""

# --- Git diff stats ---
if command -v git &>/dev/null && git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    GIT_DIFF=$(git -C "$PROJECT_ROOT" diff --stat HEAD 2>/dev/null || echo "")
    if [ -n "$GIT_DIFF" ]; then
        LINES_ADDED=$(echo "$GIT_DIFF" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' | head -1 || echo "0")
        LINES_REMOVED=$(echo "$GIT_DIFF" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' | head -1 || echo "0")
        FILES_CHANGED=$(echo "$GIT_DIFF" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' | head -1 || echo "0")
    fi
    # Capture per-file line counts: {path, added, removed}[]
    # Step 1: tracked modified files via git diff --numstat HEAD
    NUMSTAT=$(git -C "$PROJECT_ROOT" diff --numstat HEAD 2>/dev/null || echo "")
    # Step 2: new untracked files — count lines with wc
    UNTRACKED=$(git -C "$PROJECT_ROOT" ls-files --others --exclude-standard 2>/dev/null \
        | grep -v 'archive/\|\.session-tokens-tmp\|\.session-prompts-tmp\|\.json\.bak')

    # Build combined JSON array of {path, added, removed}
    FILE_OBJECTS=""
    FILE_COUNT=0
    if [ -n "$NUMSTAT" ]; then
        while IFS=$'\t' read -r added removed filepath; do
            [ -z "$filepath" ] && continue
            echo "$filepath" | grep -q 'archive/\|\.session-tokens-tmp\|\.session-prompts-tmp\|\.json\.bak' && continue
            [ "$FILE_COUNT" -ge 20 ] && break
            FILE_COUNT=$((FILE_COUNT + 1))
            ENTRY=$(jq -n --arg p "$filepath" --arg a "${added:-0}" --arg r "${removed:-0}" \
                '{path:$p, added:($a|tonumber? // 0), removed:($r|tonumber? // 0)}')
            FILE_OBJECTS="${FILE_OBJECTS}${ENTRY}"$'\n'
        done <<< "$NUMSTAT"
    fi
    if [ -n "$UNTRACKED" ]; then
        while IFS= read -r filepath; do
            [ -z "$filepath" ] && continue
            [ "$FILE_COUNT" -ge 20 ] && break
            FILE_COUNT=$((FILE_COUNT + 1))
            FULL="$PROJECT_ROOT/$filepath"
            if [ -f "$FULL" ]; then
                LINES=$(wc -l < "$FULL" 2>/dev/null || echo 0)
            else
                LINES=0
            fi
            ENTRY=$(jq -n --arg p "$filepath" --argjson a "$LINES" '{path:$p, added:$a, removed:0}')
            FILE_OBJECTS="${FILE_OBJECTS}${ENTRY}"$'\n'
        done <<< "$UNTRACKED"
    fi
    if [ -n "$FILE_OBJECTS" ]; then
        FILES_LIST=$(echo "$FILE_OBJECTS" | jq -sc '.')
    fi
    # Capture last commit message
    LAST_COMMIT=$(git -C "$PROJECT_ROOT" log --oneline -1 2>/dev/null || echo "")
fi

# --- Session prompts from UserPromptSubmit hook ---
PROMPTS_TMP="$MEMORY_DIR/.session-prompts-tmp"
if [ -f "$PROMPTS_TMP" ]; then
    PROMPTS_JSON=$(jq -sc '.' "$PROMPTS_TMP" 2>/dev/null || echo "[]")
    FIRST_PROMPT=$(head -1 "$PROMPTS_TMP" | jq -r '.' 2>/dev/null || echo "")
    rm -f "$PROMPTS_TMP"
fi

# --- Activity categories from recentChanges in active-context ---
if [ -f "$CONTEXT_FILE" ]; then
    SESSION_FOCUS=$(jq -r '.currentFocus.feature // ""' "$CONTEXT_FILE" 2>/dev/null || echo "")
    CATEGORIES=$(jq -r '
        [.context.recentChanges[]?.category // empty] | unique | join(", ")
    ' "$CONTEXT_FILE" 2>/dev/null || echo "")
fi

# --- Token estimation ---
# Input: use char-count estimate from on-session-stop.sh if passed as $1
# Otherwise fall back to fixed overhead baseline
OUTPUT_TOKENS=$(( (LINES_ADDED + LINES_REMOVED) * 20 ))
if [ -n "$1" ] && [ "$1" -gt 0 ] 2>/dev/null; then
    INPUT_TOKENS="$1"
    ESTIMATION_SOURCE="char-count+fixed-overhead"
else
    INPUT_TOKENS=2386
    ESTIMATION_SOURCE="fixed-overhead-only"
fi
TOTAL_TOKENS=$((INPUT_TOKENS + OUTPUT_TOKENS))

# Build description
DESCRIPTION="Session: +${LINES_ADDED}/-${LINES_REMOVED} lines, ${FILES_CHANGED} files"
[ -n "$CATEGORIES" ] && DESCRIPTION="$DESCRIPTION | areas: ${CATEGORIES}"
[ -n "$SESSION_FOCUS" ] && DESCRIPTION="$DESCRIPTION | focus: ${SESSION_FOCUS}"

# Build session entry
NEW_SESSION=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --argjson in "$INPUT_TOKENS" \
    --argjson out "$OUTPUT_TOKENS" \
    --argjson tot "$TOTAL_TOKENS" \
    --arg desc "$DESCRIPTION" \
    --argjson files "$FILES_CHANGED" \
    --argjson fileList "$FILES_LIST" \
    --arg cats "$CATEGORIES" \
    --arg focus "$SESSION_FOCUS" \
    --arg commit "$LAST_COMMIT" \
    --argjson prompts "$PROMPTS_JSON" \
    --arg firstPrompt "$FIRST_PROMPT" \
    '{
        timestamp: $ts,
        input: $in,
        output: $out,
        total: $tot,
        description: $desc,
        estimated: true,
        estimationSource: "char_count_div4_plus_2386_overhead",
        activity: {
            filesChanged: $files,
            files: $fileList,
            lastCommit: $commit,
            firstPrompt: $firstPrompt,
            prompts: $prompts,
            categories: $cats,
            focus: $focus
        }
    }')

# Append session and update rolling totals
UPDATED=$(jq \
    --argjson session "$NEW_SESSION" \
    --argjson in "$INPUT_TOKENS" \
    --argjson out "$OUTPUT_TOKENS" \
    --argjson tot "$TOTAL_TOKENS" \
    '.sessions += [$session] |
     .totals.input += $in |
     .totals.output += $out |
     .totals.total += $tot' \
    "$USAGE_FILE")

if [ -n "$UPDATED" ]; then
    echo "$UPDATED" > "$USAGE_FILE"
fi

exit 0
