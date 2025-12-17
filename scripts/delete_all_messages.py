#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar TODOS los mensajes de la base de datos
PAQUETEX - Sistema de Gestión de Paquetes
Fecha: 2024-12-17

⚠️ ADVERTENCIA: Este script eliminará TODOS los mensajes de forma permanente
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "CODE" / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db_url
from app.models.message import Message

def delete_all_messages():
    """Eliminar todos los mensajes de la base de datos"""
    
    print("=" * 60)
    print("🗑️  ELIMINACIÓN DE TODOS LOS MENSAJES")
    print("=" * 60)
    print()
    
    # Crear conexión a la base de datos
    db_url = get_db_url()
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Mostrar estadísticas ANTES de eliminar
        print("📊 ESTADÍSTICAS ANTES DE ELIMINAR:")
        print("-" * 60)
        
        messages = db.query(Message).all()
        total = len(messages)
        
        if total == 0:
            print("✅ No hay mensajes en la base de datos")
            return
        
        # Contar por estado
        abiertos = len([m for m in messages if m.status.value == "ABIERTO"])
        respondidos = len([m for m in messages if m.status.value == "RESPONDIDO"])
        cerrados = len([m for m in messages if m.status.value == "CERRADO"])
        leidos = len([m for m in messages if m.status.value == "LEIDO"])
        
        print(f"Total de mensajes: {total}")
        print(f"  - ABIERTOS: {abiertos}")
        print(f"  - RESPONDIDOS: {respondidos}")
        print(f"  - CERRADOS: {cerrados}")
        print(f"  - LEÍDOS: {leidos}")
        print()
        
        # Mostrar detalle de mensajes
        print("📋 DETALLE DE MENSAJES:")
        print("-" * 60)
        for msg in messages:
            tracking = msg.tracking_code or (msg.package.tracking_code if msg.package else "N/A")
            print(f"  ID: {msg.id:3d} | Estado: {msg.status.value:12s} | Tracking: {tracking:10s} | Asunto: {msg.subject[:40]}")
        print()
        
        # 2. Confirmar eliminación
        print("⚠️  ADVERTENCIA: Esta operación NO se puede deshacer")
        print()
        respuesta = input("¿Estás seguro de que deseas eliminar TODOS los mensajes? (escribe 'SI' para confirmar): ")
        
        if respuesta.strip().upper() != "SI":
            print("❌ Operación cancelada")
            return
        
        print()
        print("🗑️  Eliminando mensajes...")
        
        # 3. Eliminar todos los mensajes
        deleted_count = db.query(Message).delete()
        db.commit()
        
        print(f"✅ Se eliminaron {deleted_count} mensajes exitosamente")
        print()
        
        # 4. Verificar que se eliminaron todos
        remaining = db.query(Message).count()
        print(f"📊 Mensajes restantes en la base de datos: {remaining}")
        
        if remaining == 0:
            print("✅ Todos los mensajes fueron eliminados correctamente")
        else:
            print(f"⚠️  Advertencia: Aún quedan {remaining} mensajes en la base de datos")
        
        print()
        print("=" * 60)
        print("✅ PROCESO COMPLETADO")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error al eliminar mensajes: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        delete_all_messages()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
