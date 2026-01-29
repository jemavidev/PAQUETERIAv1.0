#!/usr/bin/env python3
"""
Script para corregir fechas futuras en supplier_invoices
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice
from datetime import datetime


def extraer_fecha_del_nombre(filename):
    """
    Extrae la fecha del nombre del archivo.
    Formato esperado: f-{cufe}_{YYYYMMDDHHMMSS}.pdf
    """
    # Buscar patrón de fecha en el nombre: YYYYMMDDHHMMSS
    match = re.search(r'_(\d{14})\.pdf$', filename)
    if match:
        fecha_str = match.group(1)
        try:
            # Parsear: YYYYMMDDHHMMSS
            fecha = datetime.strptime(fecha_str, '%Y%m%d%H%M%S')
            return fecha
        except:
            pass
    
    # Buscar patrón alternativo: YYYYMMDD
    match = re.search(r'_(\d{8})\.pdf$', filename)
    if match:
        fecha_str = match.group(1)
        try:
            fecha = datetime.strptime(fecha_str, '%Y%m%d')
            return fecha
        except:
            pass
    
    return None


def main():
    db = SessionLocal()
    
    try:
        print('='*80)
        print('CORRECCIÓN DE FECHAS FUTURAS')
        print('='*80)
        
        now = datetime.now()
        print(f'\nFecha actual: {now.strftime("%Y-%m-%d %H:%M")}')
        
        # Buscar supplier invoices con fechas futuras
        future_si = db.query(SupplierInvoice).filter(
            SupplierInvoice.invoice_date > now
        ).all()
        
        if not future_si:
            print('\n✅ No hay supplier invoices con fechas futuras')
            return
        
        print(f'\n⚠️  Encontradas {len(future_si)} supplier invoices con fechas futuras:')
        print()
        
        for si in future_si:
            print(f'ID {si.id}: {si.original_filename}')
            print(f'  Fecha actual: {si.invoice_date.strftime("%Y-%m-%d")}')
            
            # Intentar extraer fecha del nombre del archivo
            fecha_correcta = extraer_fecha_del_nombre(si.original_filename)
            
            if fecha_correcta:
                print(f'  Fecha extraída del nombre: {fecha_correcta.strftime("%Y-%m-%d")}')
                
                if fecha_correcta <= now:
                    print(f'  ✅ Fecha válida, actualizando...')
                    si.invoice_date = fecha_correcta
                else:
                    print(f'  ⚠️  La fecha extraída también es futura')
                    # Usar la fecha de subida como fallback
                    if si.uploaded_at:
                        print(f'  📅 Usando fecha de subida: {si.uploaded_at.strftime("%Y-%m-%d")}')
                        si.invoice_date = si.uploaded_at
            else:
                print(f'  ⚠️  No se pudo extraer fecha del nombre')
                # Usar la fecha de subida como fallback
                if si.uploaded_at:
                    print(f'  📅 Usando fecha de subida: {si.uploaded_at.strftime("%Y-%m-%d")}')
                    si.invoice_date = si.uploaded_at
            
            print()
        
        # Confirmar cambios
        print('='*80)
        print('RESUMEN DE CAMBIOS:')
        print('='*80)
        
        for si in future_si:
            print(f'ID {si.id}: {si.invoice_date.strftime("%Y-%m-%d")}')
        
        print()
        respuesta = input('¿Deseas guardar estos cambios? (s/n): ')
        
        if respuesta.lower() == 's':
            db.commit()
            print('\n✅ Cambios guardados exitosamente')
        else:
            db.rollback()
            print('\n❌ Cambios descartados')
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
