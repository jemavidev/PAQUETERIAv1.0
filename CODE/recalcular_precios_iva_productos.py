#!/usr/bin/env python3
"""
Script para recalcular y detectar si los precios de productos incluyen IVA
Analiza cada factura y sus productos para determinar el formato correcto
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import get_db
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from sqlalchemy import func
from decimal import Decimal

def analizar_factura(factura, db):
    """
    Analiza una factura completa para determinar si los precios incluyen IVA
    """
    productos = db.query(InvoiceProductV2).filter(
        InvoiceProductV2.cufe == factura.cufe
    ).all()
    
    if not productos:
        return None
    
    # Analizar cada producto
    resultados = []
    for prod in productos:
        if not prod.precio_unitario or not prod.cantidad or not prod.total_item:
            continue
            
        precio_unit = float(prod.precio_unitario)
        cantidad = float(prod.cantidad)
        total = float(prod.total_item)
        iva_pct = float(prod.iva_porcentaje) if prod.iva_porcentaje else 0
        iva_val = float(prod.iva_valor) if prod.iva_valor else 0
        
        # Calcular escenarios
        total_sin_iva_esperado = precio_unit * cantidad
        total_con_iva_esperado = precio_unit * cantidad * (1 + iva_pct / 100)
        total_con_iva_sumado = total + iva_val
        
        # Tolerancia del 3%
        tolerancia = 0.03
        
        # Determinar qué escenario se ajusta mejor
        iva_incluido = False
        
        if iva_val > 0 and iva_val > (total * 0.01):
            # Hay iva_valor significativo
            diff_sumado = abs(total_con_iva_sumado - total_con_iva_esperado) / max(total_con_iva_sumado, 1)
            if diff_sumado < tolerancia:
                # total NO incluye IVA (iva_valor está separado)
                iva_incluido = False
            else:
                # total YA incluye IVA
                iva_incluido = True
        else:
            # No hay iva_valor significativo
            diff_con_iva = abs(total - total_con_iva_esperado) / max(total, 1)
            diff_sin_iva = abs(total - total_sin_iva_esperado) / max(total, 1)
            
            if diff_con_iva < diff_sin_iva and diff_con_iva < tolerancia:
                iva_incluido = True
            else:
                iva_incluido = False
        
        resultados.append({
            'producto_id': prod.id,
            'descripcion': prod.descripcion[:50] if prod.descripcion else 'N/A',
            'precio_unitario': precio_unit,
            'cantidad': cantidad,
            'total_item': total,
            'iva_porcentaje': iva_pct,
            'iva_valor': iva_val,
            'iva_incluido': iva_incluido,
            'total_sin_iva_esperado': total_sin_iva_esperado,
            'total_con_iva_esperado': total_con_iva_esperado,
            'total_con_iva_sumado': total_con_iva_sumado
        })
    
    return resultados

def main():
    """
    Procesar todas las facturas y generar reporte
    """
    db = next(get_db())
    
    print("="*100)
    print("ANÁLISIS DE PRECIOS CON IVA EN PRODUCTOS")
    print("="*100)
    print()
    
    # Obtener todas las facturas
    facturas = db.query(InvoiceV2).order_by(InvoiceV2.created_at.desc()).all()
    
    print(f"📊 Total de facturas a analizar: {len(facturas)}")
    print()
    
    total_productos = 0
    productos_con_iva_incluido = 0
    productos_sin_iva_incluido = 0
    
    facturas_con_iva_incluido = []
    facturas_sin_iva_incluido = []
    
    for i, factura in enumerate(facturas, 1):
        print(f"\r⏳ Analizando factura {i}/{len(facturas)}...", end='', flush=True)
        
        resultados = analizar_factura(factura, db)
        
        if not resultados:
            continue
        
        # Determinar el patrón predominante en la factura
        iva_incluidos = sum(1 for r in resultados if r['iva_incluido'])
        iva_no_incluidos = len(resultados) - iva_incluidos
        
        factura_tiene_iva_incluido = iva_incluidos > iva_no_incluidos
        
        if factura_tiene_iva_incluido:
            facturas_con_iva_incluido.append({
                'cufe': factura.cufe,
                'numero': factura.numero_factura,
                'proveedor': factura.proveedor_nombre,
                'fecha': factura.fecha_emision,
                'productos': resultados
            })
            productos_con_iva_incluido += len(resultados)
        else:
            facturas_sin_iva_incluido.append({
                'cufe': factura.cufe,
                'numero': factura.numero_factura,
                'proveedor': factura.proveedor_nombre,
                'fecha': factura.fecha_emision,
                'productos': resultados
            })
            productos_sin_iva_incluido += len(resultados)
        
        total_productos += len(resultados)
    
    print("\r" + " "*100 + "\r", end='')
    
    print()
    print("="*100)
    print("RESULTADOS DEL ANÁLISIS")
    print("="*100)
    print()
    print(f"📦 Total de productos analizados: {total_productos}")
    print(f"✅ Productos con IVA incluido en precio: {productos_con_iva_incluido} ({productos_con_iva_incluido/total_productos*100:.1f}%)")
    print(f"❌ Productos con IVA separado: {productos_sin_iva_incluido} ({productos_sin_iva_incluido/total_productos*100:.1f}%)")
    print()
    print(f"📄 Facturas con IVA incluido: {len(facturas_con_iva_incluido)}")
    print(f"📄 Facturas con IVA separado: {len(facturas_sin_iva_incluido)}")
    print()
    
    # Mostrar ejemplos de facturas con IVA incluido
    if facturas_con_iva_incluido:
        print("="*100)
        print("EJEMPLOS DE FACTURAS CON IVA INCLUIDO EN PRECIOS")
        print("="*100)
        print()
        
        for factura_info in facturas_con_iva_incluido[:5]:  # Mostrar primeras 5
            print(f"📄 Factura: {factura_info['numero']}")
            print(f"   Proveedor: {factura_info['proveedor']}")
            print(f"   Fecha: {factura_info['fecha']}")
            print(f"   CUFE: {factura_info['cufe'][:30]}...")
            print()
            
            for prod in factura_info['productos'][:3]:  # Mostrar primeros 3 productos
                print(f"   📦 {prod['descripcion']}")
                print(f"      Precio unitario: ${prod['precio_unitario']:,.0f} (YA incluye IVA)")
                print(f"      Cantidad: {prod['cantidad']}")
                print(f"      Total: ${prod['total_item']:,.0f} (YA incluye IVA)")
                print(f"      IVA %: {prod['iva_porcentaje']}%")
                print()
            
            if len(factura_info['productos']) > 3:
                print(f"   ... y {len(factura_info['productos']) - 3} productos más")
            print()
    
    # Mostrar ejemplos de facturas con IVA separado
    if facturas_sin_iva_incluido:
        print("="*100)
        print("EJEMPLOS DE FACTURAS CON IVA SEPARADO")
        print("="*100)
        print()
        
        for factura_info in facturas_sin_iva_incluido[:5]:  # Mostrar primeras 5
            print(f"📄 Factura: {factura_info['numero']}")
            print(f"   Proveedor: {factura_info['proveedor']}")
            print(f"   Fecha: {factura_info['fecha']}")
            print(f"   CUFE: {factura_info['cufe'][:30]}...")
            print()
            
            for prod in factura_info['productos'][:3]:  # Mostrar primeros 3 productos
                precio_con_iva = prod['precio_unitario'] * (1 + prod['iva_porcentaje'] / 100)
                total_con_iva = prod['total_item'] + prod['iva_valor']
                
                print(f"   📦 {prod['descripcion']}")
                print(f"      Precio unitario SIN IVA: ${prod['precio_unitario']:,.0f}")
                print(f"      Precio unitario CON IVA: ${precio_con_iva:,.0f}")
                print(f"      Cantidad: {prod['cantidad']}")
                print(f"      Total SIN IVA: ${prod['total_item']:,.0f}")
                print(f"      Total CON IVA: ${total_con_iva:,.0f}")
                print(f"      IVA %: {prod['iva_porcentaje']}%")
                print()
            
            if len(factura_info['productos']) > 3:
                print(f"   ... y {len(factura_info['productos']) - 3} productos más")
            print()
    
    print("="*100)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*100)
    print()
    print("💡 El sistema ahora detectará automáticamente el formato de cada factura")
    print("   y mostrará los precios correctamente con IVA incluido.")
    print()

if __name__ == "__main__":
    main()
