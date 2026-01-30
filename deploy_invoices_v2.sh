#!/bin/bash

echo "=========================================="
echo "Despliegue del Sistema de Facturas V2"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# 1. Verificar sintaxis
step "Verificando sintaxis de archivos..."
bash CODE/check_syntax.sh > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Sintaxis correcta"
else
    error "Errores de sintaxis encontrados"
    bash CODE/check_syntax.sh
    exit 1
fi

# 2. Construir imagen
step "Construyendo imagen Docker..."
docker-compose -f docker-compose.staging.yml build app
if [ $? -eq 0 ]; then
    success "Imagen construida"
else
    error "Error construyendo imagen"
    exit 1
fi

# 3. Iniciar servicios
step "Iniciando servicios..."
docker-compose -f docker-compose.staging.yml up -d
if [ $? -eq 0 ]; then
    success "Servicios iniciados"
else
    error "Error iniciando servicios"
    exit 1
fi

# 4. Esperar a que la base de datos esté lista
step "Esperando a que la base de datos esté lista..."
sleep 5
success "Base de datos lista"

# 5. Aplicar migración
step "Aplicando migración de base de datos..."
docker-compose -f docker-compose.staging.yml exec -T app alembic upgrade head
if [ $? -eq 0 ]; then
    success "Migración aplicada"
else
    error "Error aplicando migración"
    echo ""
    echo "Intentando aplicar migración manualmente..."
    docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
fi

# 6. Reiniciar app para asegurar que carga correctamente
step "Reiniciando aplicación..."
docker-compose -f docker-compose.staging.yml restart app
if [ $? -eq 0 ]; then
    success "Aplicación reiniciada"
else
    error "Error reiniciando aplicación"
    exit 1
fi

# 7. Esperar a que el health check pase
step "Esperando health check..."
sleep 10

# 8. Verificar que el servicio está corriendo
step "Verificando estado del servicio..."
if docker-compose -f docker-compose.staging.yml ps app | grep -q "Up"; then
    success "Servicio corriendo correctamente"
else
    error "Servicio no está corriendo"
    echo ""
    echo "Mostrando logs:"
    docker-compose -f docker-compose.staging.yml logs --tail=50 app
    exit 1
fi

# 9. Verificar que la ruta responde
step "Verificando que la aplicación responde..."
sleep 5
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    success "Aplicación respondiendo correctamente"
else
    error "Aplicación no responde"
    echo ""
    echo "Mostrando logs:"
    docker-compose -f docker-compose.staging.yml logs --tail=50 app
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Despliegue completado exitosamente${NC}"
echo "=========================================="
echo ""
echo "Accede al sistema en:"
echo "  http://localhost:8000/invoices/facturas"
echo ""
echo "Para ver logs:"
echo "  docker-compose -f docker-compose.staging.yml logs -f app"
echo ""
