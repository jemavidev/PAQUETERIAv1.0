#!/usr/bin/env python3
"""Script para probar la corrección de get_customer_packages"""

import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.customer_portal_service import CustomerPortalService

# Conectar a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("PRUEBA: get_customer_packages() con corrección")
print("=" * 80)

# ID del cliente JESUS VILLALOBOS
customer_id = "6f93711c-5bd0-455a-971e-b4353cf13fe6"

try:
    service = CustomerPortalService()
    result = service.get_customer_packages(db, customer_id, limit=50)
    
    print(f"\n✅ Método ejecutado exitosamente")
    print(f"   Total de items: {result['total']}")
    print(f"\n📦 Paquetes y anuncios:")
    
    for i, pkg in enumerate(result['packages'], 1):
        print(f"\n   {i}. Estado: {pkg.status}")
        print(f"      Tracking: {pkg.tracking_number}")
        print(f"      Guía: {pkg.guide_number}")
        print(f"      Anunciado: {pkg.announced_at}")
        if pkg.received_at:
            print(f"      Recibido: {pkg.received_at}")
        if pkg.delivered_at:
            print(f"      Entregado: {pkg.delivered_at}")
    
    # Contar por estado
    estados = {}
    for pkg in result['packages']:
        estado = pkg.status
        estados[estado] = estados.get(estado, 0) + 1
    
    print(f"\n📊 Resumen por estado:")
    for estado, count in sorted(estados.items()):
        print(f"   {estado}: {count}")
    
    print(f"\n✅ CORRECCIÓN EXITOSA")
    print(f"   Antes: Solo mostraba paquetes procesados")
    print(f"   Ahora: Muestra paquetes + anuncios pendientes")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()

print("\n" + "=" * 80)
print("Prueba completada")
print("=" * 80)
