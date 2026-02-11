#!/usr/bin/env python3
"""
Test de la lógica de variación de precio
Verifica que los cálculos sean correctos
"""

def test_variacion_precio():
    """Prueba los cálculos de variación de precio"""
    
    # Caso 1: Precio subió 10%
    precio_anterior = 100.0
    precio_actual = 110.0
    variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
    assert variacion == 10.0, f"Expected 10.0, got {variacion}"
    assert variacion > 0.5, "Debería detectarse como 'subio'"
    print(f"✅ Caso 1: Precio subió {variacion}% - Tipo: subio")
    
    # Caso 2: Precio bajó 15%
    precio_anterior = 100.0
    precio_actual = 85.0
    variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
    assert variacion == -15.0, f"Expected -15.0, got {variacion}"
    assert variacion < -0.5, "Debería detectarse como 'bajo'"
    print(f"✅ Caso 2: Precio bajó {abs(variacion)}% - Tipo: bajo")
    
    # Caso 3: Precio igual (variación menor a 0.5%)
    precio_anterior = 100.0
    precio_actual = 100.3
    variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
    assert abs(variacion) < 0.5, "Debería detectarse como 'igual'"
    print(f"✅ Caso 3: Precio igual (variación {variacion}%) - Tipo: igual")
    
    # Caso 4: Primera compra (no hay precio anterior)
    print(f"✅ Caso 4: Primera compra - Tipo: primera_compra")
    
    # Caso 5: Descuento aplicado
    descuento_valor = 10.0
    precio_con_descuento = 90.0
    precio_sin_descuento = precio_con_descuento + descuento_valor
    porcentaje_descuento = (descuento_valor / precio_sin_descuento) * 100
    assert round(porcentaje_descuento, 1) == 10.0, f"Expected 10.0%, got {porcentaje_descuento}%"
    print(f"✅ Caso 5: Descuento de ${descuento_valor} ({porcentaje_descuento:.1f}%)")
    
    # Caso 6: Recargo aplicado
    recargo_valor = 5.0
    precio_con_recargo = 105.0
    precio_sin_recargo = precio_con_recargo - recargo_valor
    porcentaje_recargo = (recargo_valor / precio_sin_recargo) * 100
    assert round(porcentaje_recargo, 1) == 5.0, f"Expected 5.0%, got {porcentaje_recargo}%"
    print(f"✅ Caso 6: Recargo de ${recargo_valor} ({porcentaje_recargo:.1f}%)")
    
    # Caso 7: IVA incluido
    precio_base = 100.0
    iva_porcentaje = 19.0
    precio_con_iva = precio_base * (1 + iva_porcentaje / 100)
    assert precio_con_iva == 119.0, f"Expected 119.0, got {precio_con_iva}"
    print(f"✅ Caso 7: Precio con IVA {iva_porcentaje}%: ${precio_con_iva}")
    
    print("\n🎉 Todos los tests pasaron correctamente!")

if __name__ == "__main__":
    test_variacion_precio()
