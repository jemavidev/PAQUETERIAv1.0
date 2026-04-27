#!/usr/bin/env python3
"""
Script para diagnosticar el cálculo de precios de un producto específico
"""
import sys
sys.path.insert(0, '/workspace/CODE/src')

from app.database import get_db
from app.models.invoice_v2 import InvoiceProductV2
from sqlalchemy import desc

def debug_producto(descripcion_buscar="TABLA LEAJADORA"):
    """Diagnosticar un producto específico"""
    db = next(get_db())
    
    # Buscar el producto
    producto = db.query(InvoiceProductV2).filter(
        InvoiceProductV2.descripcion.ilike(f'%{descripcion_buscar}%')
    ).order_by(desc(InvoiceProductV2.created_at)).first()
    
    if not producto:
        print(f"❌ No se encontró producto con descripción: {descripcion_buscar}")
        return
    
    print(f"\n{'='*80}")
    print(f"DIAGNÓSTICO DE PRODUCTO")
    print(f"{'='*80}\n")
    
    print(f"📦 Descripción: {producto.descripcion}")
    print(f"🔢 Código: {producto.codigo_producto}")
    print(f"📊 Cantidad: {producto.cantidad}")
    print(f"💰 Precio Unitario (BD): ${producto.precio_unitario:,.2f}")
    print(f"📈 IVA %: {producto.iva_porcentaje}%")
    print(f"💵 IVA Valor (BD): ${producto.iva_valor:,.2f}" if producto.iva_valor else "💵 IVA Valor: N/A")
    print(f"💳 Total Item (BD): ${producto.total_item:,.2f}")
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DE ESCENARIOS")
    print(f"{'='*80}\n")
    
    precio_unit = float(producto.precio_unitario)
    cantidad = float(producto.cantidad)
    total = float(producto.total_item)
    iva_pct = float(producto.iva_porcentaje) if producto.iva_porcentaje else 0
    iva_val = float(producto.iva_valor) if producto.iva_valor else 0
    
    # Escenario 1: Precio SIN IVA
    total_sin_iva_esperado = precio_unit * cantidad
    precio_con_iva_calc = precio_unit * (1 + iva_pct / 100)
    total_con_iva_calc = total_sin_iva_esperado * (1 + iva_pct / 100)
    
    print(f"📌 ESCENARIO 1: Precio_unitario NO incluye IVA")
    print(f"   Precio unitario SIN IVA: ${precio_unit:,.2f}")
    print(f"   Precio unitario CON IVA: ${precio_con_iva_calc:,.2f}")
    print(f"   Total esperado SIN IVA: ${total_sin_iva_esperado:,.2f}")
    print(f"   Total esperado CON IVA: ${total_con_iva_calc:,.2f}")
    print(f"   Total en BD: ${total:,.2f}")
    print(f"   Total + IVA valor: ${total + iva_val:,.2f}")
    
    diff_sin_iva = abs(total - total_sin_iva_esperado)
    diff_con_iva = abs(total - total_con_iva_calc)
    diff_sumado = abs((total + iva_val) - total_con_iva_calc)
    
    print(f"\n   Diferencia con total SIN IVA: ${diff_sin_iva:,.2f}")
    print(f"   Diferencia con total CON IVA: ${diff_con_iva:,.2f}")
    print(f"   Diferencia sumando IVA: ${diff_sumado:,.2f}")
    
    # Escenario 2: Precio CON IVA
    precio_sin_iva_calc = precio_unit / (1 + iva_pct / 100)
    total_con_iva_esperado = precio_unit * cantidad
    
    print(f"\n📌 ESCENARIO 2: Precio_unitario YA incluye IVA")
    print(f"   Precio unitario CON IVA: ${precio_unit:,.2f}")
    print(f"   Precio unitario SIN IVA (calculado): ${precio_sin_iva_calc:,.2f}")
    print(f"   Total esperado CON IVA: ${total_con_iva_esperado:,.2f}")
    print(f"   Total en BD: ${total:,.2f}")
    
    diff_escenario2 = abs(total - total_con_iva_esperado)
    print(f"   Diferencia: ${diff_escenario2:,.2f}")
    
    # Decisión
    print(f"\n{'='*80}")
    print(f"DECISIÓN")
    print(f"{'='*80}\n")
    
    tolerancia = 0.02
    diff_sin_iva_rel = diff_sin_iva / max(total, 1)
    diff_con_iva_rel = diff_con_iva / max(total, 1)
    diff_sumado_rel = diff_sumado / max(total + iva_val, 1)
    diff_escenario2_rel = diff_escenario2 / max(total, 1)
    
    print(f"Tolerancia: {tolerancia*100}%")
    print(f"Diferencia relativa SIN IVA: {diff_sin_iva_rel*100:.2f}%")
    print(f"Diferencia relativa CON IVA: {diff_con_iva_rel*100:.2f}%")
    print(f"Diferencia relativa SUMADO: {diff_sumado_rel*100:.2f}%")
    print(f"Diferencia relativa ESCENARIO 2: {diff_escenario2_rel*100:.2f}%")
    
    if diff_escenario2_rel < tolerancia:
        print(f"\n✅ RESULTADO: Precio_unitario YA incluye IVA")
        print(f"   Mostrar precio: ${precio_unit:,.0f}")
        print(f"   Mostrar total: ${total:,.0f}")
    elif diff_sin_iva_rel < tolerancia and diff_sumado_rel < tolerancia:
        print(f"\n✅ RESULTADO: Precio_unitario NO incluye IVA")
        print(f"   Mostrar precio: ${precio_con_iva_calc:,.0f}")
        print(f"   Mostrar total: ${total + iva_val:,.0f}")
    else:
        print(f"\n⚠️ RESULTADO: Caso ambiguo, usar lógica por defecto (NO incluye IVA)")
        print(f"   Mostrar precio: ${precio_con_iva_calc:,.0f}")
        print(f"   Mostrar total: ${total + iva_val:,.0f}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_producto(sys.argv[1])
    else:
        debug_producto("TABLA LEAJADORA")
