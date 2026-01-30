#!/bin/bash

# ========================================
# Script de Restauración - Sistema de Facturas
# ========================================
# Restaura el código del sistema de facturas desde el backup
# ========================================

set -e

echo "🔄 RESTAURACIÓN - Sistema de Facturas"
echo "======================================"
echo ""

# Verificar que existe el backup
if [ ! -d "BACKUP_INVOICES_OLD" ]; then
    echo "❌ Error: No se encuentra el directorio de backup"
    exit 1
fi

echo "📦 Restaurando desde BACKUP_INVOICES_OLD/..."
echo ""

restored=0

# Restaurar rutas
if [ -f "BACKUP_INVOICES_OLD/invoices_routes_backup.py" ]; then
    cp BACKUP_INVOICES_OLD/invoices_routes_backup.py CODE/src/app/routes/invoices.py
    echo "✅ Restaurado: invoices.py"
    ((restored++))
fi

if [ -f "BACKUP_INVOICES_OLD/invoices_mockup_backup.py" ]; then
    cp BACKUP_INVOICES_OLD/invoices_mockup_backup.py CODE/src/app/routes/invoices_mockup.py
    echo "✅ Restaurado: invoices_mockup.py"
    ((restored++))
fi

# Restaurar servicios
if [ -f "BACKUP_INVOICES_OLD/invoice_service_backup.py" ]; then
    cp BACKUP_INVOICES_OLD/invoice_service_backup.py CODE/src/app/services/invoice_service.py
    echo "✅ Restaurado: invoice_service.py"
    ((restored++))
fi

if [ -f "BACKUP_INVOICES_OLD/supplier_invoice_service_backup.py" ]; then
    cp BACKUP_INVOICES_OLD/supplier_invoice_service_backup.py CODE/src/app/services/supplier_invoice_service.py
    echo "✅ Restaurado: supplier_invoice_service.py"
    ((restored++))
fi

if [ -f "BACKUP_INVOICES_OLD/pdf_extractor_service_backup.py" ]; then
    cp BACKUP_INVOICES_OLD/pdf_extractor_service_backup.py CODE/src/app/services/pdf_extractor_service.py
    echo "✅ Restaurado: pdf_extractor_service.py"
    ((restored++))
fi

# Restaurar templates
if [ -d "BACKUP_INVOICES_OLD/templates_invoices_backup" ]; then
    mkdir -p CODE/src/templates/invoices
    cp -r BACKUP_INVOICES_OLD/templates_invoices_backup/* CODE/src/templates/invoices/
    echo "✅ Restaurado: templates/invoices/"
    ((restored++))
fi

echo ""
echo "======================================"
echo "✅ Restauración completada"
echo "   Archivos restaurados: $restored"
echo ""
echo "⚠️  Recuerda verificar que main.py tenga los imports correctos"
echo ""
