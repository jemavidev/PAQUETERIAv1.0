#!/usr/bin/env python3
"""
Script para verificar qué facturas tienen archivo_proveedor_url
"""
import sys
import os

# Agregar el directorio CODE al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.models.invoice_v2 import InvoiceV2
from src.app.core.config import settings

def main():
    # Crear conexión a la base de datos
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("VERIFICACIÓN DE ARCHIVOS PDF EN FACTURAS")
        print("=" * 80)
        print()
        
        # Contar total de facturas
        total_facturas = db.query(InvoiceV2).count()
        print(f"📊 Total de facturas: {total_facturas}")
        
        # Contar facturas CON archivo
        con_archivo = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_proveedor_url.isnot(None),
            InvoiceV2.archivo_proveedor_url != ''
        ).count()
        print(f"✅ Facturas CON archivo PDF: {con_archivo}")
        
        # Contar facturas SIN archivo
        sin_archivo = db.query(InvoiceV2).filter(
            (InvoiceV2.archivo_proveedor_url.is_(None)) | 
            (InvoiceV2.archivo_proveedor_url == '')
        ).count()
        print(f"❌ Facturas SIN archivo PDF: {sin_archivo}")
        
        print()
        print("-" * 80)
        print("EJEMPLOS DE FACTURAS CON ARCHIVO:")
        print("-" * 80)
        
        # Mostrar ejemplos de facturas con archivo
        facturas_con_archivo = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_proveedor_url.isnot(None),
            InvoiceV2.archivo_proveedor_url != ''
        ).limit(5).all()
        
        if facturas_con_archivo:
            for inv in facturas_con_archivo:
                print(f"CUFE: {inv.cufe[:20]}...")
                print(f"  Proveedor: {inv.proveedor_nombre}")
                print(f"  Número: {inv.numero_factura}")
                print(f"  URL: {inv.archivo_proveedor_url[:60]}...")
                print()
        else:
            print("No hay facturas con archivo PDF")
        
        print("-" * 80)
        print("EJEMPLOS DE FACTURAS SIN ARCHIVO:")
        print("-" * 80)
        
        # Mostrar ejemplos de facturas sin archivo
        facturas_sin_archivo = db.query(InvoiceV2).filter(
            (InvoiceV2.archivo_proveedor_url.is_(None)) | 
            (InvoiceV2.archivo_proveedor_url == '')
        ).limit(5).all()
        
        if facturas_sin_archivo:
            for inv in facturas_sin_archivo:
                print(f"CUFE: {inv.cufe[:20]}...")
                print(f"  Proveedor: {inv.proveedor_nombre}")
                print(f"  Número: {inv.numero_factura}")
                print(f"  Fecha creación: {inv.created_at}")
                print()
        else:
            print("Todas las facturas tienen archivo PDF")
        
        print()
        print("=" * 80)
        print("RESUMEN")
        print("=" * 80)
        
        if sin_archivo > 0:
            porcentaje = (sin_archivo / total_facturas * 100) if total_facturas > 0 else 0
            print(f"⚠️  {porcentaje:.1f}% de las facturas NO tienen archivo PDF")
            print()
            print("POSIBLES CAUSAS:")
            print("1. Facturas creadas antes de implementar la subida a S3")
            print("2. Servicio S3 no configurado correctamente")
            print("3. Error al subir archivos a S3")
            print()
            print("SOLUCIÓN:")
            print("- El botón de descarga ahora se muestra siempre")
            print("- Aparece en VERDE si hay archivo disponible")
            print("- Aparece en GRIS (deshabilitado) si no hay archivo")
            print("- Al hacer hover muestra un tooltip explicativo")
        else:
            print("✅ Todas las facturas tienen archivo PDF disponible")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
