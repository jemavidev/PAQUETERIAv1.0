#!/usr/bin/env python3
"""
Script de diagnóstico para verificar que todos los módulos se pueden importar
"""
import sys
import traceback

print("="*80)
print("DIAGNÓSTICO DE INICIO - Sistema de Facturas V2")
print("="*80)
print()

# Lista de módulos a verificar
modules_to_check = [
    ("Modelo InvoiceV2", "src.app.models.invoice_v2", "InvoiceV2"),
    ("Modelo InvoiceProductV2", "src.app.models.invoice_v2", "InvoiceProductV2"),
    ("PDFParserService", "src.app.services.pdf_parser_service", "PDFParserService"),
    ("InvoiceV2Service", "src.app.services.invoice_v2_service", "InvoiceV2Service"),
    ("Rutas API", "src.app.routes.invoices_v2_routes", "router"),
    ("Rutas Web", "src.app.routes.invoices_v2_web_routes", "router"),
]

errors = []
success = []

for name, module_path, class_name in modules_to_check:
    try:
        print(f"Verificando {name}...", end=" ")
        module = __import__(module_path, fromlist=[class_name])
        getattr(module, class_name)
        print("✓ OK")
        success.append(name)
    except Exception as e:
        print(f"✗ ERROR")
        errors.append((name, str(e), traceback.format_exc()))

print()
print("="*80)
print("RESUMEN")
print("="*80)
print(f"✓ Exitosos: {len(success)}/{len(modules_to_check)}")
print(f"✗ Errores: {len(errors)}/{len(modules_to_check)}")
print()

if errors:
    print("DETALLES DE ERRORES:")
    print("="*80)
    for name, error, trace in errors:
        print(f"\n❌ {name}")
        print(f"   Error: {error}")
        print(f"   Traceback:")
        for line in trace.split('\n'):
            if line.strip():
                print(f"   {line}")
    print()
    sys.exit(1)
else:
    print("✅ Todos los módulos se importaron correctamente")
    print()
    sys.exit(0)
