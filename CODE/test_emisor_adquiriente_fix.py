#!/usr/bin/env python3
"""
Test rápido para verificar que el fix de emisor/adquiriente funciona correctamente
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.app.services.pdf_parser_service import PDFParserService


def test_extract_emisor_adquiriente():
    """
    Test con texto simulado de un PDF DIAN
    """
    # Texto simulado de un PDF DIAN (estructura real)
    texto_simulado = """
    DOCUMENTO EQUIVALENTE POS
    
    Código único de Documento
    ff5fcd60a8d39c4e29456d71bb2118344e099cb592a959f7a4ffe2e1e533ea03406b744ad08365da07e28f180d080635
    
    Número de documento: GRMZ36891
    Fecha y hora de expedición: 2025-09-01 11:30:36-05:00
    
    Datos del adquiriente
    Razón social: PAPYRUS SOLUCIONES INTEGRALES S.A.S.
    NIT del adquiriente: 901210008
    Tipo de contribuyente: Persona Juridica
    
    Datos del vendedor
    Razón social: VENEPLAST LTDA
    Tipo de documento: NIT
    Número de documento: 900019737
    Tipo de contribuyente: Persona Juridica
    Régimen fiscal: R-99-PN
    Responsabilidad tributaria: IVA
    
    Detalles de productos
    Nro. Código Descripción U/M Cantidad
    1 7102212397176 TERMO 20000W NIU / número 1.00
    """
    
    print("=" * 80)
    print("🧪 TEST: Extracción de Emisor y Adquiriente")
    print("=" * 80)
    print()
    
    # Extraer emisor
    print("📋 Extrayendo EMISOR (Vendedor/Proveedor)...")
    emisor = PDFParserService._extract_emisor(texto_simulado)
    print(f"   Razón Social: {emisor.get('razon_social')}")
    print(f"   NIT: {emisor.get('nit')}")
    print()
    
    # Extraer adquiriente
    print("📋 Extrayendo ADQUIRIENTE (Comprador/Cliente)...")
    adquiriente = PDFParserService._extract_adquiriente(texto_simulado)
    print(f"   Razón Social: {adquiriente.get('razon_social')}")
    print(f"   NIT: {adquiriente.get('nit')}")
    print()
    
    # Verificar resultados
    print("=" * 80)
    print("✅ VERIFICACIÓN DE RESULTADOS")
    print("=" * 80)
    
    emisor_correcto = emisor.get('razon_social') == 'VENEPLAST LTDA'
    adquiriente_correcto = adquiriente.get('razon_social') == 'PAPYRUS SOLUCIONES INTEGRALES S.A.S.'
    
    if emisor_correcto:
        print("✅ EMISOR extraído correctamente: VENEPLAST LTDA")
    else:
        print(f"❌ EMISOR incorrecto: {emisor.get('razon_social')}")
        print("   Esperado: VENEPLAST LTDA")
    
    if adquiriente_correcto:
        print("✅ ADQUIRIENTE extraído correctamente: PAPYRUS SOLUCIONES INTEGRALES S.A.S.")
    else:
        print(f"❌ ADQUIRIENTE incorrecto: {adquiriente.get('razon_social')}")
        print("   Esperado: PAPYRUS SOLUCIONES INTEGRALES S.A.S.")
    
    print()
    
    if emisor_correcto and adquiriente_correcto:
        print("🎉 ¡TEST EXITOSO! El fix funciona correctamente")
        print()
        print("Los datos se extraen en el orden correcto:")
        print("  - EMISOR (Proveedor): VENEPLAST LTDA")
        print("  - ADQUIRIENTE (Cliente): PAPYRUS SOLUCIONES INTEGRALES S.A.S.")
        return True
    else:
        print("❌ TEST FALLIDO: Los datos no se extraen correctamente")
        return False


if __name__ == "__main__":
    resultado = test_extract_emisor_adquiriente()
    sys.exit(0 if resultado else 1)
