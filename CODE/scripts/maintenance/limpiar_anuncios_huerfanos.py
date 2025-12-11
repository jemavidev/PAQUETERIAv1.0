#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Eliminar Anuncios Huérfanos
========================================
Elimina anuncios que no tienen cliente asociado (customer_id = NULL)

Autor: Sistema PAQUETEX
Fecha: 11 de Diciembre, 2025
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Colors:
    OKGREEN = '\033[92m'
    OKCYAN = '\033[96m'
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

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}LIMPIEZA DE ANUNCIOS HUÉRFANOS{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKGREEN}✅ Conectado a RDS{Colors.ENDC}\n")
    
    # Verificar anuncios huérfanos (sin cliente o con cliente inexistente)
    print(f"{Colors.OKCYAN}🔍 Buscando anuncios huérfanos...{Colors.ENDC}\n")
    
    cursor.execute("""
        SELECT a.id, a.guide_number, a.tracking_code, a.customer_name, a.customer_phone, 
               a.announced_at, a.is_processed, a.customer_id
        FROM package_announcements_new a
        LEFT JOIN customers c ON a.customer_id = c.id
        WHERE a.customer_id IS NULL OR c.id IS NULL
        ORDER BY a.announced_at DESC
    """)
    
    anuncios = cursor.fetchall()
    
    if not anuncios:
        print(f"{Colors.OKGREEN}✅ No hay anuncios huérfanos{Colors.ENDC}\n")
        cursor.close()
        conn.close()
        return
    
    print(f"{Colors.WARNING}⚠️  Encontrados {len(anuncios)} anuncios huérfanos:{Colors.ENDC}\n")
    
    for anuncio in anuncios:
        estado = "PROCESADO" if anuncio['is_processed'] else "PENDIENTE"
        print(f"  📦 {anuncio['guide_number']} | {anuncio['tracking_code']}")
        print(f"     Cliente: {anuncio['customer_name']} ({anuncio['customer_phone']})")
        print(f"     Estado: {estado} | Fecha: {anuncio['announced_at']}")
        print()
    
    # Confirmar eliminación
    print(f"{Colors.WARNING}{Colors.BOLD}⚠️  ADVERTENCIA: Estos anuncios serán eliminados permanentemente{Colors.ENDC}")
    respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (escribe 'SI' para confirmar): {Colors.ENDC}")
    
    if respuesta.strip().upper() != 'SI':
        print(f"\n{Colors.WARNING}❌ Operación cancelada{Colors.ENDC}")
        cursor.close()
        conn.close()
        return
    
    # Eliminar anuncios huérfanos
    try:
        print(f"\n{Colors.OKCYAN}🗑️  Eliminando anuncios huérfanos...{Colors.ENDC}")
        
        cursor.execute("""
            DELETE FROM package_announcements_new 
            WHERE id IN (
                SELECT a.id
                FROM package_announcements_new a
                LEFT JOIN customers c ON a.customer_id = c.id
                WHERE a.customer_id IS NULL OR c.id IS NULL
            )
        """)
        
        eliminados = cursor.rowcount
        conn.commit()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ELIMINACIÓN COMPLETADA{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Anuncios eliminados: {eliminados}{Colors.ENDC}\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Se hizo rollback. No se eliminó nada.{Colors.ENDC}\n")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
