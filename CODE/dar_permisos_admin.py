#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para dar permisos de ADMINISTRADOR a un usuario
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dar_permisos_admin(username: str):
    """Dar permisos de administrador a un usuario"""
    db = SessionLocal()
    try:
        # Buscar usuario
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.error(f"❌ Usuario '{username}' no encontrado")
            logger.info("\n📋 Usuarios disponibles:")
            users = db.query(User).all()
            for u in users:
                logger.info(f"   - {u.username} ({u.full_name}) - Rol actual: {u.role.value}")
            return False
        
        # Verificar si ya es admin
        if user.role == UserRole.ADMIN:
            logger.info(f"✅ El usuario '{username}' ya tiene permisos de ADMINISTRADOR")
            return True
        
        # Actualizar rol
        logger.info(f"🔄 Cambiando rol de '{username}' de {user.role.value} a ADMIN...")
        user.role = UserRole.ADMIN
        db.commit()
        
        logger.info(f"✅ Permisos de ADMINISTRADOR otorgados exitosamente a '{username}'")
        logger.info(f"   Nombre: {user.full_name}")
        logger.info(f"   Email: {user.email}")
        logger.info(f"   Rol anterior: {user.role.value}")
        logger.info(f"   Rol nuevo: ADMIN")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al dar permisos: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def listar_usuarios():
    """Listar todos los usuarios del sistema"""
    db = SessionLocal()
    try:
        logger.info("\n📋 Usuarios en el sistema:")
        logger.info("-" * 80)
        users = db.query(User).all()
        
        if not users:
            logger.info("   No hay usuarios en el sistema")
            return
        
        for user in users:
            status = "✅ Activo" if user.is_active else "❌ Inactivo"
            logger.info(f"   Usuario: {user.username}")
            logger.info(f"   Nombre: {user.full_name}")
            logger.info(f"   Email: {user.email}")
            logger.info(f"   Rol: {user.role.value}")
            logger.info(f"   Estado: {status}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"❌ Error al listar usuarios: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔐 SCRIPT PARA DAR PERMISOS DE ADMINISTRADOR")
    print("="*80 + "\n")
    
    if len(sys.argv) < 2:
        print("📖 Uso:")
        print(f"   python {sys.argv[0]} <username>")
        print(f"   python {sys.argv[0]} listar")
        print("\nEjemplos:")
        print(f"   python {sys.argv[0]} jveyes")
        print(f"   python {sys.argv[0]} listar")
        print()
        listar_usuarios()
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == "listar":
        listar_usuarios()
    else:
        username = sys.argv[1]
        success = dar_permisos_admin(username)
        sys.exit(0 if success else 1)
