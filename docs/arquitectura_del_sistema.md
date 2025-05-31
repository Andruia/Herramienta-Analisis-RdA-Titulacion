# Arquitectura del Sistema: Analizador de Resultados de Aprendizaje

Este documento describe la arquitectura de alto nivel de la aplicación de análisis de Resultados de Aprendizaje (RdA) desarrollada con Streamlit.

## 1. Componentes Principales

El sistema está compuesto por los siguientes módulos y componentes clave:

*   **Interfaz de Usuario (Frontend - Streamlit):**
    *   **Archivo:** `src/app.py`
    *   **Responsabilidad:** Proporcionar la interfaz web interactiva para el usuario. Permite la entrada del texto del RdA, la activación del proceso de análisis y la visualización de los resultados y la retroalimentación generada.
    *   **Tecnología:** Streamlit.

*   **Orquestador Lógico (Backend - dentro de `src/app.py`):**
    *   **Archivo:** Integrado principalmente en `src/app.py` (en las funciones que se llaman tras la interacción del usuario).
    *   **Responsabilidad:**
        *   Recibir el RdA ingresado por el usuario a través de la interfaz.
        *   Invocar secuencialmente a cada uno de los módulos de análisis especializados.
        *   Recopilar y agregar los resultados de cada analizador.
        *   Formatear los resultados consolidados para su presentación en la interfaz de Streamlit.

*   **Módulos de Análisis Especializados (Backend - NLP):**
    *   Estos módulos contienen la lógica específica para evaluar el RdA según cada criterio. Utilizan bibliotecas de Procesamiento de Lenguaje Natural (NLP) como spaCy y NLTK.
    *   **Módulo de Análisis de Taxonomía de Anderson:**
        *   **Archivo:** `src/bloom_analyzer.py` (o el nombre que le haya dado)
        *   **Responsabilidad:** Identificar el nivel cognitivo del RdA según la Taxonomía de Bloom (revisada por Anderson y Krathwohl), basándose en los verbos y la estructura de la frase.
    *   **Módulo de Análisis de Verificabilidad:**
        *   **Archivo:** `src/verificability_analyzer.py`
        *   **Responsabilidad:** Evaluar si el RdA está formulado de manera que su logro sea observable y medible.
    *   **Módulo de Análisis de Corrección:**
        *   **Archivo:** `src/correction_analyzer.py`
        *   **Responsabilidad:** Analizar la corrección gramatical, la claridad y la estructura sintáctica del RdA.
    *   **Módulo de Análisis de Autenticidad:**
        *   **Archivo:** `src/authenticity_analyzer.py`
        *   **Responsabilidad:** Evaluar la relevancia y adecuación contextual del RdA.

*   **Bibliotecas de NLP y Recursos:**
    *   **spaCy:** Utilizada para tokenización, lematización, análisis sintáctico, reconocimiento de entidades, y carga de modelos de lenguaje pre-entrenados (ej. `es_core_news_sm`).
    *   **NLTK:** Utilizada para tareas complementarias de NLP, como acceso a corpus, tokenizadores específicos, etc.
    *   **Diccionarios/Listas Personalizadas:** Archivos de datos internos (ej. listas de verbos de Bloom, palabras clave) utilizados por los analizadores, ubicados en `data/`.

## 2. Flujo de Datos y Proceso General

1.  **Entrada del Usuario:** El usuario ingresa el texto de un Resultado de Aprendizaje en la interfaz web (Streamlit - `app.py`).
2.  **Activación del Análisis:** El usuario acciona un botón (ej. "Analizar RdA").
3.  **Procesamiento en `app.py`:**
    *   La función controladora en `app.py` recibe el texto del RdA.
    *   Se invoca al `bloom_analyzer.py` con el texto del RdA.
    *   Se invoca al `verificability_analyzer.py` con el texto del RdA.
    *   Se invoca al `correction_analyzer.py` con el texto del RdA.
    *   Se invoca al `authenticity_analyzer.py` con el texto del RdA.
4.  **Análisis Individual:** Cada módulo analizador procesa el texto utilizando sus reglas específicas y las bibliotecas NLP, generando una evaluación y/o retroalimentación para su criterio particular.
5.  **Agregación de Resultados:** `app.py` recopila los resultados de todos los módulos analizadores.
6.  **Presentación de Resultados:** `app.py` formatea y muestra los resultados consolidados (puntuaciones, comentarios, sugerencias) en la interfaz de Streamlit para que el usuario los vea.

## 3. Diagrama de Arquitectura

Para una representación visual de esta arquitectura, consulte el archivo:
`diagrama_arquitectura.png` en esta misma carpeta (`/docs/`).