# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Cache Manager Optimizado
Versión: 2.0.0
Fecha: 2025-11-17
Autor: Equipo de Desarrollo
"""

import redis
import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestor de caché optimizado para mejorar el rendimiento de la aplicación
    """
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Cache Manager conectado a Redis")
        except Exception as e:
            logger.error(f"❌ Error conectando a Redis: {e}")
            self.redis_client = None
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generar clave de caché consistente"""
        return f"paqueteria:cache:{prefix}:{identifier}"
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Guardar valor en caché
        
        Args:
            key: Clave del caché
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        if not self.redis_client:
            return False
            
        try:
            serialized_value = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
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
                return pickle.loads(value)
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
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error limpiando patrón {pattern}: {e}")
            return 0
    
    # ========================================
    # MÉTODOS ESPECÍFICOS PARA PAQUETES
    # ========================================
    
    def cache_packages_list(self, packages: List[Dict], filters: Dict, ttl: int = 60) -> bool:
        """Cachear lista de paquetes con filtros específicos"""
        filter_key = json.dumps(filters, sort_keys=True)
        cache_key = self._get_key("packages_list", filter_key)
        return self.set(cache_key, packages, ttl)
    
    def get_cached_packages_list(self, filters: Dict) -> Optional[List[Dict]]:
        """Obtener lista de paquetes cacheada"""
        filter_key = json.dumps(filters, sort_keys=True)
        cache_key = self._get_key("packages_list", filter_key)
        return self.get(cache_key)
    
    def cache_package_stats(self, stats: Dict, ttl: int = 300) -> bool:
        """Cachear estadísticas de paquetes"""
        cache_key = self._get_key("stats", "packages")
        return self.set(cache_key, stats, ttl)
    
    def get_cached_package_stats(self) -> Optional[Dict]:
        """Obtener estadísticas de paquetes cacheadas"""
        cache_key = self._get_key("stats", "packages")
        return self.get(cache_key)
    
    def cache_customer_packages(self, customer_id: str, packages: List[Dict], ttl: int = 120) -> bool:
        """Cachear paquetes de un cliente específico"""
        cache_key = self._get_key("customer_packages", customer_id)
        return self.set(cache_key, packages, ttl)
    
    def get_cached_customer_packages(self, customer_id: str) -> Optional[List[Dict]]:
        """Obtener paquetes de cliente cacheados"""
        cache_key = self._get_key("customer_packages", customer_id)
        return self.get(cache_key)
    
    def invalidate_package_cache(self, package_id: Optional[str] = None, customer_id: Optional[str] = None):
        """Invalidar caché relacionado con paquetes"""
        patterns_to_clear = [
            "paqueteria:cache:packages_list:*",
            "paqueteria:cache:stats:*"
        ]
        
        if customer_id:
            patterns_to_clear.append(f"paqueteria:cache:customer_packages:{customer_id}")
        
        for pattern in patterns_to_clear:
            cleared = self.clear_pattern(pattern)
            if cleared > 0:
                logger.info(f"Invalidado caché: {pattern} ({cleared} claves)")
    
    # ========================================
    # MÉTODOS PARA CONFIGURACIÓN
    # ========================================
    
    def cache_app_config(self, config: Dict, ttl: int = 3600) -> bool:
        """Cachear configuración de la aplicación"""
        cache_key = self._get_key("config", "app")
        return self.set(cache_key, config, ttl)
    
    def get_cached_app_config(self) -> Optional[Dict]:
        """Obtener configuración de la aplicación cacheada"""
        cache_key = self._get_key("config", "app")
        return self.get(cache_key)
    
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