#!/usr/bin/env python3
"""
Script para verificar TODOS los productos y detectar si tienen IVA incluido correctamente
Analiza cada producto basándose en el precio total y genera un reporte detallado
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import get_db
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from sqlalchemy import func, desc
from decimal import Decimal

def analizar_producto(prod):
    """
    Analiza un producto individual y determina si tiene IVA incluido
    Retorna un diccionario con el análisis completo
    """
    if not prod.precio_unitario or not prod.cantidad or not prod.total_item:
        return None
    
    precio_unit = float(prod.precio_unitario)
    cantidad = float(prod.cantidad)
    total = float(prod.total_item)
    iva_pct = float(prod.iva_porcentaje) if prod.iva_porcentaje else 0
    iva_val = float(prod.iva_valor) if prod.iva_valor else 0
    
    # Calcular diferentes escenarios
    total_sin_iva_esperado = precio_unit * cantidad
    total_con_iva_esperado = precio_unit * cantidad * (1 + iva_pct / 100)
    total_con_iva_sumado = total + iva_val
    
    # Tolerancia del 3%
    tolerancia = 0.03
    
    # Determinar qué escenario se ajusta mejor
    iva_incluido = False
    confianza = "BAJA"
    razon = ""
    
    if iva_val > 0 and iva_val > (total * 0.01):
        # Hay iva_valor significativo
        diff_sumado = abs(total_con_iva_sumado - total_con_iva_esperado) / max(total_con_iva_sumado, 1)
        
        if diff_sumado < tolerancia:
            # total NO incluye IVA (iva_valor está separado)
            iva_incluido = False
            confianza = "ALTA"
            razon = f"total + iva_valor ({total_con_iva_sumado:,.0f}) ≈ precio × cant × (1+IVA) ({total_con_iva_esperado:,.0f})"
        else:
            # total YA incluye IVA
            iva_incluido = True
            confianza = "MEDIA"
            razon = f"total ({total:,.0f}) no coincide con cálculos estándar, asumiendo IVA incluido"
    else:
        # No hay iva_valor significativo
        diff_con_iva = abs(total - total_con_iva_esperado) / max(total, 1)
        diff_sin_iva = abs(total - total_sin_iva_esperado) / max(total, 1)
        
        if diff_con_iva < tolerancia and diff_con_iva < diff_sin_iva:
            # total se parece más a precio × cantidad × (1 + IVA%)
            iva_incluido = True
            confianza = "ALTA"
            razon = f"total ({total:,.0f}) ≈ precio × cant × (1+IVA) ({total_con_iva_esperado:,.0f})"
        elif diff_sin_iva < tolerancia:
            # total se parece más a precio × cantidad
            iva_incluido = False
            confianza = "ALTA"
            razon = f"total ({total:,.0f}) ≈ precio × cant ({total_sin_iva_esperado:,.0f})"
        else:
            # No está claro
            if diff_sin_iva < diff_con_iva:
                iva_incluido = False
                confianza = "BAJA"
                razon = f"Ambiguo, asumiendo SIN IVA (diff: {diff_sin_iva*100:.1f}%)"
            else:
                iva_incluido = True
                confianza = "BAJA"
                razon = f"Ambiguo, asumiendo CON IVA (diff: {diff_con_iva*100:.1f}%)"
    
    # Calcular precios para mostrar
    if iva_incluido:
        precio_mostrar = precio_unit
        total_mostrar = precio_unit * cantidad
    else:
        precio_mostrar = precio_unit * (1 + iva_pct / 100)
        total_mostrar = total + iva_val
    
    return {
        'id': prod.id,
        'cufe': prod.cufe,
        'descripcion': prod.descripcion[:60] if prod.descripcion else 'N/A',
        'codigo': prod.codigo_producto or prod.codigo_interno or 'N/A',
        'cantidad': cantidad,
        'precio_unitario_bd': precio_unit,
        'total_item_bd': total,
        'iva_porcentaje': iva_pct,
        'iva_valor_bd': iva_val,
        'iva_incluido': iva_incluido,
        'confianza': confianza,
        'razon': razon,
        'precio_mostrar': precio_mostrar,
        'total_mostrar': total_mostrar,
        'total_sin_iva_esperado': total_sin_iva_esperado,
        'total_con_iva_esperado': total_con_iva_esperado,
        'total_con_iva_sumado': total_con_iva_sumado
    }

def main():
    """
    Analizar todos los productos y generar reporte completo
    """
    db = next(get_db())
    
    print("="*120)
    print("VERIFICACIÓN COMPLETA DE PRODUCTOS - DETECCIÓN DE IVA INCLUIDO")
    print("="*120)
    print()
    
    # Obtener todos los productos
    productos = db.query(InvoiceProductV2).order_by(desc(InvoiceProductV2.created_at)).all()
    
    print(f"📊 Total de productos en base de datos: {len(productos)}")
    print()
    
    # Analizar cada producto
    resultados = []
    productos_analizados = 0
    productos_sin_datos = 0
    
    for i, prod in enumerate(productos, 1):
        if i % 100 == 0:
            print(f"\r⏳ Analizando producto {i}/{len(productos)}...", end='', flush=True)
        
        resultado = analizar_producto(prod)
        
        if resultado:
            resultados.append(resultado)
            productos_analizados += 1
        else:
            productos_sin_datos += 1
    
    print("\r" + " "*100 + "\r", end='')
    
    # Estadísticas generales
    productos_con_iva = sum(1 for r in resultados if r['iva_incluido'])
    productos_sin_iva = len(resultados) - productos_con_iva
    
    confianza_alta = sum(1 for r in resultados if r['confianza'] == 'ALTA')
    confianza_media = sum(1 for r in resultados if r['confianza'] == 'MEDIA')
    confianza_baja = sum(1 for r in resultados if r['confianza'] == 'BAJA')
    
    print("="*120)
    print("ESTADÍSTICAS GENERALES")
    print("="*120)
    print()
    print(f"📦 Productos analizados: {productos_analizados}")
    print(f"⚠️  Productos sin datos suficientes: {productos_sin_datos}")
    print()
    print(f"✅ Productos CON IVA incluido: {productos_con_iva} ({productos_con_iva/productos_analizados*100:.1f}%)")
    print(f"❌ Productos SIN IVA incluido: {productos_sin_iva} ({productos_sin_iva/productos_analizados*100:.1f}%)")
    print()
    print(f"🎯 Confianza ALTA: {confianza_alta} ({confianza_alta/productos_analizados*100:.1f}%)")
    print(f"🟡 Confianza MEDIA: {confianza_media} ({confianza_media/productos_analizados*100:.1f}%)")
    print(f"🔴 Confianza BAJA: {confianza_baja} ({confianza_baja/productos_analizados*100:.1f}%)")
    print()
    
    # Mostrar ejemplos de productos CON IVA incluido
    productos_con_iva_list = [r for r in resultados if r['iva_incluido']]
    if productos_con_iva_list:
        print("="*120)
        print("EJEMPLOS DE PRODUCTOS CON IVA INCLUIDO EN PRECIO")
        print("="*120)
        print()
        
        for resultado in productos_con_iva_list[:10]:  # Mostrar primeros 10
            print(f"📦 {resultado['descripcion']}")
            print(f"   Código: {resultado['codigo']}")
            print(f"   Cantidad: {resultado['cantidad']}")
            print(f"   Precio unitario (BD): ${resultado['precio_unitario_bd']:,.2f} (YA incluye IVA)")
            print(f"   Total (BD): ${resultado['total_item_bd']:,.2f}")
            print(f"   IVA: {resultado['iva_porcentaje']}%")
            print(f"   ➡️  MOSTRAR: Precio ${resultado['precio_mostrar']:,.0f} | Total ${resultado['total_mostrar']:,.0f}")
            print(f"   Confianza: {resultado['confianza']} - {resultado['razon']}")
            print()
        
        if len(productos_con_iva_list) > 10:
            print(f"   ... y {len(productos_con_iva_list) - 10} productos más con IVA incluido")
            print()
    
    # Mostrar ejemplos de productos SIN IVA incluido
    productos_sin_iva_list = [r for r in resultados if not r['iva_incluido']]
    if productos_sin_iva_list:
        print("="*120)
        print("EJEMPLOS DE PRODUCTOS SIN IVA INCLUIDO (IVA SEPARADO)")
        print("="*120)
        print()
        
        for resultado in productos_sin_iva_list[:10]:  # Mostrar primeros 10
            print(f"📦 {resultado['descripcion']}")
            print(f"   Código: {resultado['codigo']}")
            print(f"   Cantidad: {resultado['cantidad']}")
            print(f"   Precio unitario (BD): ${resultado['precio_unitario_bd']:,.2f} (SIN IVA)")
            print(f"   Total (BD): ${resultado['total_item_bd']:,.2f} (SIN IVA)")
            print(f"   IVA valor: ${resultado['iva_valor_bd']:,.2f}")
            print(f"   IVA: {resultado['iva_porcentaje']}%")
            print(f"   ➡️  MOSTRAR: Precio ${resultado['precio_mostrar']:,.0f} | Total ${resultado['total_mostrar']:,.0f}")
            print(f"   Confianza: {resultado['confianza']} - {resultado['razon']}")
            print()
        
        if len(productos_sin_iva_list) > 10:
            print(f"   ... y {len(productos_sin_iva_list) - 10} productos más sin IVA incluido")
            print()
    
    # Mostrar productos con confianza BAJA
    productos_baja_confianza = [r for r in resultados if r['confianza'] == 'BAJA']
    if productos_baja_confianza:
        print("="*120)
        print("⚠️  PRODUCTOS CON CONFIANZA BAJA (REVISAR MANUALMENTE)")
        print("="*120)
        print()
        
        for resultado in productos_baja_confianza[:20]:  # Mostrar primeros 20
            print(f"📦 {resultado['descripcion']}")
            print(f"   ID: {resultado['id']} | Código: {resultado['codigo']}")
            print(f"   Precio: ${resultado['precio_unitario_bd']:,.2f} | Cant: {resultado['cantidad']} | Total: ${resultado['total_item_bd']:,.2f}")
            print(f"   IVA: {resultado['iva_porcentaje']}% | IVA valor: ${resultado['iva_valor_bd']:,.2f}")
            print(f"   Razón: {resultado['razon']}")
            print(f"   ➡️  Detectado como: {'CON IVA' if resultado['iva_incluido'] else 'SIN IVA'}")
            print()
        
        if len(productos_baja_confianza) > 20:
            print(f"   ... y {len(productos_baja_confianza) - 20} productos más con baja confianza")
            print()
    
    print("="*120)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*120)
    print()
    print("💡 RESUMEN:")
    print(f"   - {productos_con_iva} productos tienen precios CON IVA incluido")
    print(f"   - {productos_sin_iva} productos tienen precios SIN IVA (IVA separado)")
    print(f"   - {confianza_baja} productos requieren revisión manual")
    print()
    print("🔄 El sistema detectará automáticamente el formato de cada producto")
    print("   y mostrará los precios correctamente en la interfaz.")
    print()

if __name__ == "__main__":
    main()
