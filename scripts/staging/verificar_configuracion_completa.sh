#!/bin/bash
# Script de verificación completa de configuración

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo "================================================================================"
echo "🔍 VERIFICACIÓN COMPLETA DE CONFIGURACIÓN"
echo "================================================================================"
echo ""

# Contador de errores
ERRORS=0
WARNINGS=0

# Función para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        ((ERRORS++))
        return 1
    fi
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

section() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}$1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# 1. VERIFICAR ARCHIVOS DE CONFIGURACIÓN
# ============================================================================
section "1️⃣  VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN"

echo "Verificando existencia de archivos..."
echo ""

# CODE/.env (Local)
if [ -f "CODE/.env" ]; then
    check "CODE/.env existe"
    
    # Verificar DATABASE_URL
    if grep -q "paqueteria_staging" CODE/.env; then
        check "CODE/.env apunta a paqueteria_staging"
    else
        warn "CODE/.env NO apunta a paqueteria_staging"
        info "Contenido actual:"
        grep DATABASE_URL CODE/.env | head -1
    fi
    
    # Verificar S3_PREFIX
    if grep -q "S3_PREFIX=staging/" CODE/.env; then
        check "CODE/.env tiene S3_PREFIX=staging/"
    else
        warn "CODE/.env no tiene S3_PREFIX=staging/"
    fi
else
    warn "CODE/.env NO existe"
fi

echo ""

# CODE/.env.staging (Staging)
if [ -f "CODE/.env.staging" ]; then
    check "CODE/.env.staging existe"
    
    # Verificar DATABASE_URL
    if grep -q "paqueteria_staging" CODE/.env.staging; then
        check "CODE/.env.staging apunta a paqueteria_staging"
    else
        warn "CODE/.env.staging NO apunta a paqueteria_staging"
    fi
else
    warn "CODE/.env.staging NO existe"
fi

echo ""

# .env.production (Producción)
if [ -f ".env.production" ]; then
    check ".env.production existe"
    
    # Verificar DATABASE_URL
    if grep -q "paqueteria_v4" .env.production; then
        check ".env.production apunta a paqueteria_v4"
    else
        warn ".env.production NO apunta a paqueteria_v4"
    fi
else
    warn ".env.production NO existe"
fi

# ============================================================================
# 2. VERIFICAR DOCKER COMPOSE
# ============================================================================
section "2️⃣  VERIFICACIÓN DE DOCKER COMPOSE"

echo "Verificando docker-compose.staging.yml..."
echo ""

if [ -f "docker-compose.staging.yml" ]; then
    check "docker-compose.staging.yml existe"
    
    # Verificar que usa CODE/.env.staging
    if grep -q "CODE/.env.staging" docker-compose.staging.yml; then
        check "docker-compose.staging.yml usa CODE/.env.staging"
    else
        warn "docker-compose.staging.yml NO usa CODE/.env.staging"
        info "Contenido actual:"
        grep -A 2 "env_file:" docker-compose.staging.yml
    fi
else
    warn "docker-compose.staging.yml NO existe"
fi

# ============================================================================
# 3. VERIFICAR ESTRUCTURA DE DIRECTORIOS
# ============================================================================
section "3️⃣  VERIFICACIÓN DE ESTRUCTURA"

echo "Verificando directorios importantes..."
echo ""

[ -d "CODE/src" ] && check "CODE/src existe" || warn "CODE/src NO existe"
[ -d "CODE/src/app" ] && check "CODE/src/app existe" || warn "CODE/src/app NO existe"
[ -d "CODE/src/app/routes" ] && check "CODE/src/app/routes existe" || warn "CODE/src/app/routes NO existe"
[ -f "CODE/src/app/database.py" ] && check "CODE/src/app/database.py existe" || warn "CODE/src/app/database.py NO existe"
[ -f "CODE/src/app/config.py" ] && check "CODE/src/app/config.py existe" || warn "CODE/src/app/config.py NO existe"
[ -f "CODE/requirements.txt" ] && check "CODE/requirements.txt existe" || warn "CODE/requirements.txt NO existe"

# ============================================================================
# 4. VERIFICAR SCRIPTS DE GESTIÓN
# ============================================================================
section "4️⃣  VERIFICACIÓN DE SCRIPTS DE GESTIÓN"

echo "Verificando scripts creados..."
echo ""

[ -f "scripts/staging/01_verify_and_init_staging_db.py" ] && check "Script de verificación DB existe" || warn "Script de verificación DB NO existe"
[ -f "scripts/staging/list_databases.py" ] && check "Script de listado DB existe" || warn "Script de listado DB NO existe"
[ -f "scripts/staging/SETUP_STAGING_GUIDE.md" ] && check "Guía de setup existe" || warn "Guía de setup NO existe"

# ============================================================================
# 5. VERIFICAR DOCUMENTACIÓN
# ============================================================================
section "5️⃣  VERIFICACIÓN DE DOCUMENTACIÓN"

echo "Verificando documentación creada..."
echo ""

[ -f "ARQUITECTURA_BASE_DATOS.md" ] && check "Arquitectura de BD documentada" || warn "Arquitectura de BD NO documentada"
[ -f "RESUMEN_FINAL_CONFIGURACION.md" ] && check "Resumen de configuración existe" || warn "Resumen de configuración NO existe"
[ -f "DEPLOY_STAGING_CHECKLIST.md" ] && check "Checklist de deploy existe" || warn "Checklist de deploy NO existe"
[ -f "ANALISIS_CONEXIONES_DB_COMPLETO.md" ] && check "Análisis de conexiones existe" || warn "Análisis de conexiones NO existe"

# ============================================================================
# 6. VERIFICAR CONTENIDO DE CONFIGURACIÓN
# ============================================================================
section "6️⃣  VERIFICACIÓN DE CONTENIDO DE CONFIGURACIÓN"

echo "Analizando contenido de CODE/.env..."
echo ""

if [ -f "CODE/.env" ]; then
    # Extraer valores importantes
    DB_URL=$(grep "^DATABASE_URL=" CODE/.env | head -1 | cut -d'=' -f2- | tr -d '"')
    POSTGRES_DB=$(grep "^POSTGRES_DB=" CODE/.env | head -1 | cut -d'=' -f2)
    S3_PREFIX=$(grep "^S3_PREFIX=" CODE/.env | head -1 | cut -d'=' -f2)
    
    echo "DATABASE_URL:"
    if [[ $DB_URL == *"paqueteria_staging"* ]]; then
        echo -e "  ${GREEN}✅ Apunta a paqueteria_staging${NC}"
    elif [[ $DB_URL == *"paqueteria_v4"* ]]; then
        echo -e "  ${RED}❌ Apunta a paqueteria_v4 (debería ser staging)${NC}"
        ((ERRORS++))
    elif [[ $DB_URL == *"amazonaws.com"* ]]; then
        echo -e "  ${YELLOW}⚠️  Apunta a AWS RDS pero BD desconocida${NC}"
        ((WARNINGS++))
    else
        echo -e "  ${RED}❌ No apunta a AWS RDS${NC}"
        ((ERRORS++))
    fi
    
    echo ""
    echo "POSTGRES_DB:"
    if [[ $POSTGRES_DB == "paqueteria_staging" ]]; then
        echo -e "  ${GREEN}✅ paqueteria_staging${NC}"
    else
        echo -e "  ${YELLOW}⚠️  $POSTGRES_DB (debería ser paqueteria_staging)${NC}"
        ((WARNINGS++))
    fi
    
    echo ""
    echo "S3_PREFIX:"
    if [[ $S3_PREFIX == "staging/" ]]; then
        echo -e "  ${GREEN}✅ staging/${NC}"
    else
        echo -e "  ${YELLOW}⚠️  '$S3_PREFIX' (debería ser staging/)${NC}"
        ((WARNINGS++))
    fi
fi

# ============================================================================
# 7. VERIFICAR PYTHON Y DEPENDENCIAS
# ============================================================================
section "7️⃣  VERIFICACIÓN DE ENTORNO PYTHON"

echo "Verificando Python..."
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check "Python instalado: $PYTHON_VERSION"
else
    warn "Python3 NO está instalado"
fi

echo ""
echo "Verificando dependencias críticas..."
echo ""

# Verificar si podemos importar módulos críticos
python3 -c "import fastapi" 2>/dev/null && check "FastAPI disponible" || warn "FastAPI NO disponible"
python3 -c "import sqlalchemy" 2>/dev/null && check "SQLAlchemy disponible" || warn "SQLAlchemy NO disponible"
python3 -c "import psycopg2" 2>/dev/null && check "psycopg2 disponible" || warn "psycopg2 NO disponible (necesario para PostgreSQL)"
python3 -c "import uvicorn" 2>/dev/null && check "Uvicorn disponible" || warn "Uvicorn NO disponible"

# ============================================================================
# 8. VERIFICAR DOCKER
# ============================================================================
section "8️⃣  VERIFICACIÓN DE DOCKER"

echo "Verificando Docker..."
echo ""

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check "Docker instalado: $DOCKER_VERSION"
    
    # Verificar si Docker está corriendo
    if docker ps &> /dev/null; then
        check "Docker daemon está corriendo"
        
        # Ver contenedores relacionados
        echo ""
        echo "Contenedores relacionados con paqueteria:"
        docker ps -a --filter "name=paqueteria" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Ninguno encontrado"
    else
        warn "Docker daemon NO está corriendo"
    fi
else
    warn "Docker NO está instalado"
fi

# ============================================================================
# 9. VERIFICAR CONECTIVIDAD A AWS RDS
# ============================================================================
section "9️⃣  VERIFICACIÓN DE CONECTIVIDAD A AWS RDS"

echo "Verificando conectividad a AWS RDS..."
echo ""

RDS_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"

# Verificar resolución DNS
if host $RDS_HOST &> /dev/null; then
    check "DNS resuelve $RDS_HOST"
else
    warn "No se puede resolver DNS de $RDS_HOST"
fi

# Verificar conectividad al puerto 5432
echo ""
info "Probando conectividad al puerto 5432..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$RDS_HOST/5432" 2>/dev/null; then
    check "Puerto 5432 accesible en $RDS_HOST"
else
    warn "No se puede conectar al puerto 5432 (puede ser firewall/security group)"
fi

# ============================================================================
# 10. RESUMEN FINAL
# ============================================================================
section "📊 RESUMEN FINAL"

echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ ¡PERFECTO! Configuración completamente correcta${NC}"
    echo ""
    echo "Todo está listo para:"
    echo "  • Desarrollo local"
    echo "  • Deploy a staging"
    echo "  • Deploy a producción"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠️  Configuración correcta con advertencias${NC}"
    echo ""
    echo -e "Errores: ${GREEN}0${NC}"
    echo -e "Advertencias: ${YELLOW}$WARNINGS${NC}"
    echo ""
    echo "La configuración funciona pero hay algunas advertencias menores."
else
    echo -e "${RED}${BOLD}❌ Se encontraron errores en la configuración${NC}"
    echo ""
    echo -e "Errores: ${RED}$ERRORS${NC}"
    echo -e "Advertencias: ${YELLOW}$WARNINGS${NC}"
    echo ""
    echo "Por favor revisa los errores arriba antes de continuar."
fi

echo ""
echo "================================================================================"
echo ""

# ============================================================================
# 11. PRÓXIMOS PASOS
# ============================================================================
if [ $ERRORS -eq 0 ]; then
    echo -e "${BOLD}🚀 PRÓXIMOS PASOS:${NC}"
    echo ""
    echo "1. Levantar servidor local:"
    echo "   cd CODE"
    echo "   uvicorn src.main:app --reload --port 8000"
    echo ""
    echo "2. Acceder a:"
    echo "   http://localhost:8000"
    echo "   http://localhost:8000/invoices"
    echo ""
    echo "3. Verificar conexión a BD:"
    echo "   curl http://localhost:8000/health"
    echo ""
    echo "4. Para deploy a staging:"
    echo "   docker-compose -f docker-compose.staging.yml up -d"
    echo ""
fi

exit $ERRORS
