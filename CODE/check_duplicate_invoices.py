#!/usr/bin/env python3
"""
Script para verificar facturas duplicadas en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.invoice_v2 import InvoiceV2
from app.database import get_database_url

def check_duplicates():
    """Verifica si hay CUFEs duplicados en la base de datos"""
    
    # Conectar a la base de datos
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔍 Verificando facturas duplicadas...\n")
    
    # Buscar CUFEs duplicados
    duplicates = session.query(
        InvoiceV2.cufe,
        func.count(InvoiceV2.cufe).label('count')
    ).group_by(InvoiceV2.cufe).having(func.count(InvoiceV2.cufe) > 1).all()
    
    if duplicates:
        print(f"❌ Se encontraron {len(duplicates)} CUFEs duplicados:\n")
        for cufe, count in duplicates:
            print(f"  • {cufe[:20]}... aparece {count} veces")
            
            # Mostrar detalles de cada duplicado
            invoices = session.query(InvoiceV2).filter_by(cufe=cufe).all()
            for i, inv in enumerate(invoices, 1):
                print(f"    {i}. ID: {inv.id if hasattr(inv, 'id') else 'N/A'}, "
                      f"Proveedor: {inv.proveedor_nombre or 'N/A'}, "
                      f"Fecha: {inv.created_at}")
            print()
    else:
        print("✅ No se encontraron CUFEs duplicados")
    
    # Contar total de facturas
    total = session.query(func.count(InvoiceV2.cufe)).scalar()
    print(f"\n📊 Total de facturas: {total}")
    
    # Mostrar algunas facturas de ejemplo
    print("\n📋 Últimas 5 facturas:")
    recent = session.query(InvoiceV2).order_by(InvoiceV2.created_at.desc()).limit(5).all()
    for inv in recent:
        print(f"  • {inv.cufe[:20]}... - {inv.proveedor_nombre or 'Sin proveedor'} - {inv.estado}")
    
    session.close()

if __name__ == "__main__":
    try:
        check_duplicates()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
