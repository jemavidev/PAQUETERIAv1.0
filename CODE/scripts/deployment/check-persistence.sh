#!/bin/bash
# ========================================
# SCRIPT DE VERIFICACIÓN DE PERSISTENCIA Y PREPARACIÓN
# ========================================
# Verifica que todo esté listo para reiniciar el servidor
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "🔍 VERIFICACIÓN DE PERSISTENCIA"
echo "========================================="
echo ""

# Función para encontrar la raíz del proyecto
find_project_root() {
    local current_dir="$1"
    local max_depth=10
    local depth=0
    
    while [ "$depth" -lt "$max_depth" ]; do
        if [ -d "$current_dir/.git" ]; then
            echo "$current_dir"
            return 0
        fi
        
        if [ "$current_dir" = "/" ]; then
            return 1
        fi
        
        current_dir="$(dirname "$current_dir")"
        depth=$((depth + 1))
    done
    
    return 1
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT=$(find_project_root "$SCRIPT_DIR")
cd "$PROJECT_ROOT"

# Contador de verificaciones
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# ========================================
# 1. VERIFICAR GIT - Cambios sin commitear
# ========================================
echo -e "${BLUE}📦 Verificando Git...${NC}"

if git diff-index --quiet HEAD --; then
    echo -e "  ${GREEN}✓${NC} No hay cambios sin commitear"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "  ${YELLOW}⚠${NC} Hay cambios sin commitear:"
    git status --short | head -5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
fi

# Verificar si hay archivos sin rastrear importantes
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -z "$UNTRACKED" ]; then
    echo -e "  ${GREEN}✓${NC} No hay archivos sin rastrear"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "  ${YELLOW}⚠${NC} Archivos sin rastrear:"
    echo "$UNTRACKED" | head -5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
fi

# Verificar estado de la rama
CURRENT_BRANCH=$(git branch --show-current)
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH 2>/dev/null || echo "")

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo -e "  ${GREEN}✓${NC} Repositorio sincronizado con remoto"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "  ${YELLOW}⚠${NC} Repositorio NO sincronizado con remoto"
    echo "    Local:  $LOCAL_COMMIT"
    echo "    Remoto: $REMOTE_COMMIT"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ========================================
# 2. VERIFICAR VOLÚMENES DOCKER
# ========================================
echo -e "${BLUE}🐳 Verificando volúmenes Docker...${NC}"

if command -v docker &> /dev/null; then
    VOLUMES=("redis_data" "uploads_data" "logs_data" "celery_beat_data" "prometheus_data" "grafana_data")
    
    for volume in "${VOLUMES[@]}"; do
        if docker volume ls | grep -q "$volume"; then
            echo -e "  ${GREEN}✓${NC} Volumen $volume existe"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} Volumen $volume NO existe (se creará al iniciar)"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
    
    # Verificar contenedores en ejecución
    if docker ps | grep -q "paqueteria"; then
        echo -e "  ${GREEN}✓${NC} Hay contenedores en ejecución"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep paqueteria | sed 's/^/    /'
    else
        echo -e "  ${YELLOW}⚠${NC} No hay contenedores en ejecución"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${RED}✗${NC} Docker no está instalado o no está en PATH"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

echo ""

# ========================================
# 3. VERIFICAR ARCHIVOS CRÍTICOS
# ========================================
echo -e "${BLUE}📄 Verificando archivos críticos...${NC}"

CRITICAL_FILES=(
    "CODE/.env"
    "docker-compose.prod.yml"
    "CODE/Dockerfile"
    "CODE/requirements.txt"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file existe"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${RED}✗${NC} $file NO existe"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
done

# Verificar que .env no esté en git (debe estar ignorado)
if git ls-files --error-unmatch CODE/.env &>/dev/null; then
    echo -e "  ${RED}✗${NC} CODE/.env está en Git (debe estar en .gitignore)"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
else
    echo -e "  ${GREEN}✓${NC} CODE/.env está ignorado por Git (correcto)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

echo ""

# ========================================
# 4. VERIFICAR DIRECTORIOS DE DATOS
# ========================================
echo -e "${BLUE}📁 Verificando directorios de datos...${NC}"

DATA_DIRS=(
    "CODE/src/uploads"
)

for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir existe"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} $dir NO existe (se creará automáticamente)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo ""

# ========================================
# 5. VERIFICAR SCRIPTS DE DEPLOYMENT
# ========================================
echo -e "${BLUE}🔧 Verificando scripts de deployment...${NC}"

SCRIPTS=(
    "CODE/scripts/deployment/pull-update.sh"
    "CODE/scripts/deployment/update.sh"
    "CODE/scripts/deployment/git-add-server-files.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo -e "  ${GREEN}✓${NC} $script existe y es ejecutable"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    elif [ -f "$script" ]; then
        echo -e "  ${YELLOW}⚠${NC} $script existe pero NO es ejecutable"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${RED}✗${NC} $script NO existe"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
done

echo ""

# ========================================
# RESUMEN
# ========================================
echo "========================================="
echo "📊 RESUMEN"
echo "========================================="
echo ""
echo -e "  ${GREEN}✓ Verificaciones exitosas: $CHECKS_PASSED${NC}"
echo -e "  ${YELLOW}⚠ Advertencias: $WARNINGS${NC}"
echo -e "  ${RED}✗ Errores: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ TODO LISTO: El servidor está listo para reiniciar${NC}"
        echo ""
        echo "Los siguientes datos son PERSISTENTES:"
        echo "  ✓ Código fuente (en Git)"
        echo "  ✓ Volúmenes Docker:"
        echo "    - redis_data (datos de Redis)"
        echo "    - uploads_data (archivos subidos)"
        echo "    - logs_data (logs de la aplicación)"
        echo "    - celery_beat_data (programación de tareas)"
        echo "    - prometheus_data (métricas)"
        echo "    - grafana_data (dashboards)"
        echo ""
        echo "Después de reiniciar:"
        echo "  1. Los contenedores se reiniciarán automáticamente (restart: unless-stopped)"
        echo "  2. Los volúmenes mantendrán todos los datos"
        echo "  3. El código se cargará desde Git (o desde el montaje local)"
        exit 0
    else
        echo -e "${YELLOW}⚠ LISTO CON ADVERTENCIAS: Revisa las advertencias arriba${NC}"
        echo ""
        echo "Puedes reiniciar, pero revisa las advertencias primero."
        exit 0
    fi
else
    echo -e "${RED}❌ NO LISTO: Hay errores que deben corregirse antes de reiniciar${NC}"
    echo ""
    echo "Revisa los errores mostrados arriba antes de proceder."
    exit 1
fi

