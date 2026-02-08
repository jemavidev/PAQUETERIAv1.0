#!/usr/bin/env python3
"""
Script simple para probar el regex del nuevo formato
"""
import re

# Líneas de ejemplo del formato nuevo
lineas_ejemplo = [
    "1 631668 BOLSA DE PAPEL SELVA 33H-20CTG-25 A9 REF:9141 94 6,00 $ 840,34 $ 0,00 $ 0,00 $ 957,99 19.00 $ 5.042,04",
    "2 631669 BOLSA PAPEL CARROS 33H-23CTG-25 A9 REF:3141 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68",
    "3 631655 BOLSA PAPEL TROPICAL 33H-24CTG-25 A9 REF:3141 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68",
]

print("=" * 80)
print("🧪 PRUEBA DE REGEX PARA NUEVO FORMATO")
print("=" * 80)
print()

# Patrón del nuevo formato
pattern = r'^(\d{1,3})\s+(\d{3,13})\s+(.+?)\s+(\d{2,3})\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)'

for i, linea in enumerate(lineas_ejemplo, 1):
    print(f"Línea {i}:")
    print(f"  Texto: {linea[:80]}...")
    print()
    
    match = re.match(pattern, linea)
    
    if match:
        nro = match.group(1)
        codigo = match.group(2)
        descripcion = match.group(3).strip()
        unidad_codigo = match.group(4)
        cantidad_str = match.group(5).replace(',', '.')
        precio_unit_str = match.group(6).replace('.', '').replace(',', '.')
        
        cantidad = float(cantidad_str)
        precio_unitario = float(precio_unit_str)
        
        # Mapear código de unidad
        unidad_map = {'94': 'NIU', '10': 'PK', '11': 'BX', '01': 'UND'}
        unidad = unidad_map.get(unidad_codigo, 'NIU')
        
        # Buscar IVA (patrón mejorado: valor_iva IVA_% $ total)
        iva_match = re.search(r'\$\s*[0-9.,]+\s+(\d{1,2})[.,]00\s+\$', linea)
        iva_porcentaje = float(iva_match.group(1)) if iva_match else 0.0
        
        # Buscar total (último valor monetario)
        valores = re.findall(r'\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', linea)
        total_str = valores[-1].replace('.', '').replace(',', '.') if valores else '0'
        total_item = float(total_str)
        
        print(f"  ✅ EXTRAÍDO:")
        print(f"     Nro: {nro}")
        print(f"     Código: {codigo}")
        print(f"     Descripción: {descripcion[:50]}...")
        print(f"     Unidad: {unidad} (código: {unidad_codigo})")
        print(f"     Cantidad: {cantidad}")
        print(f"     Precio Unit: ${precio_unitario:,.2f}")
        print(f"     IVA: {iva_porcentaje}%")
        print(f"     Total: ${total_item:,.2f}")
    else:
        print(f"  ❌ NO COINCIDE con el patrón")
    
    print()

print("=" * 80)
