#!/bin/bash
# ========================================
# PAQUETERÍA v1.0 - Script de Inicio
# ========================================
# Script para facilitar el inicio del sistema
# ========================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "No se encuentra docker-compose.prod.yml"
    print_info "Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

print_info "Iniciando PAQUETERÍA v1.0 PROD..."

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
fi

print_success "Docker y Docker Compose están instalados"

# Verificar que el archivo .env existe
if [ ! -f ".env" ]; then
    print_warning "El archivo .env no existe en la raíz del proyecto"
    if [ -f "CODE/env.example" ]; then
        print_info "Creando .env desde CODE/env.example..."
        cp CODE/env.example .env
        print_warning "⚠️  IMPORTANTE: Debes editar .env con tus valores reales antes de continuar"
        print_info "   Especialmente:"
        print_info "   - DATABASE_URL (RDS endpoint)"
        print_info "   - SECRET_KEY (generar con: openssl rand -hex 32)"
        print_info "   - REDIS_PASSWORD"
        print_info "   - Credenciales de AWS S3"
        echo ""
        read -p "¿Deseas continuar sin editar el .env? (NO recomendado) [y/N]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Edita .env y ejecuta este script nuevamente"
            exit 0
        fi
    else
        print_error "No se encuentra CODE/env.example"
        exit 1
    fi
else
    print_success "Archivo .env existe"
fi

# Verificar variables críticas en .env
print_info "Verificando variables críticas en .env..."
if grep -q "tu-rds-endpoint" .env || grep -q "tu_usuario" .env || grep -q "tu-secret-key" .env; then
    print_warning "⚠️  El archivo .env contiene valores de ejemplo"
    print_warning "   Debes editar .env con tus valores reales"
    read -p "¿Deseas continuar de todas formas? [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Edita .env y ejecuta este script nuevamente"
        exit 0
    fi
fi

# Verificar estructura de directorios
print_info "Verificando estructura de directorios..."
if [ ! -d "CODE/src" ]; then
    print_error "No se encuentra CODE/src"
    exit 1
fi

if [ ! -d "CODE/alembic" ]; then
    print_error "No se encuentra CODE/alembic"
    exit 1
fi

print_success "Estructura de directorios correcta"

# Construir imágenes Docker
print_info "Construyendo imágenes Docker..."
docker compose -f docker-compose.prod.yml build

if [ $? -eq 0 ]; then
    print_success "Imágenes Docker construidas correctamente"
else
    print_error "Error al construir imágenes Docker"
    exit 1
fi

# Verificar si necesitamos ejecutar migraciones
print_info "Verificando si necesitamos ejecutar migraciones..."
print_warning "⚠️  Asegúrate de que tu RDS esté configurado y accesible antes de continuar"
read -p "¿Deseas ejecutar las migraciones ahora? [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Ejecutando migraciones..."
    docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head
    
    if [ $? -eq 0 ]; then
        print_success "Migraciones ejecutadas correctamente"
    else
        print_error "Error al ejecutar migraciones"
        print_info "Verifica tu conexión a RDS y tus credenciales en CODE/.env"
        exit 1
    fi
else
    print_warning "Saltando migraciones. Puedes ejecutarlas después con:"
    print_info "docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head"
fi

# Iniciar servicios
print_info "Iniciando servicios..."
docker compose -f docker-compose.prod.yml up -d

if [ $? -eq 0 ]; then
    print_success "Servicios iniciados correctamente"
else
    print_error "Error al iniciar servicios"
    exit 1
fi

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."
sleep 5

# Verificar estado de los contenedores
print_info "Verificando estado de los contenedores..."
docker compose -f docker-compose.prod.yml ps

# Verificar health check
print_info "Verificando health check..."
sleep 10
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Health check exitoso"
    curl http://localhost:8000/health
else
    print_warning "Health check falló. Revisa los logs:"
    print_info "docker compose -f docker-compose.prod.yml logs -f app"
fi

# Mostrar información útil
echo ""
print_success "✅ PAQUETERÍA v1.0 PROD está ejecutándose"
echo ""
print_info "Comandos útiles:"
print_info "  Ver logs: docker compose -f docker-compose.prod.yml logs -f app"
print_info "  Ver estado: docker compose -f docker-compose.prod.yml ps"
print_info "  Detener: docker compose -f docker-compose.prod.yml down"
print_info "  Reiniciar: docker compose -f docker-compose.prod.yml restart app"
echo ""
print_info "Aplicación disponible en: http://localhost:8000"
print_info "Health check: http://localhost:8000/health"
echo ""

