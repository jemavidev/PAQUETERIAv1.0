#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v1.0 - Script de Conveniencia para Pruebas S3
# Versión: 1.0.0
# Fecha: 2025-01-24

# Script de conveniencia para probar la funcionalidad de limpieza S3

echo "🧪 PAQUETES EL CLUB v1.0 - Prueba de Limpieza S3"
echo "==============================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "SCRIPTS/database/test_cleanup_s3.py" ]; then
    echo "❌ Error: Script de prueba no encontrado"
    echo "💡 Asegúrate de estar en la raíz del proyecto"
    exit 1
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado o no está en el PATH"
    exit 1
fi

# Cargar variables de entorno
if [ -f "CODE/LOCAL/.env" ]; then
    source CODE/LOCAL/.env
    echo "✅ Variables de entorno cargadas desde CODE/LOCAL/.env"
else
    echo "❌ Error: Archivo CODE/LOCAL/.env no encontrado"
    echo "💡 Ejecuta: ./SCRIPTS/database/configure_aws_s3.sh"
    exit 1
fi

# Ejecutar las pruebas
echo "📁 Ejecutando pruebas de limpieza S3..."
python3 SCRIPTS/database/test_cleanup_s3.py

echo "✅ Script de prueba completado"
