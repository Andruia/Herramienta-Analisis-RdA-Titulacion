# Prueba simple del sistema expandido
import json
import os

# Configuración básica
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Reglas de apropiación expandidas
APPROPRIATENESS_RULES = {
    '2': {
        'bajo': [],
        'apropiado': ['recordar', 'comprender'],
        'alto': ['aplicar', 'analizar', 'evaluar', 'crear']
    },
    '4': {
        'bajo': ['recordar'],
        'apropiado': ['comprender', 'aplicar', 'analizar'],
        'alto': ['evaluar', 'crear']
    },
    '6': {
        'bajo': ['recordar','comprender'],
        'apropiado': ['aplicar', 'analizar'],
        'alto': ['evaluar', 'crear']
    },
    '8': {
        'bajo': ['recordar', 'comprender'],
        'apropiado': ['aplicar', 'analizar', 'evaluar', 'crear'],
        'alto': []
    }
}

def check_appropriateness_simple(bloom_level, academic_level):
    """Versión simplificada de verificación de apropiación"""
    academic_level_str = str(academic_level)
    bloom_level_norm = str(bloom_level).lower()
    
    if academic_level_str not in APPROPRIATENESS_RULES:
        return "Nivel Académico Desconocido"
    
    rules_for_level = APPROPRIATENESS_RULES[academic_level_str]
    
    if bloom_level_norm in rules_for_level.get('bajo', []):
        return "Potencialmente Bajo"
    elif bloom_level_norm in rules_for_level.get('apropiado', []):
        return "Apropiado"
    elif bloom_level_norm in rules_for_level.get('alto', []):
        return "Potencialmente Alto"
    else:
        return "No Categorizado"

def main():
    print("-" * 50)
    print("PRUEBA DEL SISTEMA EXPANDIDO - NIVELES 2 Y 4")
    print("-" * 50)
    
    # Casos de prueba
    test_cases = [
        {'bloom': 'recordar', 'level': 2, 'expected': 'Apropiado'},
        {'bloom': 'crear', 'level': 2, 'expected': 'Potencialmente Alto'},
        {'bloom': 'recordar', 'level': 4, 'expected': 'Potencialmente Bajo'},
        {'bloom': 'analizar', 'level': 4, 'expected': 'Apropiado'},
        {'bloom': 'evaluar', 'level': 4, 'expected': 'Potencialmente Alto'},
        {'bloom': 'aplicar', 'level': 6, 'expected': 'Apropiado'},
        {'bloom': 'crear', 'level': 8, 'expected': 'Apropiado'},
        {'bloom': 'recordar', 'level': 8, 'expected': 'Potencialmente Bajo'},
    ]
    
    print(f"{'Bloom':<12} {'Nivel':<6} {'Resultado':<20} {'Esperado':<20} {'✓/✗'}")
    print("-" * 70)
    
    for case in test_cases:
        result = check_appropriateness_simple(case['bloom'], case['level'])
        match = "✓" if result == case['expected'] else "✗"
        print(f"{case['bloom']:<12} {case['level']:<6} {result:<20} {case['expected']:<20} {match}")
    
    print("\n" + "-" * 50)
    print("MATRIZ DE APROPIACIÓN COMPLETA")
    print("-" * 50)
    
    bloom_levels = ['recordar', 'comprender', 'aplicar', 'analizar', 'evaluar', 'crear']
    academic_levels = ['2', '4', '6', '8']
    
    print(f"{'Bloom/Nivel':<12}", end="")
    for level in academic_levels:
        print(f"{'Nivel ' + level:>15}", end="")
    print()
    print("-" * 72)
    
    for bloom in bloom_levels:
        print(f"{bloom:<12}", end="")
        for academic in academic_levels:
            appropriateness = check_appropriateness_simple(bloom, int(academic))
            if appropriateness == "Apropiado":
                symbol = "✓"
            elif "Bajo" in appropriateness:
                symbol = "⚠"
            elif "Alto" in appropriateness:
                symbol = "⬆"
            else:
                symbol = "?"
            print(f"{symbol:>15}", end="")
        print()
    
    print("\nLeyenda:")
    print("✓ = Apropiado para el nivel")
    print("⚠ = Potencialmente demasiado básico")
    print("⬆ = Potencialmente demasiado avanzado")
    print("? = No categorizado")
    
    print("\n" + "-" * 50)
    print("ANÁLISIS DE PROGRESIÓN PEDAGÓGICA")
    print("-" * 50)
    
    progression_analysis = {
        '2': "Enfoque en construcción de bases conceptuales (recordar, comprender)",
        '4': "Desarrollo de aplicación y análisis (comprender, aplicar, analizar)",
        '6': "Integración y síntesis equilibrada (recordar a aplicar como base)",
        '8': "Dominio profesional avanzado (aplicar a crear como foco principal)"
    }
    
    for level, description in progression_analysis.items():
        print(f"Nivel {level}: {description}")
    
    print("-" * 50)

if __name__ == '__main__':
    main()