import spacy
import logging

# --- Listas de Palabras Clave (Ejemplos iniciales - ¡Necesitan expansión!) ---

# Verbos que tienden a ser más observables (acción física o producto tangible)
OBSERVABLE_VERBS = {
    "identificar", "listar", "nombrar", "describir", "dibujar", "construir",
    "demostrar", "operar", "ejecutar", "implementar", "calcular", "medir",
    "clasificar", "categorizar", "organizar", "comparar", "contrastar",
    "diseñar", "producir", "redactar", "presentar", "exponer", "resolver",
    "aplicar", "utilizar", "manejar", "elaborar", "preparar", "realizar",
    "registrar", "documentar"
}

# Verbos que tienden a ser menos observables (procesos cognitivos internos)
INTERNAL_VERBS = {
    "conocer", "saber", "comprender", "entender", "creer", "pensar",
    "apreciar", "valorar", "sentir", "internalizar", "reconocer", # 'Reconocer' puede ser ambiguo
    "recordar", "memorizar", "asimilar", "interpretar" # 'Interpretar' puede ser ambiguo
}

# Sustantivos/Conceptos que tienden a ser concretos/observables
CONCRETE_NOUNS = {
    "informe", "reporte", "documento", "plan", "propuesta", "diseño",
    "modelo", "maqueta", "prototipo", "diagrama", "gráfico", "tabla",
    "cálculo", "resultado", "presentación", "exposición", "demostración",
    "producto", "artefacto", "código", "programa", "solución", "respuesta",
    "lista", "resumen", "mapa conceptual", "ensayo", "artículo"
}

# Sustantivos/Conceptos que tienden a ser abstractos
ABSTRACT_NOUNS = {
    "comprensión", "conocimiento", "entendimiento", "importancia", "rol",
    "significado", "valor", "apreciación", "conciencia", "principios",
    "conceptos", "teoría", "estructura", "relación", "impacto", "efecto",
    "necesidad", "capacidad", "habilidad", "competencia", "actitud", "estrategia"
}

# Palabras clave que indican cuantificación o estándares
MEASUREMENT_KEYWORDS = {
    "%", "porcentaje", "número", "cantidad", "frecuencia", "nivel", "grado",
    "según", "acuerdo", "norma", "estándar", "criterio", "parámetro",
    "dentro de", "máximo", "mínimo", "al menos", "exactamente", "precisión",
    "eficiencia", "eficacia", "rendimiento", "tasa", "ratio", "comparar con",
    "mejorar", "optimizar", "aumentar", "disminuir"
    # Añadir números como patrones también sería útil (regex)
}

# Palabras clave que pueden indicar subjetividad si no están definidas
SUBJECTIVE_KEYWORDS = {
    "adecuado", "apropiado", "pertinente", "relevante", "efectivo", "eficiente",
    "bueno", "óptimo", "satisfactorio", "correcto", "claro", "coherente",
    "significativo"
}

# --- Función Principal ---

def check_verificability(text: str, nlp_model: spacy.language.Language) -> dict:
    """
    Analiza un texto de RA para estimar su verificabilidad según 3 criterios.

    Args:
        text: El texto del Resultado de Aprendizaje.
        nlp_model: El modelo de lenguaje spaCy cargado.

    Returns:
        Un diccionario con las puntuaciones estimadas (1-5) y una justificación.
        Ej: {'observable_score': 3, 'measurable_score': 4, 'evaluability_score': 3,
             'justification': 'Verbo observable, objeto abstracto, con cuantificador.'}
    """
    if not text or not isinstance(text, str):
        return {
            'observable_score': 1, 'measurable_score': 1, 'evaluability_score': 1,
            'justification': 'Texto de entrada inválido o vacío.'
        }
    if not nlp_model:
         return {
            'observable_score': 1, 'measurable_score': 1, 'evaluability_score': 1,
            'justification': 'Modelo NLP no disponible.'
        }

    try:
        doc = nlp_model(text.lower()) # Procesar en minúsculas para keywords

        # --- Inicialización de Puntuaciones y Justificación ---
        observable_score = 3 # Punto de partida neutro
        measurable_score = 2 # Punto de partida ligeramente bajo (medir suele ser más difícil)
        evaluability_score = 1 # Se calculará al final
        justification_parts = []

        # --- Análisis de Observabilidad ---
        main_verb = None
        direct_object = None
        verb_token = None

        # Encontrar el verbo principal (raíz del documento o verbo auxiliar principal)
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                main_verb = token.lemma_
                verb_token = token
                break
            # Considerar auxiliares si el ROOT no es verbo (ej. "ser capaz de...")
            if token.dep_ == "aux" and token.head.pos_ == "VERB":
                 main_verb = token.head.lemma_
                 verb_token = token.head
                 break
        # Si no se encontró verbo raíz, buscar el primer verbo
        if not main_verb:
             for token in doc:
                 if token.pos_ == "VERB":
                     main_verb = token.lemma_
                     verb_token = token
                     break

        if main_verb:
            justification_parts.append(f"Verbo: '{main_verb}'.")
            if main_verb in OBSERVABLE_VERBS:
                observable_score += 1
                justification_parts.append("Tipo: Observable.")
            elif main_verb in INTERNAL_VERBS:
                observable_score -= 1
                justification_parts.append("Tipo: Interno/Cognitivo.")
            else:
                 justification_parts.append("Tipo: No clasificado claramente.")


            # Encontrar el objeto directo del verbo principal
            if verb_token:
                for child in verb_token.children:
                    if child.dep_ == "dobj" and child.pos_ == "NOUN": # Objeto directo que es sustantivo
                        direct_object = child.lemma_
                        # Buscar si el objeto o sus compuestos están en las listas
                        obj_subtree_text = " ".join([t.lemma_ for t in child.subtree])
                        if any(cn in obj_subtree_text for cn in CONCRETE_NOUNS):
                             observable_score += 1
                             justification_parts.append(f"Objeto ('{direct_object}'): Concreto.")
                             break # Encontrado concreto
                        elif any(an in obj_subtree_text for an in ABSTRACT_NOUNS):
                             observable_score -= 1
                             justification_parts.append(f"Objeto ('{direct_object}'): Abstracto.")
                             break # Encontrado abstracto
                if direct_object and "Objeto" not in " ".join(justification_parts):
                     justification_parts.append(f"Objeto ('{direct_object}'): No clasificado.")


        else:
            justification_parts.append("No se identificó verbo principal claro.")
            observable_score = 1 # Penalizar si no hay verbo claro

        # --- Análisis de Medibilidad ---
        found_measurement = False
        found_subjective = False

        # Buscar palabras clave de medición/cuantificación
        text_lemmas = {token.lemma_ for token in doc}
        measurement_matches = text_lemmas.intersection(MEASUREMENT_KEYWORDS)
        if measurement_matches:
            measurable_score += len(measurement_matches) # Sumar puntos por cada tipo encontrado
            justification_parts.append(f"Indicadores de medida: {', '.join(measurement_matches)}.")
            found_measurement = True

        # Buscar números explícitos (simplificado)
        if any(token.like_num for token in doc):
             measurable_score += 1
             justification_parts.append("Presencia de números.")
             found_measurement = True

        # Buscar palabras clave subjetivas
        subjective_matches = text_lemmas.intersection(SUBJECTIVE_KEYWORDS)
        if subjective_matches:
             # Penalizar solo si no hay indicadores claros de medida que los definan
             if not found_measurement:
                 measurable_score -= 1
                 justification_parts.append(f"Términos subjetivos sin definir: {', '.join(subjective_matches)}.")
             else:
                 justification_parts.append(f"Términos subjetivos presentes: {', '.join(subjective_matches)}.")
             found_subjective = True

        if not found_measurement and not found_subjective:
             justification_parts.append("No se encontraron indicadores claros de medida o subjetividad.")
        elif not found_measurement and found_subjective:
             measurable_score = max(1, measurable_score -1) # Penalizar más si solo hay subjetividad


        # --- Ajustar y Calcular Puntuaciones Finales ---
        observable_score = max(1, min(5, observable_score)) # Asegurar rango 1-5
        measurable_score = max(1, min(5, measurable_score)) # Asegurar rango 1-5

        # Calcular Evaluabilidad (como mínimo de las otras dos)
        evaluability_score = min(observable_score, measurable_score)

        final_justification = " ".join(justification_parts)

        return {
            'observable_score': observable_score,
            'measurable_score': measurable_score,
            'evaluability_score': evaluability_score,
            'justification': final_justification
        }

    except Exception as e:
        logging.error(f"Error en check_verificability para texto '{text[:50]}...': {e}", exc_info=True)
        return {
            'observable_score': 1, 'measurable_score': 1, 'evaluability_score': 1,
            'justification': f'Error durante el análisis: {e}'
        }

# --- Ejemplo de uso (opcional, para pruebas) ---
if __name__ == '__main__':
    # Asegúrate de tener spaCy y el modelo español instalado:
    # pip install spacy
    # python -m spacy download es_core_news_sm
    try:
        nlp = spacy.load("es_core_news_sm") # o es_core_news_md / lg para más precisión

        test_ras = [
            "Comprender la importancia del liderazgo en las organizaciones.", # Bajo O, Bajo M
            "Listar tres características clave de un líder efectivo.", # Alto O, Medio M
            "Aplicar la técnica de análisis FODA para evaluar un caso de negocio específico.", # Alto O, Alto M
            "Diseñar un plan de marketing detallado con un presupuesto máximo de 5000 euros.", # Muy Alto O, Muy Alto M
            "Valorar adecuadamente las diferentes teorías de motivación.", # Bajo O, Bajo M
            "Redactar un informe claro y coherente." # Medio O, Bajo M (subjetivo)
        ]

        for ra in test_ras:
            result = check_verificability(ra, nlp)
            print(f"RA: {ra}")
            print(f"Resultado: {result}\n")

    except OSError:
        print("Error: Modelo spaCy 'es_core_news_sm' no encontrado.")
        print("Por favor, instálalo ejecutando: python -m spacy download es_core_news_sm")
    except Exception as e:
        print(f"Ocurrió un error: {e}")