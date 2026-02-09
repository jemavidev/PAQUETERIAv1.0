#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar usuarios específicos usando SQL directo
"""

import sys
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Cargar variables de entorno
load_dotenv('CODE/.env')

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

def delete_users():
    """Eliminar usuarios específicos usando SQL directo"""
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Emails de los usuarios a eliminar
        emails_to_delete = [
            "test@cache.com",
            "santiaristi2015@gmail.com"
        ]
        
        print("🔍 Buscando usuarios para eliminar...")
        print("-" * 60)
        
        deleted_count = 0
        
        for email in emails_to_delete:
            # Buscar el usuario
            cursor.execute(
                "SELECT id, email, full_name, username, role, is_active FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            
            if user:
                print(f"\n✅ Usuario encontrado:")
                print(f"   📧 Email: {user['email']}")
                print(f"   👤 Nombre: {user['full_name']}")
                print(f"   🔑 Username: {user['username']}")
                print(f"   🎭 Rol: {user['role']}")
                print(f"   ⚡ Activo: {'✅' if user['is_active'] else '❌'}")
                
                # Eliminar el usuario
                cursor.execute("DELETE FROM users WHERE id = %s", (user['id'],))
                deleted_count += 1
                print(f"   🗑️  Usuario eliminado")
            else:
                print(f"\n⚠️  Usuario no encontrado: {email}")
        
        # Confirmar cambios
        if deleted_count > 0:
            conn.commit()
            print("\n" + "=" * 60)
            print(f"✅ Se eliminaron {deleted_count} usuario(s) exitosamente")
            print("=" * 60)
        else:
            print("\n⚠️  No se encontraron usuarios para eliminar")
        
        cursor.close()
        conn.close()
        return True
            
    except Exception as e:
        print(f"\n❌ Error al eliminar usuarios: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

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
