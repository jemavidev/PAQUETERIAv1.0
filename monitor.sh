#!/bin/bash
# ========================================
# SCRIPT DE MONITOREO SIMPLE
# ========================================
# Monitoreo lightweight sin Prometheus/Grafana
# Optimizado para AWS Lightsail recursos limitados
# ========================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Función para header
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Limpiar pantalla
clear

print_header "📊 MONITOR PAQUETERÍA v1.0 - LIGHTSAIL"

# ========================================
# 1. ESTADO DE CONTENEDORES
# ========================================

print_header "🐳 Estado de Contenedores"
docker-compose -f docker-compose.lightsail.yml ps

# ========================================
# 2. USO DE RECURSOS
# ========================================

print_header "💻 Uso de Recursos"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

# ========================================
# 3. MEMORIA DEL SISTEMA
# ========================================

print_header "🧠 Memoria del Sistema"
free -h

# ========================================
# 4. DISCO
# ========================================

print_header "💾 Uso de Disco"
df -h | grep -E "Filesystem|/dev/|overlay"

# ========================================
# 5. HEALTH CHECK DE LA APLICACIÓN
# ========================================

print_header "🏥 Health Check"

if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Aplicación: SALUDABLE${NC}"
    HEALTH_DATA=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "{}")
    echo "$HEALTH_DATA"
else
    echo -e "${RED}❌ Aplicación: NO RESPONDE${NC}"
fi

echo ""

# ========================================
# 6. REDIS STATUS
# ========================================

print_header "🔴 Estado de Redis"

if docker-compose -f docker-compose.lightsail.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✅ Redis: ACTIVO${NC}"
    
    # Info de Redis
    echo ""
    echo "Información de Redis:"
    docker-compose -f docker-compose.lightsail.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" info stats 2>/dev/null | grep -E "keyspace_hits|keyspace_misses|total_connections_received|instantaneous_ops_per_sec"
    
    echo ""
    docker-compose -f docker-compose.lightsail.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" info memory 2>/dev/null | grep -E "used_memory_human|used_memory_peak_human|maxmemory_human"
    
    echo ""
    echo "Claves en BD:"
    docker-compose -f docker-compose.lightsail.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" dbsize 2>/dev/null
else
    echo -e "${RED}❌ Redis: NO DISPONIBLE${NC}"
fi

# ========================================
# 7. LOGS RECIENTES (ERRORES)
# ========================================

print_header "📋 Últimos Errores en Logs (últimos 5 minutos)"

echo "App:"
docker-compose -f docker-compose.lightsail.yml logs --since 5m app 2>/dev/null | grep -i "error\|exception\|failed\|warning" | tail -n 10 || echo "No hay errores recientes"

echo ""
echo "Celery:"
docker-compose -f docker-compose.lightsail.yml logs --since 5m celery_worker 2>/dev/null | grep -i "error\|exception\|failed" | tail -n 10 || echo "No hay errores recientes"

# ========================================
# 8. CONEXIONES DE RED
# ========================================

print_header "🌐 Conexiones Activas"

# Contar conexiones al puerto 8000
CONNECTIONS=$(netstat -an 2>/dev/null | grep ":8000" | grep ESTABLISHED | wc -l)
echo "Conexiones activas al puerto 8000: $CONNECTIONS"

# Mostrar top conexiones por IP
echo ""
echo "Top IPs conectadas:"
netstat -an 2>/dev/null | grep ":8000" | grep ESTABLISHED | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -5

# ========================================
# 9. PROCESOS TOP
# ========================================

print_header "⚡ Procesos que más consumen"
ps aux --sort=-%mem | head -n 11

# ========================================
# 10. RESUMEN DE ALERTAS
# ========================================

print_header "⚠️  Alertas"

# Verificar uso de memoria
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEM_USAGE" -gt 85 ]; then
    echo -e "${RED}❌ CRÍTICO: Uso de memoria al ${MEM_USAGE}%${NC}"
elif [ "$MEM_USAGE" -gt 75 ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Uso de memoria al ${MEM_USAGE}%${NC}"
else
    echo -e "${GREEN}✅ Memoria: ${MEM_USAGE}% (Normal)${NC}"
fi

# Verificar uso de disco
DISK_USAGE=$(df -h / | tail -1 | awk '{print int($5)}')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo -e "${RED}❌ CRÍTICO: Uso de disco al ${DISK_USAGE}%${NC}"
elif [ "$DISK_USAGE" -gt 75 ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Uso de disco al ${DISK_USAGE}%${NC}"
else
    echo -e "${GREEN}✅ Disco: ${DISK_USAGE}% (Normal)${NC}"
fi

# Verificar contenedores detenidos
STOPPED=$(docker ps -a -f "status=exited" | grep paqueteria | wc -l)
if [ "$STOPPED" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Hay $STOPPED contenedor(es) detenido(s)${NC}"
else
    echo -e "${GREEN}✅ Todos los contenedores activos${NC}"
fi

# ========================================
# 11. INFORMACIÓN ADICIONAL
# ========================================

print_header "📝 Información Adicional"

echo "Uptime del sistema:"
uptime

echo ""
echo "Load Average:"
cat /proc/loadavg

echo ""
echo "Volúmenes Docker:"
docker volume ls | grep paqueteria

# ========================================
# 12. COMANDOS ÚTILES
# ========================================

print_header "💡 Comandos Útiles"

echo "Ver logs en tiempo real:"
echo "  docker-compose -f docker-compose.lightsail.yml logs -f [servicio]"
echo ""
echo "Reiniciar servicios:"
echo "  docker-compose -f docker-compose.lightsail.yml restart [servicio]"
echo ""
echo "Limpiar caché Redis:"
echo "  docker-compose -f docker-compose.lightsail.yml exec redis redis-cli -a \$REDIS_PASSWORD FLUSHDB"
echo ""
echo "Ver estadísticas en tiempo real:"
echo "  watch -n 5 'docker stats --no-stream'"
echo ""
echo "Backup de base de datos:"
echo "  pg_dump DATABASE_URL > backup_\$(date +%Y%m%d).sql"
echo ""

print_header "✅ Monitor Completado - $(date)"

echo ""
echo "🔄 Para monitoreo continuo, usa: watch -n 30 ./monitor.sh"
echo ""

