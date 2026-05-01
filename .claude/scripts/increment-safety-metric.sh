#!/usr/bin/env bash
# Atomic increment of a safetyMetrics counter in metrics-analytics.json
# Usage: bash increment-safety-metric.sh <key>
# Keys: verificationsPassed | verificationsFailed | planModeTriggered | loopDetections

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METRICS_FILE="$SCRIPT_DIR/../memory/metrics-analytics.json"

KEY="${1:-}"

if [ -z "$KEY" ]; then
  echo "Usage: $0 <metric_key>" >&2
  exit 1
fi

if [ ! -f "$METRICS_FILE" ]; then
  echo "metrics-analytics.json not found" >&2
  exit 1
fi

command -v jq &>/dev/null || exit 0

TS=$(date -Iseconds 2>/dev/null || date)
TMP=$(mktemp)
if jq --arg k "$KEY" --arg ts "$TS" \
  '.safetyMetrics[$k] = ((.safetyMetrics[$k] // 0) | tonumber) + 1 |
   .safetyMetrics.lastUpdated = $ts' \
  "$METRICS_FILE" > "$TMP" 2>/dev/null; then
  mv "$TMP" "$METRICS_FILE"
else
  rm -f "$TMP"
  exit 1
fi
