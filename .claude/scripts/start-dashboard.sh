#!/bin/bash

###############################################################################
# BetterAgents Dashboard Launcher
# Priority: Docker container → Node.js fallback
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Central container config — single container serves all projects
CENTRAL_DIR="$HOME/.betteragents"
CENTRAL_COMPOSE="$CENTRAL_DIR/docker-compose.yml"
CONTAINER_NAME="betteragents-central"
DOCKER_CTX="--context default"
PORT=3000
DASHBOARD_URL="http://localhost:${PORT}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

open_browser() {
    if command -v xdg-open &>/dev/null; then
        xdg-open "$DASHBOARD_URL" >/dev/null 2>&1 &
    elif command -v open &>/dev/null; then
        open "$DASHBOARD_URL" >/dev/null 2>&1 &
    fi
}

print_dashboard_box() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}🌐 Dashboard URL:${NC}  $DASHBOARD_URL"
    echo -e "${GREEN}📊 Container:${NC}     $CONTAINER_NAME  (multi-project)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# ============================================================
# MODE 1 — DOCKER CENTRAL CONTAINER (preferred)
# ============================================================
if command -v docker &>/dev/null; then

    # Case A: central container already running → just show URL
    if docker $DOCKER_CTX ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        echo ""
        echo -e "${GREEN}✅ Central dashboard already running (Docker)${NC}"
        print_dashboard_box
        open_browser
        exit 0
    fi

    # Case B: central container exists but stopped → restart it
    if docker $DOCKER_CTX ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        echo ""
        echo -e "${YELLOW}▶ Restarting central container...${NC}"
        docker $DOCKER_CTX start "${CONTAINER_NAME}" >/dev/null 2>&1
        sleep 2
        echo -e "${GREEN}✅ Container restarted${NC}"
        print_dashboard_box
        open_browser
        exit 0
    fi

    # Case C: no central container yet → start from ~/.betteragents/
    if [ -f "$CENTRAL_COMPOSE" ]; then
        echo ""
        echo -e "${YELLOW}▶ Starting central container...${NC}"
        if docker $DOCKER_CTX compose -f "$CENTRAL_COMPOSE" up -d 2>/dev/null; then
            sleep 3
            echo -e "${GREEN}✅ Central container started${NC}"
            print_dashboard_box
            open_browser
            exit 0
        else
            echo -e "${YELLOW}⚠️  Docker failed — falling back to Node.js server${NC}"
            echo ""
        fi
    else
        echo -e "${YELLOW}⚠️  Central compose not found at $CENTRAL_COMPOSE — falling back to Node.js${NC}"
        echo ""
    fi
fi

# ============================================================
# MODE 2 — NODE.JS FALLBACK
# ============================================================
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       BetterAgents Memory Dashboard — Node.js Mode         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if ! command -v node &>/dev/null; then
    echo -e "${RED}❌ Node.js is not installed and Docker is not available.${NC}"
    echo "Install Node.js: https://nodejs.org/"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/serve-dashboard.js" ]; then
    echo -e "${RED}❌ serve-dashboard.js not found at $SCRIPT_DIR${NC}"
    exit 1
fi

# --- Port rotation helper ---
find_free_port() {
    local start="${1:-3000}"
    local port="$start"
    while [ "$port" -le 3099 ]; do
        if ! ss -tlnp 2>/dev/null | grep -qE ":${port}[^0-9]"; then
            echo "$port"
            return 0
        fi
        port=$((port + 1))
    done
    echo "$start"
}

PORT_IN_USE=false
if ss -tlnp 2>/dev/null | grep -qE ":${PORT}[^0-9]" || curl -s --max-time 1 "$DASHBOARD_URL" >/dev/null 2>&1; then
    PORT_IN_USE=true
fi

if [ "$PORT_IN_USE" = true ]; then
    echo -e "${YELLOW}⚠️  Port ${PORT} is already in use.${NC}"
    PIDS=$(lsof -ti :${PORT} 2>/dev/null)
    FREE_PORT=$(find_free_port $((PORT + 1)))

    # Non-interactive mode: auto-select next free port (e.g. when called from background)
    if [ ! -t 0 ]; then
        PORT="$FREE_PORT"
        DASHBOARD_URL="http://localhost:${PORT}"
        echo -e "${BLUE}   → Non-interactive mode: using next free port ${PORT}${NC}"
        if [ -f "$ENV_FILE" ]; then
            grep -q "^BETTERAGENTS_PORT=" "$ENV_FILE" 2>/dev/null \
                && sed -i "s/^BETTERAGENTS_PORT=.*/BETTERAGENTS_PORT=${PORT}/" "$ENV_FILE" \
                || echo "BETTERAGENTS_PORT=${PORT}" >> "$ENV_FILE"
        fi
    else
        if [ -n "$PIDS" ]; then
            FIRST_PID=$(echo "$PIDS" | head -1)
            PID_COUNT=$(echo "$PIDS" | wc -l | tr -d ' ')
            PNAME=$(ps -p "$FIRST_PID" -o comm= 2>/dev/null || echo "unknown")
            [ "$PID_COUNT" -gt 1 ] \
                && echo -e "${BLUE}   → $PID_COUNT processes (main: '$PNAME', PID $FIRST_PID)${NC}" \
                || echo -e "${BLUE}   → Process '$PNAME' (PID $FIRST_PID)${NC}"
        fi
        echo ""
        echo "   [k] Kill process and use port ${PORT}"
        echo "   [r] Use next free port (${FREE_PORT})"
        echo "   [n] Cancel"
        echo ""
        read -r -p "   Choose [k/r/n]: " REPLY
        echo ""
        case "${REPLY,,}" in
            k)
                [ -n "$PIDS" ] && echo "$PIDS" | xargs kill -9 2>/dev/null && sleep 2
                if ss -tlnp 2>/dev/null | grep -qE ":${PORT}[^0-9]"; then
                    echo -e "${RED}❌ Could not free port ${PORT}.${NC}"; exit 1
                fi
                echo -e "${GREEN}✓ Port ${PORT} freed${NC}"
                ;;
            r)
                PORT="$FREE_PORT"
                DASHBOARD_URL="http://localhost:${PORT}"
                echo -e "${GREEN}✓ Using port ${PORT}${NC}"
                if [ -f "$ENV_FILE" ]; then
                    grep -q "^BETTERAGENTS_PORT=" "$ENV_FILE" 2>/dev/null \
                        && sed -i "s/^BETTERAGENTS_PORT=.*/BETTERAGENTS_PORT=${PORT}/" "$ENV_FILE" \
                        || echo "BETTERAGENTS_PORT=${PORT}" >> "$ENV_FILE"
                    echo -e "${BLUE}   → Saved port ${PORT} to .env${NC}"
                fi
                ;;
            *)
                echo -e "${YELLOW}Aborted.${NC}"; exit 0 ;;
        esac
    fi
    echo ""
fi

echo -e "${GREEN}📊 Starting Node.js dashboard in background...${NC}"

# Log file location
LOG_FILE="/tmp/betteragents-dashboard.log"

# Enable multi-project mode if ~/.betteragents/projects.json has 2+ entries
CENTRAL_PROJECTS="$HOME/.betteragents/projects.json"
EXTRA_ENV=""
if [ -f "$CENTRAL_PROJECTS" ]; then
    PROJECT_COUNT=$(node -e "try{const d=JSON.parse(require('fs').readFileSync('$CENTRAL_PROJECTS'));console.log((d.projects||[]).length)}catch(e){console.log(0)}" 2>/dev/null || echo 0)
    if [ "$PROJECT_COUNT" -gt 0 ] 2>/dev/null; then
        EXTRA_ENV="MULTI_PROJECT=true PROJECTS_JSON=$CENTRAL_PROJECTS"
        echo -e "${BLUE}   → Multi-project mode: ${PROJECT_COUNT} projects from $CENTRAL_PROJECTS${NC}"
    fi
fi

# Start server with nohup (detached, persistent)
cd "$PROJECT_ROOT"
nohup env PORT="${PORT}" $EXTRA_ENV node "$SCRIPT_DIR/serve-dashboard.js" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Wait a moment to ensure it started
sleep 2

# Verify it's running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dashboard started successfully${NC}"
    print_dashboard_box
    echo -e "${YELLOW}💡 Info:${NC}"
    echo "  • Running in background (PID: $SERVER_PID)"
    echo "  • Log file: $LOG_FILE"
    echo "  • Data auto-refreshes every 30 seconds"
    echo ""
    echo -e "${BLUE}To stop the dashboard:${NC}"
    echo "  kill $SERVER_PID"
    echo "  # or"
    echo "  pkill -f serve-dashboard.js"
    echo ""
    
    # Try to open browser
    open_browser
else
    echo -e "${RED}❌ Failed to start dashboard${NC}"
    echo "Check log: $LOG_FILE"
    exit 1
fi
