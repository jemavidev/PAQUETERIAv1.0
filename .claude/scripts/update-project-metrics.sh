#!/bin/bash
# update-project-metrics.sh — Phase 4: Consolidate all memory files into project-metrics.json
# Reads: all .claude/memory/*.json files
# Writes: .claude/memory/project-metrics.json
# Called by: on-session-stop.sh (step 5, last before dashboard)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

[ -d "$MEMORY_DIR" ] || exit 0
command -v jq &>/dev/null || exit 0

NOW=$(date -Iseconds)
OUTPUT="$MEMORY_DIR/project-metrics.json"

# ── Load all memory files safely ─────────────────────────────────────────────
load_json() {
    local file="$MEMORY_DIR/$1"
    [ -f "$file" ] && cat "$file" || echo '{}'
}

PROGRESS=$(load_json "progress.json")
DECISIONS=$(load_json "decision-log.json")
PATTERNS=$(load_json "patterns.json")
METRICS=$(load_json "metrics-analytics.json")
TOKEN_ACC=$(load_json "token-accounting.json")
CONTEXT=$(load_json "active-context.json")
MEM_STATS=$(load_json "memory-stats.json")
PROJ_SIZE=$(load_json "project-size.json")
ALERTS=$(load_json "alerts-registry.json")

# ── Compute trend: compare last 2 session token totals from progress ──────────
TREND_DIRECTION=$(echo "$METRICS" | jq -r '.efficiency.trend // "stable"')

# ── Build consolidated project-metrics.json ───────────────────────────────────
TMP=$(mktemp)
if jq -n \
    --arg     now        "$NOW" \
    --arg     trend      "$TREND_DIRECTION" \
    --argjson progress   "$PROGRESS" \
    --argjson decisions  "$DECISIONS" \
    --argjson patterns   "$PATTERNS" \
    --argjson metrics    "$METRICS" \
    --argjson token_acc  "$TOKEN_ACC" \
    --argjson context    "$CONTEXT" \
    --argjson mem_stats  "$MEM_STATS" \
    --argjson proj_size  "$PROJ_SIZE" \
    --argjson alerts     "$ALERTS" \
    '
    # Helper: safe array length
    def safe_len(x): if x == null then 0 else x | length end;

    {
        "lastUpdated": $now,
        "version":     "4.0.0",

        # ── Summary snapshot ─────────────────────────────────────────────────
        "summary": {
            "phase":          ($context.project.phase // "unknown"),
            "projectName":    ($context.project.name  // "BetterAgentX"),
            "currentFocus":   ($context.currentFocus.feature // "unknown"),
            "trend":          $trend,
            "systemHealth":   (
                if ($metrics.efficiency.tokenReductionPercent // 0) > 20
                    and ($metrics.quality.codeVerificationRate // 0) >= 95
                then "excellent"
                elif ($metrics.quality.codeVerificationRate // 0) >= 80
                then "good"
                else "needs_attention" end
            )
        },

        # ── Task stats (from progress.json) ──────────────────────────────────
        "tasks": {
            "total":       (safe_len($progress.tasks)),
            "completed":   ([ ($progress.tasks // [])[] | select(.status == "completed")]  | length),
            "inProgress":  ([ ($progress.tasks // [])[] | select(.status == "in_progress")] | length),
            "pending":     ([ ($progress.tasks // [])[] | select(.status == "pending")]     | length),
            "totalTokens": ($progress.metadata.totalTokens     // 0),
            "avgTokens":   ($progress.metadata.avgTokensPerEntry // 0)
        },

        # ── Knowledge base (decisions + patterns) ────────────────────────────
        "knowledge": {
            "decisions":       (safe_len($decisions.decisions)),
            "patterns":        (safe_len($patterns.patterns)),
            "patternApplications": (
                [($patterns.patterns // [])[] | (.applications // 0)] | add // 0
            )
        },

        # ── Token accounting ─────────────────────────────────────────────────
        "tokens": {
            "allocated":       ($token_acc.metadata.totalTokensAllocated  // 200000),
            "used":            ($token_acc.metadata.totalTokensUsed       // 0),
            "remaining":       ($token_acc.metadata.totalTokensRemaining  // 200000),
            "utilizationPct":  ($token_acc.metadata.utilizationPercent    // 0),
            "runwayDays":      ($token_acc.projections.estimatedRunwayDays // 999)
        },

        # ── Efficiency metrics ───────────────────────────────────────────────
        "efficiency": {
            "avgTokensPerTask":      ($metrics.efficiency.avgTokensPerTask      // 0),
            "tokenReductionPct":     ($metrics.efficiency.tokenReductionPercent  // 0),
            "codeVerificationRate":  ($metrics.quality.codeVerificationRate      // 0),
            "trend":                 ($metrics.efficiency.trend // "stable")
        },

        # ── Safety gates ────────────────────────────────────────────────────
        "safety": {
            "loopDetections":     ($metrics.safetyMetrics.loopDetections    // 0),
            "planModeTriggered":  ($metrics.safetyMetrics.planModeTriggered // 0),
            "verificationsPassed":($metrics.safetyMetrics.verificationsPassed // 0),
            "activeAlerts":       (safe_len($alerts.alerts)),
            "criticalAlerts":     ([ ($alerts.alerts // [])[] | select(.level == "critical")] | length)
        },

        # ── Per-agent breakdown ──────────────────────────────────────────────
        "agentMetrics": ($metrics.agentMetrics // {}),

        # ── Codebase size ────────────────────────────────────────────────────
        "codebase": {
            "totalFiles":  ($proj_size.totalFiles  // 0),
            "totalSizeKB": ($proj_size.totalSizeKB // 0),
            "byCategory":  ($proj_size.byCategory  // {}),
            "memoryFiles": ($mem_stats.entries      // {})
        },

        # ── Recent activity ──────────────────────────────────────────────────
        "recentChanges": (($context.context.recentChanges // []) | .[-5:])
    }
    ' > "$TMP"; then
    mv "$TMP" "$OUTPUT"
    echo "✅ project-metrics.json consolidated"
else
    rm -f "$TMP"
    echo "❌ Failed to write project-metrics.json"
    exit 1
fi
