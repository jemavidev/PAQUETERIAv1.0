#!/usr/bin/env python3
"""
Verificar usuarios en la base de datos
"""
import sys
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

print('=' * 80)
print('USUARIOS EN LA BASE DE DATOS')
print('=' * 80)

users = db.query(User).all()

if not users:
    print('\n❌ No hay usuarios en la base de datos')
    print('\n💡 Necesitas crear un usuario para poder iniciar sesión')
else:
    print(f'\n✅ Total de usuarios: {len(users)}\n')
    for user in users:
        print(f'📧 Email: {user.email}')
        print(f'   Nombre: {user.full_name or "N/A"}')
        print(f'   Activo: {"✅" if user.is_active else "❌"}')
        print()

db.close()
