#!/bin/bash
# ========================================
# PAQUETERÍA v1.0 - Script de Configuración de .env
# ========================================
# Script para crear y configurar el archivo .env
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
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../../.." && pwd )"

cd "$PROJECT_DIR"

print_info "Configurando archivo .env para PAQUETERÍA v1.0 PROD..."

# Verificar que env.example existe
if [ ! -f "CODE/env.example" ]; then
    print_error "No se encuentra CODE/env.example"
    exit 1
fi

# Crear .env desde env.example si no existe
if [ ! -f ".env" ]; then
    print_info "Creando .env desde CODE/env.example..."
    cp CODE/env.example .env
    print_success "Archivo .env creado en la raíz del proyecto"
else
    print_warning "El archivo .env ya existe en la raíz del proyecto"
    read -p "¿Deseas sobrescribirlo? [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp CODE/env.example .env
        print_success "Archivo .env sobrescrito"
    else
        print_info "Manteniendo archivo .env existente"
    fi
fi

# Generar SECRET_KEY
print_info "Generando SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
print_success "SECRET_KEY generada: $SECRET_KEY"

# Actualizar SECRET_KEY en .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
else
    # Linux
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
fi

print_success "SECRET_KEY actualizada en .env"

# Mostrar instrucciones
echo ""
print_warning "⚠️  IMPORTANTE: Debes editar .env con tus valores reales:"
echo ""
print_info "Variables OBLIGATORIAS:"
print_info "  1. DATABASE_URL - URL de conexión a RDS"
print_info "     Ejemplo: postgresql://usuario:password@rds-endpoint.us-east-1.rds.amazonaws.com:5432/paqueteria_v4"
echo ""
print_info "  2. REDIS_PASSWORD - Contraseña de Redis"
print_info "     Genera una contraseña segura"
echo ""
print_info "  3. AWS_ACCESS_KEY_ID - Clave de acceso de AWS"
print_info "  4. AWS_SECRET_ACCESS_KEY - Clave secreta de AWS"
print_info "  5. AWS_S3_BUCKET - Nombre del bucket S3"
echo ""
print_info "Variables RECOMENDADAS:"
print_info "  - SMTP_HOST, SMTP_USER, SMTP_PASSWORD (para emails)"
print_info "  - LIWA_API_KEY, LIWA_ACCOUNT, LIWA_PASSWORD (para SMS)"
echo ""
print_info "Después de editar .env, ejecuta:"
print_info "  ./start.sh"
echo ""

