#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para verificar paquetes de un cliente
"""

import sys
import os

# Agregar el directorio CODE al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app.database import SessionLocal
from src.app.models.customer import Customer
from src.app.models.package import Package
from sqlalchemy import or_

def debug_customer_packages():
    """Verifica los paquetes asociados a un cliente"""
    db = SessionLocal()
    
    try:
        # Códigos de consulta que mencionaste
        tracking_codes = ['XNCC', 'ySVC5']
        
        print("\n" + "="*60)
        print("🔍 BUSCANDO PAQUETES POR CÓDIGO DE CONSULTA")
        print("="*60)
        
        for code in tracking_codes:
            print(f"\n📦 Buscando paquete con código: {code}")
            pkg = db.query(Package).filter(Package.tracking_number == code).first()
            
            if pkg:
                print(f"   ✅ Paquete encontrado:")
                print(f"      - ID: {pkg.id}")
                print(f"      - Tracking: {pkg.tracking_number}")
                print(f"      - Guía: {pkg.guide_number}")
                print(f"      - Estado: {pkg.status}")
                print(f"      - Customer ID: {pkg.customer_id}")
                
                if pkg.customer_id:
                    customer = db.query(Customer).filter(Customer.id == pkg.customer_id).first()
                    if customer:
                        print(f"      - Cliente: {customer.full_name}")
                        print(f"      - Teléfono: {customer.phone}")
                        print(f"      - Email: {customer.email}")
                    else:
                        print(f"      ⚠️  Cliente no encontrado con ID: {pkg.customer_id}")
                else:
                    print(f"      ⚠️  Paquete sin customer_id asignado")
            else:
                print(f"   ❌ Paquete NO encontrado")
        
        # Buscar si hay un cliente con estos paquetes
        print("\n" + "="*60)
        print("👤 BUSCANDO CLIENTES CON ESTOS PAQUETES")
        print("="*60)
        
        packages = db.query(Package).filter(
            or_(Package.tracking_number == 'XNCC', Package.tracking_number == 'ySVC5')
        ).all()
        
        customer_ids = set([pkg.customer_id for pkg in packages if pkg.customer_id])
        
        for customer_id in customer_ids:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                print(f"\n👤 Cliente: {customer.full_name}")
                print(f"   - Teléfono: {customer.phone}")
                print(f"   - Email: {customer.email}")
                print(f"   - ID: {customer.id}")
                
                # Contar todos los paquetes de este cliente
                all_packages = db.query(Package).filter(
                    Package.customer_id == customer_id
                ).all()
                
                print(f"   - Total de paquetes: {len(all_packages)}")
                print(f"\n   📦 Lista de paquetes:")
                for pkg in all_packages:
                    print(f"      • {pkg.tracking_number} - {pkg.status} - Guía: {pkg.guide_number or 'N/A'}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_customer_packages()
