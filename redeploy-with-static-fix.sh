#!/bin/bash
# Script para redesplegar con corrección de archivos estáticos

set -e

echo "========================================="
echo "REDESPLIEGUE CON CORRECCIÓN DE ESTÁTICOS"
echo "========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar el progreso
show_progress() {
    echo -e "${BLUE}▶${NC} $1"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅${NC} $1"
}

# Función para mostrar error
show_error() {
    echo -e "${RED}❌${NC} $1"
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.lightsail.yml" ]; then
    show_error "No se encuentra docker-compose.lightsail.yml"
    echo "Por favor, ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar archivos estáticos
show_progress "Verificando archivos estáticos locales..."
if [ ! -d "CODE/src/static" ]; then
    show_error "No existe el directorio CODE/src/static"
    exit 1
fi

if [ ! -f "CODE/src/static/images/favicon.png" ]; then
    show_warning "No se encuentra favicon.png"
fi

if [ ! -f "CODE/src/static/images/logo.png" ]; then
    show_warning "No se encuentra logo.png"
fi

show_success "Archivos estáticos verificados"
echo ""

# Mostrar archivos estáticos disponibles
echo "Archivos en CODE/src/static/images/:"
ls -lh CODE/src/static/images/ 2>/dev/null || echo "  (vacío)"
echo ""

# Detener contenedores
show_progress "Deteniendo contenedores actuales..."
docker compose -f docker-compose.lightsail.yml down
show_success "Contenedores detenidos"
echo ""

# Limpiar imágenes antiguas (opcional)
read -p "¿Deseas limpiar imágenes antiguas? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    show_progress "Limpiando imágenes antiguas..."
    docker image prune -f
    show_success "Imágenes limpiadas"
fi
echo ""

# Reconstruir imagen
show_progress "Reconstruyendo imagen de la aplicación..."
docker compose -f docker-compose.lightsail.yml build --no-cache app
show_success "Imagen reconstruida"
echo ""

# Iniciar contenedores
show_progress "Iniciando contenedores..."
docker compose -f docker-compose.lightsail.yml up -d
show_success "Contenedores iniciados"
echo ""

# Esperar a que la aplicación esté lista
show_progress "Esperando que la aplicación esté lista..."
sleep 15

# Verificar que los contenedores estén corriendo
show_progress "Verificando estado de contenedores..."
docker compose -f docker-compose.lightsail.yml ps
echo ""

# Obtener el nombre del contenedor
CONTAINER=$(docker ps --filter "name=paqueteria_app" --format "{{.Names}}" | head -n 1)

if [ -z "$CONTAINER" ]; then
    show_error "No se encontró el contenedor de la aplicación"
    echo ""
    echo "Contenedores activos:"
    docker ps
    exit 1
fi

show_success "Contenedor encontrado: $CONTAINER"
echo ""

# Verificar estructura de directorios
show_progress "Verificando estructura de directorios en el contenedor..."
echo ""
echo "Contenido de /app/src/static/:"
docker exec $CONTAINER ls -lh /app/src/static/ 2>/dev/null || show_error "No existe /app/src/static/"
echo ""
echo "Contenido de /app/src/static/images/:"
docker exec $CONTAINER ls -lh /app/src/static/images/ 2>/dev/null || show_error "No existe /app/src/static/images/"
echo ""

# Probar acceso a archivos estáticos
show_progress "Probando acceso a archivos estáticos..."
sleep 5

echo ""
echo "Prueba 1: favicon.png"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/favicon.png)
if [ "$HTTP_CODE" = "200" ]; then
    show_success "favicon.png accesible (HTTP $HTTP_CODE)"
else
    show_error "favicon.png no accesible (HTTP $HTTP_CODE)"
fi

echo ""
echo "Prueba 2: logo.png"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/logo.png)
if [ "$HTTP_CODE" = "200" ]; then
    show_success "logo.png accesible (HTTP $HTTP_CODE)"
else
    show_error "logo.png no accesible (HTTP $HTTP_CODE)"
fi

echo ""
echo "Prueba 3: main.css"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/css/main.css)
if [ "$HTTP_CODE" = "200" ]; then
    show_success "main.css accesible (HTTP $HTTP_CODE)"
else
    show_error "main.css no accesible (HTTP $HTTP_CODE)"
fi

echo ""
echo "Prueba 4: Health check"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_CODE" = "200" ]; then
    show_success "Health check OK (HTTP $HTTP_CODE)"
else
    show_error "Health check falló (HTTP $HTTP_CODE)"
fi

echo ""
show_progress "Logs recientes del contenedor:"
echo "----------------------------------------"
docker logs $CONTAINER --tail 30
echo "----------------------------------------"
echo ""

# Resumen final
echo "========================================="
echo -e "${GREEN}✅ REDESPLIEGUE COMPLETADO${NC}"
echo "========================================="
echo ""
echo "📊 Estado de los servicios:"
docker compose -f docker-compose.lightsail.yml ps
echo ""
echo "📝 Comandos útiles:"
echo "  Ver logs en tiempo real:    docker logs -f $CONTAINER"
echo "  Reiniciar aplicación:       docker compose -f docker-compose.lightsail.yml restart app"
echo "  Ver todos los logs:         docker compose -f docker-compose.lightsail.yml logs"
echo "  Detener todo:               docker compose -f docker-compose.lightsail.yml down"
echo ""
echo "🌐 URLs de acceso:"
echo "  Aplicación:                 http://localhost:8000"
echo "  Health check:               http://localhost:8000/health"
echo "  Favicon:                    http://localhost:8000/static/images/favicon.png"
echo ""

# Si hay errores, mostrar ayuda adicional
if [ "$HTTP_CODE" != "200" ]; then
    echo ""
    show_warning "Algunos archivos no son accesibles. Verifica:"
    echo "  1. Que los archivos existan en CODE/src/static/"
    echo "  2. Los permisos de los archivos"
    echo "  3. Los logs del contenedor para más detalles"
    echo "  4. La configuración de Nginx si está en uso"
fi
