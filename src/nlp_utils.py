import spacy
import re
import logging
import streamlit as st # Necesario para el decorador @st.cache_resource

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Carga del Modelo spaCy (con Caché) ---

def load_spacy_model_internal(model_name="es_core_news_sm"):
    """
    Función interna para cargar el modelo spaCy.
    Llamada por la versión cacheada.
    """
    nlp = None
    logging.info(f"Intentando cargar modelo spaCy '{model_name}'...")
    try:
        nlp = spacy.load(model_name)
        logging.info(f"Modelo spaCy '{model_name}' cargado exitosamente.")
    except OSError:
        logging.warning(f"Modelo '{model_name}' no encontrado localmente. Intentando descargar...")
        try:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name) # Intentar cargar de nuevo después de descargar
            logging.info(f"Modelo spaCy '{model_name}' descargado y cargado exitosamente.")
        except Exception as e:
            logging.error(f"Error CRÍTICO al descargar o cargar el modelo '{model_name}': {e}", exc_info=True)
            logging.error("Asegúrate de tener conexión a internet y permisos, o ejecuta manualmente:")
            logging.error(f"python -m spacy download {model_name}")
            st.error(f"No se pudo descargar ni cargar el modelo spaCy '{model_name}'. La aplicación no funcionará correctamente. Intenta instalarlo manualmente.")
            nlp = None # Asegura que sigue siendo None si falla
    except Exception as e:
         logging.error(f"Error inesperado al cargar el modelo '{model_name}': {e}", exc_info=True)
         st.error(f"Error inesperado al cargar el modelo spaCy '{model_name}'.")
         nlp = None # Asegura que sigue siendo None si falla
    return nlp

@st.cache_resource # Cachear el modelo cargado
def load_spacy_model(model_name="es_core_news_sm"):
    """
    Carga y cachea el modelo de spaCy especificado usando Streamlit.
    """
    logging.info("Ejecutando cached_load_spacy_model (debería ocurrir solo si la caché expira o es la primera vez)...")
    return load_spacy_model_internal(model_name)

# --- Funciones de Procesamiento de Texto ---

def clean_text(text):
    """
    Limpia el texto: convierte a minúsculas y elimina espacios extra.
    """
    if not isinstance(text, str):
        return "" # Devuelve cadena vacía si no es texto
    text = text.lower() # Convertir a minúsculas
    text = re.sub(r'\s+', ' ', text).strip() # Reemplazar múltiples espacios con uno solo y quitar los de los extremos
    return text

def find_main_verb(doc):
    """
    Encuentra el verbo principal (lema en minúsculas) en un documento spaCy procesado.
    Prioriza el verbo raíz (ROOT), luego busca otros verbos no auxiliares.
    """
    if not doc:
        return None

    root_verb = None
    first_verb = None

    for token in doc:
        # Buscar el verbo raíz (suele ser el principal)
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            root_verb = token.lemma_.lower()
            logging.debug(f"Verbo ROOT encontrado: '{token.text}' (Lema: '{root_verb}')")
            # Si el verbo raíz es infinitivo (termina en ar, er, ir), usarlo directamente
            if root_verb.endswith(('ar', 'er', 'ir')):
                 return root_verb
            # Si no es infinitivo, seguir buscando por si hay un infinitivo antes que sea mejor candidato

        # Guardar el primer verbo encontrado que no sea auxiliar, por si no hay ROOT claro
        if first_verb is None and token.pos_ == "VERB" and token.dep_ != "aux":
             # Verificar si es infinitivo
             lemma = token.lemma_.lower()
             if lemma.endswith(('ar', 'er', 'ir')):
                first_verb = lemma
                logging.debug(f"Primer verbo infinitivo no auxiliar encontrado: '{token.text}' (Lema: '{first_verb}')")


    # Decidir qué verbo devolver
    if root_verb and root_verb.endswith(('ar', 'er', 'ir')):
        logging.debug(f"Devolviendo verbo ROOT infinitivo: '{root_verb}'")
        return root_verb
    elif first_verb: # Si encontramos un infinitivo no auxiliar antes (o en lugar) del ROOT
        logging.debug(f"Devolviendo primer verbo infinitivo no auxiliar: '{first_verb}'")
        return first_verb
    elif root_verb: # Si el ROOT no era infinitivo y no hubo otro infinitivo antes
        logging.debug(f"Devolviendo verbo ROOT (no infinitivo): '{root_verb}'")
        return root_verb
    else:
        # Si no se encontró ni ROOT ni otro verbo adecuado
        logging.warning(f"No se encontró un verbo principal claro en el Doc: '{doc.text}'")
        return None


# --- Bloque para Pruebas (Opcional) ---
if __name__ == '__main__':
    # Este bloque solo se ejecuta si corres el script directamente (python src/nlp_utils.py)

    print("-" * 30)
    print("Iniciando pruebas directas de nlp_utils:")
    print("-" * 30)

    # Probar carga de modelo
    print("Probando carga de modelo...")
    nlp = load_spacy_model() # Usa la versión cacheada (aunque la caché no aplica fuera de Streamlit)
    if nlp:
        print("Modelo cargado exitosamente para prueba.")

        # Probar limpieza de texto
        print("\nProbando clean_text...")
        test_text = "  Esto   ES uNa pRUeba  con   Espacios  EXTRA.  "
        cleaned = clean_text(test_text)
        print(f"Original: '{test_text}'")
        print(f"Limpio:   '{cleaned}'")

        # Probar búsqueda de verbo
        print("\nProbando find_main_verb...")
        ejemplos_verbos = [
            "Analizar el impacto de las decisiones financieras.",
            "El estudiante podrá definir los conceptos básicos.",
            "Se deben evaluar proyectos empresariales.",
            "Generando propuestas innovadoras.", # Gerundio como ROOT
            "Correr rápidamente por el parque.",
            "Memorizar es importante.",
            "Texto sin verbo claro."
        ]
        for texto in ejemplos_verbos:
            doc_test = nlp(clean_text(texto))
            verbo = find_main_verb(doc_test)
            print(f"Texto: '{texto}' -> Verbo encontrado: '{verbo}'")

    else:
        print("Fallo al cargar el modelo. Las pruebas no pueden continuar.")