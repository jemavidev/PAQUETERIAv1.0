#!/bin/bash
# ============================================================================
# BetterAgentX Verification Script
# ============================================================================
# Verifica que BetterAgentX está correctamente integrado en PAQUETEX
# ============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERRORS=0
WARNINGS=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         BetterAgentX Verification for PAQUETEX            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Función para verificar
check_exists() {
    local path=$1
    local name=$2
    local type=$3
    
    if [ "$type" == "link" ]; then
        if [ -L "$path" ]; then
            echo -e "${GREEN}✓${NC} $name (enlace simbólico)"
            return 0
        else
            echo -e "${RED}✗${NC} $name (no es enlace simbólico)"
            ((ERRORS++))
            return 1
        fi
    elif [ "$type" == "file" ]; then
        if [ -f "$path" ]; then
            echo -e "${GREEN}✓${NC} $name"
            return 0
        else
            echo -e "${RED}✗${NC} $name (no existe)"
            ((ERRORS++))
            return 1
        fi
    elif [ "$type" == "dir" ]; then
        if [ -d "$path" ]; then
            echo -e "${GREEN}✓${NC} $name"
            return 0
        else
            echo -e "${RED}✗${NC} $name (no existe)"
            ((ERRORS++))
            return 1
        fi
    fi
}

# Verificar BetterAgentX
echo -e "${YELLOW}→ Verificando BetterAgentX...${NC}"
check_exists "$PROJECT_ROOT/BetterAgentX" "BetterAgentX directory" "dir"
check_exists "$PROJECT_ROOT/BetterAgentX/.kiro/steering/agents" "BetterAgentX agents" "dir"
echo ""

# Verificar estructura .kiro
echo -e "${YELLOW}→ Verificando estructura .kiro...${NC}"
check_exists "$PROJECT_ROOT/.kiro" ".kiro directory" "dir"
check_exists "$PROJECT_ROOT/.kiro/steering" ".kiro/steering" "dir"
check_exists "$PROJECT_ROOT/.kiro/memory" ".kiro/memory" "dir"
check_exists "$PROJECT_ROOT/.kiro/settings" ".kiro/settings" "dir"
echo ""

# Verificar enlaces simbólicos
echo -e "${YELLOW}→ Verificando enlaces simbólicos...${NC}"
check_exists "$PROJECT_ROOT/.kiro/steering/agents" "Agentes" "link"
check_exists "$PROJECT_ROOT/.kiro/steering/agentx" "AgentX" "link"
check_exists "$PROJECT_ROOT/.kiro/steering/_common" "Common" "link"
check_exists "$PROJECT_ROOT/.agents/skills" "Skills" "link"
echo ""

# Verificar archivos de configuración
echo -e "${YELLOW}→ Verificando configuración...${NC}"
check_exists "$PROJECT_ROOT/.kiro/settings/betteragents.json" "betteragents.json" "file"
check_exists "$PROJECT_ROOT/.kiro/settings/agent-skills.json" "agent-skills.json" "file"
check_exists "$PROJECT_ROOT/.betteragentx-config" ".betteragentx-config" "file"
echo ""

# Verificar archivos de memoria
echo -e "${YELLOW}→ Verificando sistema de memoria...${NC}"
check_exists "$PROJECT_ROOT/.kiro/memory/active-context.md" "active-context.md" "file"
check_exists "$PROJECT_ROOT/.kiro/memory/progress.md" "progress.md" "file"
check_exists "$PROJECT_ROOT/.kiro/memory/decision-log.md" "decision-log.md" "file"
check_exists "$PROJECT_ROOT/.kiro/memory/patterns.md" "patterns.md" "file"
echo ""

# Contar agentes disponibles
echo -e "${YELLOW}→ Verificando agentes disponibles...${NC}"
if [ -d "$PROJECT_ROOT/.kiro/steering/agents" ]; then
    AGENT_COUNT=$(ls -1 "$PROJECT_ROOT/.kiro/steering/agents" | grep -c '\.md$' || true)
    echo -e "${GREEN}✓${NC} $AGENT_COUNT agentes encontrados"
    
    # Listar agentes
    echo -e "\n${BLUE}Agentes disponibles:${NC}"
    for agent in "$PROJECT_ROOT/.kiro/steering/agents"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent" .md)
            echo -e "  • $agent_name"
        fi
    done
else
    echo -e "${RED}✗${NC} No se encontraron agentes"
    ((ERRORS++))
fi
echo ""

# Verificar skills
echo -e "${YELLOW}→ Verificando skills...${NC}"
if [ -d "$PROJECT_ROOT/.agents/skills" ]; then
    SKILL_COUNT=$(ls -1d "$PROJECT_ROOT/.agents/skills"/*/ 2>/dev/null | wc -l || echo "0")
    if [ "$SKILL_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} $SKILL_COUNT skills encontrados"
    else
        echo -e "${YELLOW}⚠${NC} No se encontraron skills"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗${NC} Directorio de skills no existe"
    ((ERRORS++))
fi
echo ""

# Verificar permisos
echo -e "${YELLOW}→ Verificando permisos...${NC}"
if [ -w "$PROJECT_ROOT/.kiro/memory" ]; then
    echo -e "${GREEN}✓${NC} Permisos de escritura en memoria"
else
    echo -e "${RED}✗${NC} Sin permisos de escritura en memoria"
    ((ERRORS++))
fi
echo ""

# Resumen
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Resumen de Verificación                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Todo está correctamente configurado${NC}"
    echo -e "\n${YELLOW}Próximos pasos:${NC}"
    echo -e "  1. Usa ${BLUE}@agentx${NC} en Kiro para empezar"
    echo -e "  2. Lee ${BLUE}QUICKSTART-BETTERAGENTX.md${NC} para ejemplos"
    echo -e "  3. Explora ${BLUE}.kiro/memory/${NC} para ver el contexto"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Configuración completa con $WARNINGS advertencias${NC}"
    echo -e "\nPuedes usar BetterAgentX, pero revisa las advertencias."
    echo ""
    exit 0
else
    echo -e "${RED}✗ Se encontraron $ERRORS errores y $WARNINGS advertencias${NC}"
    echo -e "\n${YELLOW}Solución:${NC}"
    echo -e "  Ejecuta: ${BLUE}./init-betteragentx.sh${NC}"
    echo ""
    exit 1
fi
