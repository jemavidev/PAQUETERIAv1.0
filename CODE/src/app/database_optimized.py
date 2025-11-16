# ========================================
# PAQUETES EL CLUB v1.0 - Configuración de Base de Datos OPTIMIZADA
# ========================================
# Optimizado para: AWS Lightsail con recursos limitados
# Pool de conexiones optimizado para 50 usuarios simultáneos
# ========================================

from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# URL de la base de datos desde configuración
DATABASE_URL = settings.database_url

# ========================================
# CONFIGURACIÓN OPTIMIZADA DEL ENGINE
# ========================================
# Pool size calculado para 50 usuarios simultáneos con 2 workers uvicorn:
# - 2 workers × 10 conexiones = 20 conexiones máximo
# - pool_size: 10 conexiones base por worker
# - max_overflow: 5 conexiones adicionales por worker en picos
# - Total máximo: 20 + 10 = 30 conexiones (cubre 50 usuarios con margen)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Desactivar logging de queries en producción
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
    pool_size=10,  # Conexiones base en el pool (OPTIMIZADO)
    max_overflow=5,  # Conexiones adicionales permitidas (OPTIMIZADO)
    pool_timeout=20,  # Timeout para obtener conexión del pool
    poolclass=QueuePool,  # Usar QueuePool explícitamente
    connect_args={
        "options": "-c timezone=America/Bogota",
        "connect_timeout": 10,  # Timeout de conexión
        "application_name": "paqueteria_v1_app"
    } if "postgresql" in DATABASE_URL else {},
    execution_options={
        "isolation_level": "READ COMMITTED"  # Nivel de aislamiento óptimo
    }
)

# ========================================
# OPTIMIZACIONES A NIVEL DE CONEXIÓN
# ========================================

@event.listens_for(engine, "connect")
def set_postgresql_optimizations(dbapi_connection, connection_record):
    """Optimizaciones a nivel de conexión PostgreSQL"""
    cursor = dbapi_connection.cursor()
    try:
        # Optimizaciones de performance
        cursor.execute("SET work_mem = '16MB'")  # Memoria para operaciones de ordenamiento
        cursor.execute("SET maintenance_work_mem = '64MB'")  # Memoria para VACUUM, CREATE INDEX
        cursor.execute("SET effective_cache_size = '512MB'")  # Estimación de cache disponible
        cursor.execute("SET random_page_cost = 1.1")  # Optimizado para SSD
        cursor.execute("SET effective_io_concurrency = 200")  # Para SSD
        
        # Optimizaciones de query
        cursor.execute("SET enable_seqscan = ON")
        cursor.execute("SET enable_indexscan = ON")
        cursor.execute("SET enable_bitmapscan = ON")
        
        # Timeout para queries lentas (30 segundos)
        cursor.execute("SET statement_timeout = '30000'")
        
        logger.debug("Optimizaciones PostgreSQL aplicadas a la conexión")
    except Exception as e:
        logger.warning(f"No se pudieron aplicar todas las optimizaciones: {e}")
    finally:
        cursor.close()

# ========================================
# SESSION MAKER OPTIMIZADO
# ========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,  # Desactivar autoflush para mejor control
    bind=engine,
    expire_on_commit=False  # Mantener objetos después de commit
)

# Base para modelos SQLAlchemy
Base = declarative_base()


def get_db() -> Session:
    """
    Dependencia para obtener sesión de base de datos
    Optimizada para liberar conexiones rápidamente
    
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
    Inicializar base de datos y verificar conexión
    """
    try:
        # Verificar que la conexión funciona
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        db.close()

        logger.info("✅ Base de datos inicializada correctamente")
        logger.info(f"📊 Motor: PostgreSQL")
        logger.info(f"🗄️  Versión: {version.split(',')[0]}")
        logger.info(f"🔌 Pool size: {engine.pool.size()}")
        logger.info(f"💧 Max overflow: {engine.pool._max_overflow}")
        logger.info(f"⏱️  Pool timeout: {engine.pool._timeout}s")

    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
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
        logger.error(f"❌ Error de conexión a base de datos: {e}")
        return False


def get_db_pool_status() -> dict:
    """
    Obtener estado actual del pool de conexiones
    
    Returns:
        dict: Estadísticas del pool
    """
    try:
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "max_overflow": pool._max_overflow,
            "pool_timeout": pool._timeout
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado del pool: {e}")
        return {"error": str(e)}


def get_db_info() -> dict:
    """
    Obtener información de la base de datos
    
    Returns:
        dict: Información de la configuración de BD
    """
    return {
        "database_url": DATABASE_URL.split('@')[0] + "@***",  # Ocultar credenciales
        "database_type": DATABASE_URL.split("://")[0] if "://" in DATABASE_URL else "unknown",
        "database_name": DATABASE_URL.split("/")[-1] if "/" in DATABASE_URL else "unknown",
        "engine": str(engine.url),
        "pool_status": get_db_pool_status()
    }


# ========================================
# ÍNDICES RECOMENDADOS PARA OPTIMIZACIÓN
# ========================================
"""
IMPORTANTE: Ejecutar estos índices en la base de datos PostgreSQL para mejorar performance:

-- Índices para tabla packages (consultas más frecuentes)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_customer_id ON packages(customer_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_status ON packages(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_created_at ON packages(created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_tracking_number ON packages(tracking_number);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_guide_number ON packages(guide_number);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_status_created ON packages(status, created_at DESC);

-- Índices para tabla customers
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_created_at ON customers(created_at DESC);

-- Índices para tabla messages
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_package_id ON messages(package_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_customer_id ON messages(customer_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- Índices para tabla notifications
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- Índices para tabla users
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Índices para tabla file_uploads
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_file_uploads_package_id ON file_uploads(package_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_file_uploads_created_at ON file_uploads(created_at DESC);

-- Índices compuestos para búsquedas complejas
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_customer_status ON packages(customer_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_package_status ON messages(package_id, status);

-- Análisis y vacío automático optimizado
ALTER TABLE packages SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE customers SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE messages SET (autovacuum_vacuum_scale_factor = 0.1);

-- Actualizar estadísticas
ANALYZE packages;
ANALYZE customers;
ANALYZE messages;
ANALYZE notifications;
ANALYZE users;
"""

