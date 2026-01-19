#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                    SCRIPT DE INICIO RÁPIDO - DESARROLLO                   ║
# ╚════════════════════════════════════════════════════════════════════════════╝

set -e

echo "🚀 Iniciando PAQUETEX en modo desarrollo..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que docker-compose.dev.yml existe
if [ ! -f "docker-compose.dev.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.dev.yml no encontrado${NC}"
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./start-dev.sh [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  start       Iniciar servicios (por defecto)"
    echo "  stop        Detener servicios"
    echo "  restart     Reiniciar servicios"
    echo "  logs        Ver logs en tiempo real"
    echo "  status      Ver estado de servicios"
    echo "  shell       Entrar al contenedor de la app"
    echo "  db          Conectar a PostgreSQL"
    echo "  migrate     Ejecutar migraciones"
    echo "  reprocess   Reprocesar facturas de proveedores"
    echo "  clean       Limpiar contenedores y volúmenes"
    echo "  help        Mostrar esta ayuda"
    echo ""
}

# Función para iniciar servicios
start_services() {
    echo -e "${BLUE}📦 Levantando servicios...${NC}"
    docker compose -f docker-compose.dev.yml up -d
    
    echo ""
    echo -e "${YELLOW}⏳ Esperando que los servicios estén listos...${NC}"
    sleep 5
    
    echo ""
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
    echo ""
    echo -e "${BLUE}🌐 Aplicación disponible en:${NC}"
    echo "   http://localhost:8000"
    echo ""
    echo -e "${BLUE}📚 Documentación API:${NC}"
    echo "   http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}📊 Ver logs:${NC}"
    echo "   ./start-dev.sh logs"
    echo ""
}

# Función para detener servicios
stop_services() {
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    docker compose -f docker-compose.dev.yml down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para reiniciar servicios
restart_services() {
    echo -e "${YELLOW}🔄 Reiniciando servicios...${NC}"
    docker compose -f docker-compose.dev.yml restart
    echo -e "${GREEN}✅ Servicios reiniciados${NC}"
}

# Función para ver logs
show_logs() {
    echo -e "${BLUE}📋 Mostrando logs (Ctrl+C para salir)...${NC}"
    docker compose -f docker-compose.dev.yml logs -f
}

# Función para ver estado
show_status() {
    echo -e "${BLUE}📊 Estado de servicios:${NC}"
    echo ""
    docker compose -f docker-compose.dev.yml ps
}

# Función para entrar al shell
enter_shell() {
    echo -e "${BLUE}🐚 Entrando al contenedor...${NC}"
    docker compose -f docker-compose.dev.yml exec app bash
}

# Función para conectar a BD
connect_db() {
    echo -e "${BLUE}🗄️  Conectando a PostgreSQL...${NC}"
    docker compose -f docker-compose.dev.yml exec postgres psql -U paquetex -d paqueteria
}

# Función para ejecutar migraciones
run_migrations() {
    echo -e "${BLUE}🔄 Ejecutando migraciones...${NC}"
    docker compose -f docker-compose.dev.yml exec app alembic upgrade head
    echo -e "${GREEN}✅ Migraciones completadas${NC}"
}

# Función para reprocesar facturas
reprocess_invoices() {
    echo -e "${BLUE}🔄 Reprocesando facturas de proveedores...${NC}"
    docker compose -f docker-compose.dev.yml exec app python /app/reprocesar_facturas_supplier.py
}

# Función para limpiar
clean_all() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los contenedores y volúmenes${NC}"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🧹 Limpiando...${NC}"
        docker compose -f docker-compose.dev.yml down -v
        echo -e "${GREEN}✅ Limpieza completada${NC}"
    else
        echo "Cancelado"
    fi
}

# Procesar argumentos
case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    shell)
        enter_shell
        ;;
    db)
        connect_db
        ;;
    migrate)
        run_migrations
        ;;
    reprocess)
        reprocess_invoices
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Opción no válida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
