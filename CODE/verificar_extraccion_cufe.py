#!/usr/bin/env python3
"""
Script de diagnóstico para verificar extracción de CUFE
Ejecutar en producción para ver qué está pasando
"""
import sys
import os

# Verificar que pdfplumber esté instalado
try:
    import pdfplumber
    print("✅ pdfplumber está instalado")
    print(f"   Versión: {pdfplumber.__version__}")
except ImportError as e:
    print("❌ pdfplumber NO está instalado")
    print(f"   Error: {e}")
    print("\n💡 Solución: pip install pdfplumber")
    sys.exit(1)

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app.services.pdf_parser_service import PDFParserService
    print("✅ PDFParserService importado correctamente")
except ImportError as e:
    print(f"❌ Error importando PDFParserService: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("DIAGNÓSTICO: Sistema de Extracción de CUFE")
print("="*80)

# Verificar que PDF_LIBRARY_AVAILABLE esté en True
from app.services.pdf_parser_service import PDF_LIBRARY_AVAILABLE
print(f"\nPDF_LIBRARY_AVAILABLE: {PDF_LIBRARY_AVAILABLE}")

if not PDF_LIBRARY_AVAILABLE:
    print("❌ pdfplumber no está disponible en PDFParserService")
    print("   Esto causará que todas las facturas tengan CUFE temporal")
    sys.exit(1)

print("\n✅ Sistema de extracción de CUFE está configurado correctamente")
print("\n💡 Si las facturas siguen teniendo CUFE temporal:")
print("   1. Verifica que los PDFs tengan texto extraíble (no sean imágenes)")
print("   2. Revisa los logs del servidor durante la carga de facturas")
print("   3. Prueba cargar un PDF de ejemplo manualmente")
print("\n📝 Para ver logs detallados, busca en los logs del servidor:")
print("   - '📄 Procesando X páginas del PDF'")
print("   - '🔍 Buscando CUFE en texto de X caracteres'")
print("   - '✅ CUFE válido extraído' o '❌ No se encontró patrón'")
