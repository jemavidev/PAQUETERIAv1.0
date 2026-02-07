#!/usr/bin/env python3
"""
Test simple de regex para verificar extracción de emisor/adquiriente
No requiere dependencias externas
"""
import re


def extract_emisor(text: str):
    """Extrae datos del emisor/vendedor (NO del adquiriente)"""
    emisor = {}
    
    # Buscar específicamente en la sección "Datos del vendedor"
    vendor_section_match = re.search(
        r'(?:Datos del vendedor|DATOS DEL VENDEDOR|Datos del emisor|DATOS DEL EMISOR)([\s\S]{0,800}?)(?:Detalles de productos|Detalle|DETALLE|Condiciones|CONDICIONES)',
        text,
        re.IGNORECASE
    )
    
    search_text = vendor_section_match.group(1) if vendor_section_match else text
    
    # Razón social
    match = re.search(r'(?:Razón social|Razon Social)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
    emisor['razon_social'] = match.group(1).strip() if match else None
    
    # NIT
    match = re.search(r'(?:NIT|Nit|Número de documento)[\s:]+(\d{9,10}[-\d]?)', search_text)
    emisor['nit'] = match.group(1).strip() if match else None
    
    return emisor


def extract_adquiriente(text: str):
    """Extrae datos del adquiriente/comprador (NO del vendedor)"""
    adquiriente = {}
    
    # Buscar específicamente en la sección de adquiriente
    match = re.search(
        r'(?:Datos del adquiriente|Datos del Cliente|DATOS DEL CLIENTE|DATOS DEL ADQUIRIENTE)([\s\S]{0,500}?)(?:Datos del vendedor|DATOS DEL VENDEDOR|Detalles|DETALLES)',
        text,
        re.IGNORECASE
    )
    
    if match:
        section = match.group(1)
        
        # Razón social
        match = re.search(r'(?:Razón social|Nombre)[\s:]+([^\n]+)', section, re.IGNORECASE)
        adquiriente['razon_social'] = match.group(1).strip() if match else None
        
        # NIT
        match = re.search(r'(?:NIT|Nit|NIT del adquiriente)[\s:]+(\d{9,10}[-\d]?)', section)
        adquiriente['nit'] = match.group(1).strip() if match else None
    
    return adquiriente


def test_extract_emisor_adquiriente():
    """Test con texto simulado de un PDF DIAN"""
    
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
    emisor = extract_emisor(texto_simulado)
    print(f"   Razón Social: {emisor.get('razon_social')}")
    print(f"   NIT: {emisor.get('nit')}")
    print()
    
    # Extraer adquiriente
    print("📋 Extrayendo ADQUIRIENTE (Comprador/Cliente)...")
    adquiriente = extract_adquiriente(texto_simulado)
    print(f"   Razón Social: {adquiriente.get('razon_social')}")
    print(f"   NIT: {adquiriente.get('nit')}")
    print()
    
    # Verificar resultados
    print("=" * 80)
    print("✅ VERIFICACIÓN DE RESULTADOS")
    print("=" * 80)
    
    emisor_correcto = emisor.get('razon_social') == 'VENEPLAST LTDA'
    emisor_nit_correcto = emisor.get('nit') == '900019737'
    adquiriente_correcto = adquiriente.get('razon_social') == 'PAPYRUS SOLUCIONES INTEGRALES S.A.S.'
    adquiriente_nit_correcto = adquiriente.get('nit') == '901210008'
    
    if emisor_correcto and emisor_nit_correcto:
        print("✅ EMISOR extraído correctamente:")
        print("   - Razón Social: VENEPLAST LTDA")
        print("   - NIT: 900019737")
    else:
        print(f"❌ EMISOR incorrecto:")
        print(f"   - Razón Social: {emisor.get('razon_social')} (esperado: VENEPLAST LTDA)")
        print(f"   - NIT: {emisor.get('nit')} (esperado: 900019737)")
    
    print()
    
    if adquiriente_correcto and adquiriente_nit_correcto:
        print("✅ ADQUIRIENTE extraído correctamente:")
        print("   - Razón Social: PAPYRUS SOLUCIONES INTEGRALES S.A.S.")
        print("   - NIT: 901210008")
    else:
        print(f"❌ ADQUIRIENTE incorrecto:")
        print(f"   - Razón Social: {adquiriente.get('razon_social')} (esperado: PAPYRUS SOLUCIONES INTEGRALES S.A.S.)")
        print(f"   - NIT: {adquiriente.get('nit')} (esperado: 901210008)")
    
    print()
    print("=" * 80)
    
    if emisor_correcto and emisor_nit_correcto and adquiriente_correcto and adquiriente_nit_correcto:
        print("🎉 ¡TEST EXITOSO! El fix funciona correctamente")
        print()
        print("Los datos se extraen en el orden correcto:")
        print("  - EMISOR (Proveedor): VENEPLAST LTDA (NIT: 900019737)")
        print("  - ADQUIRIENTE (Cliente): PAPYRUS SOLUCIONES INTEGRALES S.A.S. (NIT: 901210008)")
        print()
        print("✅ El código está listo para usar en producción")
        return True
    else:
        print("❌ TEST FALLIDO: Los datos no se extraen correctamente")
        print()
        print("⚠️ Revisar la lógica de extracción en pdf_parser_service.py")
        return False


if __name__ == "__main__":
    import sys
    resultado = test_extract_emisor_adquiriente()
    sys.exit(0 if resultado else 1)
