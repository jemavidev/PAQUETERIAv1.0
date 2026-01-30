#!/bin/bash

# ========================================
# Script de Limpieza Total - Sistema de Facturas
# ========================================
# Elimina todo el código existente del sistema de facturas
# para permitir una refactorización completa desde cero.
#
# ADVERTENCIA: Este script es DESTRUCTIVO
# Asegúrate de tener backup antes de ejecutar
# ========================================

set -e  # Salir si hay error

echo "🔄 REFACTORIZACIÓN COMPLETA - Sistema de Facturas"
echo "=================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para confirmar
confirm() {
    read -p "⚠️  $1 (escribe 'SI' para confirmar): " response
    if [ "$response" != "SI" ]; then
        echo "❌ Operación cancelada"
        exit 1
    fi
}

# Verificar que estamos en el directorio correcto
if [ ! -d "CODE/src/app/routes" ]; then
    echo "❌ Error: No se encuentra el directorio CODE/src/app/routes"
    echo "   Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo "📦 Verificando backup..."
if [ ! -d "BACKUP_INVOICES_OLD" ]; then
    echo "❌ Error: No se encuentra el directorio de backup"
    echo "   Ejecuta primero el backup"
    exit 1
fi

echo "✅ Backup encontrado en BACKUP_INVOICES_OLD/"
echo ""

# Mostrar qué se va a eliminar
echo "📋 Archivos que se eliminarán:"
echo "------------------------------"
echo "  Rutas:"
echo "    - CODE/src/app/routes/invoices.py"
echo "    - CODE/src/app/routes/invoices_mockup.py"
echo ""
echo "  Servicios:"
echo "    - CODE/src/app/services/invoice_service.py"
echo "    - CODE/src/app/services/supplier_invoice_service.py"
echo "    - CODE/src/app/services/pdf_extractor_service.py"
echo "    - CODE/src/app/services/enhanced_pdf_extractor.py"
echo ""
echo "  Templates:"
echo "    - CODE/src/templates/invoices/ (carpeta completa)"
echo ""

confirm "¿Estás SEGURO de que quieres eliminar TODOS estos archivos?"

echo ""
echo "🗑️  Iniciando limpieza..."
echo ""

# Contador de archivos eliminados
deleted=0

# 1. Eliminar rutas
echo "1️⃣  Eliminando rutas..."
if [ -f "CODE/src/app/routes/invoices.py" ]; then
    rm CODE/src/app/routes/invoices.py
    echo "   ✅ Eliminado: invoices.py"
    ((deleted++))
else
    echo "   ⚠️  No encontrado: invoices.py"
fi

if [ -f "CODE/src/app/routes/invoices_mockup.py" ]; then
    rm CODE/src/app/routes/invoices_mockup.py
    echo "   ✅ Eliminado: invoices_mockup.py"
    ((deleted++))
else
    echo "   ⚠️  No encontrado: invoices_mockup.py"
fi

# 2. Eliminar servicios
echo ""
echo "2️⃣  Eliminando servicios..."
services=(
    "invoice_service.py"
    "supplier_invoice_service.py"
    "pdf_extractor_service.py"
    "enhanced_pdf_extractor.py"
)

for service in "${services[@]}"; do
    if [ -f "CODE/src/app/services/$service" ]; then
        rm "CODE/src/app/services/$service"
        echo "   ✅ Eliminado: $service"
        ((deleted++))
    else
        echo "   ⚠️  No encontrado: $service"
    fi
done

# 3. Eliminar templates
echo ""
echo "3️⃣  Eliminando templates..."
if [ -d "CODE/src/templates/invoices" ]; then
    file_count=$(find CODE/src/templates/invoices -type f | wc -l)
    rm -rf CODE/src/templates/invoices
    echo "   ✅ Eliminada carpeta completa: invoices/ ($file_count archivos)"
    ((deleted++))
else
    echo "   ⚠️  No encontrada: carpeta invoices/"
fi

# 4. Limpiar __pycache__
echo ""
echo "4️⃣  Limpiando archivos compilados..."
find CODE/src/app/routes/__pycache__ -name "*invoice*" -delete 2>/dev/null || true
find CODE/src/app/services/__pycache__ -name "*invoice*" -delete 2>/dev/null || true
echo "   ✅ Archivos .pyc eliminados"

echo ""
echo "=================================================="
echo "✅ Limpieza completada"
echo "   Archivos/carpetas eliminados: $deleted"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "   1. Editar CODE/src/main.py y eliminar:"
echo "      - from app.routes.invoices import router as invoices_router"
echo "      - app.include_router(invoices_router, prefix=\"/invoices\", ...)"
echo ""
echo "   2. Editar CODE/src/templates/base/base.html y eliminar:"
echo "      - Enlace del menú a /invoices"
echo ""
echo "   3. Reiniciar el servidor para aplicar cambios"
echo ""
echo "🔄 Para restaurar desde backup:"
echo "   bash restore_invoices_backup.sh"
echo ""
