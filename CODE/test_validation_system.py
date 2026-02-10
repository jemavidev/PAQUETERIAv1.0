"""
Test del sistema de validación y corrección manual
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.services.validation_service import ValidationService
from app.models.invoice_v2 import InvoiceV2
from decimal import Decimal
from datetime import datetime, timedelta

def test_validation_service():
    """Prueba el servicio de validación"""
    db = SessionLocal()
    
    try:
        # Obtener una factura de prueba
        invoice = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).first()
        
        if not invoice:
            print("❌ No hay facturas para probar")
            return
        
        print(f"\n📄 Probando validación para factura: {invoice.cufe[:20]}...")
        print(f"   Proveedor: {invoice.proveedor_nombre or 'N/A'}")
        print(f"   Total: ${invoice.dian_total_neto or 'N/A'}")
        
        # Ejecutar validación
        result = ValidationService.validate_invoice(invoice)
        
        print(f"\n✅ Validación ejecutada:")
        print(f"   Fuente: {result.get('source', 'N/A')}")
        print(f"   Score: {result.get('validation_score', 0)}%")
        print(f"   Tiene advertencias: {result.get('has_warnings', False)}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Advertencias encontradas ({len(result['warnings'])}):")
            for warning in result['warnings']:
                severity_icon = ValidationService.get_severity_icon(warning['severity'])
                print(f"   {severity_icon} {warning['field_label']}: {warning['message']}")
                if warning.get('current_value'):
                    print(f"      Valor actual: {warning['current_value']}")
                if warning.get('suggestion'):
                    print(f"      Sugerencia: {warning['suggestion']}")
        else:
            print("\n✅ No se encontraron advertencias")
        
        # Probar con una factura simulada con problemas
        print("\n\n🧪 Probando con factura simulada (con problemas)...")
        test_invoice = InvoiceV2()
        test_invoice.cufe = "test123"
        test_invoice.dian_total_neto = None  # Problema
        test_invoice.dian_subtotal = None  # Problema
        test_invoice.dian_total_iva = None  # Problema
        test_invoice.fecha_emision = datetime.now() + timedelta(days=365)  # Fecha futura
        test_invoice.numero_factura = None  # Problema
        test_invoice.productos = []  # Sin productos
        test_invoice.dian_datos_raw = {'fuente': 'PDF'}
        
        result = ValidationService.validate_invoice(test_invoice)
        
        print(f"\n✅ Validación ejecutada:")
        print(f"   Score: {result.get('validation_score', 0)}%")
        print(f"   Advertencias: {len(result.get('warnings', []))}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Advertencias encontradas:")
            for warning in result['warnings']:
                severity_icon = ValidationService.get_severity_icon(warning['severity'])
                color = ValidationService.get_severity_color(warning['severity'])
                print(f"   {severity_icon} [{color.upper()}] {warning['field_label']}: {warning['message']}")
        
        print("\n✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Sistema de Validación y Corrección Manual")
    print("=" * 60)
    test_validation_service()
