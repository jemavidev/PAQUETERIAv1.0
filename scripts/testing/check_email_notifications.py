import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('CODE/.env')

# Obtener DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL no encontrada en .env")
    sys.exit(1)

# Crear engine
engine = create_engine(database_url)

# Consultar últimas notificaciones de email
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            id, 
            notification_type, 
            event_type, 
            recipient, 
            subject,
            status, 
            error_message,
            created_at,
            sent_at
        FROM notifications 
        WHERE notification_type = 'EMAIL' 
        ORDER BY created_at DESC 
        LIMIT 5
    """))
    
    print("\n📧 ÚLTIMAS 5 NOTIFICACIONES DE EMAIL:")
    print("=" * 120)
    
    for row in result:
        print(f"\nID: {row[0]}")
        print(f"Tipo: {row[1]} | Evento: {row[2]}")
        print(f"Destinatario: {row[3]}")
        print(f"Asunto: {row[4]}")
        print(f"Estado: {row[5]}")
        print(f"Error: {row[6] if row[6] else 'N/A'}")
        print(f"Creado: {row[7]}")
        print(f"Enviado: {row[8] if row[8] else 'Pendiente'}")
        print("-" * 120)
