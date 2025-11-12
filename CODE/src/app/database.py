# ========================================
# PAQUETES EL CLUB v1.0 - Configuración de Base de Datos
# ========================================
# Archivo: CODE/LOCAL/src/app/database/database.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Configuración de base de datos para PAQUETES EL CLUB
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from .config import settings

# URL de la base de datos desde configuración
DATABASE_URL = settings.database_url

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,  # Solo mostrar queries en desarrollo
    pool_pre_ping=True,   # Verificar conexión antes de usar
    pool_recycle=300,     # Reciclar conexiones cada 5 minutos
    connect_args={
        "options": "-c timezone=America/Bogota"
    } if "postgresql" in DATABASE_URL else {}
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos SQLAlchemy
Base = declarative_base()


def get_db() -> Session:
    """
    Dependencia para obtener sesión de base de datos

    Yields:
        Session: Sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializar base de datos y crear todas las tablas
    """
    try:
        # Las migraciones de Alembic ya crearon las tablas
        # Solo verificar que la conexión funciona
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

        print("✅ Base de datos inicializada correctamente")
        print(f"📊 Motor: {engine}")
        print(f"🗄️  Base de datos: {DATABASE_URL.split('/')[-1] if '/' in DATABASE_URL else 'unknown'}")

    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        raise


def reset_db():
    """
    Reiniciar base de datos (eliminar y recrear todas las tablas)
    ¡CUIDADO! Esto elimina todos los datos
    """
    try:
        # Importar todos los modelos
        from app.models import user, package, customer, message, notification, file_upload

        # Eliminar todas las tablas
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Tablas eliminadas")

        # Recrear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos reiniciada correctamente")

    except Exception as e:
        print(f"❌ Error al reiniciar base de datos: {e}")
        raise


def check_db_connection() -> bool:
    """
    Verificar conexión a la base de datos

    Returns:
        bool: True si la conexión es exitosa
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False


def get_db_info() -> dict:
    """
    Obtener información de la base de datos

    Returns:
        dict: Información de la configuración de BD
    """
    return {
        "database_url": DATABASE_URL,
        "database_type": DATABASE_URL.split("://")[0] if "://" in DATABASE_URL else "unknown",
        "database_name": DATABASE_URL.split("/")[-1] if "/" in DATABASE_URL else "unknown",
        "engine": str(engine),
        "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else "unknown",
        "checked_connections": engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else "unknown",
        "invalid_connections": engine.pool.invalid() if hasattr(engine.pool, 'invalid') else "unknown",
    }


# Función para ejecutar queries directos (para debugging)
def execute_query(query: str, params: dict = None):
    """
    Ejecutar query SQL directo

    Args:
        query: Query SQL
        params: Parámetros del query

    Returns:
        Resultado del query
    """
    try:
        db = SessionLocal()
        result = db.execute(query, params or {})
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# Función para obtener estadísticas de la base de datos
def get_db_stats() -> dict:
    """
    Obtener estadísticas de la base de datos

    Returns:
        dict: Estadísticas de la BD
    """
    try:
        db = SessionLocal()

        # Contar registros en tablas principales
        stats = {}

        try:
            from app.models.user import User
            stats["users"] = db.query(User).count()
        except:
            stats["users"] = "N/A"

        try:
            from app.models.package import Package
            stats["packages"] = db.query(Package).count()
        except:
            stats["packages"] = "N/A"

        try:
            from app.models.customer import Customer
            stats["customers"] = db.query(Customer).count()
        except:
            stats["customers"] = "N/A"

        try:
            from app.models.message import Message
            stats["messages"] = db.query(Message).count()
        except:
            stats["messages"] = "N/A"

        return stats

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()