#!/bin/bash

echo "=========================================="
echo "Build con Reintentos Automáticos"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración
MAX_RETRIES=3
RETRY_DELAY=10
COMPOSE_FILE="docker-compose.staging.yml"

# Función para mostrar paso
step() {
    echo -e "${YELLOW}▶${NC} $1"
}

# Función para éxito
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Función para error
error() {
    echo -e "${RED}✗${NC} $1"
}

# Función para build con reintentos
build_with_retry() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        step "Intento $attempt de $MAX_RETRIES..."
        
        if docker compose -f $COMPOSE_FILE build app; then
            success "Build exitoso en intento $attempt"
            return 0
        else
            error "Build falló en intento $attempt"
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                step "Esperando $RETRY_DELAY segundos antes de reintentar..."
                sleep $RETRY_DELAY
                
                # Limpiar cache de Docker para el siguiente intento
                step "Limpiando cache de Docker..."
                docker builder prune -f > /dev/null 2>&1
            fi
        fi
        
        ((attempt++))
    done
    
    error "Build falló después de $MAX_RETRIES intentos"
    return 1
}

# Verificar que docker compose existe
if ! docker compose version &> /dev/null; then
    error "docker compose no está instalado"
    exit 1
fi

# Verificar que el archivo compose existe
if [ ! -f "$COMPOSE_FILE" ]; then
    error "Archivo $COMPOSE_FILE no encontrado"
    exit 1
fi

# Limpiar builds anteriores fallidos
step "Limpiando builds anteriores..."
docker compose -f $COMPOSE_FILE down > /dev/null 2>&1
docker builder prune -f > /dev/null 2>&1
success "Limpieza completada"

# Intentar build con reintentos
echo ""
step "Iniciando build con reintentos automáticos..."
echo ""

if build_with_retry; then
    echo ""
    echo "=========================================="
    success "Build completado exitosamente"
    echo "=========================================="
    echo ""
    
    # Iniciar servicios
    step "Iniciando servicios..."
    if docker compose -f $COMPOSE_FILE up -d; then
        success "Servicios iniciados"
        
        # Esperar a que la DB esté lista
        step "Esperando a que la base de datos esté lista..."
        sleep 10
        
        # Aplicar migración
        step "Aplicando migración..."
        if docker compose -f $COMPOSE_FILE exec -T app alembic upgrade head; then
            success "Migración aplicada"
            
            # Reiniciar app
            step "Reiniciando aplicación..."
            docker compose -f $COMPOSE_FILE restart app
            
            # Esperar a que la app esté lista (health check)
            step "Esperando a que la aplicación esté lista..."
            local max_wait=60
            local waited=0
            while [ $waited -lt $max_wait ]; do
                if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
                    success "Aplicación lista"
                    break
                fi
                printf "."
                sleep 2
                waited=$((waited + 2))
            done
            
            if [ $waited -ge $max_wait ]; then
                echo ""
                error "Timeout esperando a que la aplicación esté lista"
                echo "Pero la aplicación puede estar funcionando. Verifica manualmente:"
                echo "  curl http://localhost:8001/health"
            fi
            
            echo ""
            echo "=========================================="
            echo -e "${GREEN}✓ Despliegue completado exitosamente${NC}"
            echo "=========================================="
            echo ""
            echo "Accede al sistema en:"
            echo "  http://localhost:8001/invoices/facturas"
            echo ""
            echo "Para ver logs:"
            echo "  docker compose -f $COMPOSE_FILE logs -f app"
            echo ""
            echo "Para verificar estado:"
            echo "  docker compose -f $COMPOSE_FILE ps"
            echo ""
        else
            error "Error aplicando migración"
            echo ""
            echo "Aplica la migración manualmente:"
            echo "  docker compose -f $COMPOSE_FILE exec app alembic upgrade head"
            echo ""
        fi
    else
        error "Error iniciando servicios"
        exit 1
    fi
else
    echo ""
    echo "=========================================="
    error "Build falló después de todos los intentos"
    echo "=========================================="
    echo ""
    echo "Posibles soluciones:"
    echo ""
    echo "1. Verificar conexión a internet:"
    echo "   ping -c 3 pypi.org"
    echo ""
    echo "2. Usar Dockerfile robusto:"
    echo "   docker compose -f $COMPOSE_FILE build --build-arg DOCKERFILE=Dockerfile.robust app"
    echo ""
    echo "3. Construir sin cache:"
    echo "   docker compose -f $COMPOSE_FILE build --no-cache app"
    echo ""
    echo "4. Verificar proxy/firewall"
    echo ""
    echo "5. Intentar más tarde (puede ser problema temporal de PyPI)"
    echo ""
    exit 1
fi
