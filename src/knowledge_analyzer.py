import spacy
import logging
from typing import List, Dict, Set

# Configurar logger
logger = logging.getLogger(__name__)

# --- Palabras Clave y Heurísticas por Dimensión del Conocimiento ---

# (Estas listas son iniciales y pueden necesitar refinamiento)

# 1. Conocimiento Factual
FACTUAL_KEYWORDS: Set[str] = {
    "hecho", "dato", "término", "detalle", "nombre", "fecha", "definición", "lista",
    "terminología", "vocabulario", "elemento", "componente", "parte", "ejemplo",
    "identificar", "nombrar", "listar", "definir", "describir (hechos)" # Verbos clave
}
# Heurística adicional: Buscar sustantivos propios (PERSON, ORG, LOC), números.

# 2. Conocimiento Conceptual
CONCEPTUAL_KEYWORDS: Set[str] = {
    "concepto", "principio", "teoría", "modelo", "estructura", "clasificación",
    "categoría", "relación", "idea", "ley", "marco", "tipo", "forma", "función",
    "propiedad", "característica", "abstracción", "generalización", "patrón",
    "comparar", "clasificar", "explicar", "interpretar", "resumir", "inferir", # Verbos clave
    "diferenciar", "relacionar", "categorizar"
}
# Heurística adicional: Buscar sustantivos abstractos, conectores lógicos (porque, entonces, si...).

# 3. Conocimiento Procedimental
PROCEDURAL_KEYWORDS: Set[str] = {
    "procedimiento", "técnica", "método", "metodología", "habilidad", "paso",
    "proceso", "aplicación", "uso", "cómo", "algoritmo", "protocolo", "rutina",
    "estrategia (para hacer algo)", "destreza", "operación",
    "aplicar", "usar", "implementar", "ejecutar", "construir", "calcular", # Verbos clave
    "demostrar", "operar", "producir", "resolver (problemas)", "desarrollar (algo)"
}
# Heurística adicional: Buscar gerundios (aplicando, usando), verbos de acción sobre objetos.

# 4. Conocimiento Metacognitivo
METACOGNITIVE_KEYWORDS: Set[str] = {
    "reflexionar", "autorregular", "monitorear", "evaluar", "planificar",
    "estrategia (cognitiva/aprendizaje)", "conciencia", "aprendizaje", "pensamiento",
    "conocimiento (propio)", "comprensión (propia)", "meta", "objetivo (personal)",
    "autoevaluación", "autocorrección", "metacognición",
    "propio", "mi", "su (aprendizaje/pensamiento)" # Adjetivos/Pronombres clave
}
# Heurística adicional: Buscar preguntas reflexivas implícitas, referencias al estudiante como agente de su aprendizaje.

# Mapeo de puntajes
SCORE_MAP = {"Bajo": 1, "Medio": 2, "Alto": 3}
SCORE_MAP_REV = {v: k for k, v in SCORE_MAP.items()} # Para notas

# --- Función Principal ---

def check_knowledge_dimension(text: str, nlp_model: spacy.language.Language) -> dict:
    """
    Estima la presencia y nivel de cada dimensión del conocimiento en un RA.

    Args:
        text: El texto del Resultado de Aprendizaje.
        nlp_model: El modelo de lenguaje spaCy cargado.

    Returns:
        Un diccionario con puntajes estimados (1-3) para cada dimensión y notas.
    """
    logger.info(f"--- Iniciando check_knowledge_dimension para: '{text}' ---")
    results = {
        'factual_score': 1, 'conceptual_score': 1,
        'procedural_score': 1, 'metacognitive_score': 1,
        'knowledge_notes': []
    }
    if not text or not isinstance(text, str):
        logger.warning("Texto de entrada inválido o vacío.")
        results['knowledge_notes'].append('Texto inválido.')
        return results
    if not nlp_model:
         logger.error("Modelo NLP no disponible para check_knowledge_dimension.")
         results['knowledge_notes'].append('Modelo NLP no disponible.')
         return results

    try:
        doc = nlp_model(text.lower())
        lemmas = {token.lemma_ for token in doc}
        tokens = [token for token in doc]

        # --- Contadores y Flags para Nivel Alto ---
        factual_hits = 0
        conceptual_hits = 0
        procedural_hits = 0
        metacognitive_hits = 0
        has_proper_nouns = any(ent.label_ in ["PER", "ORG", "LOC", "MISC"] for ent in doc.ents)
        has_numbers = any(token.like_num for token in tokens)
        has_abstract_nouns = any(token.pos_ == "NOUN" and not token.is_stop and token.lemma_ in CONCEPTUAL_KEYWORDS for token in tokens)
        has_action_verbs = any(token.pos_ == "VERB" and token.lemma_ in PROCEDURAL_KEYWORDS for token in tokens)
        has_self_reference = any(token.lemma_ in ["propio", "mi", "su"] for token in tokens)

        # --- Evaluación por Dimensión ---

        # 1. Factual
        factual_found = lemmas.intersection(FACTUAL_KEYWORDS)
        if factual_found:
            results['factual_score'] = 2
            factual_hits = len(factual_found)
            results['knowledge_notes'].append(f"Factual(Medio): Keywords={list(factual_found)}.")
            # Criterios para Alto
            if factual_hits >= 2 or (factual_hits >= 1 and (has_proper_nouns or has_numbers)):
                 results['factual_score'] = 3
                 results['knowledge_notes'][-1] = f"Factual(Alto): Keywords={list(factual_found)}, Especificidad alta."

        # 2. Conceptual
        conceptual_found = lemmas.intersection(CONCEPTUAL_KEYWORDS)
        if conceptual_found:
            results['conceptual_score'] = 2
            conceptual_hits = len(conceptual_found)
            results['knowledge_notes'].append(f"Conceptual(Medio): Keywords={list(conceptual_found)}.")
             # Criterios para Alto
            if conceptual_hits >= 2 or (conceptual_hits >= 1 and has_abstract_nouns):
                 results['conceptual_score'] = 3
                 results['knowledge_notes'][-1] = f"Conceptual(Alto): Keywords={list(conceptual_found)}, Abstracción/Estructura alta."

        # 3. Procedimental
        procedural_found = lemmas.intersection(PROCEDURAL_KEYWORDS)
        # También considerar verbos de acción no listados si tienen objeto directo claro
        main_verb = next((tok for tok in tokens if tok.dep_ == "ROOT" and tok.pos_ == "VERB"), None)
        if not main_verb: main_verb = next((tok for tok in tokens if tok.pos_ == "VERB"), None)

        has_clear_object = False
        if main_verb:
            if any(child.dep_ in ["dobj", "obj", "obl", "xcomp"] for child in main_verb.children):
                has_clear_object = True

        if procedural_found or (has_action_verbs and has_clear_object):
            results['procedural_score'] = 2
            procedural_hits = len(procedural_found)
            found_list = list(procedural_found) + ([main_verb.lemma_] if has_action_verbs and main_verb and main_verb.lemma_ not in procedural_found else [])
            results['knowledge_notes'].append(f"Procedural(Medio): Keywords/Verbos={found_list}.")
             # Criterios para Alto
            if procedural_hits >= 2 or (procedural_hits >= 1 and has_action_verbs and has_clear_object):
                 results['procedural_score'] = 3
                 results['knowledge_notes'][-1] = f"Procedural(Alto): Keywords/Verbos={found_list}, Proceso claro."

        # 4. Metacognitivo
        metacognitive_found = lemmas.intersection(METACOGNITIVE_KEYWORDS)
        if metacognitive_found:
            results['metacognitive_score'] = 2
            metacognitive_hits = len(metacognitive_found)
            results['knowledge_notes'].append(f"Metacognitivo(Medio): Keywords={list(metacognitive_found)}.")
             # Criterios para Alto
            if metacognitive_hits >= 2 or (metacognitive_hits >= 1 and has_self_reference):
                 results['metacognitive_score'] = 3
                 results['knowledge_notes'][-1] = f"Metacognitivo(Alto): Keywords={list(metacognitive_found)}, Auto-referencia/reflexión clara."

        # Unir notas
        results['knowledge_notes'] = " ".join(results['knowledge_notes']) if results['knowledge_notes'] else "No se encontraron indicadores claros para ninguna dimensión."

        logger.info(f"--- Resultado final check_knowledge_dimension: F={results['factual_score']}, C={results['conceptual_score']}, P={results['procedural_score']}, M={results['metacognitive_score']} ---")
        return results

    except Exception as e:
        logger.error(f"Error en check_knowledge_dimension para texto '{text[:50]}...': {e}", exc_info=True)
        results['knowledge_notes'] = f'Error durante el análisis: {e}'
        return results

# --- Ejemplo de uso (opcional, para pruebas) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        nlp = spacy.load("es_core_news_sm")
        test_ras = [
            "Identificar las capitales de Europa.", # Esperado: F=3, C=1, P=1, M=1
            "Definir el concepto de fotosíntesis.", # Esperado: F=2, C=3, P=1, M=1
            "Explicar la teoría de la relatividad general.", # Esperado: F=1, C=3, P=1, M=1
            "Aplicar el método de integración por partes para resolver integrales.", # Esperado: F=1, C=2, P=3, M=1
            "Diseñar un procedimiento experimental para medir la densidad de un líquido.", # Esperado: F=1, C=2, P=3, M=1
            "Evaluar la efectividad de diferentes estrategias de estudio personales.", # Esperado: F=1, C=1, P=2, M=3
            "Reflexionar sobre el propio proceso de aprendizaje al resolver problemas complejos.", # Esperado: F=1, C=1, P=1, M=3
            "Clasificar los animales según su tipo de alimentación.", # Esperado: F=2, C=3, P=1, M=1
            "Utilizar software estadístico para analizar datos de encuestas.", # Esperado: F=1, C=1, P=3, M=1
            "Memorizar la lista de verbos irregulares en inglés.", # Esperado: F=3, C=1, P=1, M=1
        ]
        for ra in test_ras:
            result = check_knowledge_dimension(ra, nlp)
            print(f"RA: {ra}")
            print(f"Resultado: {result}\n")
    except OSError:
        print("Error: Modelo spaCy 'es_core_news_sm' no encontrado.")
        print("Por favor, instálalo ejecutando: python -m spacy download es_core_news_sm")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        