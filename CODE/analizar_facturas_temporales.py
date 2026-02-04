#!/usr/bin/env python3
"""
Analiza facturas con CUFE temporal para diagnosticar por qué no se extrajo el CUFE
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.pdf_parser_service import PDFParserService
import json

print("="*80)
print("🔍 ANÁLISIS DE FACTURAS CON CUFE TEMPORAL")
print("="*80)

db = SessionLocal()
parser = PDFParserService()

try:
    # Obtener todas las facturas con CUFE temporal
    facturas_temp = db.query(InvoiceV2).filter(
        InvoiceV2.cufe.like('TEMP_%')
    ).order_by(InvoiceV2.created_at.desc()).all()
    
    if not facturas_temp:
        print("\n✅ No hay facturas con CUFE temporal")
        print("   Todas las facturas tienen CUFE real extraído correctamente")
        sys.exit(0)
    
    print(f"\n⚠️ Encontradas {len(facturas_temp)} facturas con CUFE temporal")
    print("\nAnalizando cada una para diagnosticar el problema...\n")
    
    resultados = []
    
    for i, factura in enumerate(facturas_temp, 1):
        print(f"\n{'='*80}")
        print(f"📄 FACTURA {i}/{len(facturas_temp)}")
        print(f"{'='*80}")
        print(f"CUFE Temporal: {factura.cufe[:40]}...")
        print(f"Proveedor: {factura.proveedor_nombre or 'N/A'}")
        print(f"Creada: {factura.created_at}")
        print(f"S3 Key: {factura.archivo_proveedor_s3_key or 'NO HAY ARCHIVO'}")
        
        resultado = {
            'cufe_temp': factura.cufe,
            'proveedor': factura.proveedor_nombre,
            'created_at': str(factura.created_at),
            's3_key': factura.archivo_proveedor_s3_key,
            'diagnostico': {}
        }
        
        # Verificar si hay archivo en S3
        if not factura.archivo_proveedor_s3_key:
            print("\n❌ PROBLEMA: No hay archivo en S3")
            print("   No se puede analizar el PDF porque no se subió")
            resultado['diagnostico']['error'] = 'No hay archivo en S3'
            resultados.append(resultado)
            continue
        
        # Intentar descargar y analizar el PDF desde S3
        print("\n🔍 Analizando contenido del PDF...")
        
        try:
            # Descargar PDF desde S3
            from app.services.s3_service import S3Service
            s3_service = S3Service()
            
            # Generar URL temporal
            url = s3_service.generate_presigned_url(factura.archivo_proveedor_s3_key, expiration=300)
            
            # Descargar contenido
            import requests
            import tempfile
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"❌ Error descargando PDF: HTTP {response.status_code}")
                resultado['diagnostico']['error'] = f'Error descargando: HTTP {response.status_code}'
                resultados.append(resultado)
                continue
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            # Extraer texto
            text = parser.extract_text_from_pdf(tmp_path, max_pages=5)
            
            if not text:
                print("❌ PROBLEMA: No se pudo extraer texto del PDF")
                print("   Posibles causas:")
                print("   - PDF es una imagen escaneada")
                print("   - PDF está protegido o corrupto")
                resultado['diagnostico']['error'] = 'No se pudo extraer texto'
                resultado['diagnostico']['texto_extraido'] = 0
            else:
                print(f"✅ Texto extraído: {len(text)} caracteres")
                resultado['diagnostico']['texto_extraido'] = len(text)
                
                # Mostrar muestra del texto
                print(f"\n📝 Primeros 200 caracteres:")
                print("-" * 80)
                print(text[:200])
                print("...")
                
                # Buscar CUFE
                cufe = parser.extract_cufe(text)
                
                if cufe:
                    print(f"\n✅ ¡CUFE ENCONTRADO!")
                    print(f"   {cufe}")
                    print(f"\n💡 SOLUCIÓN: Este CUFE se puede asociar manualmente")
                    resultado['diagnostico']['cufe_encontrado'] = cufe
                    resultado['diagnostico']['solucion'] = 'Asociar CUFE manualmente'
                else:
                    print(f"\n❌ PROBLEMA: No se encontró patrón de 96 caracteres hex")
                    
                    # Buscar patrones más cortos
                    shorter_matches = re.findall(r'[0-9a-fA-F]{32,}', text, re.IGNORECASE)
                    
                    if shorter_matches:
                        print(f"\n🔍 Patrones hexadecimales encontrados:")
                        resultado['diagnostico']['patrones_hex'] = []
                        for j, match in enumerate(shorter_matches[:5], 1):
                            print(f"   {j}. {match[:60]}... (longitud: {len(match)})")
                            resultado['diagnostico']['patrones_hex'].append({
                                'patron': match[:60],
                                'longitud': len(match)
                            })
                    else:
                        print(f"\n❌ No se encontraron patrones hexadecimales largos")
                        resultado['diagnostico']['patrones_hex'] = []
                    
                    # Buscar palabras clave
                    keywords = ['CUFE', 'CUDE', 'CUDS', 'Código', 'codigo', 'Hash', 'QR']
                    found_keywords = []
                    
                    for keyword in keywords:
                        if keyword.lower() in text.lower():
                            idx = text.lower().find(keyword.lower())
                            context = text[max(0, idx-30):min(len(text), idx+150)]
                            found_keywords.append((keyword, context))
                    
                    if found_keywords:
                        print(f"\n🔍 Palabras clave encontradas:")
                        resultado['diagnostico']['palabras_clave'] = []
                        for keyword, context in found_keywords[:3]:
                            print(f"\n   '{keyword}':")
                            print(f"   ...{context[:100]}...")
                            resultado['diagnostico']['palabras_clave'].append({
                                'keyword': keyword,
                                'contexto': context[:100]
                            })
                    else:
                        print(f"\n❌ No se encontraron palabras clave relacionadas con CUFE")
                        resultado['diagnostico']['palabras_clave'] = []
                    
                    # Análisis de formato
                    print(f"\n📊 Análisis del formato del PDF:")
                    print(f"   - Líneas de texto: {len(text.split(chr(10)))}")
                    print(f"   - Palabras: {len(text.split())}")
                    print(f"   - Caracteres numéricos: {sum(c.isdigit() for c in text)}")
                    print(f"   - Caracteres alfabéticos: {sum(c.isalpha() for c in text)}")
                    
                    resultado['diagnostico']['formato'] = {
                        'lineas': len(text.split('\n')),
                        'palabras': len(text.split()),
                        'numeros': sum(c.isdigit() for c in text),
                        'letras': sum(c.isalpha() for c in text)
                    }
                    
                    # Determinar causa probable
                    if len(shorter_matches) == 0:
                        print(f"\n💡 CAUSA PROBABLE: PDF escaneado o CUFE en imagen")
                        print(f"   SOLUCIÓN: Usar OCR o asociar CUFE manualmente")
                        resultado['diagnostico']['causa_probable'] = 'PDF escaneado o CUFE en imagen'
                    elif any(len(m) > 80 for m in shorter_matches):
                        print(f"\n💡 CAUSA PROBABLE: CUFE dividido o con caracteres especiales")
                        print(f"   SOLUCIÓN: Mejorar regex o asociar CUFE manualmente")
                        resultado['diagnostico']['causa_probable'] = 'CUFE dividido o con caracteres especiales'
                    else:
                        print(f"\n💡 CAUSA PROBABLE: CUFE no está en formato estándar")
                        print(f"   SOLUCIÓN: Revisar PDF manualmente y asociar CUFE")
                        resultado['diagnostico']['causa_probable'] = 'CUFE no está en formato estándar'
            
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"\n❌ Error analizando PDF: {e}")
            import traceback
            traceback.print_exc()
            resultado['diagnostico']['error'] = str(e)
        
        resultados.append(resultado)
    
    # Generar reporte final
    print(f"\n\n{'='*80}")
    print("📊 REPORTE FINAL")
    print(f"{'='*80}")
    
    total = len(facturas_temp)
    con_cufe_encontrado = sum(1 for r in resultados if r['diagnostico'].get('cufe_encontrado'))
    sin_texto = sum(1 for r in resultados if r['diagnostico'].get('texto_extraido') == 0)
    con_patrones = sum(1 for r in resultados if r['diagnostico'].get('patrones_hex'))
    
    print(f"\n📈 Estadísticas:")
    print(f"   Total facturas temporales: {total}")
    print(f"   Con CUFE encontrado (asociable): {con_cufe_encontrado}")
    print(f"   Sin texto extraíble: {sin_texto}")
    print(f"   Con patrones hex (posible CUFE dividido): {con_patrones}")
    
    print(f"\n💡 Recomendaciones:")
    if con_cufe_encontrado > 0:
        print(f"   ✅ {con_cufe_encontrado} facturas tienen CUFE extraíble")
        print(f"      → Usar botón '🔗 Asociar CUFE' para cada una")
    
    if sin_texto > 0:
        print(f"   ⚠️ {sin_texto} facturas son PDFs escaneados")
        print(f"      → Requieren OCR o asociación manual del CUFE")
    
    if con_patrones > 0:
        print(f"   🔧 {con_patrones} facturas tienen patrones hex")
        print(f"      → Revisar si el CUFE está dividido o con formato especial")
    
    # Guardar reporte en JSON
    reporte_path = 'CODE/reporte_facturas_temporales.json'
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': total,
            'estadisticas': {
                'con_cufe_encontrado': con_cufe_encontrado,
                'sin_texto': sin_texto,
                'con_patrones': con_patrones
            },
            'facturas': resultados
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte detallado guardado en: {reporte_path}")
    
finally:
    db.close()

print(f"\n{'='*80}")
print("✅ ANÁLISIS COMPLETADO")
print(f"{'='*80}\n")
