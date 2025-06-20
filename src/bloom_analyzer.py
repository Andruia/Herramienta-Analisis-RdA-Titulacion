import json
import os
import logging
import unicodedata # Importación necesaria para normalización Unicode
import streamlit as st # Necesario para el decorador @st.cache_resource (aunque esté comentado)

# --- Asumiendo que nlp_utils contiene load_spacy_model y clean_text ---
# --- y que find_main_verb está definida aquí o importada ---
try:
    # Asume que load_spacy_model ahora también está cacheada (o usa la versión no cacheada si prefieres)
    from src.nlp_utils import load_spacy_model, clean_text, find_main_verb
except ImportError:
    #logging.error("No se pudo importar desde src.nlp_utils.", exc_info=True)
    # Define funciones dummy para evitar errores posteriores
    def load_spacy_model(): return None
    def clean_text(text): return text
    def find_main_verb(doc): return None
# --------------------------------------------------------------------

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes y Configuración ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_PATH = os.path.join(os.path.dirname(CURRENT_DIR), 'data', 'bloom_taxonomy.json')

# --- REGLAS DE ADECUACIÓN (EJEMPLO - ¡AJUSTAR!) ---
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
# ----------------------------------------------------

# --- Funciones de Carga de Taxonomía (Simplificadas) ---

def load_bloom_taxonomy(taxonomy_file=TAXONOMY_PATH):
    """
    Carga la taxonomía desde JSON y devuelve ÚNICAMENTE el mapa verbo -> nivel.
    Realiza normalización robusta de claves y valores.
    """
    verb_to_level_map = {}
    logging.info(f"load_bloom_taxonomy: Iniciando carga y construcción de verb_map desde: {taxonomy_file}")

    try:
        with open(taxonomy_file, 'r', encoding='utf-8') as f:
            # Cargar asegurando que se manejen correctamente caracteres unicode
            taxonomy_data = json.load(f)
        logging.info(f"load_bloom_taxonomy: JSON cargado, {len(taxonomy_data)} niveles encontrados.")

        total_verbs_added = 0
        # Construir el mapa verbo -> nivel
        for level, verbs in taxonomy_data.items():
            # Normalizar nombre del nivel (valor en el mapa)
            level_norm = unicodedata.normalize('NFKC', level).lower().strip()
            #logging.debug(f"load_bloom_taxonomy: ---> Procesando nivel '{level_norm}'")
            count_added_for_level = 0
            for verb in verbs:
                # Normalización robusta del verbo (clave en el mapa)
                verb_norm = unicodedata.normalize('NFKC', verb).lower().strip()
                if not verb_norm: continue # Ignorar verbos vacíos

                if verb_norm not in verb_to_level_map:
                    verb_to_level_map[verb_norm] = level_norm
                    #logging.debug(f"      Añadiendo: {repr(verb_norm)} -> {repr(level_norm)}")
                    count_added_for_level += 1
                else:
                    # Advertir si un verbo se redefine (podría indicar error en JSON)
                    #logging.warning(f"      Verbo duplicado '{verb_norm}' encontrado en nivel '{level_norm}'. Mapeo anterior a '{verb_to_level_map[verb_norm]}' será sobrescrito si los niveles son diferentes, o ignorado si son iguales.")
                    # Opcionalmente, podrías decidir no sobrescribir:
                    # if verb_norm not in verb_to_level_map: verb_to_level_map[verb_norm] = level_norm

            #logging.debug(f"      Nivel '{level_norm}' procesado. {count_added_for_level} nuevos añadidos.")
                    total_verbs_added += count_added_for_level

        logging.info(f"load_bloom_taxonomy: Construcción completa. Tamaño final verb_map: {len(verb_to_level_map)}. Total añadidos: {total_verbs_added}")

    except FileNotFoundError:
        #logging.error(f"Error Crítico: No se encontró el archivo de taxonomía en '{taxonomy_file}'")
        st.error(f"Error: No se encontró el archivo de taxonomía: {taxonomy_file}")
        verb_to_level_map = {} # Devuelve vacío en error
    except json.JSONDecodeError as e:
        #logging.error(f"Error Crítico: El archivo de taxonomía '{taxonomy_file}' no es un JSON válido. Error: {e}")
        st.error(f"Error: El archivo de taxonomía '{taxonomy_file}' contiene errores de formato JSON.")
        verb_to_level_map = {}
    except Exception as e:
        #logging.error(f"Error inesperado al cargar/construir taxonomía: {e}", exc_info=True)
        st.error(f"Error inesperado al procesar la taxonomía.")
        verb_to_level_map = {}

    # Devolver SOLO el mapa construido
    return verb_to_level_map

# --- Wrapper para Carga (Caché Desactivada Temporalmente) ---
@st.cache_resource # <--- Sigue comentado temporalmente
def cached_load_bloom_taxonomy():
    """Wrapper para cargar la taxonomía. CACHE DESACTIVADA TEMPORALMENTE."""
    # Llama directamente a la función que ahora solo devuelve el mapa
    the_map = load_bloom_taxonomy()
    logging.info(f"cached_load_bloom_taxonomy: Mapa recibido de load_bloom_taxonomy. Tamaño: {len(the_map) if isinstance(the_map, dict) else 'Invalido'}")
    return the_map # Devuelve solo el mapa
# ---------------------------------------------

# --- Función Principal de Análisis de Bloom ---

def analyze_bloom_level(text):
    """
    Analiza un texto (objetivo de aprendizaje) para determinar su nivel de Bloom
    basándose en el verbo principal identificado.
    """
    # 1. Cargar recursos necesarios
    nlp = load_spacy_model() # Asume que esta función está cacheada o es eficiente
    verb_map = cached_load_bloom_taxonomy() # Obtiene el mapa (sin caché por ahora)

    # --- Verificación del mapa y NLP ---
    if not isinstance(verb_map, dict) or not verb_map:
        #logging.error("analyze_bloom_level: verb_map NO es un diccionario válido o está vacío.")
        # No mostrar error de Streamlit aquí, devolver estado de error
        return {"verb": None, "level": "Error", "error": "Fallo carga taxonomía"}

    if not nlp:
        #logging.error("analyze_bloom_level: Fallo en carga de modelo NLP.")
        return {"verb": None, "level": "Error", "error": "Fallo carga NLP"}
    # ------------------------------------
    #logging.debug(f"analyze_bloom_level: Recursos cargados OK (Mapa tamaño: {len(verb_map)}).")

    # 2. Preprocesar texto
    cleaned_objective = clean_text(text)
    if not cleaned_objective:
        #logging.warning(f"Texto vacío o inválido recibido: '{text}'")
        return {"verb": None, "level": "N/A", "error": "Texto vacío o inválido"}

    # 3. Procesar con spaCy
    doc = nlp(cleaned_objective)

    # 4. Encontrar verbo principal (lema)
    main_verb = find_main_verb(doc) # Asume que devuelve el lema normalizado o None
    logging.info(f"Texto procesado: '{cleaned_objective}'. Verbo encontrado: {repr(main_verb)}")

    if not main_verb:
         #logging.warning(f"No se encontró verbo principal en: '{cleaned_objective}'")
         return {"verb": None, "level": "No identificado", "error": "No se encontró verbo principal"}

    # Normalización robusta del verbo a buscar (ya debería venir normalizado de find_main_verb si se implementó bien, pero aseguramos)
    verb_to_search = unicodedata.normalize('NFKC', main_verb).lower().strip()
    logging.info(f"analyze_bloom_level: Intentando buscar verbo normalizado: {repr(verb_to_search)}")
    
    
    # --- BLOQUE DE DEPURACIÓN INTENSIVA ---
# -----------------------------------------

    # 5. Buscar verbo en la taxonomía
    bloom_level = verb_map.get(verb_to_search) # Busca el lema normalizado

    if bloom_level:
        # Nivel encontrado, devolver capitalizado para presentación
        logging.info(f"analyze_bloom_level: Verbo {repr(verb_to_search)} ENCONTRADO. Nivel: {repr(bloom_level)}")
        return {"verb": main_verb, "level": bloom_level.capitalize(), "error": None}
    else:
        # Nivel no encontrado para este verbo
        #logging.warning(f"analyze_bloom_level: Verbo {repr(verb_to_search)} NO encontrado en verb_map (Tamaño actual: {len(verb_map)}).")
        # Descomentar para depuración si es necesario:
        # logging.debug(f"   Primeras 15 claves del mapa usado: {list(verb_map.keys())[:15]}")
        return {"verb": main_verb, "level": "No clasificado", "error": f"Verbo '{main_verb}' no encontrado en la taxonomía"}

# --- Función de Evaluación de Adecuación ---

def check_appropriateness(bloom_level, academic_level_str):
    """
    Evalúa si un nivel de Bloom es apropiado, bajo o alto para un
    nivel académico dado, según las reglas definidas.
    """
    if not bloom_level or bloom_level in ["N/A", "Error", "No identificado", "No clasificado"]:
        return "N/A"

    # Normalizar nivel de Bloom para búsqueda en reglas (minúsculas)
    # Asegurarse de que bloom_level sea string antes de lower()
    bloom_level_norm = str(bloom_level).lower()

    if academic_level_str not in APPROPRIATENESS_RULES:
        #logging.warning(f"Nivel académico '{academic_level_str}' no encontrado en APPROPRIATENESS_RULES.")
        return "Nivel Académico Desconocido"

    rules_for_level = APPROPRIATENESS_RULES[academic_level_str]

    if bloom_level_norm in rules_for_level.get('bajo', []):
        return "Potencialmente Bajo"
    elif bloom_level_norm in rules_for_level.get('apropiado', []):
        return "Apropiado"
    elif bloom_level_norm in rules_for_level.get('alto', []):
        return "Potencialmente Alto"
    else:
        #logging.warning(f"Nivel Bloom '{bloom_level_norm}' (original: '{bloom_level}') no categorizado en reglas para nivel '{academic_level_str}'.")
        return "No Categorizado en Reglas"

# --- Bloque para Pruebas (Opcional) ---
if __name__ == '__main__':
    # Este bloque solo se ejecuta si corres el script directamente
    print("-" * 50)
    print("PRUEBAS DEL SISTEMA EXPANDIDO DE ANÁLISIS BLOOM")
    print("-" * 50)

    # Ejemplos de prueba para diferentes niveles
    test_cases = [
        {
            'text': 'El estudiante será capaz de recordar los principios básicos de auditoría',
            'level': 2,
            'description': 'Nivel 2 - Auditoría - Recordar'
        },
        {
            'text': 'El estudiante podrá analizar estados financieros y detectar irregularidades',
            'level': 4,
            'description': 'Nivel 4 - Auditoría - Analizar'
        },
        {
            'text': 'El estudiante diseñará estrategias de reclutamiento y selección de personal',
            'level': 6,
            'description': 'Nivel 6 - RRHH - Crear/Diseñar'
        },
        {
            'text': 'El estudiante evaluará críticamente políticas de gestión del talento humano',
            'level': 8,
            'description': 'Nivel 8 - RRHH - Evaluar'
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- CASO {i}: {case['description']} ---")
        print(f"Texto: {case['text']}")
        print(f"Nivel académico: {case['level']}")

        # Análisis completo con contexto
        result = analyze_bloom_with_context(case['text'], case['level'])

        print(f"Nivel Bloom detectado: {result['bloom_level']}")
        print(f"Área profesional: {result['professional_area'] or 'No detectada'}")
        print(f"Apropiación básica: {result['basic_appropriateness']}")
        print(f"Apropiación contextual: {result['contextual_appropriateness']}")

        if result['recommendations']:
            print("Recomendaciones:")
            for rec in result['recommendations']:
                print(f"  • {rec}")

    print("-" * 50)
    print("MATRIZ DE APROPIACIÓN POR NIVELES")
    print("-" * 50)

    bloom_levels = ['recordar', 'comprender', 'aplicar', 'analizar', 'evaluar', 'crear']
    academic_levels = ['2', '4', '6', '8']

    print(f"{'Bloom/Nivel':<12}", end="")
    for level in academic_levels:
        print(f"{level:>15}", end="")
    print()

    for bloom in bloom_levels:
        print(f"{bloom:<12}", end="")
        for academic in academic_levels:
            appropriateness = check_appropriateness(bloom, int(academic))
            symbol = "✓" if appropriateness == "Apropiado" else "⚠" if "Bajo" in appropriateness else "⬆" if "Alto" in appropriateness else "?"
            print(f"{symbol:>15}", end="")
        print()

    print("\nLeyenda: ✓=Apropiado, ⚠=Potencialmente Bajo, ⬆=Potencialmente Alto")
    print("-" * 50)