#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para crear un mensaje de prueba
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT', 5432),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor()

# Obtener un paquete existente
cursor.execute("SELECT id, tracking_number FROM packages ORDER BY id DESC LIMIT 1")
package = cursor.fetchone()
package_id = package[0]
tracking_number = package[1]

print(f"📦 Usando paquete: ID={package_id}, Tracking={tracking_number}")

# Crear mensaje
cursor.execute("""
    INSERT INTO messages (
        subject,
        content,
        message_type,
        priority,
        status,
        is_read,
        package_id,
        sender_name,
        sender_email,
        sender_phone,
        tracking_code,
        created_at,
        updated_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id
""", (
    f'PAQUETE {tracking_number}',
    f'Hola, quisiera saber el estado de mi paquete {tracking_number}. ¿Cuándo llegará? Necesito información urgente.',
    'CONSULTA',
    'MEDIA',
    'ABIERTO',
    False,
    package_id,
    'María González',
    'maria.gonzalez@example.com',
    '3109876543',
    tracking_number,
    datetime.now(),
    datetime.now()
))

message_id = cursor.fetchone()[0]
conn.commit()

print(f"✅ Mensaje creado con ID: {message_id}")
print(f"🌐 Ver en: https://staging.jemavi.co/messages")

cursor.close()
conn.close()
