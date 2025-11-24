#!/usr/bin/env python3
"""
Script para enviar email de prueba de reset de contraseña a jveyes@gmail.com
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

async def send_test_email():
    """Envía email de reset de contraseña a jveyes@gmail.com"""
    print("📧 Enviando email de prueba de reset de contraseña...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Buscar usuario con email jveyes@gmail.com o crear uno temporal
        user = db.query(User).filter(User.email == "jveyes@gmail.com").first()
        
        if not user:
            # Buscar cualquier usuario y usar ese para la prueba
            user = db.query(User).filter(User.email.isnot(None)).first()
            if user:
                print(f"⚠️  Usuario jveyes@gmail.com no encontrado")
                print(f"   Usando usuario: {user.username} ({user.email})")
                print(f"   Nombre: {user.full_name}")
                print()
                
                # Preguntar si continuar
                response = input("¿Enviar email a este usuario en su lugar? (s/n): ")
                if response.lower() != 's':
                    print("❌ Operación cancelada")
                    return False
            else:
                print("❌ No se encontró ningún usuario con email en la base de datos")
                return False
        else:
            print(f"✅ Usuario encontrado: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Nombre: {user.full_name}")
            print()
        
        # Generar token de reset
        reset_token = create_reset_token(str(user.id))
        print(f"✅ Token de reset generado")
        print()
        
        # Crear servicio de notificaciones
        notification_service = NotificationService()
        
        # Intentar enviar email
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
            print()
            print("Posibles causas:")
            print("1. Error de conexión SMTP")
            print("2. Credenciales incorrectas")
            print("3. Servidor SMTP no accesible")
            print("4. Error en el template de email")
            print()
            print("Revisa los logs del servidor para más detalles")
            return False
            
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR DURANTE EL ENVÍO")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    result = asyncio.run(send_test_email())
    sys.exit(0 if result else 1)
