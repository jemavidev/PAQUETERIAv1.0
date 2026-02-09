#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar usuarios específicos de la base de datos
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('CODE/.env')

# Agregar el directorio CODE/src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar después de agregar al path
from app.models.user import User

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

def delete_users():
    """Eliminar usuarios específicos"""
    
    # Crear conexión a la base de datos
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Emails de los usuarios a eliminar
        emails_to_delete = [
            "test@cache.com",
            "santiaristi2015@gmail.com"
        ]
        
        print("🔍 Buscando usuarios para eliminar...")
        print("-" * 60)
        
        deleted_count = 0
        
        for email in emails_to_delete:
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                print(f"\n✅ Usuario encontrado:")
                print(f"   📧 Email: {user.email}")
                print(f"   👤 Nombre: {user.full_name}")
                print(f"   🔑 Username: {user.username}")
                print(f"   🎭 Rol: {user.role.value}")
                print(f"   ⚡ Activo: {'✅' if user.is_active else '❌'}")
                
                # Eliminar el usuario
                db.delete(user)
                deleted_count += 1
                print(f"   🗑️  Usuario eliminado")
            else:
                print(f"\n⚠️  Usuario no encontrado: {email}")
        
        # Confirmar cambios
        if deleted_count > 0:
            db.commit()
            print("\n" + "=" * 60)
            print(f"✅ Se eliminaron {deleted_count} usuario(s) exitosamente")
            print("=" * 60)
        else:
            print("\n⚠️  No se encontraron usuarios para eliminar")
            
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error al eliminar usuarios: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  ELIMINACIÓN DE USUARIOS")
    print("=" * 60)
    
    success = delete_users()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)
