#!/usr/bin/env python3
"""
Reprocesa facturas con CUFE temporal usando la extracción mejorada
"""
import sys
import os
import tempfile
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.pdf_parser_service import PDFParserService
from app.services.s3_service import S3Service

print("="*80)
print("🔄 REPROCESANDO FACTURAS CON CUFE TEMPORAL")
print("="*80)

db = SessionLocal()
parser = PDFParserService()
s3_service = S3Service()

try:
    # Obtener todas las facturas con CUFE temporal
    facturas_temp = db.query(InvoiceV2).filter(
        InvoiceV2.cufe.like('TEMP_%')
    ).order_by(InvoiceV2.created_at.desc()).all()
    
    if not facturas_temp:
        print("\n✅ No hay facturas con CUFE temporal")
        sys.exit(0)
    
    print(f"\n📊 Encontradas {len(facturas_temp)} facturas con CUFE temporal")
    print("   Reprocesando con extracción mejorada...\n")
    
    exitosos = 0
    fallidos = 0
    
    for i, factura in enumerate(facturas_temp, 1):
        print(f"\n{'='*80}")
        print(f"📄 FACTURA {i}/{len(facturas_temp)}")
        print(f"{'='*80}")
        print(f"CUFE Temporal: {factura.cufe[:40]}...")
        print(f"Proveedor: {factura.proveedor_nombre or 'N/A'}")
        
        if not factura.archivo_proveedor_s3_key:
            print("❌ No hay archivo en S3, saltando...")
            fallidos += 1
            continue
        
        try:
            # Descargar PDF desde S3
            url = s3_service.generate_presigned_url(factura.archivo_proveedor_s3_key, expiration=300)
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Error descargando PDF: HTTP {response.status_code}")
                fallidos += 1
                continue
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            # Extraer texto
            text = parser.extract_text_from_pdf(tmp_path, max_pages=5)
            
            if not text:
                print("❌ No se pudo extraer texto del PDF")
                fallidos += 1
                os.unlink(tmp_path)
                continue
            
            # Intentar extraer CUFE con el método mejorado
            cufe = parser.extract_cufe(text)
            
            if cufe:
                print(f"✅ ¡CUFE EXTRAÍDO!")
                print(f"   {cufe}")
                
                # Verificar si ya existe una factura con este CUFE
                existing = db.query(InvoiceV2).filter(InvoiceV2.cufe == cufe).first()
                
                if existing and existing.cufe != factura.cufe:
                    print(f"⚠️ Ya existe una factura con este CUFE")
                    print(f"   Eliminando factura duplicada...")
                    
                    # Eliminar archivo de S3 si existe
                    if factura.archivo_proveedor_s3_key:
                        try:
                            s3_service.delete_file(factura.archivo_proveedor_s3_key)
                            print(f"   ✅ Archivo eliminado de S3")
                        except:
                            pass
                    
                    # Eliminar factura duplicada
                    db.delete(factura)
                    db.commit()
                    print(f"   ✅ Factura duplicada eliminada")
                    exitosos += 1
                else:
                    # Actualizar en la base de datos
                    factura.cufe = cufe
                    db.commit()
                    
                    print(f"✅ Factura actualizada en la base de datos")
                    exitosos += 1
            else:
                print(f"❌ No se pudo extraer CUFE con el método mejorado")
                fallidos += 1
            
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"❌ Error procesando factura: {e}")
            fallidos += 1
            # Rollback en caso de error
            db.rollback()
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*80}")
    print(f"\n   Total procesadas: {len(facturas_temp)}")
    print(f"   ✅ Exitosas: {exitosos}")
    print(f"   ❌ Fallidas: {fallidos}")
    print(f"   📈 Tasa de éxito: {(exitosos/len(facturas_temp)*100):.1f}%")
    
    if exitosos > 0:
        print(f"\n✅ Se extrajeron {exitosos} CUFEs correctamente")
        print(f"   Las facturas ahora tienen CUFE real en lugar de temporal")
    
    if fallidos > 0:
        print(f"\n⚠️ {fallidos} facturas aún tienen CUFE temporal")
        print(f"   Estas requieren asociación manual usando el botón '🔗 Asociar CUFE'")
    
finally:
    db.close()

print(f"\n{'='*80}")
print("✅ REPROCESAMIENTO COMPLETADO")
print(f"{'='*80}\n")
