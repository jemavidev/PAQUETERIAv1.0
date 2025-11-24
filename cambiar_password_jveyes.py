#!/usr/bin/env python3
"""
Script para cambiar la contraseña del usuario jveyes
"""
import sys
import os

# Obtener el directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))
code_src_dir = os.path.join(current_dir, 'CODE', 'src')

# Agregar el directorio CODE/src al path
sys.path.insert(0, code_src_dir)

# Cambiar al directorio CODE/src para que las importaciones funcionen
os.chdir(code_src_dir)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash

def cambiar_password():
    """Cambiar la contraseña del usuario jveyes"""
    db: Session = SessionLocal()
    
    try:
        # Buscar el usuario
        user = db.query(User).filter(User.username == "jveyes").first()
        
        if not user:
            print("❌ Usuario 'jveyes' no encontrado")
            return False
        
        # Nueva contraseña
        nueva_password = "il1111"
        
        # Hashear la nueva contraseña
        hashed_password = get_password_hash(nueva_password)
        
        # Actualizar la contraseña
        user.hashed_password = hashed_password
        db.commit()
        
        print("✅ Contraseña actualizada exitosamente")
        print(f"   Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nueva contraseña: {nueva_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cambiar la contraseña: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Cambiando contraseña del usuario 'jveyes'")
    print("=" * 50)
    cambiar_password()
