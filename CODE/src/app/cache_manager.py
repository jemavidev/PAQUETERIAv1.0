# ========================================
# PAQUETES EL CLUB v1.0 - Gestor de Caché Redis Optimizado
# ========================================
# Sistema de caché inteligente para reducir consultas a BD
# Optimizado para AWS Lightsail con 128MB de RAM para Redis
# ========================================

import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor de caché Redis optimizado para recursos limitados
    """
    
    def __init__(self):
        """Inicializar conexión a Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20  # Límite de conexiones
            )
            # Verificar conexión
            self.redis_client.ping()
            logger.info("✅ Cache Manager inicializado correctamente")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}. Cache desactivado.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verificar si Redis está disponible"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del caché
        
        Args:
            key: Clave del caché
            
        Returns:
            Valor deserializado o None
        """
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Error obteniendo caché {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Guardar valor en caché
        
        Args:
            key: Clave del caché
            value: Valor a guardar (serializable a JSON)
            ttl: Tiempo de vida en segundos (default: 5 minutos)
            
        Returns:
            True si se guardó correctamente
        """
        if not self.is_available():
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Error guardando caché {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Eliminar valor del caché
        
        Args:
            key: Clave del caché
            
        Returns:
            True si se eliminó correctamente
        """
        if not self.is_available():
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Error eliminando caché {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Eliminar todas las claves que coincidan con el patrón
        
        Args:
            pattern: Patrón de búsqueda (ej: "packages:*")
            
        Returns:
            Número de claves eliminadas
        """
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Error eliminando patrón {pattern}: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """
        Limpiar todo el caché (usar con precaución)
        
        Returns:
            True si se limpió correctamente
        """
        if not self.is_available():
            return False
        
        try:
            self.redis_client.flushdb()
            logger.info("🗑️ Caché limpiado completamente")
            return True
        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Obtener estadísticas del caché
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            info = self.redis_client.info("stats")
            memory = self.redis_client.info("memory")
            
            return {
                "status": "available",
                "total_keys": self.redis_client.dbsize(),
                "memory_used": memory.get("used_memory_human", "N/A"),
                "memory_peak": memory.get("used_memory_peak_human", "N/A"),
                "hit_rate": info.get("keyspace_hits", 0),
                "miss_rate": info.get("keyspace_misses", 0),
                "connected_clients": self.redis_client.client_list().__len__()
            }
        except Exception as e:
            logger.warning(f"Error obteniendo estadísticas: {e}")
            return {"status": "error", "message": str(e)}


# Instancia global del gestor de caché
cache_manager = CacheManager()


# ========================================
# DECORADORES DE CACHÉ
# ========================================

def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        ttl: Tiempo de vida en segundos (default: 5 minutos)
        key_prefix: Prefijo para la clave del caché
    
    Example:
        @cached(ttl=600, key_prefix="packages")
        def get_package_by_id(db, package_id):
            return db.query(Package).filter(Package.id == package_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única basada en función y argumentos
            func_name = func.__name__
            args_key = "_".join(str(arg) for arg in args[1:])  # Saltar primer arg (db)
            kwargs_key = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{func_name}:{args_key}:{kwargs_key}".replace(" ", "_")
            
            # Intentar obtener del caché
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"✅ Cache HIT: {cache_key}")
                return cached_result
            
            # Si no está en caché, ejecutar función
            logger.debug(f"❌ Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Guardar en caché si el resultado no es None
            if result is not None:
                # Convertir resultado a diccionario si es un modelo SQLAlchemy
                if hasattr(result, '__dict__'):
                    cache_data = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                else:
                    cache_data = result
                
                cache_manager.set(cache_key, cache_data, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Decorador para invalidar caché después de ejecutar una función
    
    Args:
        key_pattern: Patrón de claves a invalidar
    
    Example:
        @invalidate_cache("packages:*")
        def update_package(db, package_id, data):
            # Actualizar paquete...
            return updated_package
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Invalidar caché después de la operación
            deleted = cache_manager.delete_pattern(key_pattern)
            if deleted > 0:
                logger.debug(f"🗑️ Invalidadas {deleted} claves del patrón: {key_pattern}")
            return result
        return wrapper
    return decorator


# ========================================
# CLAVES DE CACHÉ PREDEFINIDAS
# ========================================

class CacheKeys:
    """Constantes para claves de caché organizadas por módulo"""
    
    # Paquetes
    PACKAGE_BY_ID = "packages:id:{}"
    PACKAGE_BY_TRACKING = "packages:tracking:{}"
    PACKAGE_BY_GUIDE = "packages:guide:{}"
    PACKAGES_BY_STATUS = "packages:status:{}"
    PACKAGES_LIST = "packages:list:page_{}:limit_{}"
    PACKAGES_COUNT = "packages:count"
    
    # Clientes
    CUSTOMER_BY_ID = "customers:id:{}"
    CUSTOMER_BY_PHONE = "customers:phone:{}"
    CUSTOMERS_LIST = "customers:list:page_{}:limit_{}"
    
    # Usuarios
    USER_BY_ID = "users:id:{}"
    USER_BY_EMAIL = "users:email:{}"
    
    # Tarifas
    RATES_ALL = "rates:all"
    RATE_BY_TYPE = "rates:type:{}"
    
    # Notificaciones
    NOTIFICATIONS_USER = "notifications:user_{}:page_{}:limit_{}"
    NOTIFICATIONS_UNREAD = "notifications:user_{}:unread"
    
    # Estadísticas
    STATS_DASHBOARD = "stats:dashboard"
    STATS_PACKAGES = "stats:packages"


# ========================================
# TIEMPOS DE VIDA (TTL) RECOMENDADOS
# ========================================

class CacheTTL:
    """Tiempos de vida recomendados para diferentes tipos de datos"""
    
    VERY_SHORT = 60  # 1 minuto - Datos que cambian muy frecuentemente
    SHORT = 300  # 5 minutos - Datos que cambian frecuentemente
    MEDIUM = 900  # 15 minutos - Datos que cambian ocasionalmente
    LONG = 3600  # 1 hora - Datos que rara vez cambian
    VERY_LONG = 86400  # 24 horas - Datos casi estáticos

