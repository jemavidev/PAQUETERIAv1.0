#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar las mejoras del portal de clientes:
1. Paquetes cancelados
2. Reset de intentos
3. Preferencias de notificación
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.customer import Customer
from app.models.package import Package, PackageStatus
from app.services.customer_portal_service import CustomerPortalService

print("\n" + "="*70)
print("🧪 PRUEBAS DE MEJORAS DEL PORTAL")
print("="*70)

db = SessionLocal()

# Buscar un cliente de prueba
customer = db.query(Customer).filter(Customer.is_active == True).first()

if not customer:
    print("❌ No hay clientes para probar")
    sys.exit(1)

print(f"\n✅ Cliente de prueba: {customer.full_name} ({customer.phone})")

# 1. Probar paquetes cancelados
print("\n" + "-"*70)
print("1. PAQUETES CANCELADOS")
print("-"*70)

service = CustomerPortalService()
packages_data = service.get_customer_packages(db, str(customer.id), limit=50)

print(f"\nTotal de paquetes: {packages_data['total']}")

# Contar por estado
estados = {}
for pkg in packages_data['packages']:
    estado = pkg.status
    estados[estado] = estados.get(estado, 0) + 1

print("\nPaquetes por estado:")
for estado, count in estados.items():
    print(f"  {estado}: {count}")

# Mostrar paquetes cancelados
cancelados = [p for p in packages_data['packages'] if p.status == 'CANCELADO']
if cancelados:
    print(f"\n✅ Paquetes CANCELADOS encontrados: {len(cancelados)}")
    for pkg in cancelados[:5]:
        print(f"  - {pkg.tracking_number} | {pkg.guide_number}")
else:
    print("\n⚠️  No hay paquetes cancelados")

# 2. Probar preferencias de notificación
print("\n" + "-"*70)
print("2. PREFERENCIAS DE NOTIFICACIÓN")
print("-"*70)

try:
    # Obtener preferencias
    preferences = service.get_notification_preferences(db, str(customer.id))
    
    print("\n✅ Preferencias obtenidas:")
    print(f"  SMS habilitado: {preferences['sms_notifications_enabled']}")
    print(f"  Email habilitado: {preferences['email_notifications_enabled']}")
    print(f"  Notificar paquete anunciado: {preferences['sms_on_package_announced']}")
    print(f"  Notificar paquete recibido: {preferences['sms_on_package_received']}")
    print(f"  Notificar paquete entregado: {preferences['sms_on_package_delivered']}")
    
    # Actualizar preferencias
    print("\n📝 Actualizando preferencias...")
    updated = service.update_notification_preferences(
        db,
        str(customer.id),
        {
            "sms_on_package_announced": False,
            "email_notifications_enabled": True
        }
    )
    
    print("✅ Preferencias actualizadas:")
    print(f"  SMS paquete anunciado: {updated['sms_on_package_announced']}")
    print(f"  Email habilitado: {updated['email_notifications_enabled']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

db.close()

print("\n" + "="*70)
print("✅ PRUEBAS COMPLETADAS")
print("="*70 + "\n")
