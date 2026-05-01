#!/bin/bash
# update-pattern-suggestions.sh — Pattern Learning: analyze tasks, detect clusters, suggest patterns
# Reads:  progress.json, patterns.json
# Writes: patterns.json (applications counter + suggestions[])
# Called by: on-session-stop.sh (step 3.5, after memory-stats.sh)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

[ -d "$MEMORY_DIR" ] || exit 0
command -v jq &>/dev/null || { echo "❌ jq required"; exit 1; }

PROGRESS="$MEMORY_DIR/progress.json"
PATTERNS="$MEMORY_DIR/patterns.json"
NOW=$(date -Iseconds)

[ -f "$PROGRESS" ] || { echo "⚠️  progress.json missing, skipping"; exit 0; }
[ -f "$PATTERNS" ] || { echo "⚠️  patterns.json missing, skipping"; exit 0; }

TASK_COUNT=$(jq '.tasks | length' "$PROGRESS")
echo "🔄 update-pattern-suggestions: analyzing ${TASK_COUNT} tasks..."

PROGRESS_DATA=$(cat "$PROGRESS")
PATTERNS_DATA=$(cat "$PATTERNS")

# ── Step 1: Auto-increment applications counter ───────────────────────────────
# For each pattern, count how many tasks have tags that overlap with pattern tags
# A task "matches" a pattern if its title contains any of the pattern's tag keywords
# or if the task agent is "typical" for that pattern type

TMP=$(mktemp)
if jq \
    --argjson progress "$PROGRESS_DATA" \
    --arg now "$NOW" \
    '
    def tasks: $progress.tasks // [];

    # Keyword map: pattern tag → title keywords to match against tasks
    def tag_keywords:
        {
            "safety":        ["safety", "guard", "protect", "secure", "check"],
            "loop-detection":["loop", "infinite", "cycle", "repeat", "retry"],
            "planning":      ["plan", "architect", "design", "spec", "proposal"],
            "complexity":    ["complex", "multi", "large", "refactor", "redesign"],
            "verification":  ["verify", "validate", "test", "check", "lint"],
            "quality":       ["quality", "bug", "fix", "debug", "error"],
            "automation":    ["automat", "script", "hook", "pipeline", "batch"],
            "efficiency":    ["optim", "speed", "fast", "token", "effici", "reduce"]
        };

    # Count tasks whose title matches any keyword for a given tag
    def task_matches_tag(tag):
        (tag_keywords[tag] // []) as $kws |
        [tasks[] | select(
            (.title | ascii_downcase) as $t |
            ($kws | any(. as $kw | $t | contains($kw)))
        )] | length;

    # For each pattern, sum matches across all its tags
    def count_matches(pat):
        (pat.tags // []) |
        map(task_matches_tag(.)) |
        (if length > 0 then add else 0 end);

    # Update each pattern: increment applications by new matches since last count
    # (use max of current and computed to avoid going backwards)
    .patterns = [.patterns[] |
        . as $pat |
        (count_matches($pat)) as $computed |
        # Only update if computed is higher (new tasks added)
        if $computed > ($pat.applications // 0)
        then .applications = $computed
        else .
        end
    ] |
    .lastUpdated = $now
    ' "$PATTERNS" > "$TMP"; then
    mv "$TMP" "$PATTERNS"
    echo "  ✅ applications counters updated"
else
    rm -f "$TMP"
    echo "  ❌ Failed to update applications counters"
fi

# ── Step 2: Detect emerging patterns from task clusters ───────────────────────
# Group completed tasks by agent, look for repeated task types (3+ similar titles)
# Generate suggestions[] in patterns.json if a cluster has no matching pattern yet

PATTERNS_DATA=$(cat "$PATTERNS")  # reload after step 1

SUGGESTIONS=$(jq -n \
    --argjson progress "$PROGRESS_DATA" \
    --argjson patterns "$PATTERNS_DATA" \
    '
    def tasks:    $progress.tasks    // [];
    def patterns: $patterns.patterns // [];

    # Extract "type" from task title: first 2 meaningful words, lowercased
    def task_type:
        .title | ascii_downcase |
        gsub("[^a-z ]"; "") |
        split(" ") | map(select(length > 3)) | .[0:2] | join("_");

    # Completed tasks only
    def done_tasks: [tasks[] | select(.status == "completed")];

    # Group by agent+type, find clusters of 3+
    def clusters:
        [ done_tasks | group_by(.agent)[] |
            . as $agent_tasks |
            ($agent_tasks[0].agent) as $agent |
            [ $agent_tasks | group_by(task_type)[] |
                select(length >= 2) |      # 2+ similar tasks = potential pattern
                {
                    agent:  $agent,
                    type:   (.[0] | task_type),
                    count:  length,
                    titles: [.[].title]
                }
            ][]
        ];

    # Existing pattern titles (lowercased) for dedup
    def known_titles: [patterns[].title | ascii_downcase];

    # Generate suggestions for clusters not already covered by a pattern
    [ clusters[] |
        . as $c |
        # Skip if a pattern title already contains this type
        if (known_titles | any(contains($c.type | gsub("_"; " ")))) then empty
        else {
            "type":        "suggestion",
            "agent":       $c.agent,
            "clusterType": $c.type,
            "taskCount":   $c.count,
            "titles":      $c.titles,
            "suggestedTitle": ("Pattern: \($c.agent) → \($c.type | gsub("_"; " ") | ascii_upcase | .[0:1] + .[1:] | ascii_downcase | .[0:1] | ascii_upcase + "attern" | ltrimstr("Patterntern"))" |
                              "Recurring \($c.agent) Task: \($c.type | gsub("_"; " "))"),
            "suggestedTags": [$c.agent | ascii_downcase, ($c.type | split("_")[0])],
            "detectedAt":  now | todate,
            "promoted":    false
        }
        end
    ]
    ')

if [ -z "$SUGGESTIONS" ]; then
    echo "  ❌ Suggestion detection failed"; exit 1
fi

SUGG_COUNT=$(echo "$SUGGESTIONS" | jq 'length')
echo "  📊 ${SUGG_COUNT} pattern suggestion(s) detected"

# Write suggestions back (keep last 20, deduplicated by clusterType)
TMP=$(mktemp)
if jq \
    --argjson new_sugg "$SUGGESTIONS" \
    --arg now "$NOW" \
    '
    # Merge: keep existing suggestions not in new batch, add new ones, cap at 20
    (.suggestions // []) as $existing |
    ($new_sugg | map(.clusterType)) as $new_types |
    ([$existing[] | select(.clusterType as $t | $new_types | any(. == $t) | not)] + $new_sugg | .[0:20]) as $merged |
    .suggestions = $merged |
    .metadata.lastPatternScan = $now |
    .metadata.suggestionCount = ($merged | length)
    ' "$PATTERNS" > "$TMP"; then
    mv "$TMP" "$PATTERNS"
    if [ "$SUGG_COUNT" -gt 0 ]; then
        echo "  ✅ Suggestions written to patterns.json"
        echo "$SUGGESTIONS" | jq -r '.[] | "     💡 \(.agent): \(.clusterType) (\(.taskCount) tasks)"'
    fi
else
    rm -f "$TMP"
    echo "  ❌ Failed to write suggestions"
fi

echo "✅ update-pattern-suggestions complete"
