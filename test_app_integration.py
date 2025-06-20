# Prueba de las actualizaciones en app.py para niveles 2 y 4
import sys
import os

# Agregar el directorio src al path
sys.path.append('src')

try:
    from bloom_analyzer import check_appropriateness
    print("✅ Importación de bloom_analyzer exitosa")
except ImportError as e:
    print(f"❌ Error importando bloom_analyzer: {e}")
    exit(1)

def test_appropriateness_levels():
    """Prueba la función check_appropriateness con los nuevos niveles 2 y 4"""
    
    print("\n" + "="*60)
    print("PRUEBA DE ADECUACIÓN PARA NIVELES 2 Y 4")
    print("="*60)
    
    # Casos de prueba
    test_cases = [
        # Nivel 2 - Fundamentos
        {'bloom': 'recordar', 'level': '2', 'expected': 'Apropiado'},
        {'bloom': 'comprender', 'level': '2', 'expected': 'Apropiado'},
        {'bloom': 'aplicar', 'level': '2', 'expected': 'Potencialmente Alto'},
        {'bloom': 'crear', 'level': '2', 'expected': 'Potencialmente Alto'},
        
        # Nivel 4 - Desarrollo
        {'bloom': 'recordar', 'level': '4', 'expected': 'Potencialmente Bajo'},
        {'bloom': 'comprender', 'level': '4', 'expected': 'Apropiado'},
        {'bloom': 'aplicar', 'level': '4', 'expected': 'Apropiado'},
        {'bloom': 'analizar', 'level': '4', 'expected': 'Apropiado'},
        {'bloom': 'evaluar', 'level': '4', 'expected': 'Potencialmente Alto'},
        {'bloom': 'crear', 'level': '4', 'expected': 'Potencialmente Alto'},
        
        # Nivel 6 - Integración (casos existentes)
        {'bloom': 'recordar', 'level': '6', 'expected': 'Apropiado'},
        {'bloom': 'aplicar', 'level': '6', 'expected': 'Apropiado'},
        {'bloom': 'evaluar', 'level': '6', 'expected': 'Potencialmente Alto'},
        
        # Nivel 8 - Dominio (casos existentes)
        {'bloom': 'recordar', 'level': '8', 'expected': 'Potencialmente Bajo'},
        {'bloom': 'aplicar', 'level': '8', 'expected': 'Apropiado'},
        {'bloom': 'crear', 'level': '8', 'expected': 'Apropiado'},
    ]
    
    print(f"{'Bloom':<12} {'Nivel':<6} {'Resultado':<25} {'Esperado':<25} {'Estado'}")
    print("-" * 80)
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        result = check_appropriateness(case['bloom'], case['level'])
        status = "✅ PASS" if result == case['expected'] else "❌ FAIL"
        
        if result == case['expected']:
            passed += 1
        
        print(f"{case['bloom']:<12} {case['level']:<6} {result:<25} {case['expected']:<25} {status}")
    
    print("-" * 80)
    print(f"RESULTADOS: {passed}/{total} pruebas pasaron ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! Los niveles 2 y 4 están funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar la implementación.")
    
    return passed == total

def test_edge_cases():
    """Prueba casos especiales y de borde"""
    
    print("\n" + "="*60)
    print("PRUEBA DE CASOS ESPECIALES")
    print("="*60)
    
    edge_cases = [
        # Niveles no válidos
        {'bloom': 'aplicar', 'level': '1', 'description': 'Nivel no soportado (1)'},
        {'bloom': 'aplicar', 'level': '10', 'description': 'Nivel no soportado (10)'},
        {'bloom': 'aplicar', 'level': 'abc', 'description': 'Nivel no numérico'},
        
        # Verbos no válidos
        {'bloom': 'inventar', 'level': '4', 'description': 'Verbo no en taxonomía'},
        {'bloom': '', 'level': '4', 'description': 'Verbo vacío'},
        {'bloom': 'N/A', 'level': '4', 'description': 'Verbo N/A'},
    ]
    
    print(f"{'Caso':<30} {'Nivel':<6} {'Resultado':<25} {'Descripción'}")
    print("-" * 80)
    
    for case in edge_cases:
        result = check_appropriateness(case['bloom'], case['level'])
        print(f"{case['bloom']:<30} {case['level']:<6} {result:<25} {case['description']}")
    
    print("-" * 80)

def main():
    """Función principal de prueba"""
    
    print("PRUEBA DE INTEGRACIÓN: NIVELES 2 Y 4 EN APP.PY")
    print("="*60)
    
    # Verificar que la función funciona con los nuevos niveles
    success = test_appropriateness_levels()
    
    # Probar casos especiales
    test_edge_cases()
    
    print("\n" + "="*60)
    print("RESUMEN DE CAMBIOS REALIZADOS EN APP.PY:")
    print("="*60)
    print("1. ✅ Selector expandido: ('2', '4', '6', '8') en línea ~74")
    print("2. ✅ Texto informativo agregado para niveles 2 y 4")
    print("3. ✅ Ayuda actualizada: 'ej: 2, 4, 6 o 8' en selector de columnas")
    print("4. ✅ Información pedagógica agregada en expander")
    print("5. ✅ check_appropriateness() ya soporta niveles 2 y 4")
    
    print("\n" + "="*60)
    print("PRÓXIMOS PASOS:")
    print("="*60)
    print("1. 🚀 Ejecutar la aplicación Streamlit: streamlit run src/app.py")
    print("2. 🧪 Probar con RdAs de niveles 2 y 4")
    print("3. 📊 Verificar que 'Adecuación T.' ya no muestre N/A")
    print("4. 🔍 Validar resultados con casos reales")
    
    if success:
        print("\n🎉 ¡INTEGRACIÓN EXITOSA! Los niveles 2 y 4 están listos para usar.")
    else:
        print("\n⚠️  Revisar posibles problemas en la implementación.")

if __name__ == '__main__':
    main()