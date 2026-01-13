#!/usr/bin/env python3
"""
Test para verificar la lógica de validación de IVA
"""

# Caso 1: IVA NO incluido
# Factura muestra: Subtotal $1,000,000 + IVA $190,000 = Total $1,190,000
# Items: 1 producto × $1,000,000 = $1,000,000, IVA 19% = $190,000

print("=" * 60)
print("CASO 1: IVA NO INCLUIDO")
print("=" * 60)

# Datos del item
precio_unitario = 1000000
cantidad = 1
iva_porcentaje = 19
iva_valor = 190000
valor_total = 1000000  # Sin IVA (después del fix)

# Datos de la factura
subtotal = 1000000
total_iva = 190000
total_neto = 1190000

# Validación
items_total = valor_total
items_iva = iva_valor

print(f"Item: precio={precio_unitario:,}, cantidad={cantidad}, IVA={iva_porcentaje}%")
print(f"Item: iva_valor={iva_valor:,}, valor_total={valor_total:,}")
print(f"Factura: subtotal={subtotal:,}, total_iva={total_iva:,}, total_neto={total_neto:,}")
print()

# Detectar IVA incluido
iva_esperado = int(precio_unitario * cantidad * iva_porcentaje / 100)
print(f"IVA esperado (NO incluido): {iva_esperado:,}")
print(f"IVA reportado: {iva_valor:,}")
print(f"Diferencia: {abs(iva_esperado - iva_valor):,}")

if abs(iva_esperado - iva_valor) < 10:
    iva_incluido = False
    print("✓ Detectado: IVA NO incluido")
else:
    iva_incluido = True
    print("✗ Detectado: IVA incluido (ERROR)")

print()

# Validación de totales (IVA NO incluido)
print("Validación:")
diff_subtotal = abs(items_total - subtotal)
print(f"  items_total ({items_total:,}) vs subtotal ({subtotal:,}): diff={diff_subtotal:,}")
if diff_subtotal <= 100:
    print("  ✓ Subtotal coincide")
else:
    print(f"  ✗ Subtotal NO coincide (diff: ${diff_subtotal:,})")

expected_total = items_total + items_iva
diff_total = abs(expected_total - total_neto)
print(f"  items_total + IVA ({expected_total:,}) vs total_neto ({total_neto:,}): diff={diff_total:,}")
if diff_total <= 100:
    print("  ✓ Total coincide")
else:
    print(f"  ✗ Total NO coincide (diff: ${diff_total:,})")

print()
print()

# Caso 2: IVA INCLUIDO
# Factura muestra: Total $1,190,000 (incluye IVA $190,000), Subtotal $1,000,000
# Items: 1 producto × $1,190,000 = $1,190,000, IVA 19% = $190,000

print("=" * 60)
print("CASO 2: IVA INCLUIDO")
print("=" * 60)

# Datos del item
precio_unitario = 1190000  # Incluye IVA
cantidad = 1
iva_porcentaje = 19
precio_base = int(precio_unitario / (1 + iva_porcentaje / 100))
iva_valor = int(precio_base * cantidad * iva_porcentaje / 100)
valor_total = 1190000  # Con IVA

# Datos de la factura
subtotal = 1000000
total_iva = 190000
total_neto = 1190000

# Validación
items_total = valor_total
items_iva = iva_valor

print(f"Item: precio={precio_unitario:,}, cantidad={cantidad}, IVA={iva_porcentaje}%")
print(f"Item: precio_base={precio_base:,}, iva_valor={iva_valor:,}, valor_total={valor_total:,}")
print(f"Factura: subtotal={subtotal:,}, total_iva={total_iva:,}, total_neto={total_neto:,}")
print()

# Detectar IVA incluido
iva_esperado_no_incluido = int(precio_unitario * cantidad * iva_porcentaje / 100)
iva_esperado_incluido = int(precio_base * cantidad * iva_porcentaje / 100)

print(f"IVA esperado (NO incluido): {iva_esperado_no_incluido:,}")
print(f"IVA esperado (incluido): {iva_esperado_incluido:,}")
print(f"IVA reportado: {iva_valor:,}")

if abs(iva_esperado_no_incluido - iva_valor) < 10:
    iva_incluido = False
    print("✗ Detectado: IVA NO incluido (ERROR)")
elif abs(iva_esperado_incluido - iva_valor) < 10:
    iva_incluido = True
    print("✓ Detectado: IVA incluido")
else:
    iva_incluido = None
    print("? No se pudo determinar")

print()

# Validación de totales (IVA incluido)
print("Validación:")
diff_total = abs(items_total - total_neto)
print(f"  items_total ({items_total:,}) vs total_neto ({total_neto:,}): diff={diff_total:,}")
if diff_total <= 100:
    print("  ✓ Total coincide")
else:
    print(f"  ✗ Total NO coincide (diff: ${diff_total:,})")

expected_subtotal = items_total - items_iva
diff_subtotal = abs(expected_subtotal - subtotal)
print(f"  items_total - IVA ({expected_subtotal:,}) vs subtotal ({subtotal:,}): diff={diff_subtotal:,}")
if diff_subtotal <= 100:
    print("  ✓ Subtotal coincide")
else:
    print(f"  ✗ Subtotal NO coincide (diff: ${diff_subtotal:,})")

print()
print("=" * 60)
print("FIN DE PRUEBAS")
print("=" * 60)
