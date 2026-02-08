#!/usr/bin/env python3
"""
Script para cargar los 4 archivos DIAN correctos que tienen 91 productos
"""
import sys
import os
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

# Lista de archivos DIAN a cargar
archivos_dian = [
    {
        'path': '../CUFE/CUFE/8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad.pdf',
        'cufe': '8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad',
        'numero': '006D-2956',
        'productos_esperados': 6
    },
    {
        'path': '../CUFE/CUFE/b95d05e6ff51cbaf53e1510b1d213af6a0ec838d1e4420e708b99e9c723c984926586ce3a64de8d5a621b2eeea9ec051.pdf',
        'cufe': 'b95d05e6ff51cbaf53e1510b1d213af6a0ec838d1e4420e708b99e9c723c984926586ce3a64de8d5a621b2eeea9ec051',
        'numero': '006D-2954',
        'productos_esperados': 37
    },
    {
        'path': '../CUFE/CUFE/dce84f5f446f8c609791c431e785b550a2d63cd81fa2ccd4f429ac8c3a7ba442b7137b4727dbcfb151862e7ad9f5b1ce.pdf',
        'cufe': 'dce84f5f446f8c609791c431e785b550a2d63cd81fa2ccd4f429ac8c3a7ba442b7137b4727dbcfb151862e7ad9f5b1ce',
        'numero': '006D-3340',
        'productos_esperados': 45
    },
    {
        'path': '../CUFE/CUFE/8d4f3b4bbfd27479320718fa3212ede27b147eac958e4fa4897961d2e04f66273233775c7d1946454ee4aa15ba8b1b1b.pdf',
        'cufe': '8d4f3b4bbfd27479320718fa3212ede27b147eac958e4fa4897961d2e04f66273233775c7d1946454ee4aa15ba8b1b1b',
        'numero': '9PE-15547',
        'productos_esperados': 3
    }
]

print('=' * 80)
print('CARGANDO ARCHIVOS DIAN CORRECTOS')
print('=' * 80)

db = SessionLocal()
service = InvoiceV2Service(db)

total_productos_cargados = 0

for i, archivo in enumerate(archivos_dian, 1):
    print(f'\n{i}. Procesando: {archivo["numero"]}')
    print(f'   CUFE: {archivo["cufe"][:40]}...')
    print(f'   Productos esperados: {archivo["productos_esperados"]}')
    
    # Verificar si el archivo existe
    if not os.path.exists(archivo['path']):
        print(f'   ❌ ERROR: Archivo no encontrado en {archivo["path"]}')
        continue
    
    # Verificar si ya existe una factura con este CUFE
    existing = service.get_invoice_by_cufe(archivo['cufe'])
    
    if existing:
        print(f'   ⚠️ Factura ya existe en la BD')
        print(f'   Estado actual: {existing.estado}')
        print(f'   DIAN validado: {existing.dian_validado}')
        print(f'   Productos actuales: {len(existing.productos)}')
        
        # Si no tiene archivo DIAN, procesarlo
        if not existing.dian_validado:
            print(f'   📤 Procesando archivo DIAN...')
            try:
                with open(archivo['path'], 'rb') as f:
                    invoice = service.process_dian_document(
                        archivo['cufe'],
                        archivo['path'],
                        file_obj=f
                    )
                print(f'   ✅ Archivo DIAN procesado correctamente')
                print(f'   Productos extraídos: {len(invoice.productos)}')
                total_productos_cargados += len(invoice.productos)
            except Exception as e:
                print(f'   ❌ Error procesando archivo DIAN: {e}')
        else:
            print(f'   ✅ Ya tiene archivo DIAN procesado')
            total_productos_cargados += len(existing.productos)
    else:
        print(f'   ⚠️ Factura NO existe en la BD')
        print(f'   Primero debes cargar la factura del proveedor en el TAB FACTURAS')
        print(f'   Luego asociar el archivo DIAN en el TAB CUFE')

print('\n' + '=' * 80)
print(f'📦 TOTAL DE PRODUCTOS CARGADOS: {total_productos_cargados}')
print('=' * 80)

db.close()
