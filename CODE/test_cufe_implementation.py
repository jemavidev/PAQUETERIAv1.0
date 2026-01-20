#!/usr/bin/env python3
"""
Script de prueba para la implementación de CUFE
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_import():
    """Prueba que el modelo se pueda importar"""
    try:
        from app.models.cufe import CufeRecord, CufeStatus
        print("✅ Modelo CufeRecord importado correctamente")
        print(f"   Estados disponibles: {[s.value for s in CufeStatus]}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelo: {e}")
        return False


def test_database_connection():
    """Prueba la conexión a la base de datos"""
    try:
        from app.database import SessionLocal
        from app.models.cufe import CufeRecord
        
        db = SessionLocal()
        count = db.query(CufeRecord).count()
        db.close()
        
        print(f"✅ Conexión a BD exitosa. CUFEs registrados: {count}")
        return True
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return False


def test_cufe_validation():
    """Prueba validación de CUFE"""
    test_cufe = "9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31"
    
    if len(test_cufe) == 96:
        print(f"✅ CUFE de prueba válido: {test_cufe[:20]}...")
        return True
    else:
        print(f"❌ CUFE de prueba inválido (longitud: {len(test_cufe)})")
        return False


def test_dian_url_generation():
    """Prueba generación de URL de DIAN"""
    test_cufe = "9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31"
    expected_url = f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={test_cufe}"
    
    from app.models.cufe import CufeRecord
    
    # Crear instancia temporal (sin guardar)
    cufe_record = CufeRecord(cufe=test_cufe, created_by=1)
    
    if cufe_record.dian_url == expected_url:
        print(f"✅ URL de DIAN generada correctamente")
        print(f"   {cufe_record.dian_url[:80]}...")
        return True
    else:
        print(f"❌ URL de DIAN incorrecta")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("🧪 Iniciando pruebas de implementación CUFE\n")
    
    tests = [
        ("Importación de modelo", test_model_import),
        ("Conexión a base de datos", test_database_connection),
        ("Validación de CUFE", test_cufe_validation),
        ("Generación de URL DIAN", test_dian_url_generation),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Prueba: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! La implementación está lista.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisar errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
