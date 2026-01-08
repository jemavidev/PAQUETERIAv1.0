# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Cache Manager Optimizado
Versión: 3.0.0 - Optimizado para rendimiento CRUD
Fecha: 2026-01-08
Autor: Equipo de Desarrollo
"""

import redis
import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# ========================================
# CONFIGURACIÓN DE TTL OPTIMIZADA
# ========================================
# TTLs ajustados para balance entre frescura y rendimiento
CACHE_TTL = {
    "packages_list": 60,        # 1 minuto (antes 15s) - Lista de paquetes
    "package_detail": 300,      # 5 minutos - Detalle de paquete individual
    "package_stats": 300,       # 5 minutos - Estadísticas de paquetes
    "customer_packages": 120,   # 2 minutos - Paquetes de un cliente
    "customer_search": 120,     # 2 minutos - Búsqueda de clientes
    "customer_stats": 300,      # 5 minutos - Estadísticas de clientes
    "dashboard": 60,            # 1 minuto - Dashboard admin
    "app_config": 3600,         # 1 hora - Configuración de la app
    "default": 120,             # 2 minutos - Por defecto
}


class CacheManager:
    """
    Gestor de caché optimizado para mejorar el rendimiento de la aplicación
    Versión 3.0 con TTLs optimizados y mejor gestión de invalidación
    """
    
    def __init__(self):
        self._connection_failed = False
        try:
            self.redis_client = redis.from_url(
                settings.redis_url, 
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Cache Manager conectado a Redis")
        except Exception as e:
            logger.error(f"❌ Error conectando a Redis: {e}")
            self.redis_client = None
            self._connection_failed = True
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generar clave de caché consistente"""
        return f"paqueteria:cache:{prefix}:{identifier}"
    
    def _get_hash_key(self, data: Dict) -> str:
        """Generar hash único para filtros de búsqueda"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()[:16]
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Guardar valor en caché
        
        Args:
            key: Clave del caché
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (usa default si no se especifica)
        """
        if not self.redis_client:
            return False
        
        if ttl is None:
            ttl = CACHE_TTL["default"]
            
        try:
            serialized_value = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error guardando en caché {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        if not self.redis_client:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return pickle.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo del caché {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Eliminar clave del caché"""
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando del caché {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Eliminar todas las claves que coincidan con un patrón"""
        if not self.redis_client:
            return 0
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.debug(f"Cache CLEAR pattern {pattern}: {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error limpiando patrón {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verificar si una clave existe en caché"""
        if not self.redis_client:
            return False
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error verificando existencia de {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Obtener TTL restante de una clave"""
        if not self.redis_client:
            return -1
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error obteniendo TTL de {key}: {e}")
            return -1
    
    # ========================================
    # MÉTODOS ESPECÍFICOS PARA PAQUETES
    # ========================================
    
    def cache_packages_list(self, packages: List[Dict], filters: Dict, ttl: int = None) -> bool:
        """Cachear lista de paquetes con filtros específicos"""
        if ttl is None:
            ttl = CACHE_TTL["packages_list"]
        filter_hash = self._get_hash_key(filters)
        cache_key = self._get_key("packages_list", filter_hash)
        return self.set(cache_key, packages, ttl)
    
    def get_cached_packages_list(self, filters: Dict) -> Optional[List[Dict]]:
        """Obtener lista de paquetes cacheada"""
        filter_hash = self._get_hash_key(filters)
        cache_key = self._get_key("packages_list", filter_hash)
        return self.get(cache_key)
    
    def cache_package_detail(self, package_id: str, package_data: Dict, ttl: int = None) -> bool:
        """Cachear detalle de un paquete específico"""
        if ttl is None:
            ttl = CACHE_TTL["package_detail"]
        cache_key = self._get_key("package_detail", str(package_id))
        return self.set(cache_key, package_data, ttl)
    
    def get_cached_package_detail(self, package_id: str) -> Optional[Dict]:
        """Obtener detalle de paquete cacheado"""
        cache_key = self._get_key("package_detail", str(package_id))
        return self.get(cache_key)
    
    def cache_package_stats(self, stats: Dict, ttl: int = None) -> bool:
        """Cachear estadísticas de paquetes"""
        if ttl is None:
            ttl = CACHE_TTL["package_stats"]
        cache_key = self._get_key("stats", "packages")
        return self.set(cache_key, stats, ttl)
    
    def get_cached_package_stats(self) -> Optional[Dict]:
        """Obtener estadísticas de paquetes cacheadas"""
        cache_key = self._get_key("stats", "packages")
        return self.get(cache_key)
    
    def cache_customer_packages(self, customer_id: str, packages: List[Dict], ttl: int = None) -> bool:
        """Cachear paquetes de un cliente específico"""
        if ttl is None:
            ttl = CACHE_TTL["customer_packages"]
        cache_key = self._get_key("customer_packages", customer_id)
        return self.set(cache_key, packages, ttl)
    
    def get_cached_customer_packages(self, customer_id: str) -> Optional[List[Dict]]:
        """Obtener paquetes de cliente cacheados"""
        cache_key = self._get_key("customer_packages", customer_id)
        return self.get(cache_key)
    
    def invalidate_package_cache(self, package_id: Optional[str] = None, customer_id: Optional[str] = None):
        """Invalidar caché relacionado con paquetes de forma inteligente"""
        patterns_to_clear = [
            "paqueteria:cache:packages_list:*",
            "paqueteria:cache:stats:*"
        ]
        
        if package_id:
            patterns_to_clear.append(f"paqueteria:cache:package_detail:{package_id}")
        
        if customer_id:
            patterns_to_clear.append(f"paqueteria:cache:customer_packages:{customer_id}")
        
        total_cleared = 0
        for pattern in patterns_to_clear:
            cleared = self.clear_pattern(pattern)
            total_cleared += cleared
        
        if total_cleared > 0:
            logger.info(f"🗑️ Cache invalidado: {total_cleared} claves (package_id={package_id}, customer_id={customer_id})")
    
    def invalidate_all_packages_cache(self):
        """Invalidar todo el caché de paquetes (usar con precaución)"""
        patterns = [
            "paqueteria:cache:packages_list:*",
            "paqueteria:cache:package_detail:*",
            "paqueteria:cache:customer_packages:*",
            "paqueteria:cache:stats:*"
        ]
        total = 0
        for pattern in patterns:
            total += self.clear_pattern(pattern)
        logger.info(f"🗑️ Cache de paquetes completamente invalidado: {total} claves")
    
    # ========================================
    # MÉTODOS PARA CONFIGURACIÓN
    # ========================================
    
    def cache_app_config(self, config: Dict, ttl: int = None) -> bool:
        """Cachear configuración de la aplicación"""
        if ttl is None:
            ttl = CACHE_TTL["app_config"]
        cache_key = self._get_key("config", "app")
        return self.set(cache_key, config, ttl)
    
    def get_cached_app_config(self) -> Optional[Dict]:
        """Obtener configuración de la aplicación cacheada"""
        cache_key = self._get_key("config", "app")
        return self.get(cache_key)
    
    # ========================================
    # MÉTODOS PARA DASHBOARD
    # ========================================
    
    def cache_dashboard(self, dashboard_data: Dict, period_days: int, ttl: int = None) -> bool:
        """Cachear datos del dashboard"""
        if ttl is None:
            ttl = CACHE_TTL["dashboard"]
        cache_key = self._get_key("dashboard", f"period_{period_days}")
        return self.set(cache_key, dashboard_data, ttl)
    
    def get_cached_dashboard(self, period_days: int) -> Optional[Dict]:
        """Obtener datos del dashboard cacheados"""
        cache_key = self._get_key("dashboard", f"period_{period_days}")
        return self.get(cache_key)
    
    def invalidate_dashboard_cache(self):
        """Invalidar caché del dashboard"""
        self.clear_pattern("paqueteria:cache:dashboard:*")
    
    # ========================================
    # MÉTODOS DE MONITOREO
    # ========================================
    
    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del caché"""
        if not self.redis_client:
            return {"error": "Redis no disponible"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "total_keys": self._count_app_keys()
            }
        except Exception as e:
            return {"error": f"Error obteniendo estadísticas: {e}"}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calcular tasa de aciertos del caché"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def _count_app_keys(self) -> int:
        """Contar claves de la aplicación"""
        try:
            keys = self.redis_client.keys("paqueteria:cache:*")
            return len(keys)
        except:
            return 0

# Instancia global del cache manager
cache_manager = CacheManager()