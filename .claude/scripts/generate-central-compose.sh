#!/usr/bin/env bash
# generate-central-compose.sh
# Registers a project with the central BetterAgents container and regenerates
# docker-compose.yml in ~/.betteragents/
#
# Usage:
#   bash generate-central-compose.sh <project-name> <memory-absolute-path>
#   bash generate-central-compose.sh <project-name> <memory-absolute-path> --unregister

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
PROJECT_NAME="${1:-}"
MEMORY_PATH="${2:-}"
UNREGISTER=false

for arg in "${@:3}"; do
    [ "$arg" = "--unregister" ] && UNREGISTER=true
done

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Usage: bash generate-central-compose.sh <project-name> <memory-path> [--unregister]" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Require jq
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
    echo "❌ jq is required but not found. Install with: sudo apt install jq" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CENTRAL_DIR="$HOME/.betteragents"
PROJECTS_FILE="$CENTRAL_DIR/projects.json"
COMPOSE_FILE="$CENTRAL_DIR/docker-compose.yml"
NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$CENTRAL_DIR"

# ---------------------------------------------------------------------------
# Bootstrap projects.json if missing
# ---------------------------------------------------------------------------
if [ ! -f "$PROJECTS_FILE" ]; then
    echo '{"version":"1.0.0","port":3000,"updated_at":"","projects":[]}' \
        | jq --arg ts "$NOW" '.updated_at = $ts' > "$PROJECTS_FILE"
fi

# ---------------------------------------------------------------------------
# --unregister: remove project entry
# ---------------------------------------------------------------------------
if [ "$UNREGISTER" = true ]; then
    REMAINING=$(jq --arg name "$PROJECT_NAME" '
        .projects |= map(select(.name != $name))
        | .updated_at = "'$NOW'"
    ' "$PROJECTS_FILE")

    echo "$REMAINING" > /tmp/_betteragents_projects.json
    mv /tmp/_betteragents_projects.json "$PROJECTS_FILE"

    COUNT=$(jq '.projects | length' "$PROJECTS_FILE")
    if [ "$COUNT" -eq 0 ]; then
        echo "⚠️  No projects remain."
        echo "   Stop the container with:"
        echo "   docker --context default compose -f ~/.betteragents/docker-compose.yml down"
    else
        echo "✅ Project '$PROJECT_NAME' removed from registry ($COUNT project(s) remaining)"
    fi
else
    # -----------------------------------------------------------------------
    # Register / update project entry
    # -----------------------------------------------------------------------
    if [ -z "$MEMORY_PATH" ]; then
        echo "❌ <memory-path> is required when registering a project" >&2
        exit 1
    fi

    # Resolve to absolute path (no ~ expansion in Docker volumes)
    MEMORY_ABS="$(cd "$MEMORY_PATH" 2>/dev/null && pwd || echo "$MEMORY_PATH")"
    PROJECT_DIR="$(dirname "$(dirname "$MEMORY_ABS")")"

    NEW_ENTRY=$(jq -n \
        --arg name "$PROJECT_NAME" \
        --arg mp "$MEMORY_ABS" \
        --arg pd "$PROJECT_DIR" \
        --arg ts "$NOW" \
        '{name:$name, memory_path:$mp, project_dir:$pd, registered_at:$ts, status:"active"}')

    # Upsert: replace if same name exists, otherwise append
    UPDATED=$(jq \
        --argjson entry "$NEW_ENTRY" \
        --arg ts "$NOW" \
        '
        .updated_at = $ts
        | .projects = (
            [ .projects[] | select(.name != $entry.name) ]
            + [$entry]
          )
        ' "$PROJECTS_FILE")

    echo "$UPDATED" > /tmp/_betteragents_projects.json
    mv /tmp/_betteragents_projects.json "$PROJECTS_FILE"
fi

# ---------------------------------------------------------------------------
# Copy latest server files to CENTRAL_DIR
# ---------------------------------------------------------------------------
SERVER_JS="$SCRIPT_DIR/serve-dashboard.js"
DASHBOARD_HTML="$INSTALLER_DIR/templates/memory/dashboard.html"

if [ -f "$SERVER_JS" ]; then
    cp "$SERVER_JS" "$CENTRAL_DIR/serve-dashboard.js"
else
    echo "⚠️  serve-dashboard.js not found at $SERVER_JS — skipping copy" >&2
fi

if [ -f "$DASHBOARD_HTML" ]; then
    cp "$DASHBOARD_HTML" "$CENTRAL_DIR/dashboard.html"
else
    echo "⚠️  dashboard.html not found at $DASHBOARD_HTML — skipping copy" >&2
fi

# ---------------------------------------------------------------------------
# Generate docker-compose.yml from projects.json
# ---------------------------------------------------------------------------
PORT=$(jq -r '.port // 3000' "$PROJECTS_FILE")
COUNT=$(jq '.projects | length' "$PROJECTS_FILE")

# Build volume lines for each registered project
VOLUME_LINES=""
while IFS= read -r line; do
    proj_name=$(echo "$line" | jq -r '.name')
    proj_mp=$(echo "$line" | jq -r '.memory_path')
    VOLUME_LINES="${VOLUME_LINES}      - \"${proj_mp}:/memory/${proj_name}:ro\"
"
done < <(jq -c '.projects[]' "$PROJECTS_FILE")

cat > "$COMPOSE_FILE" << COMPOSE_EOF
# AUTO-GENERATED by generate-central-compose.sh — do not edit manually
# Regenerated on: ${NOW}
# Projects: ${COUNT}

services:
  betteragents-central:
    image: node:20-alpine
    container_name: betteragents-central
    working_dir: /app
    command: node serve-dashboard.js
    ports:
      - "\${PORT:-${PORT}}:3000"
    volumes:
${VOLUME_LINES}      - ${CENTRAL_DIR}/serve-dashboard.js:/app/serve-dashboard.js:ro
      - ${CENTRAL_DIR}/dashboard.html:/app/dashboard.html:ro
    environment:
      - PORT=3000
      - MULTI_PROJECT=true
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "wget -q --spider http://localhost:3000 || exit 1"]
      interval: 15s
      timeout: 5s
      start_period: 10s
      retries: 3
COMPOSE_EOF

# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------
echo "✅ Central container configured: ${COUNT} project(s) | Port: ${PORT}"
echo ""
echo "Registered projects:"
jq -r '.projects[] | "  • \(.name)  →  \(.memory_path)"' "$PROJECTS_FILE"
echo ""
echo "Config: $PROJECTS_FILE"
echo "Compose: $COMPOSE_FILE"
