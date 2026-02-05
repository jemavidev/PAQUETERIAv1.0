#!/usr/bin/env python3
"""
Test rápido de la extracción mejorada de CUFE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

# Texto de ejemplo de los PDFs problemáticos
texto_ejemplo = """
TPV : TPV023002
Cajero : GARCIA ENSUCHO KARINA ISABEL
Fecha : 2025/9/2 Hora: 11:12:40
DOCUMENTO ELECTRONICO EQUIVALENTE:
GRM229570
Vendedor : 0103 GALVIS RIVERA ELVIA PATR
Condicion de Pago:CON CONTADO
Cliente : PUBLICO EN GENERAL
NIT: 222222222222
Direccion : CARTAGENA
Telefono : 0
Correo : PUBLICO@PUBLICO.COM
Descripcion Cantidad Precio Valor
BOLSA BASURA NEGRA 30 X 40 CALIBRE 1.00 $1,500 $1,500
1.5 VENEPLAST
BOLSA BASURA NEGRA 40 X 60 CALIBRE 1.00 $2,500 $2,500
1.5 VENEPLAST
BOLSA BASURA NEGRA 50 X 60 CALIBRE 1.00 $3,000 $3,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 60 X 90 CALIBRE 1.00 $5,000 $5,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 70 X 90 CALIBRE 1.00 $6,000 $6,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 80 X 110 CALIBRE 1.00 $8,000 $8,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 90 X 120 CALIBRE 1.00 $10,000 $10,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 100 X 120 CALIBRE 1.00 $12,000 $12,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 110 X 140 CALIBRE 1.00 $15,000 $15,000
1.5 VENEPLAST
BOLSA BASURA NEGRA 120 X 140 CALIBRE 1.00 $18,000 $18,000
1.5 VENEPLAST
Subtotal: $79,000
Descuento: $0
IVA 19%: $15,010
Total: $94,010
Forma de Pago: EFECTIVO
Medio de Pago: EFECTIVO
Moneda: COP
Proveedor Tecnológico: Siesa-Invoicing
NIT: 890.319.193-3
CUFE:ff5fcd60a8d39c4e29456d71bb211834
4e099cb592a959f7a4ffe2e1e533ea03
406b744ad08365da07e28f180d080635
"""

print("="*80)
print("🧪 TEST DE EXTRACCIÓN MEJORADA DE CUFE")
print("="*80)

parser = PDFParserService()

print("\n📝 Texto de ejemplo (fragmento):")
print("-" * 80)
print(texto_ejemplo[texto_ejemplo.find("CUFE:"):texto_ejemplo.find("CUFE:")+150])
print("-" * 80)

print("\n🔍 Extrayendo CUFE...")
cufe = parser.extract_cufe(texto_ejemplo)

if cufe:
    print(f"\n✅ ¡ÉXITO! CUFE extraído:")
    print(f"   {cufe}")
    print(f"\n   Longitud: {len(cufe)} caracteres")
    print(f"   Primeros 20: {cufe[:20]}")
    print(f"   Últimos 20: {cufe[-20:]}")
    
    # Verificar que es el CUFE correcto
    expected = "ff5fcd60a8d39c4e29456d71bb2118344e099cb592a959f7a4ffe2e1e533ea03406b744ad08365da07e28f180d080635"
    if cufe == expected:
        print(f"\n   ✅ CUFE CORRECTO - Coincide con el esperado")
    else:
        print(f"\n   ⚠️ CUFE DIFERENTE al esperado")
        print(f"   Esperado: {expected}")
else:
    print(f"\n❌ FALLO - No se pudo extraer el CUFE")

print("\n" + "="*80)
