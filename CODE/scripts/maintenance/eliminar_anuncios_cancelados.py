#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Eliminar Anuncios Cancelados
=========================================
Elimina anuncios con is_active = False (cancelados)

Autor: Sistema PAQUETEX
Fecha: 11 de Diciembre, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_db_connection():
    """Obtener conexión a la base de datos RDS"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error conectando a la base de datos: {e}{Colors.ENDC}")
        sys.exit(1)

def crear_backup(conn):
    """Crear backup de anuncios cancelados"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'backup_anuncios_cancelados_{timestamp}.json'
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKCYAN}📦 Creando backup...{Colors.ENDC}")
    
    cursor.execute("""
        SELECT * FROM package_announcements_new WHERE is_active = false
    """)
    backup_data = {'anuncios_cancelados': [dict(row) for row in cursor.fetchall()]}
    
    cursor.close()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"{Colors.OKGREEN}✅ Backup creado: {backup_file}{Colors.ENDC}")
    return str(backup_file)

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}ELIMINAR ANUNCIOS CANCELADOS{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKGREEN}✅ Conectado a RDS{Colors.ENDC}\n")
    
    # Verificar anuncios cancelados
    print(f"{Colors.BOLD}📊 VERIFICANDO ANUNCIOS CANCELADOS{Colors.ENDC}\n")
    
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM package_announcements_new 
        WHERE is_active = false
    """)
    total_cancelados = cursor.fetchone()['total']
    
    if total_cancelados == 0:
        print(f"{Colors.OKGREEN}✅ No hay anuncios cancelados para eliminar{Colors.ENDC}\n")
        cursor.close()
        conn.close()
        return
    
    # Mostrar anuncios cancelados
    cursor.execute("""
        SELECT id, guide_number, tracking_code, customer_name, customer_phone,
               announced_at, is_processed, package_id
        FROM package_announcements_new 
        WHERE is_active = false
        ORDER BY announced_at DESC
    """)
    
    anuncios = cursor.fetchall()
    
    print(f"{Colors.WARNING}⚠️  Encontrados {total_cancelados} anuncios cancelados{Colors.ENDC}\n")
    
    for anuncio in anuncios:
        estado = "PROCESADO" if anuncio['is_processed'] else "PENDIENTE"
        tiene_paquete = "Sí" if anuncio['package_id'] else "No"
        print(f"  📦 {anuncio['guide_number']} | {anuncio['tracking_code']}")
        print(f"     Cliente: {anuncio['customer_name']} ({anuncio['customer_phone']})")
        print(f"     Estado: {estado} | Tiene paquete: {tiene_paquete}")
        print(f"     Fecha: {anuncio['announced_at']}")
        print()
    
    # Estadísticas
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN is_processed = true THEN 1 END) as procesados,
            COUNT(CASE WHEN is_processed = false THEN 1 END) as pendientes,
            COUNT(CASE WHEN package_id IS NOT NULL THEN 1 END) as con_paquete
        FROM package_announcements_new 
        WHERE is_active = false
    """)
    
    stats = cursor.fetchone()
    
    print(f"{Colors.OKCYAN}Estadísticas:{Colors.ENDC}")
    print(f"  - Total: {stats['total']}")
    print(f"  - Procesados: {stats['procesados']}")
    print(f"  - Pendientes: {stats['pendientes']}")
    print(f"  - Con paquete asociado: {stats['con_paquete']}")
    
    # Confirmar
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  ADVERTENCIA: Estos anuncios serán eliminados permanentemente{Colors.ENDC}")
    print(f"{Colors.WARNING}Se creará un backup antes de eliminar{Colors.ENDC}")
    print(f"{Colors.WARNING}Los clientes NO serán eliminados{Colors.ENDC}\n")
    
    respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (escribe 'SI' para confirmar): {Colors.ENDC}")
    
    if respuesta.strip().upper() != 'SI':
        print(f"\n{Colors.WARNING}❌ Operación cancelada{Colors.ENDC}")
        cursor.close()
        conn.close()
        return
    
    # Crear backup
    backup_file = crear_backup(conn)
    
    # Ejecutar eliminación
    try:
        print(f"\n{Colors.BOLD}🚀 INICIANDO ELIMINACIÓN{Colors.ENDC}\n")
        
        print(f"{Colors.OKCYAN}Eliminando anuncios cancelados...{Colors.ENDC}")
        
        cursor.execute("""
            DELETE FROM package_announcements_new 
            WHERE is_active = false
        """)
        
        eliminados = cursor.rowcount
        
        # Commit
        conn.commit()
        
        # Reporte
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ELIMINACIÓN COMPLETADA EXITOSAMENTE{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📊 RESUMEN:{Colors.ENDC}\n")
        print(f"  - Anuncios eliminados: {eliminados}")
        
        print(f"\n{Colors.OKGREEN}✅ Backup guardado en: {backup_file}{Colors.ENDC}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ ERROR: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Se hizo rollback. No se eliminó nada.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Backup disponible en: {backup_file}{Colors.ENDC}")
    
    finally:
        cursor.close()
        conn.close()
        print(f"\n{Colors.OKCYAN}Conexión cerrada{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
