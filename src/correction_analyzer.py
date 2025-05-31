import spacy
import logging
from typing import List, Dict, Set, Optional

# Configurar logger
logger = logging.getLogger(__name__)

# Palabras o frases que indican vaguedad (pueden expandirse)
VAGUE_WORDS: Set[str] = {
    "cosa", "aspecto", "elemento", "tema", "área", "campo",
    "general", "diverso", "varios", "algunos", "ciertos",
    "relevante", "importante", "adecuado", "apropiado"
}

# Preposiciones o inicios de cláusulas que SUELEN indicar nivel/condición/método
LEVEL_INDICATOR_STARTERS: Set[str] = {
    "según", "con", "bajo", "mediante", "utilizando", "considerando",
    "aplicando", "de acuerdo a", "en base a", "a través de", "por medio de",
    "de forma", "de manera", # Seguidos por adjetivo/sustantivo
    "para", "con el fin de", "con el objetivo de" # Indican propósito, a veces implican nivel
}

# Mínima longitud esperada para un RA potencialmente bien formulado (ajustable)
MIN_REASONABLE_LENGTH = 5 # Número de tokens

def find_main_verb_and_object(doc: spacy.tokens.Doc) -> Dict[str, Optional[spacy.tokens.Token]]:
    """
    Intenta encontrar el verbo principal (ROOT) y su objeto directo o complemento principal.
    (Sin cambios respecto a la versión anterior)
    """
    results = {"verb": None, "object": None}
    verb = None
    obj = None
    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            verb = token
            break
    if not verb:
        for token in doc:
            if token.pos_ == "VERB":
                verb = token
                break
    if verb:
        results["verb"] = verb
        for child in verb.children:
            if child.dep_ in ["dobj", "obj"]:
                obj = child
                break
            elif child.dep_ in ["ccomp", "xcomp"]:
                obj_token_in_comp = next((t for t in child.subtree if t.dep_ in ["dobj", "obj"]), None)
                obj = obj_token_in_comp if obj_token_in_comp else child
                break
        if not obj:
             for child in verb.children:
                 if child.dep_ == "obl":
                     obj_token = next((t for t in child.subtree if t.pos_ == "NOUN"), None)
                     obj = obj_token if obj_token else child
                     break
                 elif child.dep_ == "prep":
                     pobj_token = next((t for t in child.children if t.dep_ == "pobj"), None)
                     if pobj_token:
                         obj = pobj_token
                         break
        results["object"] = obj
    logger.debug(f"Verbo principal encontrado: {verb.text if verb else 'Ninguno'}")
    logger.debug(f"Objeto/Complemento encontrado: {obj.text if obj else 'Ninguno'}")
    return results

def check_level_phrase_clause(verb: Optional[spacy.tokens.Token]) -> Dict[str, bool | str]:
    """
    Busca frases preposicionales (obl) o cláusulas adverbiales (advcl)
    asociadas al verbo que indiquen nivel, condición o método.
    IGNORA adverbios simples (advmod) directamente modificando al verbo.
    """
    found = False
    phrase_text = ""
    if not verb:
        return {"found": False, "text": ""}

    relevant_deps = ["obl", "advcl"] # Dependencias que buscamos
    # Podríamos añadir 'acl' (cláusula adjetiva) si modifica al objeto y da nivel

    for child in verb.children:
        # Ignorar adverbios simples directamente modificando el verbo
        if child.dep_ == "advmod" and child.pos_ == "ADV":
            logger.debug(f"Ignorando adverbio simple: {child.text}")
            continue

        # Buscar frases preposicionales o cláusulas adverbiales
        if child.dep_ in relevant_deps:
            # Verificar si la frase/cláusula empieza con un indicador común
            start_token = child if child.dep_ == "advcl" else next(child.subtree, None) # Primer token de la frase/cláusula
            if start_token and start_token.lemma_.lower() in LEVEL_INDICATOR_STARTERS:
                found = True
                phrase_text = " ".join(t.text for t in child.subtree)
                logger.debug(f"Encontrada frase/cláusula de nivel/condición ({child.dep_}): '{phrase_text}'")
                break # Encontrar una es suficiente por ahora

            # Caso especial: "de forma [adjetivo]" o "de manera [adjetivo]"
            elif start_token and start_token.lemma_.lower() in ["de"]:
                 next_token = start_token.nbor(1) if start_token.i + 1 < len(start_token.doc) else None
                 if next_token and next_token.lemma_.lower() in ["forma", "manera"]:
                     adj_token = next_token.nbor(1) if next_token.i + 1 < len(next_token.doc) else None
                     if adj_token and adj_token.pos_ == "ADJ":
                         found = True
                         phrase_text = f"{start_token.text} {next_token.text} {adj_token.text}"
                         logger.debug(f"Encontrada frase/cláusula de nivel/condición (de forma/manera ADJ): '{phrase_text}'")
                         break


    # Podríamos buscar también modificadores del objeto si fuera relevante
    # obj = find_object...
    # if obj:
    #    for child in obj.children:
    #        if child.dep_ == 'acl': # Cláusula adjetiva modificando el objeto
    #             # Analizar si esta cláusula indica un nivel/condición

    return {"found": found, "text": phrase_text}


def check_correction(text: str, nlp_model: spacy.language.Language) -> dict:
    """
    Evalúa la corrección de la formulación de un RA según la rúbrica 0-2.
    Se enfoca en: Verbo claro, Contenido específico, Frase/Cláusula de Nivel/Condición, Claridad general.
    IGNORA adverbios simples como indicadores de nivel.

    Args:
        text: El texto del Resultado de Aprendizaje.
        nlp_model: El modelo de lenguaje spaCy cargado.

    Returns:
        Un diccionario con 'correction_score' (0, 1, o 2) y 'correction_notes'.
    """
    logger.info(f"--- Iniciando check_correction para: '{text}' ---")
    score = 0 # Por defecto, no definido correctamente
    notes = []

    if not text or not isinstance(text, str) or len(text.split()) < 3:
        logger.warning("Texto inválido o demasiado corto.")
        notes.append("Texto inválido o demasiado corto para análisis.")
        return {'correction_score': 0, 'correction_notes': " ".join(notes)}
    if not nlp_model:
         logger.error("Modelo NLP no disponible para check_correction.")
         notes.append('Modelo NLP no disponible.')
         return {'correction_score': 0, 'correction_notes': " ".join(notes)}

    try:
        doc = nlp_model(text)
        tokens = [token for token in doc if not token.is_punct and not token.is_space]

        if len(tokens) < MIN_REASONABLE_LENGTH:
             notes.append(f"Formulación muy breve (menos de {MIN_REASONABLE_LENGTH} palabras significativas).")

        analysis_verb_obj = find_main_verb_and_object(doc)
        verb = analysis_verb_obj["verb"]
        obj = analysis_verb_obj["object"]

        has_verb = verb is not None
        has_object = obj is not None
        is_content_specific = False
        has_level_phrase_clause = False
        level_phrase_text = ""
        is_clear = True # Asumir claridad inicial

        if not has_verb:
            notes.append("No se identificó un verbo de desempeño claro.")
            score = 0
            logger.debug("Resultado: Score 0 (Sin verbo)")
            return {'correction_score': score, 'correction_notes': " ".join(notes)}

        # Si hay verbo, evaluar contenido y frase/cláusula de nivel
        if has_object:
            object_subtree_lemmas = {t.lemma_.lower() for t in obj.subtree}
            if not VAGUE_WORDS.intersection(object_subtree_lemmas) and obj.lemma_.lower() not in VAGUE_WORDS:
                 is_content_specific = True
                 notes.append(f"Verbo '{verb.text}' con contenido específico: '{' '.join(t.text for t in obj.subtree)}'.")
            else:
                notes.append(f"Verbo '{verb.text}' presente, pero el contenido '{' '.join(t.text for t in obj.subtree)}' parece vago o general.")
        else:
            notes.append(f"Verbo '{verb.text}' presente, pero no se identificó un contenido (objeto/complemento) claro.")

        # Buscar frase/cláusula de nivel/condición
        level_check = check_level_phrase_clause(verb)
        has_level_phrase_clause = level_check["found"]
        level_phrase_text = level_check["text"]
        if has_level_phrase_clause:
            notes.append(f"Se identificó frase/cláusula indicando nivel/condición: '{level_phrase_text}'.")
        else:
            notes.append("No se identificó frase/cláusula clara indicando nivel/condición/método.")


        # --- Asignación de Puntuación (0, 1, 2) ---
        if has_verb and has_object and is_content_specific and has_level_phrase_clause and is_clear:
            score = 2 # Todo presente y claro/específico
            notes.append("Formulación clara con verbo, contenido específico y nivel/condición.")
            logger.debug("Resultado: Score 2")
        elif has_verb and (not has_object or not is_content_specific or not has_level_phrase_clause):
             # Si falta CUALQUIERA de los componentes (objeto específico O frase de nivel), es 1
             score = 1
             missing_parts = []
             if not has_object: missing_parts.append("contenido claro")
             elif not is_content_specific: missing_parts.append("contenido específico")
             if not has_level_phrase_clause: missing_parts.append("frase/cláusula de nivel/condición")
             notes.append(f"Presenta limitaciones: falta { ' y '.join(missing_parts) }.")
             logger.debug(f"Resultado: Score 1 (Falta {' y '.join(missing_parts)})")
        # El caso de score 0 ya se manejó si no hay verbo. Si hay verbo pero falta todo lo demás, cae en score 1.
        # Podríamos hacer el score 0 más estricto si falta verbo Y objeto Y nivel?
        elif not has_verb: # Redundante, pero para claridad
             score = 0
             notes.append("Carece de verbo de desempeño claro.")
             logger.debug("Resultado: Score 0 (Sin verbo - verificado de nuevo)")


        # Limpiar notas duplicadas o redundantes
        final_notes = []
        seen_notes = set()
        # Priorizar mensajes clave
        if score == 2: final_notes.append("Formulación clara con verbo, contenido específico y nivel/condición.")
        elif score == 1:
            missing_parts = []
            if not has_object: missing_parts.append("contenido claro")
            elif not is_content_specific: missing_parts.append("contenido específico")
            if not has_level_phrase_clause: missing_parts.append("frase/cláusula de nivel/condición")
            if missing_parts: final_notes.append(f"Presenta limitaciones: falta { ' y '.join(missing_parts) }.")
            else: final_notes.append("Presenta limitaciones en la formulación.") # Nota genérica si no se identificó qué falta
        elif score == 0:
             if not has_verb: final_notes.append("No se identificó un verbo de desempeño claro.")
             else: final_notes.append("Carece de elementos básicos o formulación incorrecta.")

        # Añadir detalles específicos si existen y no son redundantes
        if has_verb: final_notes.append(f"Verbo: '{verb.text}'.")
        if has_object and is_content_specific: final_notes.append(f"Contenido: '{' '.join(t.text for t in obj.subtree)}'.")
        elif has_object: final_notes.append(f"Contenido (vago/general?): '{' '.join(t.text for t in obj.subtree)}'.")
        if has_level_phrase_clause: final_notes.append(f"Nivel/Condición: '{level_phrase_text}'.")


        logger.info(f"--- Resultado final check_correction: Score={score} ---")
        return {'correction_score': score, 'correction_notes': " ".join(list(dict.fromkeys(final_notes)))} # Eliminar duplicados exactos

    except Exception as e:
        logger.error(f"Error en check_correction para texto '{text[:50]}...': {e}", exc_info=True)
        return {'correction_score': 0, 'correction_notes': f'Error durante el análisis de corrección: {e}'}

# --- Ejemplo de uso (opcional, para pruebas) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        nlp = spacy.load("es_core_news_sm")

        test_ras = [
            "Analizar los estados financieros de la empresa X según las normas NIIF.", # Esperado: 2
            "Comprender los conceptos básicos de marketing digital.", # Esperado: 1 (Falta frase/cláusula de nivel)
            "Aplicar técnicas de análisis estadístico utilizando software R.", # Esperado: 2
            "Describir aspectos relevantes.", # Esperado: 1 (Contenido vago, falta frase/cláusula de nivel)
            "Evaluar la situación considerando los riesgos asociados.", # Esperado: 2
            "Marketing.", # Esperado: 0
            "Realizar diversas tareas administrativas de forma eficiente.", # Esperado: 2 ('de forma eficiente' detectado)
            "Identificar los componentes clave del sistema de gestión de calidad.", # Esperado: 1 (Falta frase/cláusula de nivel)
            "El estudiante conocerá los fundamentos.", # Esperado: 1 (Falta frase/cláusula de nivel)
            "Ser capaz de explicar el proceso con claridad.", # Esperado: 2 ('con claridad' detectado)
            "Conocer.", # Esperado: 0
            "Implementar soluciones innovadoras para problemas complejos definidos según criterios de eficiencia.", # Esperado: 2 ('según criterios...' detectado)
            "Redactar informes técnicos correctamente.", # Esperado: 1 (Ignora 'correctamente', falta frase/cláusula)
            "Redactar informes técnicos de acuerdo a la plantilla estándar.", # Esperado: 2
        ]

        print("\n--- Pruebas de Corrección (Escala 0-2, con Frases/Cláusulas Nivel) ---")
        for ra in test_ras:
            result = check_correction(ra, nlp)
            print(f"RA: '{ra}'")
            print(f"Resultado: Score={result['correction_score']}, Notas: {result['correction_notes']}\n")

    except OSError:
        print("\nError: Modelo spaCy 'es_core_news_sm' no encontrado.")
        print("Por favor, instálalo ejecutando: python -m spacy download es_core_news_sm")
    except Exception as e:
        print(f"\nOcurrió un error durante las pruebas: {e}")