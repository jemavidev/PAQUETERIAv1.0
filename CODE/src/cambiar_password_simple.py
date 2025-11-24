#!/usr/bin/env python3
"""
Script simple para cambiar la contraseña del usuario jveyes
"""
import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configurar el contexto de password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashear una contraseña"""
    return pwd_context.hash(password)

def cambiar_password():
    """Cambiar la contraseña del usuario jveyes"""
    
    # Leer la URL de la base de datos del archivo .env
    # Buscar en CODE/.env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    database_url = None
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    
    # Si no se encuentra en .env, usar la base de datos por defecto
    if not database_url:
        database_url = "sqlite:///./paquetex.db"
        print(f"⚠️  Usando base de datos por defecto: {database_url}")
    else:
        # Ocultar la contraseña en el log
        safe_url = database_url.split('@')[1] if '@' in database_url else database_url
        print(f"✓ Conectando a base de datos: ...@{safe_url}")
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        # Nueva contraseña
        nueva_password = "il1111"
        hashed_password = get_password_hash(nueva_password)
        
        # Actualizar la contraseña
        with engine.connect() as conn:
            # Verificar si el usuario existe
            result = conn.execute(
                text("SELECT id, username, email FROM users WHERE username = :username"),
                {"username": "jveyes"}
            )
            user = result.fetchone()
            
            if not user:
                print("❌ Usuario 'jveyes' no encontrado")
                return False
            
            print(f"✓ Usuario encontrado:")
            print(f"   ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   Email: {user[2]}")
            
            # Actualizar la contraseña
            conn.execute(
                text("UPDATE users SET password_hash = :password WHERE username = :username"),
                {"password": hashed_password, "username": "jveyes"}
            )
            conn.commit()
            
            print("\n✅ Contraseña actualizada exitosamente")
            print(f"   Nueva contraseña: {nueva_password}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error al cambiar la contraseña: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Cambiando contraseña del usuario 'jveyes'")
    print("=" * 60)
    print()
    cambiar_password()
