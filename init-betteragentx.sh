#!/bin/bash
# ============================================================================
# BetterAgentX Initialization Script
# ============================================================================
# Este script inicializa BetterAgentX en el proyecto PAQUETEX
# Crea enlaces simbólicos para integrar los agentes y skills sin duplicar archivos
# ============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorios
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BETTERAGENTX_DIR="$PROJECT_ROOT/BetterAgentX"
KIRO_DIR="$PROJECT_ROOT/.kiro"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         BetterAgentX Initialization for PAQUETEX          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que BetterAgentX existe
if [ ! -d "$BETTERAGENTX_DIR" ]; then
    echo -e "${RED}✗ Error: BetterAgentX no encontrado en $BETTERAGENTX_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ BetterAgentX encontrado${NC}"

# Crear estructura .kiro si no existe
echo -e "\n${YELLOW}→ Creando estructura .kiro...${NC}"
mkdir -p "$KIRO_DIR/steering"
mkdir -p "$KIRO_DIR/memory"
mkdir -p "$KIRO_DIR/settings"
mkdir -p "$PROJECT_ROOT/.agents"

# Función para crear enlace simbólico seguro
create_symlink() {
    local source=$1
    local target=$2
    local name=$3
    
    if [ -L "$target" ]; then
        echo -e "${YELLOW}  ⚠ $name ya existe (enlace simbólico), actualizando...${NC}"
        rm "$target"
    elif [ -e "$target" ]; then
        echo -e "${YELLOW}  ⚠ $name ya existe (archivo/directorio), respaldando...${NC}"
        mv "$target" "${target}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    ln -s "$source" "$target"
    echo -e "${GREEN}  ✓ $name enlazado${NC}"
}

# Enlazar agentes
echo -e "\n${YELLOW}→ Enlazando agentes especializados...${NC}"
create_symlink \
    "$BETTERAGENTX_DIR/.kiro/steering/agents" \
    "$KIRO_DIR/steering/agents" \
    "Agentes"

# Enlazar AgentX (orquestador)
create_symlink \
    "$BETTERAGENTX_DIR/.kiro/steering/agentx" \
    "$KIRO_DIR/steering/agentx" \
    "AgentX Orchestrator"

# Enlazar common
create_symlink \
    "$BETTERAGENTX_DIR/.kiro/steering/_common" \
    "$KIRO_DIR/steering/_common" \
    "Common Steering"

# Enlazar skills
echo -e "\n${YELLOW}→ Enlazando skills...${NC}"
create_symlink \
    "$BETTERAGENTX_DIR/.agents/skills" \
    "$PROJECT_ROOT/.agents/skills" \
    "Skills"

# Copiar configuración (no enlazar, para permitir personalización)
echo -e "\n${YELLOW}→ Configurando BetterAgentX...${NC}"

if [ ! -f "$KIRO_DIR/settings/betteragents.json" ]; then
    cp "$BETTERAGENTX_DIR/config/betteragents.json" "$KIRO_DIR/settings/betteragents.json"
    echo -e "${GREEN}  ✓ Configuración copiada${NC}"
else
    echo -e "${YELLOW}  ⚠ Configuración ya existe, no se sobrescribe${NC}"
fi

if [ ! -f "$KIRO_DIR/settings/agent-skills.json" ]; then
    cp "$BETTERAGENTX_DIR/config/agent-skills.json" "$KIRO_DIR/settings/agent-skills.json"
    echo -e "${GREEN}  ✓ Configuración de skills copiada${NC}"
else
    echo -e "${YELLOW}  ⚠ Configuración de skills ya existe, no se sobrescribe${NC}"
fi

# Crear archivos de memoria si no existen
echo -e "\n${YELLOW}→ Inicializando sistema de memoria...${NC}"

if [ ! -f "$KIRO_DIR/memory/active-context.md" ]; then
    cat > "$KIRO_DIR/memory/active-context.md" << 'EOF'
# 📋 Contexto Activo - PAQUETEX

## Proyecto
**Nombre:** PAQUETEX v1.0
**Tipo:** Sistema de gestión de facturas y proveedores
**Stack:** Python/Flask

## Contexto Actual
- Sistema de facturación electrónica
- Gestión de proveedores
- Procesamiento de XML/PDF
- Deploy automatizado

## Última Actualización
$(date +"%Y-%m-%d %H:%M:%S")
EOF
    echo -e "${GREEN}  ✓ active-context.md creado${NC}"
else
    echo -e "${YELLOW}  ⚠ active-context.md ya existe${NC}"
fi

if [ ! -f "$KIRO_DIR/memory/progress.md" ]; then
    cat > "$KIRO_DIR/memory/progress.md" << 'EOF'
# 📊 Progreso - PAQUETEX

## Tareas Completadas
- [x] Inicialización de BetterAgentX

## Tareas en Progreso
- [ ] Integración completa del sistema

## Tareas Pendientes
- [ ] Configuración personalizada de agentes

## Última Actualización
$(date +"%Y-%m-%d %H:%M:%S")
EOF
    echo -e "${GREEN}  ✓ progress.md creado${NC}"
else
    echo -e "${YELLOW}  ⚠ progress.md ya existe${NC}"
fi

if [ ! -f "$KIRO_DIR/memory/decision-log.md" ]; then
    cat > "$KIRO_DIR/memory/decision-log.md" << 'EOF'
# 📝 Registro de Decisiones - PAQUETEX

## ADR-001: Integración de BetterAgentX
**Fecha:** $(date +"%Y-%m-%d")
**Estado:** Aceptado

### Contexto
Necesitamos un sistema de agentes especializados para mejorar el desarrollo.

### Decisión
Integrar BetterAgentX mediante enlaces simbólicos.

### Consecuencias
- ✅ Mantiene BetterAgentX actualizable
- ✅ No duplica archivos
- ✅ Fácil de mantener
EOF
    echo -e "${GREEN}  ✓ decision-log.md creado${NC}"
else
    echo -e "${YELLOW}  ⚠ decision-log.md ya existe${NC}"
fi

if [ ! -f "$KIRO_DIR/memory/patterns.md" ]; then
    cat > "$KIRO_DIR/memory/patterns.md" << 'EOF'
# 🎯 Patrones Identificados - PAQUETEX

## Patrones de Arquitectura
- Sistema modular con servicios especializados
- Separación de concerns (routes, services, models)

## Patrones de Código
- Flask blueprints para organización
- Servicios para lógica de negocio

## Última Actualización
$(date +"%Y-%m-%d %H:%M:%S")
EOF
    echo -e "${GREEN}  ✓ patterns.md creado${NC}"
else
    echo -e "${YELLOW}  ⚠ patterns.md ya existe${NC}"
fi

# Crear archivo de configuración del proyecto
echo -e "\n${YELLOW}→ Creando configuración del proyecto...${NC}"
cat > "$PROJECT_ROOT/.betteragentx-config" << EOF
# BetterAgentX Configuration for PAQUETEX
BETTERAGENTX_VERSION=3.1.0
BETTERAGENTX_ENABLED=true
BETTERAGENTX_DIR=$BETTERAGENTX_DIR
PROJECT_NAME=PAQUETEX
PROJECT_VERSION=1.0
INITIALIZED_DATE=$(date +"%Y-%m-%d %H:%M:%S")
EOF
echo -e "${GREEN}  ✓ Configuración del proyecto creada${NC}"

# Resumen
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✓ Inicialización Completa              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}BetterAgentX está ahora integrado en PAQUETEX${NC}"
echo ""
echo -e "${YELLOW}Estructura creada:${NC}"
echo -e "  📁 .kiro/steering/agents/     → Agentes especializados"
echo -e "  📁 .kiro/steering/agentx/     → Orquestador AgentX"
echo -e "  📁 .kiro/steering/_common/    → Configuración común"
echo -e "  📁 .kiro/memory/              → Sistema de memoria"
echo -e "  📁 .agents/skills/            → Skills especializados"
echo -e "  📄 .kiro/settings/            → Configuraciones"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo -e "  1. Usa ${BLUE}@agentx${NC} para interactuar con el orquestador"
echo -e "  2. Usa ${BLUE}@architect${NC}, ${BLUE}@coder${NC}, etc. para agentes específicos"
echo -e "  3. Revisa ${BLUE}.kiro/memory/${NC} para ver el contexto del proyecto"
echo ""
echo -e "${GREEN}¡Listo para usar! 🚀${NC}"
