#!/bin/bash
# BetterAgents - Skills Detection & Content Loader
# Detects relevant skills for a given agent/task and outputs their content
# for injection into agent prompts.
#
# Usage:
#   bash detect-skills.sh "<query>" [agent-name] [--content]
#
# Options:
#   --content   Output full skill content (for prompt injection), not just names
#
# Examples:
#   bash detect-skills.sh "build REST API" architect          → skill names
#   bash detect-skills.sh "build REST API" architect --content → skill content blocks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
CACHE_FILE="$PROJECT_ROOT/.claude/cache/skills-detection-cache.json"
REGISTRY="$PROJECT_ROOT/config/agent-skills.json"

QUERY="${1:-}"
AGENT="${2:-}"
OUTPUT_CONTENT=false
[ "${3:-}" = "--content" ] && OUTPUT_CONTENT=true

CACHE_TTL=3600
NOW=$(date +%s)

# Known agent command files — never treated as skills
AGENT_FILES="architect coder critic security tester ux-designer writer teacher
             product-manager devops data-scientist researcher memory metrics"

is_agent_file() {
    local name="$1"
    for a in $AGENT_FILES; do
        [ "$a" = "$name" ] && return 0
    done
    return 1
}

mkdir -p "$(dirname "$CACHE_FILE")"
[ -f "$CACHE_FILE" ] || echo "{}" > "$CACHE_FILE"

# Cache key (only for name resolution, not content)
CACHE_KEY=$(echo "${QUERY}:${AGENT}" | md5sum | cut -d' ' -f1)

# Check cache (names only)
if command -v jq &>/dev/null && [ -f "$CACHE_FILE" ] && [ "$OUTPUT_CONTENT" = false ]; then
    CACHED=$(jq -r --arg k "$CACHE_KEY" '.[$k] // empty' "$CACHE_FILE" 2>/dev/null)
    if [ -n "$CACHED" ]; then
        CACHED_TIME=$(echo "$CACHED" | jq -r '.timestamp // 0')
        AGE=$((NOW - CACHED_TIME))
        if [ "$AGE" -lt "$CACHE_TTL" ]; then
            echo "$CACHED" | jq -r '.skills[]'
            exit 0
        fi
    fi
fi

SKILLS_FOUND=()

# --- Step 1: Get recommended skills for the agent from registry ---
if [ -f "$REGISTRY" ] && command -v jq &>/dev/null && [ -n "$AGENT" ]; then
    while IFS= read -r skill; do
        [ -z "$skill" ] && continue
        SKILLS_FOUND+=("$skill")
    done < <(jq -r --arg a "$AGENT" '.[$a].recommended // [] | .[]' "$REGISTRY" 2>/dev/null)
fi

# --- Step 2: Score by task keyword relevance ---
# Keep only skills whose name matches keywords in the query (when registry returned results)
# If no registry match, fall back to scanning all commands
QUERY_LOWER=$(echo "$QUERY" | tr '[:upper:]' '[:lower:]' | tr '-' ' ')

FILTERED=()
if [ ${#SKILLS_FOUND[@]} -gt 0 ]; then
    for skill in "${SKILLS_FOUND[@]}"; do
        skill_words=$(echo "$skill" | tr '-' ' ')
        # Check if any word in skill name appears in the query
        matched=false
        for word in $skill_words; do
            [ ${#word} -lt 3 ] && continue
            echo "$QUERY_LOWER" | grep -qi "$word" && matched=true && break
        done
        $matched && FILTERED+=("$skill")
    done
    # If keyword filter removed everything, fall back to top 3 recommended
    if [ ${#FILTERED[@]} -eq 0 ]; then
        FILTERED=("${SKILLS_FOUND[@]:0:3}")
    fi
else
    # Fallback: scan .claude/commands/ for skills matching the query
    if [ -d "$COMMANDS_DIR" ]; then
        for f in "$COMMANDS_DIR"/*.md; do
            [ -f "$f" ] || continue
            name=$(basename "$f" .md)
            is_agent_file "$name" && continue
            skill_words=$(echo "$name" | tr '-' ' ')
            for word in $skill_words; do
                [ ${#word} -lt 3 ] && continue
                if echo "$QUERY_LOWER" | grep -qi "$word"; then
                    FILTERED+=("$name")
                    break
                fi
            done
        done
    fi
fi

# Deduplicate
UNIQUE=()
declare -A SEEN
for s in "${FILTERED[@]}"; do
    [ "${SEEN[$s]+set}" ] && continue
    SEEN[$s]=1
    UNIQUE+=("$s")
done

# Cap at 3 skills max (avoid context bloat)
RESULT=("${UNIQUE[@]:0:3}")

if [ ${#RESULT[@]} -eq 0 ]; then
    exit 0
fi

# --- Output ---
if [ "$OUTPUT_CONTENT" = true ]; then
    # Output skill content blocks for prompt injection
    for skill in "${RESULT[@]}"; do
        SKILL_FILE="$COMMANDS_DIR/${skill}.md"
        if [ -f "$SKILL_FILE" ]; then
            echo "--- skill: ${skill} ---"
            # Strip frontmatter before outputting
            awk 'BEGIN{fm=0;done=0} /^---/{fm++; if(fm==2){done=1;next}} done{print}' "$SKILL_FILE"
            echo "--- end skill: ${skill} ---"
            echo ""
        fi
    done
else
    # Output skill names only
    for skill in "${RESULT[@]}"; do
        echo "$skill"
    done

    # Update cache
    if command -v jq &>/dev/null; then
        SKILLS_JSON=$(printf '%s\n' "${RESULT[@]}" | jq -R . | jq -s .)
        CACHE_ENTRY=$(jq -n --argjson skills "$SKILLS_JSON" --argjson ts "$NOW" \
            '{"skills": $skills, "timestamp": $ts}')
        jq --arg k "$CACHE_KEY" --argjson e "$CACHE_ENTRY" '.[$k] = $e' \
            "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
    fi
fi

exit 0
