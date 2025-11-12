#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v4.0 - Script de Conveniencia para Limpieza Simple (DB + S3)
# Versión: 1.0.0
# Fecha: 2025-01-24

# Script de conveniencia para ejecutar la limpieza simple del sistema
# (Base de datos + AWS S3) desde la raíz del proyecto

echo "🚀 PAQUETES EL CLUB v4.0 - Limpieza Simple (DB + S3)"
echo "==================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "SCRIPTS/database/cleanup_database_simple_s3.py" ]; then
    echo "❌ Error: Script de limpieza simple no encontrado"
    echo "💡 Asegúrate de estar en la raíz del proyecto"
    exit 1
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado o no está en el PATH"
    exit 1
fi

# Verificar que boto3 está instalado
if ! python3 -c "import boto3" &> /dev/null; then
    echo "❌ Error: boto3 no está instalado"
    echo "💡 Instala con: pip install boto3"
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

# Verificar variables AWS requeridas
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_S3_BUCKET" ]; then
    echo "❌ Error: Variables de entorno AWS no configuradas"
    echo "💡 Configura AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY y AWS_S3_BUCKET en CODE/LOCAL/.env"
    exit 1
fi

# Ejecutar el script de limpieza simple
echo "📁 Ejecutando limpieza simple (DB + S3)..."
python3 SCRIPTS/database/cleanup_database_simple_s3.py

echo "✅ Script de conveniencia completado"
