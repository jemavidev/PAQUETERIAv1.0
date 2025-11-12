#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v1.0 - Configurador de AWS S3
# Versión: 1.0.0
# Fecha: 2025-01-24

# Script para configurar las variables AWS S3 en CODE/LOCAL/.env

echo "🔧 PAQUETES EL CLUB v1.0 - Configurador de AWS S3"
echo "================================================="

if [ ! -f "CODE/LOCAL/.env" ]; then
    echo "❌ Error: Archivo CODE/LOCAL/.env no encontrado"
    echo "💡 Asegúrate de estar en la raíz del proyecto"
    exit 1
fi

echo "✅ Archivo CODE/LOCAL/.env encontrado"

# Verificar si ya existen las variables AWS
if grep -q "AWS_ACCESS_KEY_ID" CODE/LOCAL/.env; then
    echo "⚠️ Las variables AWS ya están configuradas en CODE/LOCAL/.env"
    echo "📋 Variables actuales:"
    grep "AWS_" CODE/LOCAL/.env
    echo ""
    read -p "¿Quieres actualizarlas? (s/n): " update_vars
    if [ "$update_vars" != "s" ] && [ "$update_vars" != "S" ]; then
        echo "✅ Configuración mantenida"
        exit 0
    fi
fi

echo ""
echo "📝 Configuración de AWS S3"
echo "=========================="
echo "Necesitarás las siguientes credenciales de AWS:"
echo "• AWS Access Key ID"
echo "• AWS Secret Access Key"
echo "• Nombre del bucket S3"
echo "• Región de AWS (opcional, default: us-east-1)"
echo ""

# Solicitar credenciales
read -p "AWS Access Key ID: " aws_access_key
read -p "AWS Secret Access Key: " aws_secret_key
read -p "Nombre del bucket S3: " aws_bucket
read -p "Región AWS (us-east-1): " aws_region

# Usar valores por defecto si están vacíos
aws_region=${aws_region:-us-east-1}

# Validar que no estén vacíos
if [ -z "$aws_access_key" ] || [ -z "$aws_secret_key" ] || [ -z "$aws_bucket" ]; then
    echo "❌ Error: Las credenciales no pueden estar vacías"
    exit 1
fi

echo ""
echo "📋 Resumen de configuración:"
echo "• Access Key ID: $aws_access_key"
echo "• Secret Access Key: ${aws_secret_key:0:4}****"
echo "• Bucket: $aws_bucket"
echo "• Región: $aws_region"
echo ""

read -p "¿Confirmar configuración? (s/n): " confirm

if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo "❌ Configuración cancelada"
    exit 0
fi

# Crear backup del archivo original
cp CODE/LOCAL/.env CODE/LOCAL/.env.backup
echo "✅ Backup creado: CODE/LOCAL/.env.backup"

# Eliminar variables AWS existentes si las hay
sed -i '/^AWS_/d' CODE/LOCAL/.env

# Agregar nuevas variables AWS
echo "" >> CODE/LOCAL/.env
echo "# Configuración AWS S3" >> CODE/LOCAL/.env
echo "AWS_ACCESS_KEY_ID=$aws_access_key" >> CODE/LOCAL/.env
echo "AWS_SECRET_ACCESS_KEY=$aws_secret_key" >> CODE/LOCAL/.env
echo "AWS_S3_BUCKET=$aws_bucket" >> CODE/LOCAL/.env
echo "AWS_REGION=$aws_region" >> CODE/LOCAL/.env

echo "✅ Variables AWS configuradas en CODE/LOCAL/.env"
echo ""
echo "📋 Próximos pasos:"
echo "1. Probar la configuración:"
echo "   ./test-s3-cleanup.sh"
echo ""
echo "2. Ejecutar limpieza completa:"
echo "   ./cleanup-complete.sh"
echo ""
echo "3. O ejecutar limpieza selectiva:"
echo "   python SCRIPTS/database/cleanup_selective.py"
echo ""
echo "✅ Configuración completada"
