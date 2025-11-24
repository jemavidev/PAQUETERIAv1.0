#!/usr/bin/env python3
"""
Script de prueba para verificar el envío de email de reset de contraseña
"""
import sys
import os
import asyncio

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from app.database import SessionLocal
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.auth import create_reset_token

async def test_password_reset_email():
    """Prueba el envío de email de reset de contraseña"""
    print("🧪 Probando envío de email de reset de contraseña...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Buscar un usuario de prueba (el primero que encuentre)
        user = db.query(User).filter(User.email.isnot(None)).first()
        
        if not user:
            print("❌ No se encontró ningún usuario con email en la base de datos")
            return False
        
        print(f"✅ Usuario encontrado: {user.username} ({user.email})")
        print(f"   Nombre: {user.full_name}")
        print()
        
        # Generar token de reset
        reset_token = create_reset_token(str(user.id))
        print(f"✅ Token de reset generado")
        print()
        
        # Crear servicio de notificaciones
        notification_service = NotificationService()
        
        # Intentar enviar email
        print("📧 Enviando email de reset...")
        result = await notification_service.send_password_reset_email(db, user, reset_token)
        
        if result:
            print("✅ Email enviado exitosamente!")
            print()
            print("Verifica:")
            print(f"1. La bandeja de entrada de: {user.email}")
            print(f"2. La carpeta de spam")
            print(f"3. Los logs del servidor SMTP")
            return True
        else:
            print("❌ Error al enviar email")
            print()
            print("Posibles causas:")
            print("1. Configuración SMTP incorrecta")
            print("2. Credenciales inválidas")
            print("3. Servidor SMTP no accesible")
            print("4. Template de email con errores")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    result = asyncio.run(test_password_reset_email())
    sys.exit(0 if result else 1)
