# Importar la función principal de análisis
from .bloom_analyzer import analyze_bloom_level, load_bloom_taxonomy, load_spacy_model

# --- Puedes añadir aquí más objetivos para probar ---
lista_objetivos_prueba = [
    "Identificar las principales teorías administrativas.",
    "Explicar el concepto de punto de equilibrio.",
    "Calcular el VAN y la TIR de un proyecto.",
    "Diferenciar entre liderazgo transaccional y transformacional.",
    "Justificar la selección de una estrategia de mercado específica.",
    "Formular un modelo de negocio canvas para una startup.",
    "Listar los documentos necesarios para exportar.",
    "Nadar en la piscina.", # Verbo no clasificado
    "", # Texto vacío
    123 # Texto inválido
]

def run_analysis():
    """
    Función principal para ejecutar el análisis de la lista de objetivos.
    """
    print("=" * 50)
    print("   INICIO DEL ANÁLISIS DE OBJETIVOS (PROTOTIPO)")
    print("=" * 50)

    # Cargar recursos una vez al inicio
    print("\nCargando recursos...")
    nlp_model_loaded = load_spacy_model() is not None
    taxonomy_loaded = load_bloom_taxonomy()[0] is not None # Carga ambos y verifica el primero

    if not nlp_model_loaded or not taxonomy_loaded:
        print("\nERROR CRÍTICO: No se pudieron cargar los recursos necesarios. Abortando.")
        return # Salir si los recursos no cargan

    print("\nRecursos cargados. Iniciando análisis...")
    print("-" * 50)

    for i, objetivo in enumerate(lista_objetivos_prueba):
        print(f"\n{i+1}. Analizando Objetivo: '{objetivo}'")
        resultado = analyze_bloom_level(str(objetivo)) # Convertir a str por si acaso

        print(f"   - Verbo Identificado: {resultado.get('verb')}")
        print(f"   - Nivel de Bloom:     {resultado.get('level')}")
        if resultado.get('error'):
            print(f"   - Nota/Error:         {resultado.get('error')}")
        print("-" * 30)

    print("\n" + "=" * 50)
    print("   FIN DEL ANÁLISIS")
    print("=" * 50)

# Punto de entrada principal
if __name__ == '__main__':
    run_analysis()