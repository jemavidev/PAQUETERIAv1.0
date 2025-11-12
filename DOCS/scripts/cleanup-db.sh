#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v1.0 - Script de Conveniencia para Limpieza de Base de Datos
# Versión: 1.0.0
# Fecha: 2025-01-24

# Script de conveniencia para ejecutar la limpieza de base de datos
# desde la raíz del proyecto

echo "🚀 PAQUETES EL CLUB v1.0 - Limpieza de Base de Datos"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "SCRIPTS/database/cleanup_database.sh" ]; then
    echo "❌ Error: Script de limpieza no encontrado"
    echo "💡 Asegúrate de estar en la raíz del proyecto"
    exit 1
fi

# Ejecutar el script de limpieza
echo "📁 Ejecutando script de limpieza..."
./SCRIPTS/database/cleanup_database.sh

echo "✅ Script de conveniencia completado"
