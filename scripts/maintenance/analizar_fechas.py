#!/usr/bin/env python3
"""
Script para analizar fechas en el sistema
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice import Invoice, SupplierInvoice
from datetime import datetime
from sqlalchemy import desc


def main():
    db = SessionLocal()
    
    try:
        print('='*80)
        print('ANÁLISIS DE FECHAS EN EL SISTEMA')
        print('='*80)
        
        now = datetime.now()
        print(f'\nFecha actual: {now.strftime("%Y-%m-%d %H:%M")}')
        
        print('\n1. FACTURAS PROCESADAS CON FECHAS FUTURAS:')
        print('-'*80)
        future_invoices = db.query(Invoice).filter(
            Invoice.fecha_emision > now,
            Invoice.is_active == True
        ).order_by(Invoice.fecha_emision).all()
        
        if future_invoices:
            for inv in future_invoices:
                print(f'  ID {inv.id}: {inv.numero_documento}')
                print(f'    Fecha: {inv.fecha_emision.strftime("%Y-%m-%d %H:%M")}')
                print(f'    Proveedor: {inv.supplier.razon_social if inv.supplier else "N/A"}')
                print(f'    Total: ${inv.total_neto:,}')
                print()
        else:
            print('  ✅ No hay facturas con fechas futuras')
        
        print('\n2. SUPPLIER INVOICES CON FECHAS FUTURAS:')
        print('-'*80)
        future_si = db.query(SupplierInvoice).filter(
            SupplierInvoice.invoice_date > now
        ).order_by(SupplierInvoice.invoice_date).all()
        
        if future_si:
            for si in future_si:
                print(f'  ID {si.id}: {si.original_filename}')
                print(f'    Fecha: {si.invoice_date.strftime("%Y-%m-%d %H:%M")}')
                print(f'    Status: {si.status.value}')
                print()
        else:
            print('  ✅ No hay supplier invoices con fechas futuras')
        
        print('\n3. ÚLTIMAS 10 FACTURAS PROCESADAS (orden actual por imported_at):')
        print('-'*80)
        recent = db.query(Invoice).filter(
            Invoice.is_active == True
        ).order_by(desc(Invoice.imported_at)).limit(10).all()
        
        for inv in recent:
            fecha_factura = inv.fecha_emision.strftime("%Y-%m-%d") if inv.fecha_emision else "N/A"
            fecha_import = inv.imported_at.strftime("%Y-%m-%d %H:%M") if inv.imported_at else "N/A"
            print(f'  ID {inv.id}: {inv.numero_documento} - Fecha factura: {fecha_factura} - Importada: {fecha_import}')
        
        print('\n4. ÚLTIMAS 10 SUPPLIER INVOICES (orden actual por uploaded_at):')
        print('-'*80)
        recent_si = db.query(SupplierInvoice).order_by(desc(SupplierInvoice.uploaded_at)).limit(10).all()
        
        for si in recent_si:
            fecha_str = si.invoice_date.strftime('%Y-%m-%d') if si.invoice_date else 'N/A'
            fecha_upload = si.uploaded_at.strftime("%Y-%m-%d %H:%M") if si.uploaded_at else "N/A"
            print(f'  ID {si.id}: {si.original_filename[:50]} - Fecha factura: {fecha_str} - Subida: {fecha_upload}')
        
        print('\n' + '='*80)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
