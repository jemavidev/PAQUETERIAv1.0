#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║           VERIFICACIÓN DE SEGURIDAD - SINCRONIZACIÓN BD                    ║
# ║     Verifica que la configuración es segura antes de sincronizar           ║
# ╚════════════════════════════════════════════════════════════════════════════╝

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CODE_DIR="$PROJECT_ROOT/CODE"

ENV_PROD="$CODE_DIR/.env"
ENV_STAGING="$CODE_DIR/.env.staging"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           VERIFICACIÓN DE SEGURIDAD - SINCRONIZACIÓN BD                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Contador de verificaciones
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

log_success() { 
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

log_error() { 
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

log_warning() { 
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++))
}

log_info() { 
    echo -e "${CYAN}ℹ${NC} $1"
}

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "1. VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Verificar .env de producción
if [ -f "$ENV_PROD" ]; then
    log_success "Archivo .env de producción existe"
else
    log_error "Archivo .env de producción NO existe: $ENV_PROD"
fi

# Verificar .env.staging
if [ -f "$ENV_STAGING" ]; then
    log_success "Archivo .env.staging existe"
else
    log_error "Archivo .env.staging NO existe: $ENV_STAGING"
    log_info "Crea el archivo con: cp $CODE_DIR/.env.staging.example $ENV_STAGING"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "2. VERIFICACIÓN DE CREDENCIALES"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Extraer DATABASE_URL de producción
if [ -f "$ENV_PROD" ]; then
    PROD_DB_URL=$(grep "^DATABASE_URL=" "$ENV_PROD" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [ -n "$PROD_DB_URL" ]; then
        log_success "DATABASE_URL de producción encontrado"
        
        # Extraer host de producción
        PROD_HOST=$(echo "$PROD_DB_URL" | sed 's/.*@\([^:]*\):.*/\1/')
        PROD_DB=$(echo "$PROD_DB_URL" | sed 's/.*\/\([^?]*\).*/\1/')
        
        echo -e "  ${BLUE}Host:${NC} $PROD_HOST"
        echo -e "  ${BLUE}Base de datos:${NC} $PROD_DB"
    else
        log_error "DATABASE_URL de producción está vacío"
    fi
fi

# Extraer DATABASE_URL de staging
if [ -f "$ENV_STAGING" ]; then
    STAGING_DB_URL=$(grep "^DATABASE_URL=" "$ENV_STAGING" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [ -n "$STAGING_DB_URL" ]; then
        log_success "DATABASE_URL de staging encontrado"
        
        # Extraer host de staging
        STAGING_HOST=$(echo "$STAGING_DB_URL" | sed 's/.*@\([^:]*\):.*/\1/')
        STAGING_DB=$(echo "$STAGING_DB_URL" | sed 's/.*\/\([^?]*\).*/\1/')
        
        echo -e "  ${BLUE}Host:${NC} $STAGING_HOST"
        echo -e "  ${BLUE}Base de datos:${NC} $STAGING_DB"
    else
        log_error "DATABASE_URL de staging está vacío"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "3. VERIFICACIÓN DE SEGURIDAD CRÍTICA"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Verificar que los hosts son diferentes
if [ -n "$PROD_HOST" ] && [ -n "$STAGING_HOST" ]; then
    if [ "$PROD_HOST" != "$STAGING_HOST" ]; then
        log_success "Los hosts de RDS son DIFERENTES (seguro)"
        echo -e "  ${GREEN}Producción:${NC} $PROD_HOST"
        echo -e "  ${GREEN}Staging:${NC} $STAGING_HOST"
    else
        log_error "¡PELIGRO! Los hosts de RDS son IGUALES"
        echo -e "  ${RED}Ambos apuntan a:${NC} $PROD_HOST"
        log_error "NO ejecutes la sincronización con esta configuración"
    fi
fi

# Verificar que las bases de datos son diferentes
if [ -n "$PROD_DB" ] && [ -n "$STAGING_DB" ]; then
    if [ "$PROD_DB" != "$STAGING_DB" ]; then
        log_success "Los nombres de BD son DIFERENTES (recomendado)"
        echo -e "  ${GREEN}Producción:${NC} $PROD_DB"
        echo -e "  ${GREEN}Staging:${NC} $STAGING_DB"
    else
        log_warning "Los nombres de BD son IGUALES"
        echo -e "  ${YELLOW}Ambos:${NC} $PROD_DB"
        log_warning "Esto es seguro SI los hosts son diferentes"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "4. VERIFICACIÓN DE SCRIPT DE SINCRONIZACIÓN"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

SYNC_SCRIPT="$SCRIPT_DIR/sync_rds_prod_to_staging.sh"

if [ -f "$SYNC_SCRIPT" ]; then
    log_success "Script de sincronización existe"
    
    if [ -x "$SYNC_SCRIPT" ]; then
        log_success "Script es ejecutable"
    else
        log_warning "Script NO es ejecutable"
        log_info "Hazlo ejecutable con: chmod +x $SYNC_SCRIPT"
    fi
else
    log_error "Script de sincronización NO existe: $SYNC_SCRIPT"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "5. VERIFICACIÓN DE COMANDOS PELIGROSOS EN EL SCRIPT"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f "$SYNC_SCRIPT" ]; then
    # Verificar que NO hay comandos DROP en producción
    if grep -q "DROP.*PROD" "$SYNC_SCRIPT"; then
        log_error "¡PELIGRO! Se encontró comando DROP con PROD en el script"
    else
        log_success "No se encontraron comandos DROP en producción"
    fi
    
    # Verificar que NO hay comandos DELETE en producción
    if grep -q "DELETE.*PROD" "$SYNC_SCRIPT"; then
        log_error "¡PELIGRO! Se encontró comando DELETE con PROD en el script"
    else
        log_success "No se encontraron comandos DELETE en producción"
    fi
    
    # Verificar que solo usa pg_dump en producción
    if grep -q "pg_dump.*PROD" "$SYNC_SCRIPT"; then
        log_success "Script usa pg_dump (solo lectura) en producción"
    else
        log_warning "No se encontró pg_dump en el script"
    fi
    
    # Verificar que DROP solo se usa en staging
    if grep -q "DROP.*STAGING" "$SYNC_SCRIPT"; then
        log_success "Comandos DROP solo se usan en staging"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "6. VERIFICACIÓN DE CONECTIVIDAD (OPCIONAL)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Verificar si psql está instalado
if command -v psql >/dev/null 2>&1; then
    log_success "PostgreSQL client (psql) está instalado"
    
    # Intentar conectar a producción (solo si las credenciales están disponibles)
    if [ -n "$PROD_DB_URL" ]; then
        log_info "Probando conexión a producción (solo lectura)..."
        if psql "$PROD_DB_URL" -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Conexión a producción exitosa"
        else
            log_warning "No se pudo conectar a producción (verifica credenciales)"
        fi
    fi
    
    # Intentar conectar a staging
    if [ -n "$STAGING_DB_URL" ]; then
        log_info "Probando conexión a staging..."
        if psql "$STAGING_DB_URL" -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Conexión a staging exitosa"
        else
            log_warning "No se pudo conectar a staging (verifica credenciales)"
        fi
    fi
else
    log_warning "PostgreSQL client (psql) NO está instalado"
    log_info "Instala con: sudo apt-get install postgresql-client"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "RESUMEN DE VERIFICACIÓN"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${GREEN}Verificaciones exitosas:${NC} $CHECKS_PASSED"
echo -e "${YELLOW}Advertencias:${NC} $CHECKS_WARNING"
echo -e "${RED}Errores:${NC} $CHECKS_FAILED"

echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✅ CONFIGURACIÓN SEGURA - PUEDES EJECUTAR LA SINCRONIZACIÓN  ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${CYAN}Para ejecutar la sincronización:${NC}"
        echo -e "  cd $SCRIPT_DIR"
        echo -e "  ./sync_rds_prod_to_staging.sh"
        echo ""
        exit 0
    else
        echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠️  CONFIGURACIÓN CON ADVERTENCIAS - REVISA ANTES DE EJECUTAR║${NC}"
        echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${YELLOW}Revisa las advertencias arriba antes de continuar${NC}"
        echo ""
        exit 0
    fi
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ CONFIGURACIÓN INSEGURA - NO EJECUTES LA SINCRONIZACIÓN    ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}Corrige los errores arriba antes de continuar${NC}"
    echo ""
    exit 1
fi
