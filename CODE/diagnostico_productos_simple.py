#!/usr/bin/env python3
"""
Script de diagnóstico simple para el TAB de PRODUCTOS
Consulta directamente la BD sin importar modelos complejos
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    exit(1)

engine = create_engine(DATABASE_URL)

def main():
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DEL TAB DE PRODUCTOS")
    print("=" * 80)
    print()
    
    with engine.connect() as conn:
        # 1. Contar facturas
        print("📊 ESTADÍSTICAS GENERALES")
        print("-" * 80)
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2"))
        total_facturas = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2 WHERE estado = 'completo'"))
        facturas_completas = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2 WHERE estado = 'pendiente_dian'"))
        facturas_pendientes = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2 WHERE estado = 'sin_cufe'"))
        facturas_sin_cufe = result.scalar()
        
        print(f"Total de facturas: {total_facturas}")
        print(f"  - Completas (con DIAN): {facturas_completas}")
        print(f"  - Pendientes DIAN: {facturas_pendientes}")
        print(f"  - Sin CUFE: {facturas_sin_cufe}")
        print()
        
        # 2. Contar productos
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2"))
        total_productos = result.scalar()
        
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
        print("📦 PRODUCTOS POR FACTURA (Top 10)")
        print("-" * 80)
        
        query = text("""
            SELECT 
                i.cufe,
                i.proveedor_nombre,
                i.numero_factura,
                COUNT(p.id) as total_productos
            FROM invoices_v2 i
            JOIN invoice_products_v2 p ON i.cufe = p.cufe
            GROUP BY i.cufe, i.proveedor_nombre, i.numero_factura
            ORDER BY total_productos DESC
            LIMIT 10
        """)
        
        result = conn.execute(query)
        rows = result.fetchall()
        
        for i, row in enumerate(rows, 1):
            cufe = row[0]
            proveedor = row[1] or 'Sin proveedor'
            numero = row[2] or 'Sin número'
            total = row[3]
            
            cufe_short = cufe[:16] + '...' if len(cufe) > 16 else cufe
            print(f"{i:2d}. {cufe_short} | {proveedor[:30]:30s} | {numero[:15]:15s} | {total:3d} productos")
        print()
        
        # 4. Últimos productos extraídos
        print("🆕 ÚLTIMOS 10 PRODUCTOS EXTRAÍDOS")
        print("-" * 80)
        
        query = text("""
            SELECT 
                codigo_producto,
                descripcion,
                cantidad,
                unidad_medida,
                precio_unitario
            FROM invoice_products_v2
            ORDER BY id DESC
            LIMIT 10
        """)
        
        result = conn.execute(query)
        rows = result.fetchall()
        
        for i, row in enumerate(rows, 1):
            codigo = row[0] or 'Sin código'
            descripcion = row[1] or 'Sin descripción'
            cantidad = row[2] or 0
            unidad = row[3] or 'NIU'
            precio = row[4] or 0
            
            if len(descripcion) > 40:
                descripcion = descripcion[:40] + '...'
            
            print(f"{i:2d}. {codigo[:15]:15s} | {descripcion:42s} | {cantidad:8.2f} {unidad:4s} | ${precio:,.0f}")
        print()
        
        # 5. Estadísticas de campos
        print("📈 ESTADÍSTICAS DE CAMPOS")
        print("-" * 80)
        
        queries = {
            'con código': "SELECT COUNT(*) FROM invoice_products_v2 WHERE codigo_producto IS NOT NULL AND codigo_producto != ''",
            'con descripción': "SELECT COUNT(*) FROM invoice_products_v2 WHERE descripcion IS NOT NULL AND descripcion != ''",
            'con precio': "SELECT COUNT(*) FROM invoice_products_v2 WHERE precio_unitario IS NOT NULL",
            'con cantidad': "SELECT COUNT(*) FROM invoice_products_v2 WHERE cantidad IS NOT NULL",
            'con IVA': "SELECT COUNT(*) FROM invoice_products_v2 WHERE iva_porcentaje IS NOT NULL",
            'con total': "SELECT COUNT(*) FROM invoice_products_v2 WHERE total_item IS NOT NULL",
        }
        
        for label, query_str in queries.items():
            result = conn.execute(text(query_str))
            count = result.scalar()
            percentage = (count / total_productos * 100) if total_productos > 0 else 0
            print(f"Productos {label:20s}: {count:5d} / {total_productos} ({percentage:.1f}%)")
        print()
        
        # 6. Trazabilidad
        print("🔍 TRAZABILIDAD DE PRODUCTOS")
        print("-" * 80)
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE variacion_tipo IS NOT NULL"))
        productos_con_trazabilidad = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE variacion_tipo = 'primera_compra'"))
        productos_primera_compra = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE variacion_tipo = 'subio'"))
        productos_subio = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE variacion_tipo = 'bajo'"))
        productos_bajo = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE variacion_tipo = 'igual'"))
        productos_igual = result.scalar()
        
        percentage = (productos_con_trazabilidad / total_productos * 100) if total_productos > 0 else 0
        print(f"Productos con trazabilidad: {productos_con_trazabilidad:5d} / {total_productos} ({percentage:.1f}%)")
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
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE codigo_producto IS NOT NULL AND codigo_producto != ''"))
        productos_con_codigo = result.scalar()
        if productos_con_codigo / total_productos < 0.8:
            print("⚠️  Muchos productos sin código. Revisar parser de productos.")
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2 WHERE precio_unitario IS NOT NULL"))
        productos_con_precio = result.scalar()
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
    
    print("=" * 80)
    print("✅ Diagnóstico completado")
    print("=" * 80)

if __name__ == '__main__':
    main()
