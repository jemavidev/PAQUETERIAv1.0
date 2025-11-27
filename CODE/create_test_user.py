#!/usr/bin/env python3
"""
Script para crear un usuario de prueba
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, '/app/src')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash
from app.utils.datetime_utils import get_colombia_now
import uuid

def create_test_user():
    """Crear usuario de prueba para tests"""
    db = SessionLocal()
    
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.username == "testuser").first()
        
        if existing_user:
            print(f"✓ Usuario 'testuser' ya existe (ID: {existing_user.id})")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role.value if existing_user.role else 'N/A'}")
            print(f"  Active: {existing_user.is_active}")
            return existing_user
        
        # Crear nuevo usuario
        password_hash = get_password_hash("test123")
        
        new_user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="testuser@test.com",
            password_hash=password_hash,
            full_name="Test User",
            phone="+573001234567",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=get_colombia_now(),
            updated_at=get_colombia_now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✓ Usuario 'testuser' creado exitosamente")
        print(f"  ID: {new_user.id}")
        print(f"  Username: {new_user.username}")
        print(f"  Email: {new_user.email}")
        print(f"  Password: test123")
        print(f"  Role: {new_user.role.value}")
        
        return new_user
        
    except Exception as e:
        print(f"✗ Error creando usuario: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("========================================")
    print("Creando usuario de prueba")
    print("========================================")
    print("")
    
    user = create_test_user()
    
    if user:
        print("")
        print("========================================")
        print("Credenciales para tests:")
        print("========================================")
        print("Username: testuser")
        print("Password: test123")
        print("========================================")
