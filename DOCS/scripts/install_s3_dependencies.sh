#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v4.0 - Instalador de Dependencias S3
# Versión: 1.0.0
# Fecha: 2025-01-24

# Script para instalar las dependencias necesarias para la limpieza con S3

echo "🚀 PAQUETES EL CLUB v4.0 - Instalador de Dependencias S3"
echo "======================================================="

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    echo "💡 Instala Python3 antes de continuar"
    exit 1
fi

echo "✅ Python3 encontrado"

# Verificar que pip está disponible
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 no está instalado"
    echo "💡 Instala pip3 antes de continuar"
    exit 1
fi

echo "✅ pip3 encontrado"

# Instalar boto3
echo "📦 Instalando boto3..."
pip3 install boto3

if [ $? -eq 0 ]; then
    echo "✅ boto3 instalado correctamente"
else
    echo "❌ Error instalando boto3"
    exit 1
fi

# Verificar instalación
echo "🔍 Verificando instalación..."
python3 -c "import boto3; print('✅ boto3 importado correctamente')"

if [ $? -eq 0 ]; then
    echo "✅ Todas las dependencias están instaladas"
    echo ""
    echo "📋 Próximos pasos:"
    echo "1. Configura las variables AWS en CODE/LOCAL/.env:"
    echo "   - AWS_ACCESS_KEY_ID=tu_access_key"
    echo "   - AWS_SECRET_ACCESS_KEY=tu_secret_key"
    echo "   - AWS_S3_BUCKET=tu_bucket_name"
    echo "   - AWS_REGION=us-east-1"
    echo ""
    echo "2. Ejecuta la limpieza completa:"
    echo "   ./cleanup-complete.sh"
    echo ""
    echo "3. O ejecuta limpieza selectiva:"
    echo "   python SCRIPTS/database/cleanup_selective.py"
else
    echo "❌ Error verificando boto3"
    exit 1
fi

echo "✅ Instalación completada"
