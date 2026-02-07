#!/bin/bash

# Script para corregir el intercambio de emisor/adquiriente en facturas DIAN
# Este script reprocesa todos los archivos DIAN con la lógica corregida

echo "=========================================="
echo "🔧 Corrección Emisor/Adquiriente"
echo "=========================================="
echo ""
echo "Este script corregirá el problema donde:"
echo "  - El EMISOR (vendedor/proveedor) estaba siendo guardado como ADQUIRIENTE"
echo "  - El ADQUIRIENTE (comprador/cliente) estaba siendo guardado como EMISOR"
echo ""
echo "Se reprocesarán todos los archivos DIAN existentes."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "CODE/scripts/maintenance/fix_emisor_adquiriente_swap.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "CODE/.venv" ]; then
    echo "🔄 Activando entorno virtual..."
    source CODE/.venv/bin/activate
fi

# Ejecutar script de corrección
echo "🚀 Ejecutando script de corrección..."
echo ""
python3 CODE/scripts/maintenance/fix_emisor_adquiriente_swap.py

echo ""
echo "=========================================="
echo "✅ Script completado"
echo "=========================================="
