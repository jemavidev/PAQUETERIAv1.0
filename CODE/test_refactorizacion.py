#!/usr/bin/env python3
"""
Script de prueba rápida para verificar la refactorización
"""

import sys
sys.path.insert(0, 'src')

def test_imports():
    """Verifica que todos los imports funcionen"""
    print("🔍 Verificando imports...")
    
    try:
        from app.services.enhanced_pdf_extractor import EnhancedPDFExtractor, FieldExtraction, EnhancedInvoiceData
        print("  ✅ EnhancedPDFExtractor importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando EnhancedPDFExtractor: {e}")
        return False
    
    try:
        from app.services.supplier_invoice_service import SupplierInvoiceService
        print("  ✅ SupplierInvoiceService importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando SupplierInvoiceService: {e}")
        return False
    
    try:
        from app.models.invoice import SupplierInvoice
        print("  ✅ SupplierInvoice model importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando SupplierInvoice: {e}")
        return False
    
    return True


def test_extractor():
    """Prueba básica del extractor mejorado"""
    print("\n🧪 Probando extractor mejorado...")
    
    try:
        from app.services.enhanced_pdf_extractor import EnhancedPDFExtractor
        
        extractor = EnhancedPDFExtractor()
        print("  ✅ Extractor instanciado correctamente")
        
        # Verificar que tiene los patrones de proveedores
        assert 'EXITO' in extractor.PROVIDER_PATTERNS
        assert 'MAKRO' in extractor.PROVIDER_PATTERNS
        assert 'COLANTA' in extractor.PROVIDER_PATTERNS
        print("  ✅ Patrones de proveedores configurados")
        
        # Verificar métodos
        assert hasattr(extractor, 'extract_from_pdf')
        assert hasattr(extractor, '_extract_supplier_name')
        assert hasattr(extractor, '_extract_nit')
        assert hasattr(extractor, '_extract_invoice_number')
        assert hasattr(extractor, '_extract_date')
        assert hasattr(extractor, '_extract_total')
        assert hasattr(extractor, '_extract_cufe')
        print("  ✅ Todos los métodos de extracción presentes")
        
        return True
    except Exception as e:
        print(f"  ❌ Error probando extractor: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model():
    """Verifica que el modelo tenga el campo extraction_quality"""
    print("\n📊 Verificando modelo...")
    
    try:
        from app.models.invoice import SupplierInvoice
        from sqlalchemy import inspect
        
        # Verificar que el campo existe en el modelo
        mapper = inspect(SupplierInvoice)
        columns = [col.key for col in mapper.columns]
        
        if 'extraction_quality' in columns:
            print("  ✅ Campo extraction_quality presente en modelo")
        else:
            print("  ⚠️  Campo extraction_quality NO presente en modelo")
            print("     Ejecuta: cd CODE && alembic upgrade head")
        
        return True
    except Exception as e:
        print(f"  ❌ Error verificando modelo: {e}")
        return False


def test_service():
    """Verifica que el servicio tenga el extractor mejorado"""
    print("\n⚙️  Verificando servicio...")
    
    try:
        from app.services.supplier_invoice_service import SupplierInvoiceService
        from app.database import SessionLocal
        
        db = SessionLocal()
        service = SupplierInvoiceService(db)
        
        # Verificar que tiene el extractor mejorado
        assert hasattr(service, 'enhanced_extractor')
        print("  ✅ Servicio tiene enhanced_extractor")
        
        # Verificar que el método process_uploaded_file tiene el parámetro use_enhanced
        import inspect
        sig = inspect.signature(service.process_uploaded_file)
        params = list(sig.parameters.keys())
        
        if 'use_enhanced' in params:
            print("  ✅ Método process_uploaded_file tiene parámetro use_enhanced")
        else:
            print("  ⚠️  Método process_uploaded_file NO tiene parámetro use_enhanced")
        
        db.close()
        return True
    except Exception as e:
        print(f"  ❌ Error verificando servicio: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 70)
    print("🚀 VERIFICACIÓN DE REFACTORIZACIÓN")
    print("=" * 70)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Extractor", test_extractor()))
    results.append(("Modelo", test_model()))
    results.append(("Servicio", test_service()))
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:20} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("=" * 70)
        print("\n✅ La refactorización está lista para usar")
        print("\nPróximos pasos:")
        print("  1. Ejecutar migración: cd CODE && alembic upgrade head")
        print("  2. Reiniciar servidor: docker-compose restart")
        print("  3. Probar en: https://staging.jemavi.co/invoices")
        return 0
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("=" * 70)
        print("\n⚠️  Revisa los errores arriba y corrige antes de usar")
        return 1


if __name__ == "__main__":
    sys.exit(main())
