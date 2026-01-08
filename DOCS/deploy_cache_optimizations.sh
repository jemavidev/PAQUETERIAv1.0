#!/bin/bash

# ========================================
# DEPLOY: Optimizaciones de Cache a Staging
# ========================================

set -e  # Exit on error

echo "🚀 DEPLOY: Optimizaciones de Cache a Staging"
echo "=============================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Paso 1: Verificar que estamos en staging
echo "📍 Paso 1: Verificando servidor..."
if [ "$(hostname)" != "ip-172-26-13-155" ]; then
    print_error "Este script debe ejecutarse en el servidor staging"
    echo "Ejecuta: ssh staging"
    exit 1
fi
print_success "Servidor staging confirmado"
echo ""

# Paso 2: Ir al directorio del proyecto
echo "📂 Paso 2: Navegando al directorio del proyecto..."
cd /home/ubuntu/PAQUETERIA\ v1.0 || exit 1
print_success "Directorio: $(pwd)"
echo ""

# Paso 3: Pull de cambios
echo "📥 Paso 3: Descargando cambios desde GitHub..."
git fetch origin staging
BEFORE_COMMIT=$(git rev-parse HEAD)
git pull origin staging
AFTER_COMMIT=$(git rev-parse HEAD)

if [ "$BEFORE_COMMIT" = "$AFTER_COMMIT" ]; then
    print_warning "No hay cambios nuevos"
else
    print_success "Cambios descargados: $BEFORE_COMMIT -> $AFTER_COMMIT"
fi
echo ""

# Paso 4: Verificar que Redis esté corriendo
echo "🔍 Paso 4: Verificando Redis..."
if docker-compose -f docker-compose.staging.yml ps redis | grep -q "Up"; then
    print_success "Redis está corriendo"
else
    print_error "Redis no está corriendo"
    exit 1
fi
echo ""

# Paso 5: Rebuild containers
echo "🔨 Paso 5: Rebuilding containers..."
print_warning "Esto tomará 1-2 minutos..."
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d --build

# Esperar a que la app esté lista
echo ""
echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

# Verificar que los containers estén corriendo
if docker-compose -f docker-compose.staging.yml ps app | grep -q "Up"; then
    print_success "Aplicación corriendo"
else
    print_error "Aplicación no está corriendo"
    docker-compose -f docker-compose.staging.yml logs --tail=50 app
    exit 1
fi
echo ""

# Paso 6: Verificar logs
echo "📋 Paso 6: Verificando logs de inicio..."
docker-compose -f docker-compose.staging.yml logs --tail=20 app | grep -E "(startup|Uvicorn|ERROR)" || true
echo ""

# Paso 7: Verificar Redis stats
echo "📊 Paso 7: Verificando Redis..."
docker-compose -f docker-compose.staging.yml exec -T redis redis-cli INFO stats | grep -E "(connected_clients|used_memory|keyspace)" || true
echo ""

# Paso 8: Health check
echo "🏥 Paso 8: Health check..."
HEALTH_RESPONSE=$(curl -s https://staging.jemavi.co/health || echo "ERROR")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    print_success "Health check: OK"
else
    print_error "Health check: FAILED"
    echo "Response: $HEALTH_RESPONSE"
fi
echo ""

# Resumen
echo "=============================================="
echo "🎉 DEPLOY COMPLETADO"
echo "=============================================="
echo ""
echo "📊 Próximos pasos:"
echo "1. Ejecutar tests de cache desde tu máquina local:"
echo "   bash test_cache_with_cookies.sh"
echo ""
echo "2. Monitorear cache hit rate:"
echo "   docker-compose -f docker-compose.staging.yml exec redis redis-cli INFO stats"
echo ""
echo "3. Ver logs en tiempo real:"
echo "   docker-compose -f docker-compose.staging.yml logs -f app | grep Cache"
echo ""
echo "4. Leer el resumen completo:"
echo "   cat RESUMEN_OPTIMIZACION_CACHE.md"
echo ""
print_success "Deploy exitoso! 🚀"
