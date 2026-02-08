#!/usr/bin/env python3
"""
Script de diagnóstico para el TAB de PRODUCTOS
Verifica que los productos se están extrayendo y guardando correctamente
"""
import sys
import os

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from src.app.models.invoice_v2 import InvoiceV2, InvoiceProductV2

# Crear sesión de BD directamente
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DEL TAB DE PRODUCTOS")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # 1. Contar facturas
        print("📊 ESTADÍSTICAS GENERALES")
        print("-" * 80)
        
        total_facturas = db.query(InvoiceV2).count()
        facturas_completas = db.query(InvoiceV2).filter_by(estado='completo').count()
        facturas_pendientes = db.query(InvoiceV2).filter_by(estado='pendiente_dian').count()
        facturas_sin_cufe = db.query(InvoiceV2).filter_by(estado='sin_cufe').count()
        
        print(f"Total de facturas: {total_facturas}")
        print(f"  - Completas (con DIAN): {facturas_completas}")
        print(f"  - Pendientes DIAN: {facturas_pendientes}")
        print(f"  - Sin CUFE: {facturas_sin_cufe}")
        print()
        
        # 2. Contar productos
        total_productos = db.query(InvoiceProductV2).count()
        print(f"Total de productos extraídos: {total_productos}")
        print()
        
        if total_productos == 0:
            print("⚠️  NO HAY PRODUCTOS EN LA BASE DE DATOS")
            print()
            print("Posibles causas:")
            print("1. No se han cargado archivos DIAN (solo facturas de proveedor)")
            print("2. El parser no está extrayendo productos correctamente")
            print("3. Los productos no se están guardando en la BD")
            print()
            print("Solución:")
            print("1. Ir al TAB CUFE")
            print("2. Seleccionar una factura")
            print("3. Cargar el archivo PDF de la DIAN")
            print("4. Verificar que se extraen productos en los logs")
            print()
            return
        
        # 3. Productos por factura
        print("📦 PRODUCTOS POR FACTURA")
        print("-" * 80)
        
        productos_por_factura = db.query(
            InvoiceV2.cufe,
            InvoiceV2.proveedor_nombre,
            InvoiceV2.numero_factura,
            func.count(InvoiceProductV2.id).label('total_productos')
        ).join(InvoiceProductV2).group_by(
            InvoiceV2.cufe,
            InvoiceV2.proveedor_nombre,
            InvoiceV2.numero_factura
        ).order_by(desc('total_productos')).limit(10).all()
        
        for i, (cufe, proveedor, numero, total) in enumerate(productos_por_factura, 1):
            cufe_short = cufe[:16] + '...' if len(cufe) > 16 else cufe
            print(f"{i:2d}. {cufe_short} | {proveedor or 'Sin proveedor':30s} | {numero or 'Sin número':15s} | {total:3d} productos")
        print()
        
        # 4. Últimos productos extraídos
        print("🆕 ÚLTIMOS 10 PRODUCTOS EXTRAÍDOS")
        print("-" * 80)
        
        ultimos_productos = db.query(InvoiceProductV2).order_by(
            InvoiceProductV2.id.desc()
        ).limit(10).all()
        
        for i, prod in enumerate(ultimos_productos, 1):
            codigo = prod.codigo_producto or 'Sin código'
            descripcion = (prod.descripcion[:40] + '...') if prod.descripcion and len(prod.descripcion) > 40 else (prod.descripcion or 'Sin descripción')
            precio = f"${prod.precio_unitario:,.0f}" if prod.precio_unitario else 'Sin precio'
            cantidad = f"{prod.cantidad:.2f}" if prod.cantidad else '0'
            unidad = prod.unidad_medida or 'NIU'
            
            print(f"{i:2d}. {codigo:15s} | {descripcion:42s} | {cantidad:8s} {unidad:4s} | {precio:12s}")
        print()
        
        # 5. Estadísticas de campos
        print("📈 ESTADÍSTICAS DE CAMPOS")
        print("-" * 80)
        
        productos_con_codigo = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.codigo_producto.isnot(None),
            InvoiceProductV2.codigo_producto != ''
        ).count()
        
        productos_con_descripcion = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.descripcion.isnot(None),
            InvoiceProductV2.descripcion != ''
        ).count()
        
        productos_con_precio = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.precio_unitario.isnot(None)
        ).count()
        
        productos_con_cantidad = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.cantidad.isnot(None)
        ).count()
        
        productos_con_iva = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.iva_porcentaje.isnot(None)
        ).count()
        
        productos_con_total = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.total_item.isnot(None)
        ).count()
        
        print(f"Productos con código:      {productos_con_codigo:5d} / {total_productos} ({productos_con_codigo/total_productos*100:.1f}%)")
        print(f"Productos con descripción: {productos_con_descripcion:5d} / {total_productos} ({productos_con_descripcion/total_productos*100:.1f}%)")
        print(f"Productos con precio:      {productos_con_precio:5d} / {total_productos} ({productos_con_precio/total_productos*100:.1f}%)")
        print(f"Productos con cantidad:    {productos_con_cantidad:5d} / {total_productos} ({productos_con_cantidad/total_productos*100:.1f}%)")
        print(f"Productos con IVA:         {productos_con_iva:5d} / {total_productos} ({productos_con_iva/total_productos*100:.1f}%)")
        print(f"Productos con total:       {productos_con_total:5d} / {total_productos} ({productos_con_total/total_productos*100:.1f}%)")
        print()
        
        # 6. Trazabilidad
        print("🔍 TRAZABILIDAD DE PRODUCTOS")
        print("-" * 80)
        
        productos_con_trazabilidad = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.variacion_tipo.isnot(None)
        ).count()
        
        productos_primera_compra = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.variacion_tipo == 'primera_compra'
        ).count()
        
        productos_subio = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.variacion_tipo == 'subio'
        ).count()
        
        productos_bajo = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.variacion_tipo == 'bajo'
        ).count()
        
        productos_igual = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.variacion_tipo == 'igual'
        ).count()
        
        print(f"Productos con trazabilidad: {productos_con_trazabilidad:5d} / {total_productos} ({productos_con_trazabilidad/total_productos*100:.1f}%)")
        print(f"  - Primera compra:         {productos_primera_compra:5d}")
        print(f"  - Precio subió:           {productos_subio:5d}")
        print(f"  - Precio bajó:            {productos_bajo:5d}")
        print(f"  - Precio igual:           {productos_igual:5d}")
        print()
        
        # 7. Recomendaciones
        print("💡 RECOMENDACIONES")
        print("-" * 80)
        
        if total_productos < 10:
            print("⚠️  Pocos productos en la BD. Cargar más archivos DIAN para tener datos suficientes.")
        
        if productos_con_codigo / total_productos < 0.8:
            print("⚠️  Muchos productos sin código. Revisar parser de productos.")
        
        if productos_con_precio / total_productos < 0.9:
            print("⚠️  Muchos productos sin precio. Revisar extracción de precios.")
        
        if productos_con_trazabilidad / total_productos < 0.5:
            print("⚠️  Poca trazabilidad. Cargar más facturas para tener historial.")
        
        if productos_con_trazabilidad / total_productos > 0.8:
            print("✅ Buena trazabilidad de productos. Sistema funcionando correctamente.")
        
        if total_productos > 100:
            print("✅ Suficientes productos para análisis. Sistema listo para usar.")
        
        print()
        
        # 8. Próximos pasos
        print("🚀 PRÓXIMOS PASOS")
        print("-" * 80)
        print("1. Ir a http://localhost:8000/invoices/productos")
        print("2. Verificar que los productos se muestran correctamente")
        print("3. Probar búsqueda y filtros")
        print("4. Ver historial de un producto")
        print("5. Verificar que la paginación funciona")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("=" * 80)
    print("✅ Diagnóstico completado")
    print("=" * 80)

if __name__ == '__main__':
    main()
