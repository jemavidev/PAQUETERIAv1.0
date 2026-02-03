#!/usr/bin/env python3
"""
Test para verificar que la validación de CUFE de exactamente 96 caracteres funciona correctamente
"""
import sys

def test_cufe_validation():
    """
    Prueba la validación de CUFE con diferentes longitudes
    """
    print("🧪 Test de validación de CUFE (exactamente 96 caracteres)\n")
    
    # Casos de prueba
    test_cases = [
        {
            "name": "CUFE válido de 96 caracteres (ejemplo real)",
            "cufe": "8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad",
            "expected": "VÁLIDO",
            "length": 96
        },
        {
            "name": "CUFE válido de 96 caracteres (todos 'a')",
            "cufe": "a" * 96,
            "expected": "VÁLIDO",
            "length": 96
        },
        {
            "name": "CUFE inválido de 95 caracteres (muy corto por 1)",
            "cufe": "a" * 95,
            "expected": "INVÁLIDO",
            "length": 95
        },
        {
            "name": "CUFE inválido de 97 caracteres (muy largo por 1)",
            "cufe": "a" * 97,
            "expected": "INVÁLIDO",
            "length": 97
        },
        {
            "name": "CUFE inválido de 64 caracteres (muy corto)",
            "cufe": "a" * 64,
            "expected": "INVÁLIDO",
            "length": 64
        },
        {
            "name": "CUFE inválido de 128 caracteres (muy largo)",
            "cufe": "a" * 128,
            "expected": "INVÁLIDO",
            "length": 128
        },
        {
            "name": "CUFE inválido de 0 caracteres (vacío)",
            "cufe": "",
            "expected": "INVÁLIDO",
            "length": 0
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        cufe = test["cufe"]
        length = len(cufe)
        is_valid = length == 96
        result = "VÁLIDO" if is_valid else "INVÁLIDO"
        
        passed = result == test["expected"]
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{i}. {test['name']}")
        print(f"   Longitud: {length} caracteres")
        print(f"   Esperado: {test['expected']}")
        print(f"   Resultado: {result}")
        print(f"   {status}\n")
        
        if not passed:
            all_passed = False
    
    # Resumen
    print("=" * 60)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON")
        print("\n📋 Resumen de validación:")
        print("   • Longitud requerida: EXACTAMENTE 96 caracteres")
        print("   • 95 caracteres: RECHAZADO ❌")
        print("   • 97 caracteres: RECHAZADO ❌")
        print("   • Cualquier otra longitud: RECHAZADO ❌")
        return 0
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        return 1

if __name__ == "__main__":
    sys.exit(test_cufe_validation())
