#!/usr/bin/env python3
"""
Verificación completa de todos los archivos CUFE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from app.services.pdf_parser_service import PDFParserService
from pathlib import Path

def verificar_todos_cufe():
    """Verifica la extracción de todos los archivos CUFE"""
    
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    if not cufe_dir.exists():
        print(f"✗ Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = sorted(list(cufe_dir.glob("*.pdf")))
    
    print(f"\n{'='*80}")
    print(f"Verificación Completa de Archivos CUFE")
    print(f"{'='*80}\n")
    print(f"Total de archivos: {len(pdf_files)}\n")
    
    resultados = {
        'exitosos': 0,
        'con_productos': 0,
        'sin_productos': 0,
        'errores': 0,
        'total_productos': 0
    }
    
    for i, pdf_file in enumerate(pdf_files, 1):
        nombre_corto = pdf_file.name[:40] + "..." if len(pdf_file.name) > 40 else pdf_file.name
        
        try:
            result = PDFParserService.parse_dian_document(str(pdf_file))
            
            if result:
                resultados['exitosos'] += 1
                productos = result.get('productos', [])
                
                if productos:
                    resultados['con_productos'] += 1
                    resultados['total_productos'] += len(productos)
                    
                    # Verificar que las descripciones no estén vacías
                    descripciones_vacias = sum(1 for p in productos if not p.get('descripcion', '').strip())
                    
                    status = "✓"
                    if descripciones_vacias > 0:
                        status = f"⚠ ({descripciones_vacias} sin desc)"
                    
                    print(f"{i:2d}. {status} {nombre_corto:45s} | {len(productos):3d} productos")
                else:
                    resultados['sin_productos'] += 1
                    print(f"{i:2d}. ⚠ {nombre_corto:45s} | Sin productos")
            else:
                resultados['errores'] += 1
                print(f"{i:2d}. ✗ {nombre_corto:45s} | Error al parsear")
                
        except Exception as e:
            resultados['errores'] += 1
            print(f"{i:2d}. ✗ {nombre_corto:45s} | Error: {str(e)[:30]}")
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"Resumen de Verificación")
    print(f"{'='*80}\n")
    print(f"  Archivos procesados exitosamente: {resultados['exitosos']}/{len(pdf_files)}")
    print(f"  Archivos con productos extraídos: {resultados['con_productos']}")
    print(f"  Archivos sin productos:           {resultados['sin_productos']}")
    print(f"  Archivos con errores:             {resultados['errores']}")
    print(f"  Total de productos extraídos:     {resultados['total_productos']}")
    
    if resultados['con_productos'] > 0:
        promedio = resultados['total_productos'] / resultados['con_productos']
        print(f"  Promedio de productos por archivo: {promedio:.1f}")
    
    print(f"\n{'='*80}")
    
    # Calcular tasa de éxito
    if len(pdf_files) > 0:
        tasa_exito = (resultados['con_productos'] / len(pdf_files)) * 100
        print(f"\n✓ Tasa de éxito: {tasa_exito:.1f}%")
        
        if tasa_exito >= 90:
            print("✓ Excelente! La extracción funciona correctamente")
        elif tasa_exito >= 70:
            print("⚠ Bueno, pero hay margen de mejora")
        else:
            print("✗ Necesita revisión")

if __name__ == "__main__":
    verificar_todos_cufe()
