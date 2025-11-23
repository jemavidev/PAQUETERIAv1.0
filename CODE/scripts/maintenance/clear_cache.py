#!/usr/bin/env python3
"""Script para limpiar el caché de paquetes"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.cache_manager import cache_manager

def clear_cache():
    try:
        # Limpiar caché de paquetes
        deleted = cache_manager.clear_pattern("paqueteria:cache:packages:*")
        print(f"✅ Caché limpiado: {deleted} claves eliminadas")
        
        # También limpiar caché general
        deleted_general = cache_manager.clear_pattern("paqueteria:cache:*")
        print(f"✅ Caché general limpiado: {deleted_general} claves eliminadas")
        
    except Exception as e:
        print(f"❌ Error limpiando caché: {e}")

if __name__ == "__main__":
    clear_cache()
