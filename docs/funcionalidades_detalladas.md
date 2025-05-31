# Funcionalidades Detalladas: Analizador de Resultados de Aprendizaje

Este documento detalla las funcionalidades clave de la aplicación de análisis de Resultados de Aprendizaje (RdA).

## 1. Funcionalidad Principal: Análisis Integral de un Resultado de Aprendizaje o varios Resultados de Aprendizaje.

La aplicación permite al usuario ingresar el o los Resultados de Aprendizaje (RdA) en formato de texto como en formato archivo estructurado (tabla) para su análisis exhaustivo a través de cuatro dimensiones críticas.

*   **Entrada:**
    *   Un campo de texto en la interfaz web donde el usuario puede escribir o pegar el/los RdA.
*   **Proceso de Activación:**
    *   Un botón (ej. "Analizar ") que, al ser presionado, inicia el proceso de análisis.
*   **Salida (Visualización en Interfaz):**
    *   La interfaz muestra una sección de resultados para cada una de las dimensiones analizadas, presentando:
        *   `Resultados de Analisis detallado` por Rda con Una puntuación o clasificación.
        *   Comentarios específicos o retroalimentación.
        *   Sugerencias de mejora (cuando aplique).
        *   Un `Resumen General` del análisis realizado (frecuencias o promedios de las dimensiones analizadas).
        *   Rdas que no cumplen con los criterios de análisis, si los hay (`RdAs que requieren atención`-en todas las dimensiones).

## 2. Detalle de las Dimensiones de Análisis

### 2.1. Análisis según Taxonomía de Bloom (Dimensión Cognitiva)

*   **Objetivo:** Identificar y clasificar el nivel de proceso cognitivo que el RdA demanda del estudiante, según la taxonomía revisada de Bloom (Anderson y Krathwohl: Recordar, Comprender, Aplicar, Analizar, Evaluar, Crear).
*   **Método (General):**
    *   El módulo `bloom_analyzer.py` procesa el texto del RdA.
    *   Identifica los verbos principales y los compara con listas de verbos asociados (`taxonomy_bloom.json`) a cada nivel cognitivo.
    *   Puede considerar la estructura de la frase para refinar la clasificación.
*   **Salida Específica:**
    *   El nivel cognitivo identificado (ej. "Aplicar").
    *   Posiblemente, el verbo clave que llevó a esa clasificación.

### 2.2. Análisis de Verificabilidad

*   **Objetivo:** Evaluar si el RdA está redactado de tal forma que su consecución pueda ser verificada a través de evidencias observables y medibles.
*   **Método (General):**
    *   El módulo `verificability_analyzer.py` examina:
        *   La presencia de verbos de acción claros y observables.
        *   La especificidad del resultado esperado.
        *   La ausencia de ambigüedades que dificulten la evaluación.
*   **Salida Específica:**
    *   Una puntuación o indicador de verificabilidad (ej. "Alto", "Medio", "Bajo", o un puntaje numérico).
    *   Comentarios sobre por qué se asigna esa evaluación (ej. "El verbo 'comprender' es difícil de observar directamente. Considere usar verbos como 'explicar', 'resumir', 'comparar'.").

### 2.3. Análisis de Corrección (Lingüística y Estructural)

*   **Objetivo:** Revisar la calidad de la redacción del RdA en términos de corrección gramatical, claridad, concisión y estructura sintáctica adecuada.
*   **Método (General):**
    *   El módulo `correction_analyzer.py` utiliza herramientas de NLP para:
        *   Detectar posibles errores gramaticales o de ortografía.
        *   Evaluar la complejidad de la frase.
        *   Identificar frases pasivas o construcciones ambiguas.
*   **Salida Específica:**
    *   Indicadores de corrección (ej. "Buena redacción", "Requiere revisión").
    *   Señalamiento de posibles errores o áreas de mejora (ej. "Frase demasiado larga", "Posible error de concordancia").

### 2.4. Análisis de Autenticidad

*   **Objetivo:** Valorar la relevancia, pertinencia y adecuación contextual del RdA. Se busca que el aprendizaje propuesto sea significativo y aplicable.
*   **Método (General):**
    *   El módulo `authenticity_analyzer.py` puede considerar:
        *   La conexión del RdA con contextos reales o profesionales (inferido en base a la rúbrica).
        *   La adecuación al nivel educativo o perfil del estudiante (si se proporciona esta información o se infiere).
        *   La alineación con competencias más amplias (`professional_keywords.json`).
*   **Salida Específica:**
    *   Una evaluación cualitativa o cuantitativa de la autenticidad.
    *   Comentarios sobre la aplicabilidad o relevancia del RdA.

## 3. Otras Funcionalidades 

*   *   **Descarga de Reporte**
    *   **Descripción:** "La aplicación permite al usuario descargar un resumen del Análisis detallado del RdA y un Resumen Generalen formato xlsx.".
    *   **Acceso:** "Un botón 'Descargar Analisis Detallado' y otro botón 'Descargar Resumen General' aparece después de completar el análisis visualmente identificables.".