#!/bin/bash
# ============================================================================
# Script: Verificar Configuración de Staging
# Descripción: Verifica que todo esté configurado correctamente
# Uso: ./verify_staging_setup.sh
# ============================================================================

# No usar set -e para que continúe con todas las verificaciones

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🔍 VERIFICACIÓN DE CONFIGURACIÓN STAGING               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0
WARNINGS=0

# Función para verificar
check() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "  Verificando: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Función para advertencia
warn() {
    local test_name="$1"
    local message="$2"
    
    echo -e "  ${YELLOW}⚠️  $test_name: $message${NC}"
    ((WARNINGS++))
}

echo "📋 VERIFICACIÓN DE ARCHIVOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar archivos de configuración
check ".env (producción)" "test -f .env"
check ".env.production (backup)" "test -f .env.production"
check ".env.staging" "test -f .env.staging"
check "docker-compose.prod.yml" "test -f docker-compose.prod.yml"
check "docker-compose.staging.yml" "test -f docker-compose.staging.yml"

echo ""
echo "📋 VERIFICACIÓN DE CONTENIDO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar que .env apunta a producción
if grep -q "paqueteria_v4" .env; then
    echo -e "  ${GREEN}✅ .env apunta a paqueteria_v4 (producción)${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ .env NO apunta a paqueteria_v4${NC}"
    ((FAILED++))
fi

# Verificar que .env.staging apunta a staging
if grep -q "paqueteria_staging" .env.staging; then
    echo -e "  ${GREEN}✅ .env.staging apunta a paqueteria_staging${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ .env.staging NO apunta a paqueteria_staging${NC}"
    ((FAILED++))
fi

# Verificar que .env.production es igual a .env
if diff -q .env .env.production > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ .env.production es idéntico a .env${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ .env.production NO es idéntico a .env${NC}"
    ((FAILED++))
fi

# Verificar que docker-compose.staging.yml usa .env.staging
if grep -q ".env.staging" docker-compose.staging.yml; then
    echo -e "  ${GREEN}✅ docker-compose.staging.yml usa .env.staging${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ docker-compose.staging.yml NO usa .env.staging${NC}"
    ((FAILED++))
fi

# Verificar que docker-compose.prod.yml NO usa .env.staging
if ! grep -q ".env.staging" docker-compose.prod.yml; then
    echo -e "  ${GREEN}✅ docker-compose.prod.yml NO usa .env.staging${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ docker-compose.prod.yml usa .env.staging (ERROR)${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 VERIFICACIÓN DE SCRIPTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar scripts de base de datos
check "create_staging_database_docker.sh" "test -x scripts/database/create_staging_database_docker.sh"
check "sync_prod_to_staging_initial.sh" "test -x scripts/database/sync_prod_to_staging_initial.sh"
check "sync_prod_to_staging_daily.sh" "test -x scripts/database/sync_prod_to_staging_daily.sh"

echo ""
echo "📋 VERIFICACIÓN DE SINTAXIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar sintaxis de docker-compose (solo si está instalado)
if command -v docker-compose > /dev/null 2>&1; then
    if docker-compose -f docker-compose.staging.yml config > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ docker-compose.staging.yml tiene sintaxis válida${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}❌ docker-compose.staging.yml tiene errores de sintaxis${NC}"
        ((FAILED++))
    fi

    if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ docker-compose.prod.yml tiene sintaxis válida${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}❌ docker-compose.prod.yml tiene errores de sintaxis${NC}"
        ((FAILED++))
    fi
elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
    # Intentar con docker compose (v2)
    if docker compose -f docker-compose.staging.yml config > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ docker-compose.staging.yml tiene sintaxis válida${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}❌ docker-compose.staging.yml tiene errores de sintaxis${NC}"
        ((FAILED++))
    fi

    if docker compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ docker-compose.prod.yml tiene sintaxis válida${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}❌ docker-compose.prod.yml tiene errores de sintaxis${NC}"
        ((FAILED++))
    fi
else
    warn "docker-compose" "No está instalado, saltando verificación de sintaxis"
fi

# Verificar sintaxis de scripts bash
for script in scripts/database/*.sh; do
    if [ -f "$script" ]; then
        if bash -n "$script" 2>/dev/null; then
            echo -e "  ${GREEN}✅ $(basename $script) tiene sintaxis válida${NC}"
            ((PASSED++))
        else
            echo -e "  ${RED}❌ $(basename $script) tiene errores de sintaxis${NC}"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "📋 VERIFICACIÓN DE PUERTOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar puertos en docker-compose.staging.yml
if grep -q "8001:8000" docker-compose.staging.yml; then
    echo -e "  ${GREEN}✅ Staging usa puerto 8001 (no conflicto con producción)${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ Staging NO usa puerto 8001${NC}"
    ((FAILED++))
fi

if grep -q "6380:6380" docker-compose.staging.yml; then
    echo -e "  ${GREEN}✅ Redis staging usa puerto 6380 (no conflicto)${NC}"
    ((PASSED++))
else
    echo -e "  ${RED}❌ Redis staging NO usa puerto 6380${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 VERIFICACIÓN DE DOCUMENTACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "INSTRUCCIONES_CREAR_DB_STAGING.md" "test -f INSTRUCCIONES_CREAR_DB_STAGING.md"
check "GUIA_CREACION_DB_STAGING.md" "test -f GUIA_CREACION_DB_STAGING.md"
check "ESTRATEGIA_BASES_DATOS_STAGING.md" "test -f ESTRATEGIA_BASES_DATOS_STAGING.md"
check "ANALISIS_ESTRUCTURA_PROD_VS_STAGING.md" "test -f ANALISIS_ESTRUCTURA_PROD_VS_STAGING.md"

echo ""
echo "📋 VERIFICACIÓN DE SEGURIDAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar que las contraseñas no estén en archivos de documentación
if ! grep -r "a?HC!2.\*1#?\[==:|289qAI=)#V4kDzl" *.md 2>/dev/null; then
    echo -e "  ${GREEN}✅ No hay contraseñas en archivos .md${NC}"
    ((PASSED++))
else
    warn "Contraseñas" "Se encontraron contraseñas en archivos .md"
fi

# Verificar que .env no esté en git
if grep -q "^\.env$" .gitignore; then
    echo -e "  ${GREEN}✅ .env está en .gitignore${NC}"
    ((PASSED++))
else
    warn ".gitignore" ".env debería estar en .gitignore"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                      📊 RESUMEN                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}✅ Pruebas exitosas: $PASSED${NC}"
echo -e "  ${RED}❌ Pruebas fallidas: $FAILED${NC}"
echo -e "  ${YELLOW}⚠️  Advertencias: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ TODAS LAS VERIFICACIONES PASARON                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🎯 Próximos pasos:"
    echo ""
    echo "1. Crear la base de datos staging en AWS RDS:"
    echo "   - Opción A: Usar AWS Console Query Editor"
    echo "   - Opción B: Ejecutar desde servidor con acceso a RDS:"
    echo "     ./scripts/database/create_staging_database_docker.sh"
    echo ""
    echo "2. Sincronizar datos de producción a staging:"
    echo "   ./scripts/database/sync_prod_to_staging_initial.sh"
    echo ""
    echo "3. Iniciar staging:"
    echo "   docker-compose -f docker-compose.staging.yml up -d"
    echo ""
    echo "4. Verificar que funcione:"
    echo "   curl http://localhost:8001/health"
    echo ""
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║          ❌ ALGUNAS VERIFICACIONES FALLARON                      ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Por favor, revisa los errores arriba y corrígelos antes de continuar."
    echo ""
    exit 1
fi
