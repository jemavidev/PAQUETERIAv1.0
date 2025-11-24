#!/usr/bin/env python3
"""
Script para crear usuario jveyes@gmail.com y enviar email de reset
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.notification_service import NotificationService
from app.utils.auth import create_reset_token, get_password_hash

async def create_and_send():
    """Crea usuario jveyes@gmail.com y envía email de reset"""
    print("👤 Creando/Actualizando usuario jveyes@gmail.com...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Buscar si el usuario ya existe
        user = db.query(User).filter(User.email == "jveyes@gmail.com").first()
        
        if user:
            print(f"✅ Usuario ya existe: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Nombre: {user.full_name}")
        else:
            # Crear nuevo usuario
            print("📝 Creando nuevo usuario...")
            user = User(
                username="jveyes",
                email="jveyes@gmail.com",
                full_name="Jesus Villalobos",
                phone="3000000000",
                role=UserRole.ADMIN,
                is_active=True,
                password_hash=get_password_hash("temporal123")  # Contraseña temporal
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Usuario creado: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Contraseña temporal: temporal123")
        
        print()
        
        # Generar token de reset
        reset_token = create_reset_token(str(user.id))
        print(f"✅ Token de reset generado")
        print()
        
        # Enviar email
        notification_service = NotificationService()
        print("📧 Enviando email de reset de contraseña...")
        print(f"   Destinatario: {user.email}")
        print()
        
        result = await notification_service.send_password_reset_email(db, user, reset_token)
        
        if result:
            print("=" * 60)
            print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
            print("=" * 60)
            print()
            print(f"📬 Verifica la bandeja de entrada de: {user.email}")
            print(f"📂 También revisa la carpeta de spam/correo no deseado")
            print()
            print("El email contiene:")
            print("  • Un enlace para restablecer la contraseña")
            print("  • El enlace expira en 1 hora")
            print("  • Solo puede usarse una vez")
            print()
            return True
        else:
            print("=" * 60)
            print("❌ ERROR AL ENVIAR EMAIL")
            print("=" * 60)
            return False
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    result = asyncio.run(create_and_send())
    sys.exit(0 if result else 1)
