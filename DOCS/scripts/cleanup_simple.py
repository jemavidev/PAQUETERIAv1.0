#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza Simple
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script ejecuta la limpieza usando la configuración del contenedor.
"""

import sys
import os
sys.path.append('/app/src')

# Configuración de base de datos (extraída de los logs)
DATABASE_URL = "postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl$***@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_v4"

from sqlalchemy import create_engine, text

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Limpieza de Base de Datos")
    print("="*60)
    
    # Obtener conexión
    try:
        engine = create_engine(DATABASE_URL)
        print("✅ Conexión a base de datos establecida")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False
    
    # Tablas a limpiar en orden correcto
    tables = [
        'file_uploads',
        'messages', 
        'package_history',
        'package_announcements_new',
        'packages',
        'customers'
    ]
    
    total_deleted = 0
    
    print("\n📊 Estado actual de la base de datos:")
    
    with engine.connect() as conn:
        # Mostrar conteo actual
        for table in tables:
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                print(f'📊 {table}: {count} registros')
                total_deleted += count
            except Exception as e:
                print(f'⚠️ Error al contar {table}: {e}')
        
        print(f"\nTotal de registros a eliminar: {total_deleted}")
        
        if total_deleted == 0:
            print("✅ La base de datos ya está vacía")
            return True
        
        # Solicitar confirmación
        print("\n" + "="*60)
        print("⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS  ⚠️")
        print("="*60)
        print("Este script eliminará TODOS los datos de las siguientes tablas:")
        for table in tables:
            print(f"• {table}")
        print("\nEsta acción NO SE PUEDE DESHACER.")
        print("="*60)
        
        response = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ").strip()
        if response != 'SI':
            print("❌ Operación cancelada por el usuario")
            return False
        
        print("\n🧹 Iniciando limpieza...")
        
        # Ejecutar limpieza
        total_deleted = 0
        for table in tables:
            try:
                # Contar registros antes
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count_before = result.scalar()
                
                if count_before > 0:
                    # Eliminar registros
                    result = conn.execute(text(f'DELETE FROM {table}'))
                    deleted = result.rowcount
                    total_deleted += deleted
                    print(f'🗑️ {table}: {deleted} registros eliminados')
                else:
                    print(f'✅ {table}: Ya está vacía')
                    
            except Exception as e:
                print(f'❌ Error en {table}: {e}')
        
        # Commit cambios
        conn.commit()
        print(f'\n🎉 Limpieza completada. Total eliminado: {total_deleted} registros')
        
        # Verificar limpieza
        print("\n🔍 Verificando limpieza...")
        all_empty = True
        for table in tables:
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                if count > 0:
                    print(f'⚠️ {table} aún tiene {count} registros')
                    all_empty = False
                else:
                    print(f'✅ {table} está vacía')
            except Exception as e:
                print(f'❌ Error al verificar {table}: {e}')
        
        if all_empty:
            print("\n🎉 Verificación exitosa: Todas las tablas están vacías")
        else:
            print("\n⚠️ Algunas tablas no se limpiaron completamente")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
