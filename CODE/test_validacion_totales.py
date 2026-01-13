#!/usr/bin/env python3
"""
Test de validación de totales de facturas
Simula la factura del usuario para verificar que la lógica funciona
"""

# Simular un item de la factura
class MockItem:
    def __init__(self, valor_total, iva_valor, iva_porcentaje):
        self.valor_total = valor_total
        self.iva_valor = iva_valor
        self.iva_porcentaje = iva_porcentaje

# Función de detección mejorada
def detect_iva_incluido(item):
    """Detecta si el IVA está incluido en el precio del item"""
    if item.iva_porcentaje == 0:
        return None
    
    if item.iva_valor > 0 and item.valor_total > 0:
        # Método 1: IVA NO incluido
        iva_esperado_no_incluido = int(item.valor_total * item.iva_porcentaje / 100)
        diff_no_incluido = abs(iva_esperado_no_incluido - item.iva_valor)
        tolerancia = max(50, int(item.iva_valor * 0.05))
        
        if diff_no_incluido <= tolerancia:
            return False
        
        # Método 2: IVA incluido
        base_si_incluido = item.valor_total / (1 + item.iva_porcentaje / 100)
        iva_esperado_incluido = int(base_si_incluido * item.iva_porcentaje / 100)
        diff_incluido = abs(iva_esperado_incluido - item.iva_valor)
        
        if diff_incluido <= tolerancia:
            return True
        
        # Método 3: Comparar diferencias
        if diff_no_incluido < diff_incluido:
            return False
        elif diff_incluido < diff_no_incluido:
            return True
    
    return None

# Test con datos de la factura real
print("=" * 60)
print("TEST DE VALIDACIÓN DE TOTALES")
print("=" * 60)
print()

# Datos de la factura del usuario
subtotal_factura = 909472
descuento_factura = 10895
total_bruto_factura = 909472
iva_factura = 112578
total_neto_factura = 1011155

# Simular algunos items (ejemplos de la imagen)
items = [
    MockItem(valor_total=25256, iva_valor=4799, iva_porcentaje=19),  # Item 42
    MockItem(valor_total=30450, iva_valor=0, iva_porcentaje=0),      # Item 43 (sin IVA)
    MockItem(valor_total=12017, iva_valor=2283, iva_porcentaje=19),  # Item 44
    MockItem(valor_total=7815, iva_valor=1485, iva_porcentaje=19),   # Item 45
    MockItem(valor_total=12804, iva_valor=0, iva_porcentaje=0),      # Item 46 (sin IVA)
    MockItem(valor_total=3781, iva_valor=719, iva_porcentaje=19),    # Item 47
]

print("📊 Datos de la factura:")
print(f"  Subtotal: ${subtotal_factura:,}")
print(f"  Descuento: ${descuento_factura:,}")
print(f"  Total Bruto: ${total_bruto_factura:,}")
print(f"  IVA: ${iva_factura:,}")
print(f"  TOTAL NETO: ${total_neto_factura:,}")
print()

print("🔍 Analizando items:")
items_con_iva_incluido = 0
items_sin_iva_incluido = 0

for i, item in enumerate(items, 1):
    resultado = detect_iva_incluido(item)
    items_con_iva_incluido += 1 if resultado == True else 0
    items_sin_iva_incluido += 1 if resultado == False else 0
    
    status = "✓ IVA NO incluido" if resultado == False else ("✗ IVA incluido" if resultado == True else "? Indeterminado")
    print(f"  Item {i}: Total=${item.valor_total:,}, IVA=${item.iva_valor:,} ({item.iva_porcentaje}%) → {status}")

print()
print(f"📈 Resumen de detección:")
print(f"  Items con IVA incluido: {items_con_iva_incluido}")
print(f"  Items sin IVA incluido: {items_sin_iva_incluido}")
print()

# Determinar tipo de factura
iva_incluido_en_items = items_con_iva_incluido > items_sin_iva_incluido
print(f"🎯 Tipo de factura detectado: {'IVA INCLUIDO' if iva_incluido_en_items else 'IVA NO INCLUIDO'}")
print()

# Calcular totales
items_subtotal = sum(item.valor_total for item in items)
items_iva = sum(item.iva_valor for item in items)

print("💰 Cálculos:")
print(f"  Suma de items: ${items_subtotal:,}")
print(f"  Suma de IVA: ${items_iva:,}")
print()

if iva_incluido_en_items:
    expected_total = items_subtotal
    print(f"  Total esperado (IVA incluido): ${expected_total:,}")
else:
    expected_total = items_subtotal + items_iva
    print(f"  Total esperado (items + IVA): ${expected_total:,}")

print(f"  Total neto factura: ${total_neto_factura:,}")
print()

# Validar
diff_total = abs(expected_total - total_neto_factura)
print("✅ VALIDACIÓN:")
print(f"  Diferencia: ${diff_total:,}")

if diff_total <= 100:
    print("  ✓ CORRECTO - Los totales coinciden")
elif abs(diff_total - items_iva) <= 100:
    print("  ⚠ ADVERTENCIA - La diferencia es exactamente el IVA")
    print("    Esto sugiere que la detección de IVA incluido/no incluido puede estar incorrecta")
else:
    print("  ✗ ERROR - Los totales NO coinciden")

print()
print("=" * 60)
