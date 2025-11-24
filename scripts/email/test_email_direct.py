#!/usr/bin/env python3
"""
Script para probar envío directo de email y verificar configuración SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv('CODE/.env')

# Configuración SMTP
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'PAQUETEX')

print("🔧 CONFIGURACIÓN SMTP:")
print(f"   Host: {SMTP_HOST}")
print(f"   Port: {SMTP_PORT}")
print(f"   User: {SMTP_USER}")
print(f"   From: {SMTP_FROM_EMAIL}")
print(f"   Name: {SMTP_FROM_NAME}")
print()

# Email de prueba
recipient = "jveyes@gmail.com"

try:
    print("📧 Conectando al servidor SMTP...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    server.set_debuglevel(1)  # Mostrar debug
    
    print("\n🔐 Iniciando TLS...")
    server.starttls()
    
    print("\n🔑 Autenticando...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    
    print("\n✉️ Creando mensaje...")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🧪 TEST - Email de Preferencias PAQUETEX"
    msg['From'] = formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
    msg['To'] = recipient
    
    # Contenido HTML
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #4F46E5;">🧪 Email de Prueba - PAQUETEX</h2>
        <p>Este es un email de prueba para verificar el sistema de notificaciones.</p>
        <p><strong>Si recibes este email, el sistema está funcionando correctamente.</strong></p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            Enviado desde: PAQUETEX EL CLUB<br>
            Servidor: taylor.mxrouting.net<br>
            Hora: """ + str(os.popen('date').read().strip()) + """
        </p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    print("\n📤 Enviando email...")
    server.send_message(msg)
    
    print("\n✅ EMAIL ENVIADO EXITOSAMENTE")
    print(f"   Destinatario: {recipient}")
    print(f"   Asunto: {msg['Subject']}")
    
    server.quit()
    print("\n🎉 Proceso completado. Revisa tu bandeja de entrada (y spam).")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN: {e}")
    print("   Verifica SMTP_USER y SMTP_PASSWORD en .env")
except smtplib.SMTPException as e:
    print(f"\n❌ ERROR SMTP: {e}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
