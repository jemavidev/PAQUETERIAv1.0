#!/usr/bin/env python3
"""
Test suite para las nuevas capacidades de extracción de CUFE
Valida los 5 patrones de nombres de archivo identificados en FACTURAS/
"""
import sys
sys.path.insert(0, './CODE/src')

from app.services.pdf_parser_service import PDFParserService

def test_cufe_format_validation():
    """Test validación de formato CUFE"""
    print("\n✅ TEST 1: Validación de formato CUFE")
    print("=" * 60)

    # CUFE válido (96 caracteres hex)
    valid_cufe = "a" * 96
    assert PDFParserService.validate_cufe_format(valid_cufe) == True
    print(f"✓ CUFE válido (96 chars): {valid_cufe[:20]}... PASS")

    # CUDE válido (variable longitud)
    valid_cude = "ad00454539650892500016306"  # 26 caracteres
    assert PDFParserService.validate_cufe_format(valid_cude) == True
    print(f"✓ CUDE válido ({len(valid_cude)} chars): {valid_cude} PASS")

    # Inválido (muy corto)
    assert PDFParserService.validate_cufe_format("abc123") == False
    print("✓ Código inválido (muy corto): PASS")

    # Nulo
    assert PDFParserService.validate_cufe_format(None) == False
    print("✓ Validación de None: PASS")

    print("\n✅ Todos los tests de validación pasaron\n")


def test_filename_extraction():
    """Test extracción de CUFE del nombre de archivo"""
    print("\n✅ TEST 2: Extracción de CUFE del nombre de archivo")
    print("=" * 60)

    valid_cufe = "a" * 96

    # Patrón 1: Prefijo "f-"
    filename = f"f-{valid_cufe}_20250101120000.pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result == valid_cufe
    print(f"✓ Patrón 'f-' prefix: {filename[:30]}... PASS")

    # Patrón 2: Estándar directo
    filename = f"{valid_cufe}_20250101120000.pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result == valid_cufe
    print(f"✓ Patrón estándar: {filename[:30]}... PASS")

    # Patrón 3: Con duplicado (1)
    filename = f"{valid_cufe} (1).pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result == valid_cufe
    print(f"✓ Patrón con duplicado (1): {filename[:30]}... PASS")

    # Patrón 4: CUDE corto (variable longitud)
    cude = "ad00454539650892500016306"
    filename = f"{cude}.pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result == cude
    print(f"✓ Patrón CUDE corto: {filename} PASS")

    # Patrón 5: Código específico FV
    filename = "FV09006851640112400000125.pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result is not None
    print(f"✓ Patrón específico (FV): {filename} PASS")

    # Patrón 5: Código específico AD
    filename = "AD09006851640112400000125.pdf"
    result = PDFParserService.extract_cufe_from_filename(filename)
    assert result is not None
    print(f"✓ Patrón específico (AD): {filename} PASS")

    print("\n✅ Todos los tests de extracción de filename pasaron\n")


def test_combined_strategy():
    """Test estrategia combinada (filename + PDF text)"""
    print("\n✅ TEST 3: Estrategia combinada (filename + PDF text)")
    print("=" * 60)

    valid_cufe = "b" * 96
    mock_pdf_text = f"CUFE: {valid_cufe}\nEsta es una factura de prueba"

    # Caso 1: Extraer del filename
    filename = f"{valid_cufe}_20250101.pdf"
    cufe, strategy = PDFParserService.extract_cufe_combined(filename, "")
    assert cufe == valid_cufe and strategy == 'filename'
    print(f"✓ Extracción desde filename: {strategy.upper()} PASS")

    # Caso 2: Fallback a PDF text
    filename = "documento_sin_cufe.pdf"
    cufe, strategy = PDFParserService.extract_cufe_combined(filename, mock_pdf_text)
    assert cufe == valid_cufe and strategy == 'pdf_text'
    print(f"✓ Fallback a PDF text: {strategy.upper()} PASS")

    # Caso 3: Requiere entrada manual
    filename = "documento_incompleto.pdf"
    cufe, strategy = PDFParserService.extract_cufe_combined(filename, "Sin CUFE")
    assert cufe is None and strategy == 'manual_required'
    print(f"✓ Caso manual required: {strategy.upper()} PASS")

    print("\n✅ Todos los tests de estrategia combinada pasaron\n")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("🚀 SUITE DE TESTS: EXTRACCIÓN MEJORADA DE CUFE")
        print("=" * 60)

        test_cufe_format_validation()
        test_filename_extraction()
        test_combined_strategy()

        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
