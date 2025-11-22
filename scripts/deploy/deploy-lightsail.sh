#!/bin/bash
# ========================================
# SCRIPT DE DESPLIEGUE AWS LIGHTSAIL
# ========================================
# Optimizado para: 1GB RAM, 20GB Disco, 2 CPUs
# ========================================

set -e  # Salir si hay error

echo "========================================="
echo "🚀 DESPLIEGUE PAQUETERÍA v1.0 - LIGHTSAIL"
echo "========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ========================================
# 1. VERIFICAR REQUISITOS
# ========================================

log_info "Verificando requisitos..."

if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    exit 1
fi

if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    log_error "Docker Compose no está instalado"
    exit 1
fi

log_success "Requisitos verificados"
echo ""

# ========================================
# 2. VERIFICAR ARCHIVO .env
# ========================================

log_info "Verificando archivo .env..."

if [ ! -f "CODE/.env" ]; then
    log_error "Archivo CODE/.env no encontrado"
    log_info "Copiando desde env.example..."
    cp CODE/env.example CODE/.env
    log_warning "Debes configurar las variables en CODE/.env antes de continuar"
    exit 1
fi

log_success "Archivo .env encontrado"
echo ""

# ========================================
# 3. LIMPIEZA DE LOGS ANTIGUOS
# ========================================

log_info "Limpiando logs antiguos..."

# Limpiar logs de más de 7 días
find CODE/src -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

log_success "Logs antiguos limpiados"
echo ""

# ========================================
# 4. DETENER CONTENEDORES ANTERIORES
# ========================================

log_info "Deteniendo contenedores anteriores..."

docker compose -f docker-compose.lightsail.yml down 2>/dev/null || true

log_success "Contenedores detenidos"
echo ""

# ========================================
# 5. LIMPIAR RECURSOS NO USADOS
# ========================================

log_info "Limpiando recursos Docker no usados..."

# Eliminar imágenes dangling
docker image prune -f

# Eliminar contenedores detenidos
docker container prune -f

# Eliminar redes no usadas
docker network prune -f

log_success "Recursos limpiados"
echo ""

# ========================================
# 6. CONSTRUIR IMAGEN OPTIMIZADA
# ========================================

log_info "Construyendo imagen Docker optimizada..."

cd CODE

# Construir con Dockerfile optimizado
docker build -f Dockerfile.lightsail -t paqueteria_v1_app:lightsail . --no-cache

cd ..

log_success "Imagen construida correctamente"
echo ""

# ========================================
# 7. INICIAR SERVICIOS
# ========================================

log_info "Iniciando servicios..."

docker compose -f docker-compose.lightsail.yml up -d

log_success "Servicios iniciados"
echo ""

# ========================================
# 8. ESPERAR A QUE LOS SERVICIOS ESTÉN LISTOS
# ========================================

log_info "Esperando a que los servicios estén listos..."

sleep 10

# Verificar Redis
log_info "Verificando Redis..."
for i in {1..30}; do
    if docker compose -f docker-compose.lightsail.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" ping &>/dev/null; then
        log_success "Redis está listo"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Redis no responde después de 30 intentos"
        exit 1
    fi
    sleep 2
done

# Verificar App
log_info "Verificando aplicación..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &>/dev/null; then
        log_success "Aplicación está lista"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Aplicación no responde después de 30 intentos"
        log_info "Verifica los logs con: docker compose -f docker-compose.lightsail.yml logs app"
        exit 1
    fi
    sleep 2
done

echo ""

# ========================================
# 9. EJECUTAR MIGRACIONES (opcional)
# ========================================

read -p "¿Ejecutar migraciones de Alembic? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Ejecutando migraciones..."
    docker compose -f docker-compose.lightsail.yml exec app sh -c "cd /app && alembic upgrade head"
    log_success "Migraciones ejecutadas"
fi

echo ""

# ========================================
# 10. OPTIMIZAR BASE DE DATOS (opcional)
# ========================================

read -p "¿Ejecutar optimizaciones de base de datos? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Ejecutando optimizaciones..."
    log_warning "Esto puede tardar varios minutos..."
    
    # Requiere DATABASE_URL configurado
    if grep -q "DATABASE_URL=" CODE/.env; then
        DB_URL=$(grep "DATABASE_URL=" CODE/.env | cut -d '=' -f2)
        log_info "Ejecuta manualmente: psql $DB_URL -f CODE/optimize_database.sql"
    else
        log_warning "DATABASE_URL no encontrado en .env"
    fi
fi

echo ""

# ========================================
# 11. MOSTRAR ESTADO
# ========================================

log_info "Estado de los contenedores:"
docker compose -f docker-compose.lightsail.yml ps

echo ""

# ========================================
# 12. MOSTRAR INFORMACIÓN DE USO DE RECURSOS
# ========================================

log_info "Uso de recursos:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""

# ========================================
# 13. RESUMEN FINAL
# ========================================

echo "========================================="
log_success "DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "========================================="
echo ""
echo "📊 URLs disponibles:"
echo "   - Aplicación: http://localhost:8000"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Métricas: http://localhost:8000/metrics"
echo ""
echo "📝 Comandos útiles:"
echo "   - Ver logs: docker compose -f docker-compose.lightsail.yml logs -f [servicio]"
echo "   - Reiniciar: docker compose -f docker-compose.lightsail.yml restart [servicio]"
echo "   - Detener: docker compose -f docker-compose.lightsail.yml down"
echo "   - Estado: docker compose -f docker-compose.lightsail.yml ps"
echo "   - Estadísticas: docker stats"
echo ""
echo "🔍 Monitoreo:"
echo "   - Recursos: watch -n 5 docker stats --no-stream"
echo "   - Logs en tiempo real: docker compose -f docker-compose.lightsail.yml logs -f"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Configura Nginx como reverse proxy en el puerto 80/443"
echo "   - Configura SSL con Let's Encrypt (certbot)"
echo "   - Configura backups automáticos de la base de datos"
echo "   - Monitorea el uso de disco regularmente"
echo ""
log_warning "Recuerda configurar el firewall y SSL antes de abrir al público"
echo ""

