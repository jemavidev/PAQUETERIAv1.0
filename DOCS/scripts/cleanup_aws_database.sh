#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos AWS RDS
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configurar variables de base de datos AWS RDS
DB_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="paqueteria_v4"
DB_USER="jveyes"
DB_PASSWORD="a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"

# Configurar variable de entorno para psql
export PGPASSWORD="$DB_PASSWORD"

# Función para confirmar limpieza
confirm_cleanup() {
    echo
    echo "============================================================"
    echo "⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS AWS RDS  ⚠️"
    echo "============================================================"
    echo "Este script eliminará TODOS los datos de las siguientes tablas:"
    echo "• packages"
    echo "• package_history"
    echo "• package_announcements_new"
    echo "• messages"
    echo "• file_uploads"
    echo "• customers"
    echo
    echo "Esta acción NO SE PUEDE DESHACER."
    echo "============================================================"
    echo
    read -p "¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): " response
    
    if [ "$response" = "SI" ]; then
        return 0
    else
        echo "❌ Operación cancelada por el usuario"
        return 1
    fi
}

# Función para obtener conteos de tablas
get_table_counts() {
    log "📊 Obteniendo conteo de registros..."
    
    tables=("packages" "package_history" "package_announcements_new" "messages" "file_uploads" "customers")
    total_records=0
    
    for table in "${tables[@]}"; do
        count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ' || echo "0")
        echo "📊 $table: $count registros"
        total_records=$((total_records + count))
    done
    
    echo "Total de registros a eliminar: $total_records"
    return $total_records
}

# Función para limpiar tablas
cleanup_tables() {
    log "🧹 Iniciando limpieza de base de datos AWS RDS..."
    
    # Orden de eliminación (respetando foreign keys)
    cleanup_queries=(
        "DELETE FROM file_uploads;"
        "DELETE FROM messages;"
        "DELETE FROM package_history;"
        "DELETE FROM package_announcements_new;"
        "DELETE FROM packages;"
        "DELETE FROM customers;"
    )
    
    total_deleted=0
    
    for query in "${cleanup_queries[@]}"; do
        table_name=$(echo "$query" | grep -o 'FROM [a-zA-Z_]*' | cut -d' ' -f2)
        
        # Contar registros antes de eliminar
        count_before=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table_name;" 2>/dev/null | tr -d ' ' || echo "0")
        
        if [ "$count_before" -gt 0 ]; then
            # Ejecutar eliminación
            deleted_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "$query" 2>/dev/null | grep -o 'DELETE [0-9]*' | cut -d' ' -f2 || echo "0")
            total_deleted=$((total_deleted + deleted_count))
            log "🗑️ $table_name: $deleted_count registros eliminados"
        else
            log "✅ $table_name: Ya está vacía"
        fi
    done
    
    success "Limpieza completada. Total de registros eliminados: $total_deleted"
}

# Función para resetear secuencias
reset_sequences() {
    log "🔄 Reseteando secuencias..."
    
    sequences=("packages_id_seq" "messages_id_seq" "file_uploads_id_seq")
    
    for sequence in "${sequences[@]}"; do
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "ALTER SEQUENCE $sequence RESTART WITH 1;" 2>/dev/null || warning "No se pudo resetear $sequence"
        log "🔄 Secuencia $sequence reseteada"
    done
    
    success "Secuencias reseteadas correctamente"
}

# Función para verificar limpieza
verify_cleanup() {
    log "🔍 Verificando limpieza..."
    
    tables=("packages" "package_history" "package_announcements_new" "messages" "file_uploads" "customers")
    all_empty=true
    
    for table in "${tables[@]}"; do
        count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ' || echo "0")
        if [ "$count" -gt 0 ]; then
            warning "$table aún tiene $count registros"
            all_empty=false
        else
            log "✅ $table está vacía"
        fi
    done
    
    if [ "$all_empty" = true ]; then
        success "Verificación exitosa: Todas las tablas están vacías"
    else
        warning "Algunas tablas no se limpiaron completamente"
    fi
    
    return $([ "$all_empty" = true ] && echo 0 || echo 1)
}

# Función principal
main() {
    echo "🚀 PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos AWS RDS"
    echo "====================================================================="
    
    # Verificar conexión a la base de datos
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        error "No se puede conectar a la base de datos AWS RDS"
        echo "💡 Verifica las credenciales y la conectividad"
        exit 1
    fi
    
    # Mostrar conteo actual
    get_table_counts
    total_records=$?
    
    if [ $total_records -eq 0 ]; then
        success "La base de datos ya está vacía"
        exit 0
    fi
    
    # Solicitar confirmación
    if ! confirm_cleanup; then
        exit 0
    fi
    
    # Ejecutar limpieza
    cleanup_tables
    
    # Resetear secuencias
    reset_sequences
    
    # Verificar limpieza
    verify_cleanup
    
    success "Limpieza completada exitosamente"
    echo "📝 Revisa los logs para más detalles"
}

# Ejecutar función principal
main "$@"

