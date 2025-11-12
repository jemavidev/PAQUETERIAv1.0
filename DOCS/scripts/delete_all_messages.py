#!/usr/bin/env python3
"""
PAQUETERÍA v4.0 - Script para eliminar todos los mensajes de la base de datos
"""

import psycopg2
import sys
import os
from datetime import datetime

def delete_all_messages():
    """Eliminar todos los mensajes de la base de datos"""

    # Credenciales de conexión (usando las mismas que el script de creación de BD)
    db_config = {
        'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
        'port': 5432,
        'user': 'jveyes',
        'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$',
        'database': 'paqueteria_v4'
    }

    try:
        print("🔄 Conectando a la base de datos...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        print("✅ Conexión exitosa")

        # Contar mensajes antes de eliminar
        cursor.execute("SELECT COUNT(*) FROM messages")
        messages_before = cursor.fetchone()[0]
        print(f"📊 Mensajes antes de eliminar: {messages_before}")

        if messages_before == 0:
            print("ℹ️  No hay mensajes para eliminar")
            cursor.close()
            conn.close()
            return True

        # Mostrar tipos de mensajes
        cursor.execute("SELECT message_type, COUNT(*) FROM messages GROUP BY message_type")
        message_types = cursor.fetchall()
        print("📋 Tipos de mensajes encontrados:")
        for msg_type, count in message_types:
            print(f"   - {msg_type}: {count}")

        # Confirmar eliminación (automática para evitar interacción)
        print(f"\n⚠️  ATENCIÓN: Se eliminarán {messages_before} mensajes")
        print("🔄 Procediendo con la eliminación automática...")

        # Eliminar todos los mensajes
        print("🗑️  Eliminando mensajes...")
        cursor.execute("DELETE FROM messages")
        deleted_count = cursor.rowcount

        # Commit de la transacción
        conn.commit()

        print(f"✅ Eliminados {deleted_count} mensajes exitosamente")

        # Verificar que se eliminaron
        cursor.execute("SELECT COUNT(*) FROM messages")
        remaining = cursor.fetchone()[0]
        print(f"📊 Mensajes restantes: {remaining}")

        if remaining == 0:
            print("🎉 Todos los mensajes han sido eliminados correctamente")
        else:
            print(f"⚠️  Quedaron {remaining} mensajes sin eliminar")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

        print("🔄 Conectando a la base de datos...")

        # Obtener estadísticas antes de eliminar
        stats_before = get_db_stats()
        messages_before = stats_before.get("messages", 0)

        print(f"📊 Mensajes antes de eliminar: {messages_before}")

        # Crear sesión de base de datos
        db = SessionLocal()

        try:
            # Contar mensajes por tipo antes de eliminar
            from models.message import MessageType
            message_types = db.query(Message.message_type, Message.message_type).distinct().all()
            print("📋 Tipos de mensajes encontrados:")
            for msg_type in message_types:
                count = db.query(Message).filter(Message.message_type == msg_type[0]).count()
                print(f"   - {msg_type[0].value if hasattr(msg_type[0], 'value') else str(msg_type[0])}: {count}")

            # Confirmar eliminación
            print(f"\n⚠️  ATENCIÓN: Se eliminarán {messages_before} mensajes")
            if messages_before == 0:
                print("ℹ️  No hay mensajes para eliminar")
                return True

            response = input("¿Está seguro de que desea eliminar TODOS los mensajes? (y/N): ")
            if response.lower() != 'y':
                print("ℹ️  Operación cancelada")
                return True

            # Eliminar todos los mensajes
            print("🗑️  Eliminando mensajes...")
            deleted_count = db.query(Message).delete()

            # Commit de la transacción
            db.commit()

            print(f"✅ Eliminados {deleted_count} mensajes exitosamente")

            # Verificar que se eliminaron
            remaining = db.query(Message).count()
            print(f"📊 Mensajes restantes: {remaining}")

            if remaining == 0:
                print("🎉 Todos los mensajes han sido eliminados correctamente")
            else:
                print(f"⚠️  Quedaron {remaining} mensajes sin eliminar")

            return True

        except Exception as e:
            db.rollback()
            print(f"❌ Error durante la eliminación: {e}")
            return False

        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PAQUETERÍA v4.0 - ELIMINACIÓN DE MENSAJES")
    print("="*50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    success = delete_all_messages()

    if success:
        print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        sys.exit(0)
    else:
        print("\n❌ ERROR EN LA ELIMINACIÓN")
        sys.exit(1)

if __name__ == "__main__":
    main()