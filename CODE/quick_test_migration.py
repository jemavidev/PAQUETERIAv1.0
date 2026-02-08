#!/usr/bin/env python3
"""
Script rápido para probar la migración con pocas facturas
"""
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from migrate_reprocess_products import ProductMigration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRUEBA RÁPIDA DE MIGRACIÓN                                ║
║                  (Procesa 3 facturas en modo DRY-RUN)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("🔍 Ejecutando en modo DRY-RUN (sin cambios en DB)")
    print("📊 Procesando 3 facturas de prueba...\n")
    
    # Ejecutar migración en modo dry-run con límite de 3
    migration = ProductMigration(dry_run=True)
    migration.run(limit=3)
    
    print("\n💡 Para ejecutar la migración completa:")
    print("   python3 migrate_reprocess_products.py --dry-run 10  # Prueba con 10 facturas")
    print("   python3 migrate_reprocess_products.py 10            # Migra 10 facturas")
    print("   python3 migrate_reprocess_products.py               # Migra TODAS las facturas")
    print("")

if __name__ == "__main__":
    main()
